from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json

from .model import (
    A0,
    OMEGA_STAR,
    O_N,
    W_N,
    ImplementationError,
    MachineState,
    Provenance,
    ScopeStatus,
)

_FORBIDDEN_TOKENS = (
    "w_c",
    "o_c",
    "e_star",
    "c_star",
    "a1",
    "CORRECTION",
    "CORR_AUTH",
    "E5",
    "E6",
)


@dataclass(frozen=True)
class NormalWorkloadInput:
    world: str
    observation: str
    context: str
    expected_action: str
    baseline_cost: int


@dataclass(frozen=True)
class CompiledDispatch:
    context: str
    action: str
    provenance: Provenance


@dataclass(frozen=True)
class CustodyRecord:
    optimization_inputs: tuple[str, ...]
    optimization_input_hashes: tuple[tuple[str, str], ...]
    optimization_input_sha256: str
    forbidden_artifact_manifest: tuple[str, ...]
    finalized_artifact_sha256: str
    construction_log: tuple[str, ...]


@dataclass(frozen=True)
class CustodyCheck:
    passed: bool
    reason: str


def _canonical_json(payload: dict[str, object]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _normal_payload(normal: NormalWorkloadInput) -> dict[str, object]:
    return {
        "baseline_cost": normal.baseline_cost,
        "context": normal.context,
        "expected_action": normal.expected_action,
        "observation": normal.observation,
        "world": normal.world,
    }


def _artifact_payload(artifact: CompiledDispatch) -> dict[str, object]:
    return {
        "action": artifact.action,
        "context": artifact.context,
        "provenance": artifact.provenance.value,
    }


def compile_dispatch(normal: NormalWorkloadInput) -> tuple[CompiledDispatch, CustodyRecord]:
    if normal != NormalWorkloadInput(
        world=W_N,
        observation=O_N,
        context=OMEGA_STAR,
        expected_action=A0,
        baseline_cost=6,
    ):
        raise ImplementationError("compiler input must equal frozen normal workload")

    payload = _normal_payload(normal)
    optimization_inputs = tuple(f"{key}={payload[key]}" for key in sorted(payload))
    input_json = _canonical_json(payload)
    artifact = CompiledDispatch(
        context=normal.context,
        action=normal.expected_action,
        provenance=Provenance.COMPILE_DISPATCH,
    )
    artifact_hash = _sha256_text(_canonical_json(_artifact_payload(artifact)))
    input_hashes = tuple(
        (key, _sha256_text(_canonical_json({key: payload[key]}))) for key in sorted(payload)
    )
    record = CustodyRecord(
        optimization_inputs=optimization_inputs,
        optimization_input_hashes=input_hashes,
        optimization_input_sha256=_sha256_text(input_json),
        forbidden_artifact_manifest=_FORBIDDEN_TOKENS,
        finalized_artifact_sha256=artifact_hash,
        construction_log=(
            "NORMAL_WORKLOAD_ONLY",
            "FINALIZED_BEFORE_CORRECTIVE_REPLAY",
        ),
    )
    return artifact, record


def validate_custody(record: CustodyRecord, artifact: CompiledDispatch) -> CustodyCheck:
    joined = "\n".join(record.optimization_inputs)
    if any(token in joined for token in _FORBIDDEN_TOKENS):
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")

    expected_artifact_hash = _sha256_text(_canonical_json(_artifact_payload(artifact)))
    if record.finalized_artifact_sha256 != expected_artifact_hash:
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    if artifact.provenance is not Provenance.COMPILE_DISPATCH:
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    if "NORMAL_WORKLOAD_ONLY" not in record.construction_log:
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    if "FINALIZED_BEFORE_CORRECTIVE_REPLAY" not in record.construction_log:
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")

    expected_normal = NormalWorkloadInput(W_N, O_N, OMEGA_STAR, A0, 6)
    expected_payload = _normal_payload(expected_normal)
    expected_inputs = tuple(
        f"{key}={expected_payload[key]}" for key in sorted(expected_payload)
    )
    expected_input_hashes = tuple(
        (key, _sha256_text(_canonical_json({key: expected_payload[key]})))
        for key in sorted(expected_payload)
    )
    expected_input_hash = _sha256_text(_canonical_json(expected_payload))
    if record.optimization_inputs != expected_inputs:
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    if record.optimization_input_hashes != expected_input_hashes:
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    if record.optimization_input_sha256 != expected_input_hash:
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")
    if record.forbidden_artifact_manifest != _FORBIDDEN_TOKENS:
        return CustodyCheck(False, "OPTIMIZATION_LEAKAGE")

    return CustodyCheck(True, "OK")


def apply_noop(state: MachineState) -> MachineState:
    return state


def apply_compiled(state: MachineState, artifact: CompiledDispatch) -> MachineState:
    if artifact.provenance is not Provenance.COMPILE_DISPATCH:
        raise ImplementationError("compiled intervention provenance mismatch")
    if artifact.context != OMEGA_STAR or artifact.action != A0:
        raise ImplementationError("compiled intervention differs from frozen normal artifact")
    return replace(state, compiled_mode=1)


def apply_valid_scope_closure(state: MachineState) -> MachineState:
    return replace(state, scope_status=ScopeStatus.CLOSED_VALID)
