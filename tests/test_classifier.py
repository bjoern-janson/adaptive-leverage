from dataclasses import replace

import pytest

from adaptive_leverage.classify import (
    AssayFacts,
    ClassificationError,
    Outcome,
    classify,
)


def positive_facts():
    return AssayFacts(
        precheck_passed=True,
        identity_matched=True,
        control_route_nonempty=True,
        positive_control_valid=True,
        optimization_custody_passed=True,
        capability_gain=True,
        warrant_preserved=True,
        a_route_nonempty=False,
        unique_missing_edge="E5",
        route_loss_provenance="COMPILE_DISPATCH",
        licensing_epistemic_event=False,
    )


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("precheck_passed", False, Outcome.PRECHECK_FAIL),
        ("identity_matched", False, Outcome.IDENTITY_MISMATCH),
        ("control_route_nonempty", False, Outcome.CONTROL_MISMATCH),
        ("positive_control_valid", False, Outcome.POSITIVE_CONTROL_FAIL),
        ("optimization_custody_passed", False, Outcome.OPTIMIZATION_LEAKAGE),
        ("capability_gain", False, Outcome.NO_CAPABILITY_GAIN),
        ("warrant_preserved", False, Outcome.WARRANT_DRIFT),
        ("unique_missing_edge", None, Outcome.TRACE_AMBIGUOUS),
    ],
)
def test_stop_and_invalid_precedence(field, value, expected):
    assert classify(replace(positive_facts(), **{field: value})) is expected


def test_clean_null_when_route_is_preserved():
    facts = replace(positive_facts(), a_route_nonempty=True, unique_missing_edge=None)
    assert classify(facts) is Outcome.NULL_ROUTE_PRESERVED


def test_positive_fixture_requires_all_conjuncts():
    assert classify(positive_facts()) is Outcome.POSITIVE_ADAPTIVE_FORECLOSURE


def test_licensing_event_cannot_be_silently_mapped_to_scientific_outcome():
    facts = replace(positive_facts(), licensing_epistemic_event=True)
    with pytest.raises(ClassificationError):
        classify(facts)


def test_wrong_route_loss_provenance_cannot_be_silently_mapped_to_scientific_outcome():
    facts = replace(positive_facts(), route_loss_provenance="BASE_MACHINE")
    with pytest.raises(ClassificationError):
        classify(facts)
