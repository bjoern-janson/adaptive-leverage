from dataclasses import replace

import pytest

from adaptive_leverage.model import ImplementationError, initial_state
from adaptive_leverage.v1.assay import (
    JointAdmissionReason,
    fork_v1_arms,
    joint_admit,
    measure_v1_normal,
    require_corrective_release,
)
from adaptive_leverage.v1.mechanisms import (
    MechanismKind,
    construct_mechanism,
    frozen_normal_transcript,
    frozen_objective,
    validate_mechanism_custody,
)


def build_all():
    return {
        kind: construct_mechanism(
            kind,
            frozen_normal_transcript(),
            frozen_objective(),
            finalization_sequence=i,
        )
        for i, kind in enumerate(MechanismKind, start=1)
    }


def measurements_and_custody(built, bundle):
    observations = {}
    custody = {}
    for arm, kind in (("B", MechanismKind.B), ("P", MechanismKind.P), ("T", MechanismKind.T)):
        artifact, record = built[kind]
        observations[arm] = measure_v1_normal(
            arm,
            getattr(bundle, arm.lower()),
            artifact,
            record.finalized_artifact_sha256,
        )
        custody[arm] = validate_mechanism_custody(record, artifact)
    return observations, custody


def test_all_five_arms_are_byte_identical_before_registered_interventions():
    bundle = fork_v1_arms(initial_state())
    assert len(set(bundle.prefork_serialized.values())) == 1
    assert set(bundle.prefork_serialized) == {"C", "B", "P", "T", "E"}


def test_joint_admission_requires_all_three_exact_cost_five_and_matching_correctness():
    built = build_all()
    bundle = fork_v1_arms(initial_state())
    baseline = measure_v1_normal("C", bundle.c, None, None)
    observations, custody = measurements_and_custody(built, bundle)
    admission = joint_admit(baseline, observations, custody, built)
    assert admission.passed
    assert admission.release_token is not None
    require_corrective_release(admission.release_token, built)


def test_one_cost_mismatch_fails_the_entire_joint_gate_without_release_token():
    built = build_all()
    bundle = fork_v1_arms(initial_state())
    baseline = measure_v1_normal("C", bundle.c, None, None)
    observations, custody = measurements_and_custody(built, bundle)
    observations["P"] = replace(observations["P"], cost=4)
    admission = joint_admit(baseline, observations, custody, built)
    assert not admission.passed
    assert admission.reason is JointAdmissionReason.COST_MISMATCH
    assert admission.release_token is None


def test_one_correctness_mismatch_fails_the_entire_joint_gate():
    built = build_all()
    bundle = fork_v1_arms(initial_state())
    baseline = measure_v1_normal("C", bundle.c, None, None)
    observations, custody = measurements_and_custody(built, bundle)
    observations["B"] = replace(observations["B"], action="synthetic_wrong_action", correctness=False)
    admission = joint_admit(baseline, observations, custody, built)
    assert not admission.passed
    assert admission.reason is JointAdmissionReason.NORMAL_CORRECTNESS_MISMATCH
    assert admission.release_token is None


def test_release_token_rejects_hash_tampering():
    built = build_all()
    bundle = fork_v1_arms(initial_state())
    baseline = measure_v1_normal("C", bundle.c, None, None)
    observations, custody = measurements_and_custody(built, bundle)
    token = joint_admit(baseline, observations, custody, built).release_token
    assert token is not None
    tampered = replace(token, b_artifact_sha256="0" * 64)
    with pytest.raises(ImplementationError):
        require_corrective_release(tampered, built)
