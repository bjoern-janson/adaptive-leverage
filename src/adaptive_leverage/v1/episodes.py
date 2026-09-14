from __future__ import annotations

from dataclasses import replace

from adaptive_leverage.model import (
    OMEGA_STAR,
    W_N,
    Edge,
    Episode,
    ImplementationError,
    MachineState,
    Phase,
    PolicyMode,
    Provenance,
    Step,
    run_dynamic_episode,
)
from adaptive_leverage.v1.mechanisms import (
    MechanismArtifact,
    MechanismKind,
    downstream_matches,
    upstream_matches,
)


def _require_installed(state: MachineState) -> None:
    if state.compiled_mode != 1:
        raise ImplementationError("V1 mechanism episode requires installed compiled_mode=1")
    if state.phase is not Phase.READY:
        raise ImplementationError("V1 mechanism episode must start from READY state")


def _downstream_compiled_episode(
    world: str,
    state: MachineState,
    artifact: MechanismArtifact,
) -> Episode:
    dynamic = run_dynamic_episode(world, state)
    prefix = dynamic.steps[:4]
    authorized = prefix[-1].after
    if not downstream_matches(artifact, dynamic.context, authorized.authority_status.value):
        return dynamic

    acted = replace(
        authorized,
        phase=Phase.ACTED,
        policy_mode=PolicyMode(artifact.normal_policy_mode),
    )
    compiled_step = Step(
        transition_id="V1_DOWNSTREAM_E5_E6_COMPILED",
        edge=Edge.E5A,
        before=authorized,
        after=acted,
        evidence=dynamic.evidence,
        action=artifact.normal_action,
        provenance=Provenance.COMPILE_DISPATCH,
    )
    return Episode(
        world=dynamic.world,
        context=dynamic.context,
        observation=dynamic.observation,
        evidence=dynamic.evidence,
        contradiction_id=dynamic.contradiction_id,
        steps=tuple(prefix) + (compiled_step,),
        terminal_state=acted,
        action=artifact.normal_action,
    )


def _upstream_compiled_episode(
    world: str,
    state: MachineState,
    artifact: MechanismArtifact,
) -> Episode:
    dynamic = run_dynamic_episode(world, state)
    if not upstream_matches(artifact, world, dynamic.context):
        return dynamic

    evidenced = dynamic.steps[1].after
    compiled_step = Step(
        transition_id="V1_UPSTREAM_E1_E2_COMPILED",
        edge=Edge.E5A,
        before=state,
        after=evidenced,
        observation=artifact.compiled_observation,
        evidence=artifact.compiled_evidence,
        provenance=Provenance.COMPILE_DISPATCH,
    )
    suffix = dynamic.steps[2:]
    return Episode(
        world=dynamic.world,
        context=dynamic.context,
        observation=artifact.compiled_observation or dynamic.observation,
        evidence=artifact.compiled_evidence or dynamic.evidence,
        contradiction_id=dynamic.contradiction_id,
        steps=(compiled_step,) + tuple(suffix),
        terminal_state=dynamic.terminal_state,
        action=dynamic.action,
    )


def run_v1_world_episode(
    world: str,
    state: MachineState,
    artifact: MechanismArtifact,
) -> Episode:
    _require_installed(state)
    if artifact.kind in {MechanismKind.B, MechanismKind.P}:
        return _downstream_compiled_episode(world, state, artifact)
    if artifact.kind is MechanismKind.T:
        return _upstream_compiled_episode(world, state, artifact)
    raise ImplementationError(f"unknown V1 mechanism kind: {artifact.kind!r}")


def run_v1_normal_episode(state: MachineState, artifact: MechanismArtifact) -> Episode:
    return run_v1_world_episode(W_N, state, artifact)
