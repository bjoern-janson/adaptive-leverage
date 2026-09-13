from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from hashlib import sha256
import json
from typing import Mapping

from adaptive_leverage.interventions import apply_valid_scope_closure
from adaptive_leverage.model import (
    A0,
    W_N,
    ImplementationError,
    MachineState,
    canonical_state_bytes,
    run_dynamic_episode,
)
from adaptive_leverage.v1.episodes import run_v1_normal_episode
from adaptive_leverage.v1.mechanisms import (
    CustodyCheck,
    MechanismArtifact,
    MechanismCustodyRecord,
    MechanismKind,
    mechanism_artifact_sha256,
)
from adaptive_leverage.v1.trace import V1TraceEvent, build_v1_trace, validate_v1_trace


@dataclass(frozen=True)
class V1ArmBundle:
    c: MachineState
    b: MachineState
    p: MachineState
    t: MachineState
    e: MachineState
    prefork_serialized: dict[str, bytes]


@dataclass(frozen=True)
class NormalObservation:
    arm: str
    action: str
    correctness: bool
    cost: int
    trace: tuple[V1TraceEvent, ...]
    mechanism_artifact_sha256: str | None


class JointAdmissionReason(str, Enum):
    CUSTODY_FAILURE = "CUSTODY_FAILURE"
    OPTIMIZATION_LEAKAGE = "OPTIMIZATION_LEAKAGE"
    NORMAL_CORRECTNESS_MISMATCH = "NORMAL_CORRECTNESS_MISMATCH"
    COST_MISMATCH = "COST_MISMATCH"
    MECHANISM_FINALIZATION_FAILURE = "MECHANISM_FINALIZATION_FAILURE"


@dataclass(frozen=True)
class CorrectiveReleaseToken:
    b_artifact_sha256: str
    p_artifact_sha256: str
    t_artifact_sha256: str
    admission_sha256: str


@dataclass(frozen=True)
class JointAdmission:
    passed: bool
    reason: JointAdmissionReason | None
    release_token: CorrectiveReleaseToken | None
    admitted_artifact_hashes: tuple[tuple[str, str], ...]


def fork_v1_arms(m0: MachineState) -> V1ArmBundle:
    snapshot = canonical_state_bytes(m0)
    prefork = {arm: bytes(snapshot) for arm in ("C", "B", "P", "T", "E")}
    installed = replace(m0, compiled_mode=1)
    return V1ArmBundle(
        c=m0,
        b=installed,
        p=installed,
        t=installed,
        e=apply_valid_scope_closure(m0),
        prefork_serialized=prefork,
    )


def measure_v1_normal(
    arm: str,
    state: MachineState,
    artifact: MechanismArtifact | None,
    mechanism_artifact_sha256_value: str | None,
) -> NormalObservation:
    if arm in {"B", "P", "T"}:
        if artifact is None or mechanism_artifact_sha256_value is None:
            raise ImplementationError(f"{arm} normal measurement requires finalized mechanism")
        expected_kind = {"B": MechanismKind.B, "P": MechanismKind.P, "T": MechanismKind.T}[arm]
        if artifact.kind is not expected_kind:
            raise ImplementationError(f"{arm} mechanism identity mismatch")
        if mechanism_artifact_sha256(artifact) != mechanism_artifact_sha256_value:
            raise ImplementationError(f"{arm} finalized mechanism hash mismatch")
        episode = run_v1_normal_episode(state, artifact)
    elif arm in {"C", "E"}:
        if artifact is not None or mechanism_artifact_sha256_value is not None:
            raise ImplementationError(f"{arm} control must not bind a V1 mechanism artifact")
        episode = run_dynamic_episode(W_N, state)
    else:
        raise ImplementationError(f"unknown V1 arm: {arm!r}")

    trace = build_v1_trace(
        episode,
        arm=arm,
        run_id=f"software-normal-{arm.lower()}",
        mechanism_artifact_sha256=mechanism_artifact_sha256_value,
    )
    validate_v1_trace(trace)
    return NormalObservation(
        arm=arm,
        action=episode.action,
        correctness=episode.action == A0,
        cost=len(trace),
        trace=trace,
        mechanism_artifact_sha256=mechanism_artifact_sha256_value,
    )


