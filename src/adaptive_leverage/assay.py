from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from pathlib import Path

from .interventions import (
    CompiledDispatch,
    apply_compiled,
    apply_noop,
    apply_valid_scope_closure,
)
from .model import (
    A0,
    A1,
    E_STAR,
    OMEGA_STAR,
    W_C,
    W_N,
    AuthorityStatus,
    Edge,
    Episode,
    ImplementationError,
    MachineState,
    Phase,
    PolicyMode,
    Provenance,
    ScopeStatus,
    Step,
    WarrantStatus,
    canonical_state_bytes,
    run_dynamic_episode,
)
from .trace import TraceEvent, build_trace, validate_trace

_FROZEN_EDGE_VALUES = ("E1", "E2", "E3", "E4", "E5", "E6")

_FROZEN_PROTOCOL_HASHES = {
    "prereg/ALCF_V0_PREREG_FROZEN.md": (
        "05e8edd5c9aa7d5e15cf46575eb1efe2c91d1674054e53e6ed3a23a94e7f8192"
    ),
    "prereg/ALCF_V0_PROTOCOL_FROZEN.json": (
        "7b476c5020f0b81e6a1bceb712b877f5d52d0cbf6d99b0e164e7f705f06c1188"
    ),
}


def verify_frozen_protocol_hashes(repo_root: Path) -> None:
    for relative_path, expected in _FROZEN_PROTOCOL_HASHES.items():
        path = repo_root / relative_path
        try:
            observed = sha256(path.read_bytes()).hexdigest()
        except OSError as exc:
            raise ImplementationError(f"unable to read frozen protocol artifact: {relative_path}") from exc
        if observed != expected:
            raise ImplementationError(
                f"frozen protocol hash mismatch for {relative_path}: {observed}"
            )


@dataclass(frozen=True)
class ArmBundle:
    c: MachineState
    a: MachineState
    e: MachineState
    prefork_serialized_c: bytes
    prefork_serialized_a: bytes
    prefork_serialized_e: bytes


@dataclass(frozen=True)
class CapabilityObservation:
    arm: str
    action: str
    cost: int
    trace: tuple[TraceEvent, ...]


@dataclass(frozen=True)
class CorrectionObservation:
    arm: str
    action: str
    trace: tuple[TraceEvent, ...]
    route_nonempty: bool
    warrant_preserved: bool
    scope_closed_valid: bool
    licensing_epistemic_event: bool
    missing_edge: Edge | None
    route_loss_provenance: str


def _compiled_episode(
    world: str, state: MachineState, artifact: CompiledDispatch
) -> Episode:
    if state.compiled_mode != 1:
        raise ImplementationError("compiled episode requires compiled_mode=1")
    if artifact.context != OMEGA_STAR or artifact.action != A0:
        raise ImplementationError("compiled artifact does not match frozen normal dispatch")
    if artifact.provenance is not Provenance.COMPILE_DISPATCH:
        raise ImplementationError("compiled artifact provenance mismatch")

    dynamic = run_dynamic_episode(world, state)
    prefix = dynamic.steps[:4]
    authorized = prefix[-1].after
    acted = replace(authorized, phase=Phase.ACTED)
    compiled_step = Step(
        transition_id="T5A_COMPILED",
        edge=Edge.E5A,
        before=authorized,
        after=acted,
        observation=None,
        evidence=dynamic.evidence,
        action=artifact.action,
        provenance=Provenance.COMPILE_DISPATCH,
    )
    return Episode(
        world=world,
        context=OMEGA_STAR,
        observation=dynamic.observation,
        evidence=dynamic.evidence,
        contradiction_id=dynamic.contradiction_id,
        steps=tuple(prefix) + (compiled_step,),
        terminal_state=acted,
        action=artifact.action,
    )


def qualified_route(trace: tuple[TraceEvent, ...]) -> bool:
    if tuple(event.edge_id for event in trace) != _FROZEN_EDGE_VALUES:
        return False
    by_edge = {event.edge_id: event for event in trace}
    return (
        any(event.evidence == E_STAR for event in trace)
        and by_edge["E3"].warrant_status == WarrantStatus.CORRECTION.value
        and by_edge["E4"].authority_status == AuthorityStatus.CORR_AUTH.value
        and by_edge["E5"].policy_mode_after == PolicyMode.CORRECTED.value
        and by_edge["E6"].action == A1
    )


