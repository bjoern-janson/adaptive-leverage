from dataclasses import replace

import pytest

from adaptive_leverage.model import (
    A1,
    C_STAR,
    E_STAR,
    OMEGA_STAR,
    O_C,
    W_C,
    AuthorityStatus,
    Edge,
    Episode,
    ImplementationError,
    Phase,
    PolicyMode,
    Provenance,
    Step,
    WarrantStatus,
    initial_state,
)
from adaptive_leverage.v1.assay import (
    CorrectionObservation,
    correction_identity_valid,
    qualified_v1_route,
    replay_v1_correction,
)
from adaptive_leverage.v1.trace import build_v1_trace


def synthetic_episode(*, corrected_policy=True, evidence=E_STAR):
    s0 = initial_state()
    s1 = replace(s0, phase=Phase.OBSERVED)
    s2 = replace(s1, phase=Phase.EVIDENCED)
    s3 = replace(s2, phase=Phase.WARRANTED, warrant_status=WarrantStatus.CORRECTION)
    s4 = replace(s3, phase=Phase.AUTHORIZED, authority_status=AuthorityStatus.CORR_AUTH)
    policy = PolicyMode.CORRECTED if corrected_policy else PolicyMode.BASE
    s5 = replace(s4, phase=Phase.UPDATED, policy_mode=policy)
    s6 = replace(s5, phase=Phase.ACTED)
    action = A1
    steps = (
        Step("FIXTURE_E1", Edge.E1, s0, s1, observation=O_C, provenance=Provenance.BASE_MACHINE),
        Step("FIXTURE_E2", Edge.E2, s1, s2, observation=O_C, evidence=evidence, provenance=Provenance.BASE_MACHINE),
        Step("FIXTURE_E3", Edge.E3, s2, s3, evidence=evidence, provenance=Provenance.BASE_MACHINE),
        Step("FIXTURE_E4", Edge.E4, s3, s4, evidence=evidence, provenance=Provenance.BASE_MACHINE),
        Step("FIXTURE_E5", Edge.E5, s4, s5, evidence=evidence, provenance=Provenance.BASE_MACHINE),
        Step("FIXTURE_E6", Edge.E6, s5, s6, evidence=evidence, action=action, provenance=Provenance.BASE_MACHINE),
    )
    return Episode(
        world=W_C,
        context=OMEGA_STAR,
        observation=O_C,
        evidence=evidence,
        contradiction_id=C_STAR,
        steps=steps,
        terminal_state=s6,
        action=action,
    )


def synthetic_trace(**kwargs):
    return build_v1_trace(
        synthetic_episode(**kwargs),
        arm="FIXTURE",
        run_id="software-fixture-qualified",
        mechanism_artifact_sha256=None,
    )


def synthetic_observation(*, evidence=E_STAR):
    trace = synthetic_trace(evidence=evidence)
    return CorrectionObservation(
        arm="FIXTURE",
        world=W_C,
        context=OMEGA_STAR,
        observation=O_C,
        evidence=evidence,
        contradiction_id=C_STAR,
        action=A1,
        trace=trace,
        route_nonempty=qualified_v1_route(trace),
        warrant_drift=False,
        scope_closed_valid=False,
        licensing_epistemic_event=False,
        route_loss_provenance=Provenance.BASE_MACHINE.value,
    )


def test_qualified_route_requires_evidence_warrant_authority_corrected_policy_and_a1_in_order():
    assert qualified_v1_route(synthetic_trace())


def test_missing_corrected_policy_makes_route_empty():
    assert not qualified_v1_route(synthetic_trace(corrected_policy=False))


def test_changed_evidence_identity_is_warrant_drift_not_a_reachability_bit():
    observation = synthetic_observation(evidence="synthetic_wrong_evidence")
    assert not correction_identity_valid(observation)


def test_corrective_replay_without_joint_release_stops_before_episode(monkeypatch):
    called = False

    def forbidden(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("episode constructed before corrective release")

    monkeypatch.setattr("adaptive_leverage.v1.assay.run_v1_world_episode", forbidden)
    with pytest.raises(ImplementationError):
        replay_v1_correction(
            "B",
            initial_state(),
            artifact=None,
            mechanism_artifact_sha256_value=None,
            release_token=None,
            built={},
            run_id="software-no-release",
        )
    assert not called
