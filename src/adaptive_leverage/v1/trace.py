from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json

from adaptive_leverage.model import Edge, Episode, Provenance
from adaptive_leverage.v1.protocol import V1_PROTOCOL_ID


class V1TraceValidationError(RuntimeError):
    """Malformed V1 implementation trace; never a scientific classification."""


@dataclass(frozen=True)
class V1TraceEvent:
    protocol_id: str
    run_id: str
    arm: str
    mechanism_artifact_sha256: str | None
    seq: int
    transition_id: str
    edge_id: str
    represented_source_edges: tuple[str, ...]
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


_REQUIRED_FIELDS = tuple(V1TraceEvent.__dataclass_fields__)
_KNOWN_DYNAMIC_EDGES = {edge.value for edge in Edge}
_KNOWN_V1_EDGE_IDS = _KNOWN_DYNAMIC_EDGES | {"E5_E6_COMPILED", "E1_E2_COMPILED"}
_KNOWN_PROVENANCE = {provenance.value for provenance in Provenance}


def _event_payload(event: V1TraceEvent, *, include_event_hash: bool) -> dict[str, object]:
    payload = asdict(event)
    if not include_event_hash:
        payload.pop("event_sha256", None)
    return payload


def canonical_v1_event_json(
    event: V1TraceEvent,
    *,
    include_event_hash: bool = False,
) -> str:
    return json.dumps(
        _event_payload(event, include_event_hash=include_event_hash),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _hash_event(event: V1TraceEvent) -> str:
    return sha256(
        canonical_v1_event_json(event, include_event_hash=False).encode("utf-8")
    ).hexdigest()


def _edge_binding(transition_id: str, step_edge: str) -> tuple[str, tuple[str, ...]]:
    if transition_id == "V1_DOWNSTREAM_E5_E6_COMPILED":
        return "E5_E6_COMPILED", ("E5", "E6")
    if transition_id == "V1_UPSTREAM_E1_E2_COMPILED":
        return "E1_E2_COMPILED", ("E1", "E2")
    return step_edge, (step_edge,)


def build_v1_trace(
    episode: Episode,
    *,
    arm: str,
    run_id: str,
    mechanism_artifact_sha256: str | None,
) -> tuple[V1TraceEvent, ...]:
    events: list[V1TraceEvent] = []
    previous_hash: str | None = None
    for index, step in enumerate(episode.steps):
        edge_id, represented = _edge_binding(step.transition_id, step.edge.value)
        event = V1TraceEvent(
            protocol_id=V1_PROTOCOL_ID,
            run_id=run_id,
            arm=arm,
            mechanism_artifact_sha256=mechanism_artifact_sha256,
            seq=index,
            transition_id=step.transition_id,
            edge_id=edge_id,
            represented_source_edges=represented,
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
            prev_event_sha256=previous_hash,
            event_sha256="",
        )
        digest = _hash_event(event)
        event = V1TraceEvent(**{**asdict(event), "event_sha256": digest})
        events.append(event)
        previous_hash = digest
    return tuple(events)


def _expected_binding(event: V1TraceEvent) -> tuple[str, tuple[str, ...]]:
    if event.transition_id == "V1_DOWNSTREAM_E5_E6_COMPILED":
        return "E5_E6_COMPILED", ("E5", "E6")
    if event.transition_id == "V1_UPSTREAM_E1_E2_COMPILED":
        return "E1_E2_COMPILED", ("E1", "E2")
    return event.edge_id, (event.edge_id,)


def validate_v1_trace(events: tuple[V1TraceEvent, ...]) -> None:
    if not isinstance(events, tuple):
        raise V1TraceValidationError("trace must be an immutable tuple")
    if not events:
        raise V1TraceValidationError("trace must contain at least one event")

    expected_arm = events[0].arm
    expected_run_id = events[0].run_id
    expected_mechanism_hash = events[0].mechanism_artifact_sha256
    previous_hash: str | None = None

    for index, event in enumerate(events):
        payload = asdict(event)
        if tuple(payload) != _REQUIRED_FIELDS:
            raise V1TraceValidationError("trace event fields differ from V1 schema")
        if event.protocol_id != V1_PROTOCOL_ID:
            raise V1TraceValidationError("trace protocol id mismatch")
        if event.arm != expected_arm or event.run_id != expected_run_id:
            raise V1TraceValidationError("trace identity changed within event chain")
        if event.mechanism_artifact_sha256 != expected_mechanism_hash:
            raise V1TraceValidationError("mechanism artifact hash changed within trace")
        if event.seq != index or event.microstep_index != index:
            raise V1TraceValidationError("trace sequence is not contiguous")
        if event.edge_id not in _KNOWN_V1_EDGE_IDS:
            raise V1TraceValidationError(f"unknown V1 edge id: {event.edge_id}")
        if event.provenance not in _KNOWN_PROVENANCE:
            raise V1TraceValidationError(f"unknown provenance: {event.provenance}")
        expected_edge, expected_represented = _expected_binding(event)
        if event.edge_id != expected_edge or event.represented_source_edges != expected_represented:
            raise V1TraceValidationError("compiled-source edge binding mismatch")
        if event.prev_event_sha256 != previous_hash:
            raise V1TraceValidationError("broken previous-event hash link")
        expected_hash = _hash_event(event)
        if event.event_sha256 != expected_hash:
            raise V1TraceValidationError("event content hash mismatch")
        previous_hash = event.event_sha256
