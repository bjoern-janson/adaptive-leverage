from dataclasses import replace
from pathlib import Path

import pytest

from adaptive_leverage.v2.assay import (
    V2_JOINT_ADMISSION_FAIL,
    joint_admit,
    prepare_v2,
)
from adaptive_leverage.v2.compiler import CandidateScore
from adaptive_leverage.v2.topology import RefinementMode, WriteMode


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def valid_prepared(run_id: str = "software-admission"):
    return prepare_v2(repo_root(), run_id=run_id)


def assert_rejected(prepared, expected_check: str):
    admission = joint_admit(replace(prepared, joint_admission=None))
    assert admission.passed is False
    assert admission.reason == V2_JOINT_ADMISSION_FAIL
    assert admission.failed_check == expected_check
    assert admission.release_token is None


def test_valid_joint_admission_binds_all_pre_replay_custody_objects():
    prepared = valid_prepared()
    admission = prepared.joint_admission
    assert admission is not None
    assert admission.passed is True
    assert admission.reason is None
    assert admission.failed_check is None
    token = admission.release_token
    assert token is not None

    assert token.alpha_artifact_sha256 == prepared.alpha.custody.finalized_artifact_sha256
    assert token.beta_artifact_sha256 == prepared.beta.custody.finalized_artifact_sha256
    assert token.correction_partition_sha256 == prepared.correction_partition_sha256
    assert token.alpha_partition_sha256 == prepared.alpha_partition.partition_sha256
    assert token.alpha_predictor_sha256 == prepared.alpha_partition.predictor_sha256
    assert token.beta_partition_sha256 == prepared.beta_partition.partition_sha256
    assert token.beta_predictor_sha256 == prepared.beta_partition.predictor_sha256
    assert token.topology_sha256s == tuple(x.sha256 for x in prepared.topologies)
    assert token.admission_sha256 == admission.admission_sha256


def test_authority_hash_mutation_fails_closed():
    prepared = valid_prepared("mut-authority")
    assert_rejected(replace(prepared, authority_binding_sha256="0" * 64), "authority")


def test_x_normal_hash_mutation_fails_closed():
    prepared = valid_prepared("mut-x-normal")
    assert_rejected(replace(prepared, normal_data_sha256="0" * 64), "normal_inputs")


def test_objective_hash_mutation_fails_closed():
    prepared = valid_prepared("mut-objective")
    assert_rejected(replace(prepared, objective_sha256="0" * 64), "normal_inputs")


def test_candidate_family_mutation_fails_closed():
    prepared = valid_prepared("mut-family")
    bad_custody = replace(
        prepared.alpha.custody,
        candidate_names=("g_AA", "g_AB", "g_BA", "g_BB"),
    )
    bad_alpha = replace(prepared.alpha, custody=bad_custody)
    assert_rejected(replace(prepared, alpha=bad_alpha), "candidate_families")


def test_unique_minimizer_mutation_fails_closed():
    prepared = valid_prepared("mut-minimizer")
    bad_alpha = replace(prepared.alpha, selected_candidate="g_AA")
    assert_rejected(replace(prepared, alpha=bad_alpha), "unique_minimizer")


def test_observed_correctness_mutation_fails_closed():
    prepared = valid_prepared("mut-correctness")
    bad_alpha = replace(prepared.alpha, observed_correctness=(True, False))
    assert_rejected(replace(prepared, alpha=bad_alpha), "normal_admission")


def test_observed_cost_mutation_fails_closed():
    prepared = valid_prepared("mut-cost")
    bad_alpha = replace(prepared.alpha, observed_cost=6)
    assert_rejected(replace(prepared, alpha=bad_alpha), "normal_admission")


def test_withheld_state_construction_leakage_fails_closed():
    prepared = valid_prepared("mut-leakage")
    leaked = prepared.adaptive_example_states + ("s01",)
    assert_rejected(replace(prepared, adaptive_example_states=leaked), "withholding")


def test_dispatch_canonicalization_mutation_fails_closed():
    prepared = valid_prepared("mut-dispatch")
    bad_partition = replace(prepared.alpha_partition, dispatch_sha256="0" * 64)
    assert_rejected(replace(prepared, alpha_partition=bad_partition), "dispatch")


def test_partition_predictor_custody_mutation_fails_closed():
    prepared = valid_prepared("mut-predictor")
    bad_partition = replace(prepared.beta_partition, predictor_sha256="0" * 64)
    assert_rejected(replace(prepared, beta_partition=bad_partition), "prospective_predictor")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("refinement", RefinementMode.NO_REFINE),
        ("write", WriteMode.BLOCKED),
    ],
)
def test_topology_descriptor_mutation_fails_closed(field, value):
    prepared = valid_prepared(f"mut-topology-{field}")
    descriptor = prepared.topologies[0]
    mutated = replace(descriptor, **{field: value})
    topologies = (mutated,) + prepared.topologies[1:]
    assert_rejected(replace(prepared, topologies=topologies), "topology")


def test_candidate_score_mutation_fails_closed_even_if_selected_artifact_unchanged():
    prepared = valid_prepared("mut-score-table")
    scores = list(prepared.alpha.custody.candidate_scores)
    scores[0] = CandidateScore("g_AA", (True, True), 5)
    bad_custody = replace(prepared.alpha.custody, candidate_scores=tuple(scores))
    bad_alpha = replace(prepared.alpha, custody=bad_custody)
    assert_rejected(replace(prepared, alpha=bad_alpha), "candidate_scoring")


def test_finalized_artifact_content_mutation_fails_even_if_custody_hash_is_unchanged():
    prepared = valid_prepared("mut-artifact-content")
    bad_artifact = replace(prepared.alpha.artifact, output_for_zero="ACT_NB")
    bad_alpha = replace(prepared.alpha, artifact=bad_artifact)
    assert_rejected(replace(prepared, alpha=bad_alpha), "finalized_artifacts")


def test_dispatch_table_content_mutation_fails_even_if_dispatch_hash_is_unchanged():
    prepared = valid_prepared("mut-dispatch-content")
    rows = list(prepared.alpha_partition.dispatch_table)
    rows[0] = replace(rows[0], action="ACT_NB")
    bad_partition = replace(prepared.alpha_partition, dispatch_table=tuple(rows))
    assert_rejected(replace(prepared, alpha_partition=bad_partition), "dispatch")


def test_hypothesis_descriptor_hash_mutation_fails_candidate_family_gate():
    prepared = valid_prepared("mut-family-descriptor")
    bad_custody = replace(prepared.beta.custody, hypothesis_descriptor_sha256="0" * 64)
    bad_beta = replace(prepared.beta, custody=bad_custody)
    assert_rejected(replace(prepared, beta=bad_beta), "candidate_families")
