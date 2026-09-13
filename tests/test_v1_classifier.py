from dataclasses import replace
import itertools

from adaptive_leverage.v1.classify import (
    V1Stop,
    V1ValidityFacts,
    classify_v1,
)


def valid_facts(bits=(False, False, False)):
    return V1ValidityFacts(
        precheck_passed=True,
        identity_matched=True,
        joint_admission_passed=True,
        joint_admission_reason=None,
        warrant_drift=False,
        control_route_nonempty=True,
        positive_control_valid=True,
        trace_ambiguous=False,
        b_route_nonempty=bits[0],
        p_route_nonempty=bits[1],
        t_route_nonempty=bits[2],
    )


def test_invalidity_emits_no_scientific_outcome():
    decision = classify_v1(replace(valid_facts(), joint_admission_passed=False, joint_admission_reason="COST_MISMATCH"))
    assert decision.stop is V1Stop.V1_JOINT_ADMISSION_FAIL
    assert decision.scientific_outcome is None


def test_all_eight_signatures_are_emitted_without_preference_or_ordering():
    observed = set()
    for bits in itertools.product((False, True), repeat=3):
        decision = classify_v1(valid_facts(bits))
        assert decision.stop is None
        outcome = decision.scientific_outcome
        assert outcome is not None
        observed.add(outcome.signature.text)
        assert not hasattr(outcome, "score")
        assert not hasattr(outcome, "rank")
        assert not hasattr(outcome, "bit_count")
    assert observed == {"000", "001", "010", "011", "100", "101", "110", "111"}


def test_pairwise_contrasts_are_signed_differences_only():
    outcome = classify_v1(valid_facts((False, True, False))).scientific_outcome
    assert outcome is not None
    assert outcome.d_bp == 1
    assert outcome.d_bt == 0
    assert outcome.d_pt == -1


def test_only_positive_bp_contrast_gets_single_property_statement():
    outcome = classify_v1(valid_facts((False, True, False))).scientific_outcome
    assert outcome is not None
    assert any("authority-sensitive specialization" in text for text in outcome.licensed_statements)
    opposite = classify_v1(valid_facts((True, False, False))).scientific_outcome
    assert opposite is not None
    assert not any("preserved warranted corrective reachability where otherwise matched" in text for text in opposite.licensed_statements)


def test_stop_precedence_follows_frozen_order():
    facts = replace(
        valid_facts(),
        precheck_passed=False,
        identity_matched=False,
        joint_admission_passed=False,
        trace_ambiguous=True,
        control_route_nonempty=False,
        positive_control_valid=False,
        warrant_drift=True,
    )
    assert classify_v1(facts).stop is V1Stop.PRECHECK_FAIL
    facts = replace(facts, precheck_passed=True)
    assert classify_v1(facts).stop is V1Stop.IDENTITY_MISMATCH
    facts = replace(facts, identity_matched=True)
    assert classify_v1(facts).stop is V1Stop.V1_JOINT_ADMISSION_FAIL
    facts = replace(facts, joint_admission_passed=True)
    assert classify_v1(facts).stop is V1Stop.TRACE_AMBIGUOUS
    facts = replace(facts, trace_ambiguous=False)
    assert classify_v1(facts).stop is V1Stop.CONTROL_MISMATCH
    facts = replace(facts, control_route_nonempty=True)
    assert classify_v1(facts).stop is V1Stop.POSITIVE_CONTROL_FAIL
    facts = replace(facts, positive_control_valid=True)
    assert classify_v1(facts).stop is V1Stop.WARRANT_DRIFT