def _expected_hashes(
    built: Mapping[MechanismKind, tuple[MechanismArtifact, MechanismCustodyRecord]],
) -> tuple[tuple[str, str], ...]:
    pairs: list[tuple[str, str]] = []
    for arm, kind in (("B", MechanismKind.B), ("P", MechanismKind.P), ("T", MechanismKind.T)):
        if kind not in built:
            raise ImplementationError(f"missing finalized mechanism: {arm}")
        artifact, record = built[kind]
        digest = mechanism_artifact_sha256(artifact)
        if artifact.kind is not kind or record.mechanism_kind != kind.value:
            raise ImplementationError(f"finalized mechanism identity mismatch: {arm}")
        if record.finalized_artifact_sha256 != digest:
            raise ImplementationError(f"finalized mechanism hash mismatch: {arm}")
        pairs.append((arm, digest))
    return tuple(pairs)


def _admission_digest(hashes: tuple[tuple[str, str], ...]) -> str:
    payload = {
        "admission": "JOINT_ADMISSION_PASS",
        "artifacts": {arm: digest for arm, digest in hashes},
        "required_cost": 5,
        "required_normal_action": A0,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def _failed(reason: JointAdmissionReason) -> JointAdmission:
    return JointAdmission(
        passed=False,
        reason=reason,
        release_token=None,
        admitted_artifact_hashes=(),
    )


def joint_admit(
    baseline: NormalObservation,
    observations: Mapping[str, NormalObservation],
    custody: Mapping[str, CustodyCheck],
    built: Mapping[MechanismKind, tuple[MechanismArtifact, MechanismCustodyRecord]],
) -> JointAdmission:
    try:
        hashes = _expected_hashes(built)
    except ImplementationError:
        return _failed(JointAdmissionReason.MECHANISM_FINALIZATION_FAILURE)

    if len({digest for _, digest in hashes}) != 3:
        return _failed(JointAdmissionReason.MECHANISM_FINALIZATION_FAILURE)
    sequences = [built[kind][1].finalization_sequence for kind in MechanismKind]
    if len(set(sequences)) != 3 or any(sequence <= 0 for sequence in sequences):
        return _failed(JointAdmissionReason.MECHANISM_FINALIZATION_FAILURE)

    for arm in ("B", "P", "T"):
        check = custody.get(arm)
        if check is None or not check.passed:
            if check is not None and check.reason == "OPTIMIZATION_LEAKAGE":
                return _failed(JointAdmissionReason.OPTIMIZATION_LEAKAGE)
            return _failed(JointAdmissionReason.CUSTODY_FAILURE)

    if baseline.arm != "C" or baseline.action != A0 or not baseline.correctness:
        return _failed(JointAdmissionReason.NORMAL_CORRECTNESS_MISMATCH)
    if baseline.cost != 6:
        return _failed(JointAdmissionReason.COST_MISMATCH)

    hash_by_arm = dict(hashes)
    for arm in ("B", "P", "T"):
        observation = observations.get(arm)
        if observation is None:
            return _failed(JointAdmissionReason.NORMAL_CORRECTNESS_MISMATCH)
        if observation.mechanism_artifact_sha256 != hash_by_arm[arm]:
            return _failed(JointAdmissionReason.MECHANISM_FINALIZATION_FAILURE)
        if observation.action != baseline.action or observation.correctness != baseline.correctness:
            return _failed(JointAdmissionReason.NORMAL_CORRECTNESS_MISMATCH)

    if any(observations[arm].cost != 5 for arm in ("B", "P", "T")):
        return _failed(JointAdmissionReason.COST_MISMATCH)

    digest = _admission_digest(hashes)
    token = CorrectiveReleaseToken(
        b_artifact_sha256=hash_by_arm["B"],
        p_artifact_sha256=hash_by_arm["P"],
        t_artifact_sha256=hash_by_arm["T"],
        admission_sha256=digest,
    )
    return JointAdmission(
        passed=True,
        reason=None,
        release_token=token,
        admitted_artifact_hashes=hashes,
    )


def require_corrective_release(
    token: CorrectiveReleaseToken | None,
    built: Mapping[MechanismKind, tuple[MechanismArtifact, MechanismCustodyRecord]],
) -> None:
    if token is None:
        raise ImplementationError("V1 corrective condition has not been jointly released")
    try:
        hashes = _expected_hashes(built)
    except ImplementationError as exc:
        raise ImplementationError("V1 corrective release artifact mismatch") from exc
    hash_by_arm = dict(hashes)
    if (
        token.b_artifact_sha256 != hash_by_arm["B"]
        or token.p_artifact_sha256 != hash_by_arm["P"]
        or token.t_artifact_sha256 != hash_by_arm["T"]
        or token.admission_sha256 != _admission_digest(hashes)
    ):
        raise ImplementationError("V1 corrective release token mismatch")
