from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from enum import Enum
from hashlib import sha256
import json

from adaptive_leverage.model import (
    A0,
    E_N,
    OMEGA_STAR,
    O_N,
    W_N,
    AuthorityStatus,
    ImplementationError,
    MachineState,
    PolicyMode,
    WarrantStatus,
)


class MechanismKind(str, Enum):
    B = "T_B_AUTHORITY_INSENSITIVE_DOWNSTREAM"
    P = "T_P_AUTHORITY_SENSITIVE_DOWNSTREAM_FALLBACK"
    T = "T_T_UPSTREAM_PROTECTED_AUTHORITY_STATE"


@dataclass(frozen=True)
class NormalTranscript:
    world: str
    observation: str
    evidence: str
    context: str
    action: str
    baseline_cost: int
    edge_sequence: tuple[str, ...]
    warrant_status: str
    authority_status: str
    policy_mode: str


@dataclass(frozen=True)
class ObjectiveSpec:
    preserve_normal_correctness: bool
    optimize_metric: str
    direction: str


@dataclass(frozen=True)
class MechanismArtifact:
    kind: MechanismKind
    optimization_site: str
    key_fields: tuple[str, ...]
    key_values: tuple[str, ...]
    normal_action: str
    normal_policy_mode: str
    compiled_observation: str | None
    compiled_evidence: str | None
    represented_source_edges: tuple[str, ...]
    protected_semantic_classes: tuple[str, ...]
    generic_mismatch_fallback: bool


@dataclass(frozen=True)
class MechanismCustodyRecord:
    mechanism_kind: str
    normal_manifest_json: str
    normal_input_hashes: tuple[tuple[str, str], ...]
    normal_manifest_sha256: str
    objective_json: str
    objective_sha256: str
    forbidden_artifact_manifest: tuple[str, ...]
    transformation_rule_sha256: str
    finalized_artifact_sha256: str
    finalization_sequence: int
    construction_log: tuple[str, ...]


@dataclass(frozen=True)
class CustodyCheck:
    passed: bool
    reason: str


_FORBIDDEN_CONSTRUCTION_TOKENS = (
    "w_c",
    "o_c",
    "e_star",
    "c_star",
    "a1",
    "CORRECTION",
    "CORR_AUTH",
    "corrective_replay_trace",
    "v1_corrective_outcome",
    "partial_v1_corrective_outcome",
)


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def frozen_normal_transcript() -> NormalTranscript:
    return NormalTranscript(
        world=W_N,
        observation=O_N,
        evidence=E_N,
        context=OMEGA_STAR,
        action=A0,
        baseline_cost=6,
        edge_sequence=("E1", "E2", "E3", "E4", "E5", "E6"),
        warrant_status=WarrantStatus.BASE.value,
        authority_status=AuthorityStatus.BASE_AUTH.value,
        policy_mode=PolicyMode.BASE.value,
    )


def frozen_objective() -> ObjectiveSpec:
    return ObjectiveSpec(
        preserve_normal_correctness=True,
        optimize_metric="causal_micro_transition_cost",
        direction="minimize",
    )


def _normal_payload(normal: NormalTranscript) -> dict[str, object]:
    return {
        "action": normal.action,
        "authority_status": normal.authority_status,
        "baseline_cost": normal.baseline_cost,
        "context": normal.context,
        "edge_sequence": list(normal.edge_sequence),
        "evidence": normal.evidence,
        "observation": normal.observation,
        "policy_mode": normal.policy_mode,
        "warrant_status": normal.warrant_status,
        "world": normal.world,
    }


def _objective_payload(objective: ObjectiveSpec) -> dict[str, object]:
    return asdict(objective)


def mechanism_artifact_payload(artifact: MechanismArtifact) -> dict[str, object]:
    return {
        "compiled_evidence": artifact.compiled_evidence,
        "compiled_observation": artifact.compiled_observation,
        "generic_mismatch_fallback": artifact.generic_mismatch_fallback,
        "key_fields": list(artifact.key_fields),
        "key_values": list(artifact.key_values),
        "kind": artifact.kind.value,
        "normal_action": artifact.normal_action,
        "normal_policy_mode": artifact.normal_policy_mode,
        "optimization_site": artifact.optimization_site,
        "protected_semantic_classes": list(artifact.protected_semantic_classes),
        "represented_source_edges": list(artifact.represented_source_edges),
    }


def mechanism_artifact_sha256(artifact: MechanismArtifact) -> str:
    return _sha256_text(_canonical_json(mechanism_artifact_payload(artifact)))


def _artifact_for(kind: MechanismKind, normal: NormalTranscript) -> MechanismArtifact:
    if kind is MechanismKind.B:
        return MechanismArtifact(
            kind=kind,
            optimization_site="DOWNSTREAM_E5_E6",
            key_fields=("context",),
            key_values=(normal.context,),
            normal_action=normal.action,
            normal_policy_mode=normal.policy_mode,
            compiled_observation=None,
            compiled_evidence=None,
            represented_source_edges=("E5", "E6"),
            protected_semantic_classes=(),
            generic_mismatch_fallback=True,
        )
    if kind is MechanismKind.P:
        return MechanismArtifact(
            kind=kind,
            optimization_site="DOWNSTREAM_E5_E6",
            key_fields=("context", "authority_identity"),
            key_values=(normal.context, normal.authority_status),
            normal_action=normal.action,
            normal_policy_mode=normal.policy_mode,
            compiled_observation=None,
            compiled_evidence=None,
            represented_source_edges=("E5", "E6"),
            protected_semantic_classes=(),
            generic_mismatch_fallback=True,
        )
    if kind is MechanismKind.T:
        return MechanismArtifact(
            kind=kind,
            optimization_site="UPSTREAM_E1_E2",
            key_fields=("world", "context"),
            key_values=(normal.world, normal.context),
            normal_action=normal.action,
            normal_policy_mode=normal.policy_mode,
            compiled_observation=normal.observation,
            compiled_evidence=normal.evidence,
            represented_source_edges=("E1", "E2"),
            protected_semantic_classes=("AUTHORITY_TO_CONSEQUENTIAL_STATE",),
            generic_mismatch_fallback=True,
        )
    raise ImplementationError(f"unknown V1 mechanism kind: {kind!r}")


