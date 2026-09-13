from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import re

from adaptive_leverage.v2.protocol import V2_PROTOCOL_ID


class V2TraceValidationError(RuntimeError):
    """Malformed V2 pre-replay custody trace; never a scientific result."""


@dataclass(frozen=True)
class V2TraceEvent:
    protocol_id: str
    run_id: str
    seq: int
    stage: str
    status: str
    object_sha256: str
    details: tuple[tuple[str, str], ...]
    prev_event_sha256: str | None
    event_sha256: str


_REQUIRED_FIELDS = tuple(V2TraceEvent.__dataclass_fields__)
_ALLOWED_STATUS = {"VERIFIED", "DERIVED", "FINALIZED", "ADMITTED"}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _event_payload(event: V2TraceEvent, *, include_event_hash: bool) -> dict[str, object]:
    payload = asdict(event)
    if not include_event_hash:
        payload.pop("event_sha256", None)
    return payload


def canonical_v2_event_json(
    event: V2TraceEvent,
    *,
    include_event_hash: bool = False,
) -> str:
    return json.dumps(
        _event_payload(event, include_event_hash=include_event_hash),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _hash_event(event: V2TraceEvent) -> str:
    return sha256(
        canonical_v2_event_json(event, include_event_hash=False).encode("utf-8")
    ).hexdigest()


def append_v2_trace_event(
    events: tuple[V2TraceEvent, ...],
    *,
    run_id: str,
    stage: str,
    status: str,
    object_sha256: str,
    details: tuple[tuple[str, str], ...] = (),
) -> tuple[V2TraceEvent, ...]:
    if not run_id:
        raise V2TraceValidationError("V2 trace run id must be nonempty")
    if not stage:
        raise V2TraceValidationError("V2 trace stage must be nonempty")
    if status not in _ALLOWED_STATUS:
        raise V2TraceValidationError(f"unknown V2 trace status: {status}")
    if _SHA256_RE.fullmatch(object_sha256) is None:
        raise V2TraceValidationError("V2 trace object hash is not SHA-256")
    if tuple(sorted(details)) != details:
        raise V2TraceValidationError("V2 trace details must be canonically sorted")

    event = V2TraceEvent(
        protocol_id=V2_PROTOCOL_ID,
        run_id=run_id,
        seq=len(events),
        stage=stage,
        status=status,
        object_sha256=object_sha256,
        details=details,
        prev_event_sha256=events[-1].event_sha256 if events else None,
        event_sha256="",
    )
    event = V2TraceEvent(**{**asdict(event), "event_sha256": _hash_event(event)})
    return events + (event,)


def validate_v2_trace(events: tuple[V2TraceEvent, ...]) -> None:
    if not isinstance(events, tuple):
        raise V2TraceValidationError("V2 trace must be an immutable tuple")
    if not events:
        raise V2TraceValidationError("V2 trace must contain at least one event")

    expected_run_id = events[0].run_id
    previous_hash: str | None = None
    for index, event in enumerate(events):
        payload = asdict(event)
        if tuple(payload) != _REQUIRED_FIELDS:
            raise V2TraceValidationError("V2 trace event fields differ from schema")
        if event.protocol_id != V2_PROTOCOL_ID:
            raise V2TraceValidationError("V2 trace protocol id mismatch")
        if event.run_id != expected_run_id:
            raise V2TraceValidationError("V2 trace run id changed within chain")
        if event.seq != index:
            raise V2TraceValidationError("V2 trace sequence is not contiguous")
        if event.status not in _ALLOWED_STATUS:
            raise V2TraceValidationError("V2 trace contains unknown status")
        if not event.stage:
            raise V2TraceValidationError("V2 trace stage is empty")
        if _SHA256_RE.fullmatch(event.object_sha256) is None:
            raise V2TraceValidationError("V2 trace object hash is malformed")
        if tuple(sorted(event.details)) != event.details:
            raise V2TraceValidationError("V2 trace details are not canonical")
        if event.prev_event_sha256 != previous_hash:
            raise V2TraceValidationError("V2 trace hash chain is broken")
        expected_hash = _hash_event(event)
        if event.event_sha256 != expected_hash:
            raise V2TraceValidationError("V2 trace event content hash mismatch")
        previous_hash = event.event_sha256
