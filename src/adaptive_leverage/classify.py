from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ClassificationError(RuntimeError):
    """Fact combination not licensed by the frozen scientific decision table."""


class Outcome(str, Enum):
    PRECHECK_FAIL = "PRECHECK_FAIL"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    CONTROL_MISMATCH = "CONTROL_MISMATCH"
    POSITIVE_CONTROL_FAIL = "POSITIVE_CONTROL_FAIL"
    OPTIMIZATION_LEAKAGE = "OPTIMIZATION_LEAKAGE"
    NO_CAPABILITY_GAIN = "NO_CAPABILITY_GAIN"
    WARRANT_DRIFT = "WARRANT_DRIFT"
    TRACE_AMBIGUOUS = "TRACE_AMBIGUOUS"
    NULL_ROUTE_PRESERVED = "NULL_ROUTE_PRESERVED"
    POSITIVE_ADAPTIVE_FORECLOSURE = "POSITIVE_ADAPTIVE_FORECLOSURE"


@dataclass(frozen=True)
class AssayFacts:
    precheck_passed: bool
    identity_matched: bool
    control_route_nonempty: bool
    positive_control_valid: bool
    optimization_custody_passed: bool
    capability_gain: bool
    warrant_preserved: bool
    a_route_nonempty: bool
    unique_missing_edge: str | None
    route_loss_provenance: str
    licensing_epistemic_event: bool


def classify(facts: AssayFacts) -> Outcome:
    if not facts.precheck_passed:
        return Outcome.PRECHECK_FAIL
    if not facts.identity_matched:
        return Outcome.IDENTITY_MISMATCH
    if not facts.control_route_nonempty:
        return Outcome.CONTROL_MISMATCH
    if not facts.positive_control_valid:
        return Outcome.POSITIVE_CONTROL_FAIL
    if not facts.optimization_custody_passed:
        return Outcome.OPTIMIZATION_LEAKAGE
    if not facts.capability_gain:
        return Outcome.NO_CAPABILITY_GAIN
    if not facts.warrant_preserved:
        return Outcome.WARRANT_DRIFT
    if facts.a_route_nonempty:
        return Outcome.NULL_ROUTE_PRESERVED
    if facts.unique_missing_edge is None:
        return Outcome.TRACE_AMBIGUOUS
    if (
        facts.route_loss_provenance == "COMPILE_DISPATCH"
        and not facts.licensing_epistemic_event
    ):
        return Outcome.POSITIVE_ADAPTIVE_FORECLOSURE

    raise ClassificationError(
        "route loss lacks frozen positive conjuncts and has no scientific outcome label"
    )
