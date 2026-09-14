from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping

from adaptive_leverage.model import ImplementationError
from adaptive_leverage.v2.assay import PreparedV2Run
from adaptive_leverage.v2.classify import RawReachabilityMatrix, V2Decision
from adaptive_leverage.v2.domain import carrier
from adaptive_leverage.v2.protocol import (
    V2_AUDIT_SHA256,
    V2_ENUMERATION_SHA256,
    V2_FREEZE_RECORD_SHA256,
    V2_PREREG_MANIFEST_SHA256,
    V2_PREREG_SHA256,
    V2_PROTOCOL_ID,
    V2_REALIZATION_MANIFEST_SHA256,
    V2_REALIZATION_SHA256,
)
from adaptive_leverage.v2.topology import RefinementMode, WriteMode


_PRE_REPLAY_FILENAMES = (
    "authority_identity.json",
    "source_baseline.json",
    "reference_partition.json",
    "normal_data.json",
    "objective.json",
    "alpha_candidate_scores.json",
    "beta_candidate_scores.json",
    "T_ALPHA.json",
    "T_BETA.json",
    "alpha_compiler_custody.json",
    "beta_compiler_custody.json",
    "alpha_dispatch.json",
    "beta_dispatch.json",
    "alpha_partition.json",
    "beta_partition.json",
    "topology_descriptors.json",
    "joint_admission.json",
    "release_identity.json",
)

_RESULT_FILENAMES = (
    "raw_R_matrix.json",
    "F_vector.json",
    "C_MF_obs.json",
    "D_contrasts.json",
    "validity.json",
)

_TRANSFORMATIONS = ("T_ALPHA", "T_BETA")


@dataclass(frozen=True)
class ValidityRecord:
    validity_passed: bool
    reason: str | None

    def __post_init__(self) -> None:
        if type(self.validity_passed) is not bool:
            raise ImplementationError("validity record must use a boolean pass flag")
        if self.validity_passed and self.reason is not None:
            raise ImplementationError("passing validity record may not carry a failure reason")
        if not self.validity_passed and not self.reason:
            raise ImplementationError("failing validity record requires a reason")


