from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json

from .model import Edge, Episode, PROTOCOL_ID, Provenance


class TraceValidationError(RuntimeError):
    """Malformed implementation trace; never a scientific classification."""


@dataclass(frozen=True)
class TraceEvent:
    protocol_id: str
    run_id: str
    arm: str
    seq: int
    transition_id: str
    edge_id: str
    world: str
    context: str
    observation: str | None
    evidence: str | None
    contradiction_id: str | None
    scope_status: str
    warrant_status: str
    authority_status: str
    policy_mode_before: str
    policy_mode_after: str
    compiled_mode: int
    action: str | None
    microstep_index: int
    provenance: str
    prev_event_sha256: str | None
    event_sha256: str


_REQUIRED_FIELDS = tuple(TraceEvent.__dataclass_fields__)
_KNOWN_EDGES = {edge.value for edge in Edge}
_KNOWN_PROVENANCE = {provenance.value for provenance in Provenance}


def _event_payload(event: TraceEvent, *, include_event_hash: bool) -> dict[str, object]:
    payload = asdict(event)
    if not include_event_hash:
        payload.pop("event_sha256", None)
    return payload


def canonical_event_json(event: TraceEvent, *, include_event_hash: bool = False) -> str:
    return json.dumps(
        _event_payload(event, include_event_hash=include_event_hash),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _hash_event(event: TraceEvent) -> str:
    raw = canonical_event_json(event, include_event_hash=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_trace(episode: Episode, *, arm: str, run_id: str) -> tuple[TraceEvent, ...]:
    events: list[TraceEvent] = []
    prev_hash: str | None = None

    for index, step in enumerate(episode.steps):
        event = TraceEvent(
            protocol_id=PROTOCOL_ID,
            run_id=run_id,
            arm=arm,
            seq=index,
            transition_id=step.transition_id,
            edge_id=step.edge.value,
            world=episode.world,
            context=episode.context,
            observation=step.observation,
            evidence=step.evidence,
            contradiction_id=episode.contradiction_id,
            scope_status=step.after.scope_status.value,
            warrant_status=step.after.warrant_status.value,
            authority_status=step.after.authority_status.value,
            policy_mode_before=step.before.policy_mode.value,
            policy_mode_after=step.after.policy_mode.value,
            compiled_mode=step.after.compiled_mode,
            action=step.action,
            microstep_index=index,
            provenance=step.provenance.value,
            prev_event_sha256=prev_hash,
            event_sha256="",
        )
        event_hash = _hash_event(event)
        event = TraceEvent(**{**asdict(event), "event_sha256": event_hash})
        events.append(event)
        prev_hash = event_hash

    return tuple(events)


def validate_trace(events: tuple[TraceEvent, ...]) -> None:
    if not isinstance(events, tuple):
        raise TraceValidationError("trace must be an immutable tuple")

    previous_hash: str | None = None
    for index, event in enumerate(events):
        payload = asdict(event)
        if tuple(payload) != _REQUIRED_FIELDS:
            raise TraceValidationError("trace event fields differ from frozen schema")
        if event.seq != index or event.microstep_index != index:
            raise TraceValidationError("trace sequence is not contiguous")
        if event.edge_id not in _KNOWN_EDGES:
            raise TraceValidationError(f"unknown edge id: {event.edge_id}")
        if event.provenance not in _KNOWN_PROVENANCE:
            raise TraceValidationError(f"unknown provenance: {event.provenance}")
        if event.prev_event_sha256 != previous_hash:
            raise TraceValidationError("broken previous-event hash link")
        expected_hash = _hash_event(event)
        if event.event_sha256 != expected_hash:
            raise TraceValidationError("event content hash mismatch")
        previous_hash = event.event_sha256
