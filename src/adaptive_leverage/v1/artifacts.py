from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from adaptive_leverage.model import ImplementationError
from adaptive_leverage.v1.classify import V1Decision
from adaptive_leverage.v1.trace import V1TraceEvent


EXECUTION_FILENAMES = (
    "protocol_identity.json",
    "prefork_identity.json",
    "B_mechanism.json",
    "P_mechanism.json",
    "T_mechanism.json",
    "B_custody.json",
    "P_custody.json",
    "T_custody.json",
    "C_normal_trace.jsonl",
    "B_normal_trace.jsonl",
    "P_normal_trace.jsonl",
    "T_normal_trace.jsonl",
    "E_normal_trace.jsonl",
    "joint_admission.json",
    "C_correction_trace.jsonl",
    "B_correction_trace.jsonl",
    "P_correction_trace.jsonl",
    "T_correction_trace.jsonl",
    "E_correction_trace.jsonl",
    "validity_facts.json",
    "classification.json",
    "SHA256SUMS.txt",
)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, bytes):
        return value.hex()
    if is_dataclass(value):
        return {field.name: _jsonable(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


def _canonical_line(value: Any) -> str:
    return json.dumps(
        _jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def write_json(path: Path, value: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_canonical_line(value) + "\n", encoding="utf-8")
    return path


def write_trace_jsonl(path: Path, trace: tuple[V1TraceEvent, ...]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(_canonical_line(event) + "\n" for event in trace)
    path.write_text(body, encoding="utf-8")
    return path


def _decision_payload(decision: V1Decision) -> dict[str, object]:
    if decision.stop is not None or decision.scientific_outcome is None:
        raise ImplementationError(
            "stopped V1 decision cannot be serialized as a scientific classification"
        )
    outcome = decision.scientific_outcome
    return {
        "scientific_outcome": {
            "d_bp": outcome.d_bp,
            "d_bt": outcome.d_bt,
            "d_pt": outcome.d_pt,
            "licensed_statements": list(outcome.licensed_statements),
            "signature": {
                "b": outcome.signature.b,
                "p": outcome.signature.p,
                "t": outcome.signature.t,
                "text": outcome.signature.text,
            },
        },
        "stop": None,
        "stop_detail": None,
    }


def write_decision_json(path: Path, decision: V1Decision) -> Path:
    return write_json(path, _decision_payload(decision))


def write_sha256_manifest(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    manifest = directory / "SHA256SUMS.txt"
    paths = sorted(
        path
        for path in directory.rglob("*")
        if path.is_file() and path != manifest
    )
    lines = []
    for path in paths:
        relative = path.relative_to(directory).as_posix()
        digest = sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {relative}")
    manifest.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return manifest