def construct_mechanism(
    kind: MechanismKind,
    normal: NormalTranscript,
    objective: ObjectiveSpec,
    *,
    finalization_sequence: int,
) -> tuple[MechanismArtifact, MechanismCustodyRecord]:
    if normal != frozen_normal_transcript():
        raise ImplementationError("V1 mechanism input must equal frozen X_normal")
    if objective != frozen_objective():
        raise ImplementationError("V1 mechanism objective must equal frozen J")
    if finalization_sequence <= 0:
        raise ImplementationError("finalization_sequence must be positive")

    normal_payload = _normal_payload(normal)
    objective_payload = _objective_payload(objective)
    normal_json = _canonical_json(normal_payload)
    objective_json = _canonical_json(objective_payload)

    construction_text = normal_json + "\n" + objective_json
    if any(token in construction_text for token in _FORBIDDEN_CONSTRUCTION_TOKENS):
        raise ImplementationError("forbidden corrective artifact present in V1 construction inputs")

    artifact = _artifact_for(kind, normal)
    artifact_hash = mechanism_artifact_sha256(artifact)
    input_hashes = tuple(
        (key, _sha256_text(_canonical_json({key: normal_payload[key]})))
        for key in sorted(normal_payload)
    )
    record = MechanismCustodyRecord(
        mechanism_kind=kind.value,
        normal_manifest_json=normal_json,
        normal_input_hashes=input_hashes,
        normal_manifest_sha256=_sha256_text(normal_json),
        objective_json=objective_json,
        objective_sha256=_sha256_text(objective_json),
        forbidden_artifact_manifest=_FORBIDDEN_CONSTRUCTION_TOKENS,
        transformation_rule_sha256=artifact_hash,
        finalized_artifact_sha256=artifact_hash,
        finalization_sequence=finalization_sequence,
        construction_log=(
            "NORMAL_WORKLOAD_ONLY",
            "COMMON_OBJECTIVE_J",
            "FINALIZED_BEFORE_CORRECTIVE_RELEASE",
        ),
    )
    return artifact, record


def validate_mechanism_custody(
    record: MechanismCustodyRecord,
    artifact: MechanismArtifact,
) -> CustodyCheck:
    expected_normal = frozen_normal_transcript()
    expected_objective = frozen_objective()
    normal_payload = _normal_payload(expected_normal)
    objective_payload = _objective_payload(expected_objective)
    normal_json = _canonical_json(normal_payload)
    objective_json = _canonical_json(objective_payload)

    if any(token in (record.normal_manifest_json + "\n" + record.objective_json) for token in _FORBIDDEN_CONSTRUCTION_TOKENS):
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    if record.forbidden_artifact_manifest != _FORBIDDEN_CONSTRUCTION_TOKENS:
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    if record.mechanism_kind != artifact.kind.value:
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    if record.normal_manifest_json != normal_json:
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    if record.normal_manifest_sha256 != _sha256_text(normal_json):
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    expected_input_hashes = tuple(
        (key, _sha256_text(_canonical_json({key: normal_payload[key]})))
        for key in sorted(normal_payload)
    )
    if record.normal_input_hashes != expected_input_hashes:
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    if record.objective_json != objective_json:
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    if record.objective_sha256 != _sha256_text(objective_json):
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    expected_artifact = _artifact_for(artifact.kind, expected_normal)
    if artifact != expected_artifact:
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    artifact_hash = mechanism_artifact_sha256(artifact)
    if record.transformation_rule_sha256 != artifact_hash:
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    if record.finalized_artifact_sha256 != artifact_hash:
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    if record.finalization_sequence <= 0:
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    required_log = {
        "NORMAL_WORKLOAD_ONLY",
        "COMMON_OBJECTIVE_J",
        "FINALIZED_BEFORE_CORRECTIVE_RELEASE",
    }
    if not required_log.issubset(record.construction_log):
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    return CustodyCheck(True, "OK")


def downstream_matches(
    artifact: MechanismArtifact,
    context: str,
    authority_identity: str,
) -> bool:
    if artifact.kind is MechanismKind.B:
        return context == artifact.key_values[0]
    if artifact.kind is MechanismKind.P:
        return (context, authority_identity) == artifact.key_values
    return False


def upstream_matches(artifact: MechanismArtifact, world: str, context: str) -> bool:
    if artifact.kind is not MechanismKind.T:
        return False
    return (world, context) == artifact.key_values


def install_mechanism(state: MachineState, artifact: MechanismArtifact) -> MachineState:
    if artifact.kind not in {MechanismKind.B, MechanismKind.P, MechanismKind.T}:
        raise ImplementationError("unknown V1 mechanism kind")
    return replace(state, compiled_mode=1)
