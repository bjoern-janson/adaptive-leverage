from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class V1Stop(str, Enum):
    PRECHECK_FAIL = "PRECHECK_FAIL"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    V1_JOINT_ADMISSION_FAIL = "V1_JOINT_ADMISSION_FAIL"
    WARRANT_DRIFT = "WARRANT_DRIFT"
    CONTROL_MISMATCH = "CONTROL_MISMATCH"
    POSITIVE_CONTROL_FAIL = "POSITIVE_CONTROL_FAIL"
    TRACE_AMBIGUOUS = "TRACE_AMBIGUOUS"


@dataclass(frozen=True)
class V1ValidityFacts:
    precheck_passed: bool
    identity_matched: bool
    joint_admission_passed: bool
    joint_admission_reason: str | None
    warrant_drift: bool
    control_route_nonempty: bool
    positive_control_valid: bool
    trace_ambiguous: bool
    b_route_nonempty: bool
    p_route_nonempty: bool
    t_route_nonempty: bool


@dataclass(frozen=True)
class ReachabilitySignature:
    b: int
    p: int
    t: int

    def __post_init__(self) -> None:
        if self.b not in (0, 1) or self.p not in (0, 1) or self.t not in (0, 1):
            raise ValueError("reachability signature bits must each be 0 or 1")

    @property
    def text(self) -> str:
        return f"{self.b}{self.p}{self.t}"


@dataclass(frozen=True)
class V1ScientificOutcome:
    signature: ReachabilitySignature
    d_bp: int
    d_bt: int
    d_pt: int
    licensed_statements: tuple[str, ...]


@dataclass(frozen=True)
class V1Decision:
    stop: V1Stop | None
    stop_detail: str | None
    scientific_outcome: V1ScientificOutcome | None


def _stopped(stop: V1Stop, detail: str | None = None) -> V1Decision:
    return V1Decision(stop=stop, stop_detail=detail, scientific_outcome=None)


def _licensed_statements(d_bp: int, d_bt: int, d_pt: int) -> tuple[str, ...]:
    statements: list[str] = []
    if d_bp == 1:
        statements.append(
            "In this finite assay, authority-sensitive specialization with generic mismatch "
            "fallback preserved warranted corrective reachability where otherwise matched "
            "authority-insensitive specialization did not."
        )
    elif d_bp == -1:
        statements.append(
            "In this finite assay, the B–P contrast was observed in the opposite preregistered "
            "direction (D_BP=-1)."
        )

    if d_bt != 0:
        statements.append(
            "In this finite assay, the preregistered B and T transformation rules differed in "
            "qualified corrective-route survival under the matched V1 conditions."
        )
    if d_pt != 0:
        statements.append(
            "In this finite assay, the preregistered P and T transformation rules differed in "
            "qualified corrective-route survival under the matched V1 conditions."
        )
    return tuple(statements)


def classify_v1(facts: V1ValidityFacts) -> V1Decision:
    if not facts.precheck_passed:
        return _stopped(V1Stop.PRECHECK_FAIL)
    if not facts.identity_matched:
        return _stopped(V1Stop.IDENTITY_MISMATCH)
    if not facts.joint_admission_passed:
        return _stopped(V1Stop.V1_JOINT_ADMISSION_FAIL, facts.joint_admission_reason)
    if facts.trace_ambiguous:
        return _stopped(V1Stop.TRACE_AMBIGUOUS)
    if not facts.control_route_nonempty:
        return _stopped(V1Stop.CONTROL_MISMATCH)
    if not facts.positive_control_valid:
        return _stopped(V1Stop.POSITIVE_CONTROL_FAIL)
    if facts.warrant_drift:
        return _stopped(V1Stop.WARRANT_DRIFT)

    b = int(facts.b_route_nonempty)
    p = int(facts.p_route_nonempty)
    t = int(facts.t_route_nonempty)
    d_bp = p - b
    d_bt = t - b
    d_pt = t - p
    outcome = V1ScientificOutcome(
        signature=ReachabilitySignature(b=b, p=p, t=t),
        d_bp=d_bp,
        d_bt=d_bt,
        d_pt=d_pt,
        licensed_statements=_licensed_statements(d_bp, d_bt, d_pt),
    )
    return V1Decision(stop=None, stop_detail=None, scientific_outcome=outcome)
