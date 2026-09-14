from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import json

W_N = "w_n"
W_C = "w_c"
O_N = "o_n"
O_C = "o_c"
E_N = "e_n"
E_STAR = "e_star"
C_STAR = "c_star"
OMEGA_STAR = "alpha"
A0 = "a0"
A1 = "a1"
PROTOCOL_ID = "ALCF-V0"


class ImplementationError(RuntimeError):
    """Software-contract failure; never a scientific classification."""


class Phase(str, Enum):
    READY = "READY"
    OBSERVED = "OBSERVED"
    EVIDENCED = "EVIDENCED"
    WARRANTED = "WARRANTED"
    AUTHORIZED = "AUTHORIZED"
    UPDATED = "UPDATED"
    ACTED = "ACTED"


class PolicyMode(str, Enum):
    BASE = "BASE"
    CORRECTED = "CORRECTED"


class WarrantStatus(str, Enum):
    NONE = "NONE"
    BASE = "BASE"
    CORRECTION = "CORRECTION"


class AuthorityStatus(str, Enum):
    NONE = "NONE"
    BASE_AUTH = "BASE_AUTH"
    CORR_AUTH = "CORR_AUTH"


class ScopeStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED_VALID = "CLOSED_VALID"


class Edge(str, Enum):
    E1 = "E1"
    E2 = "E2"
    E3 = "E3"
    E4 = "E4"
    E5 = "E5"
    E6 = "E6"
    E5A = "E5A"


class Provenance(str, Enum):
    BASE_MACHINE = "BASE_MACHINE"
    NOOP = "NOOP"
    COMPILE_DISPATCH = "COMPILE_DISPATCH"
    VALID_SCOPE_CLOSURE = "VALID_SCOPE_CLOSURE"


@dataclass(frozen=True)
class MachineState:
    phase: Phase
    policy_mode: PolicyMode
    warrant_status: WarrantStatus
    authority_status: AuthorityStatus
    compiled_mode: int
    scope_status: ScopeStatus


@dataclass(frozen=True)
class Step:
    transition_id: str
    edge: Edge
    before: MachineState
    after: MachineState
    observation: str | None = None
    evidence: str | None = None
    action: str | None = None
    provenance: Provenance = Provenance.BASE_MACHINE


@dataclass(frozen=True)
class Episode:
    world: str
    context: str
    observation: str
    evidence: str
    contradiction_id: str | None
    steps: tuple[Step, ...]
    terminal_state: MachineState
    action: str


def initial_state() -> MachineState:
    return MachineState(
        phase=Phase.READY,
        policy_mode=PolicyMode.BASE,
        warrant_status=WarrantStatus.NONE,
        authority_status=AuthorityStatus.NONE,
        compiled_mode=0,
        scope_status=ScopeStatus.OPEN,
    )


def canonical_state_bytes(state: MachineState) -> bytes:
    payload = {
        "authority_status": state.authority_status.value,
        "compiled_mode": state.compiled_mode,
        "phase": state.phase.value,
        "policy_mode": state.policy_mode.value,
        "scope_status": state.scope_status.value,
        "warrant_status": state.warrant_status.value,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _step(
    transition_id: str,
    edge: Edge,
    before: MachineState,
    after: MachineState,
    *,
    observation: str | None = None,
    evidence: str | None = None,
    action: str | None = None,
    provenance: Provenance = Provenance.BASE_MACHINE,
) -> Step:
    return Step(
        transition_id=transition_id,
        edge=edge,
        before=before,
        after=after,
        observation=observation,
        evidence=evidence,
        action=action,
        provenance=provenance,
    )


def run_dynamic_episode(world: str, state: MachineState) -> Episode:
    if state.phase is not Phase.READY:
        raise ImplementationError("episode must start from READY state")
    if world not in {W_N, W_C}:
        raise ImplementationError(f"unknown world: {world!r}")

    observation = O_C if world == W_C else O_N
    evidence = E_STAR if world == W_C else E_N
    contradiction_id = C_STAR if world == W_C else None

    steps: list[Step] = []

    s1 = replace(state, phase=Phase.OBSERVED)
    steps.append(_step("T1_C" if world == W_C else "T1_N", Edge.E1, state, s1, observation=observation))

    s2 = replace(s1, phase=Phase.EVIDENCED)
    steps.append(_step("T2_C" if world == W_C else "T2_N", Edge.E2, s1, s2, observation=observation, evidence=evidence))

    if world == W_C and s2.scope_status is ScopeStatus.OPEN:
        warrant = WarrantStatus.CORRECTION
        t3 = "T3_C_OPEN"
    else:
        warrant = WarrantStatus.BASE
        t3 = "T3_C_CLOSED" if world == W_C else "T3_N"
    s3 = replace(s2, phase=Phase.WARRANTED, warrant_status=warrant)
    steps.append(_step(t3, Edge.E3, s2, s3, observation=observation, evidence=evidence))

    authority = AuthorityStatus.CORR_AUTH if warrant is WarrantStatus.CORRECTION else AuthorityStatus.BASE_AUTH
    s4 = replace(s3, phase=Phase.AUTHORIZED, authority_status=authority)
    steps.append(_step("T4_CORR" if authority is AuthorityStatus.CORR_AUTH else "T4_BASE", Edge.E4, s3, s4, evidence=evidence))

    policy = PolicyMode.CORRECTED if authority is AuthorityStatus.CORR_AUTH else PolicyMode.BASE
    s5 = replace(s4, phase=Phase.UPDATED, policy_mode=policy)
    steps.append(_step("T5_CORR_DYNAMIC" if policy is PolicyMode.CORRECTED else "T5_BASE_DYNAMIC", Edge.E5, s4, s5, evidence=evidence))

    action = A1 if policy is PolicyMode.CORRECTED else A0
    s6 = replace(s5, phase=Phase.ACTED)
    steps.append(_step("T6_CORR" if action == A1 else "T6_BASE", Edge.E6, s5, s6, evidence=evidence, action=action))

    return Episode(
        world=world,
        context=OMEGA_STAR,
        observation=observation,
        evidence=evidence,
        contradiction_id=contradiction_id,
        steps=tuple(steps),
        terminal_state=s6,
        action=action,
    )