def _jsonable(value: object) -> object:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {
            field.name: _jsonable(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise ImplementationError("canonical JSON mappings require string keys")
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (set, frozenset)):
        converted = [_jsonable(item) for item in value]
        return sorted(
            converted,
            key=lambda item: json.dumps(
                item,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ),
        )
    raise ImplementationError(f"unsupported canonical JSON value: {type(value).__name__}")


def canonical_json_bytes(record: object) -> bytes:
    payload = _jsonable(record)
    return (
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")


def _require_basename(filename: str) -> str:
    if not filename or Path(filename).name != filename or filename in {".", ".."}:
        raise ImplementationError(f"artifact filename must be a basename: {filename!r}")
    return filename


def _write_exact(path: Path, payload: bytes) -> Path:
    path = Path(path)
    if path.exists():
        try:
            existing = path.read_bytes()
        except OSError as exc:
            raise ImplementationError(f"unable to read existing custody artifact: {path.name}") from exc
        if existing != payload:
            raise ImplementationError(
                f"refusing to overwrite existing different custody artifact: {path.name}"
            )
        return path
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    except OSError as exc:
        raise ImplementationError(f"unable to write custody artifact: {path.name}") from exc
    return path


def _write_batch(directory: Path, records: tuple[tuple[str, bytes], ...]) -> tuple[Path, ...]:
    directory = Path(directory)
    names = tuple(_require_basename(name) for name, _ in records)
    if len(set(names)) != len(names):
        raise ImplementationError("duplicate artifact filename in custody batch")

    for name, payload in records:
        target = directory / name
        if target.exists():
            try:
                existing = target.read_bytes()
            except OSError as exc:
                raise ImplementationError(f"unable to read existing custody artifact: {name}") from exc
            if existing != payload:
                raise ImplementationError(
                    f"refusing to overwrite existing different custody artifact: {name}"
                )

    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ImplementationError("unable to create custody directory") from exc

    return tuple(_write_exact(directory / name, payload) for name, payload in records)


def write_json(path: Path, record: object) -> Path:
    return _write_exact(Path(path), canonical_json_bytes(record))


def write_jsonl(path: Path, records: tuple[object, ...]) -> Path:
    if not isinstance(records, tuple):
        raise ImplementationError("JSONL custody records must be an immutable tuple")
    payload = b"".join(canonical_json_bytes(record) for record in records)
    return _write_exact(Path(path), payload)


def write_sha256_manifest(directory: Path, filenames: tuple[str, ...]) -> Path:
    if not isinstance(filenames, tuple):
        raise ImplementationError("manifest filenames must be an immutable tuple")
    checked = tuple(sorted(_require_basename(name) for name in filenames))
    if len(set(checked)) != len(checked):
        raise ImplementationError("manifest contains duplicate filenames")
    if "SHA256SUMS.txt" in checked:
        raise ImplementationError("manifest may not hash itself")

    directory = Path(directory)
    lines: list[str] = []
    for name in checked:
        path = directory / name
        if not path.is_file():
            raise ImplementationError(f"manifest target missing: {name}")
        try:
            digest = sha256(path.read_bytes()).hexdigest()
        except OSError as exc:
            raise ImplementationError(f"unable to hash manifest target: {name}") from exc
        lines.append(f"{digest}  {name}\n")
    return _write_exact(directory / "SHA256SUMS.txt", "".join(lines).encode("utf-8"))


def _candidate_score_payload(prepared: PreparedV2Run, *, alpha: bool) -> dict[str, object]:
    result = prepared.alpha if alpha else prepared.beta
    return {
        "candidate_scores": result.custody.candidate_scores,
        "coordinate_index": result.custody.coordinate_index,
        "family_name": result.custody.family_name,
        "selected_candidate": result.custody.selected_candidate,
    }


def _partition_payload(partition: object) -> dict[str, object]:
    return {
        "coordinate_index": partition.coordinate_index,
        "family_name": partition.family_name,
        "mismatch": partition.mismatch,
        "partition": partition.partition,
        "partition_sha256": partition.partition_sha256,
        "predictor_sha256": partition.predictor_sha256,
        "witnesses": partition.witnesses,
    }


def _authority_identity_payload(prepared: PreparedV2Run) -> dict[str, object]:
    return {
        "authority_binding_sha256": prepared.authority_binding_sha256,
        "protocol_id": V2_PROTOCOL_ID,
        "frozen_authority": {
            "audit_sha256": V2_AUDIT_SHA256,
            "enumeration_sha256": V2_ENUMERATION_SHA256,
            "freeze_record_sha256": V2_FREEZE_RECORD_SHA256,
            "prereg_manifest_sha256": V2_PREREG_MANIFEST_SHA256,
            "prereg_sha256": V2_PREREG_SHA256,
            "realization_manifest_sha256": V2_REALIZATION_MANIFEST_SHA256,
            "realization_sha256": V2_REALIZATION_SHA256,
        },
    }


def write_pre_replay_custody(directory: Path, prepared: PreparedV2Run) -> tuple[Path, ...]:
    if not isinstance(prepared, PreparedV2Run):
        raise ImplementationError("pre-replay custody requires a PreparedV2Run record")
    admission = prepared.joint_admission
    if admission is None or not admission.passed or admission.release_token is None:
        raise ImplementationError("pre-replay custody requires passing joint admission")

    source_path = Path(prepared.repo_root) / "records" / "ALCF_V2_0_SOURCE_BASELINE.json"
    try:
        source_baseline_bytes = source_path.read_bytes()
    except OSError as exc:
        raise ImplementationError("source baseline custody record is unavailable") from exc

    records = (
        ("authority_identity.json", canonical_json_bytes(_authority_identity_payload(prepared))),
        ("source_baseline.json", source_baseline_bytes),
        (
            "reference_partition.json",
            canonical_json_bytes(
                {
                    "carrier_sha256": prepared.carrier_sha256,
                    "correction_partition_sha256": prepared.correction_partition_sha256,
                    "i_spec_sha256": prepared.i_spec_sha256,
                    "k_corr_sha256": prepared.k_corr_sha256,
                    "qstar_custody_sha256": prepared.qstar_custody_sha256,
                }
            ),
        ),
        (
            "normal_data.json",
            canonical_json_bytes(
                {
                    "adaptive_example_states": prepared.adaptive_example_states,
                    "sha256": prepared.normal_data_sha256,
                }
            ),
        ),
        ("objective.json", canonical_json_bytes({"sha256": prepared.objective_sha256})),
        ("alpha_candidate_scores.json", canonical_json_bytes(_candidate_score_payload(prepared, alpha=True))),
        ("beta_candidate_scores.json", canonical_json_bytes(_candidate_score_payload(prepared, alpha=False))),
        ("T_ALPHA.json", canonical_json_bytes(prepared.alpha.artifact)),
        ("T_BETA.json", canonical_json_bytes(prepared.beta.artifact)),
        ("alpha_compiler_custody.json", canonical_json_bytes(prepared.alpha.custody)),
        ("beta_compiler_custody.json", canonical_json_bytes(prepared.beta.custody)),
        ("alpha_dispatch.json", canonical_json_bytes(prepared.alpha_partition.dispatch_table)),
        ("beta_dispatch.json", canonical_json_bytes(prepared.beta_partition.dispatch_table)),
        ("alpha_partition.json", canonical_json_bytes(_partition_payload(prepared.alpha_partition))),
        ("beta_partition.json", canonical_json_bytes(_partition_payload(prepared.beta_partition))),
        ("topology_descriptors.json", canonical_json_bytes(prepared.topologies)),
        (
            "joint_admission.json",
            canonical_json_bytes(
                {
                    "admission_sha256": admission.admission_sha256,
                    "failed_check": admission.failed_check,
                    "passed": admission.passed,
                    "reason": admission.reason,
                }
            ),
        ),
        ("release_identity.json", canonical_json_bytes(admission.release_token)),
    )
    if tuple(name for name, _ in records) != _PRE_REPLAY_FILENAMES:
        raise ImplementationError("pre-replay custody filename contract drift")
    return _write_batch(Path(directory), records)


def _raw_matrix_payload(raw_matrix: RawReachabilityMatrix) -> dict[str, object]:
    return {"rows": raw_matrix.rows}


def _f_vector_payload(decision: V2Decision) -> dict[str, object]:
    outcome = decision.scientific_outcome
    if outcome is None:
        raise ImplementationError("scientific result writer requires a valid scientific outcome")
    return {"f_vector": outcome.f_vector}


def _d_contrasts_payload(decision: V2Decision) -> dict[str, object]:
    outcome = decision.scientific_outcome
    if outcome is None:
        raise ImplementationError("scientific result writer requires a valid scientific outcome")
    return {"d_contrasts": outcome.d_contrasts}


def _c_mf_obs_payload(decision: V2Decision) -> dict[str, object]:
    outcome = decision.scientific_outcome
    if outcome is None:
        raise ImplementationError("scientific result writer requires a valid scientific outcome")
    return {"c_mf_obs": outcome.c_mf_obs}


def write_scientific_results(
    directory: Path,
    *,
    raw_matrix: RawReachabilityMatrix,
    decision: V2Decision,
    validity: ValidityRecord | None,
) -> tuple[Path, ...]:
    if not isinstance(raw_matrix, RawReachabilityMatrix):
        raise ImplementationError("scientific result writer requires a typed raw reachability matrix")
    if not isinstance(decision, V2Decision) or decision.stop is not None or decision.scientific_outcome is None:
        raise ImplementationError("scientific result writer requires a valid scientific outcome")
    if not isinstance(validity, ValidityRecord):
        raise ImplementationError("scientific result writer requires an explicit validity record")
    if not validity.validity_passed:
        raise ImplementationError("scientific result writer requires passing validity")

    records = (
        ("raw_R_matrix.json", canonical_json_bytes(_raw_matrix_payload(raw_matrix))),
        ("F_vector.json", canonical_json_bytes(_f_vector_payload(decision))),
        ("C_MF_obs.json", canonical_json_bytes(_c_mf_obs_payload(decision))),
        ("D_contrasts.json", canonical_json_bytes(_d_contrasts_payload(decision))),
        ("validity.json", canonical_json_bytes(validity)),
    )
    if tuple(name for name, _ in records) != _RESULT_FILENAMES:
        raise ImplementationError("scientific result filename contract drift")
    return _write_batch(Path(directory), records)


def arm_trace_filename(
    transformation: str,
    refinement: RefinementMode,
    write: WriteMode,
    state: str,
) -> str:
    if transformation not in _TRANSFORMATIONS:
        raise ImplementationError(f"unknown V2 transformation arm: {transformation!r}")
    if not isinstance(refinement, RefinementMode):
        raise ImplementationError(f"unknown V2 refinement mode: {refinement!r}")
    if not isinstance(write, WriteMode):
        raise ImplementationError(f"unknown V2 write mode: {write!r}")
    states = tuple(item.value for item in carrier())
    if state not in states:
        raise ImplementationError(f"unknown V2 carrier state: {state!r}")
    return f"arm_{transformation}_{refinement.value}_{write.value}_{state}_trace.jsonl"


def write_arm_trace(
    directory: Path,
    *,
    transformation: str,
    refinement: RefinementMode,
    write: WriteMode,
    state: str,
    records: tuple[object, ...],
) -> Path:
    filename = arm_trace_filename(transformation, refinement, write, state)
    return write_jsonl(Path(directory) / filename, records)