def first_missing_frozen_edge(trace: tuple[TraceEvent, ...]) -> Edge | None:
    expected_index = 0
    for event in trace:
        edge_id = event.edge_id
        if expected_index >= len(_FROZEN_EDGE_VALUES):
            if edge_id in _FROZEN_EDGE_VALUES:
                return None
            continue
        expected = _FROZEN_EDGE_VALUES[expected_index]
        if edge_id == expected:
            expected_index += 1
            continue
        if edge_id in _FROZEN_EDGE_VALUES:
            # A later/repeated frozen edge after a gap makes localization ambiguous.
            return None
        if edge_id != Edge.E5A.value:
            return None

    if expected_index == len(_FROZEN_EDGE_VALUES):
        return None
    return Edge(_FROZEN_EDGE_VALUES[expected_index])


def _warrant_preserved(trace: tuple[TraceEvent, ...]) -> bool:
    return (
        any(event.evidence == E_STAR for event in trace)
        and any(
            event.warrant_status == WarrantStatus.CORRECTION.value
            and event.scope_status == ScopeStatus.OPEN.value
            for event in trace
        )
        and any(
            event.authority_status == AuthorityStatus.CORR_AUTH.value
            for event in trace
        )
    )


def precheck(m0: MachineState) -> CorrectionObservation:
    episode = run_dynamic_episode(W_C, m0)
    trace = build_trace(episode, arm="PRECHECK", run_id="precheck")
    validate_trace(trace)
    route = qualified_route(trace)
    return CorrectionObservation(
        arm="PRECHECK",
        action=episode.action,
        trace=trace,
        route_nonempty=route,
        warrant_preserved=_warrant_preserved(trace),
        scope_closed_valid=False,
        licensing_epistemic_event=False,
        missing_edge=first_missing_frozen_edge(trace) if not route else None,
        route_loss_provenance=Provenance.BASE_MACHINE.value,
    )


def fork_arms(m0: MachineState, artifact: CompiledDispatch) -> ArmBundle:
    snapshot = canonical_state_bytes(m0)
    # Three independent serialized custody values are captured before intervention.
    c_before = bytes(snapshot)
    a_before = bytes(snapshot)
    e_before = bytes(snapshot)
    return ArmBundle(
        c=apply_noop(m0),
        a=apply_compiled(m0, artifact),
        e=apply_valid_scope_closure(m0),
        prefork_serialized_c=c_before,
        prefork_serialized_a=a_before,
        prefork_serialized_e=e_before,
    )


def measure_capability(
    arm: str,
    state: MachineState,
    artifact: CompiledDispatch | None = None,
) -> CapabilityObservation:
    if arm == "A":
        if artifact is None:
            raise ImplementationError("A capability measurement requires compiled artifact")
        episode = _compiled_episode(W_N, state, artifact)
    elif arm in {"C", "E"}:
        episode = run_dynamic_episode(W_N, state)
    else:
        raise ImplementationError(f"unknown arm: {arm}")

    trace = build_trace(episode, arm=arm, run_id=f"fixture-normal-{arm.lower()}")
    validate_trace(trace)
    return CapabilityObservation(arm=arm, action=episode.action, cost=len(trace), trace=trace)


def replay_correction(
    arm: str,
    state: MachineState,
    artifact: CompiledDispatch | None = None,
) -> CorrectionObservation:
    if arm == "A":
        if artifact is None:
            raise ImplementationError("A correction replay requires compiled artifact")
        episode = _compiled_episode(W_C, state, artifact)
        provenance = Provenance.COMPILE_DISPATCH.value
        licensing = False
    elif arm == "C":
        episode = run_dynamic_episode(W_C, state)
        provenance = Provenance.BASE_MACHINE.value
        licensing = False
    elif arm == "E":
        if state.scope_status is not ScopeStatus.CLOSED_VALID:
            raise ImplementationError("E correction replay requires valid scope closure")
        episode = run_dynamic_episode(W_C, state)
        provenance = Provenance.VALID_SCOPE_CLOSURE.value
        licensing = True
    else:
        raise ImplementationError(f"unknown arm: {arm}")

    trace = build_trace(episode, arm=arm, run_id=f"fixture-correction-{arm.lower()}")
    validate_trace(trace)
    route = qualified_route(trace)
    return CorrectionObservation(
        arm=arm,
        action=episode.action,
        trace=trace,
        route_nonempty=route,
        warrant_preserved=_warrant_preserved(trace),
        scope_closed_valid=state.scope_status is ScopeStatus.CLOSED_VALID,
        licensing_epistemic_event=licensing,
        missing_edge=first_missing_frozen_edge(trace) if not route else None,
        route_loss_provenance=provenance,
    )
