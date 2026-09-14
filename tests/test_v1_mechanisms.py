from dataclasses import replace

from adaptive_leverage.model import A0, AuthorityStatus, OMEGA_STAR, W_N, initial_state
from adaptive_leverage.v1.mechanisms import (
    MechanismKind,
    construct_mechanism,
    downstream_matches,
    frozen_normal_transcript,
    frozen_objective,
    install_mechanism,
    upstream_matches,
    validate_mechanism_custody,
)


def build(kind, sequence):
    return construct_mechanism(
        kind,
        frozen_normal_transcript(),
        frozen_objective(),
        finalization_sequence=sequence,
    )


def test_all_mechanisms_share_identical_normal_input_and_objective_hashes():
    built = [build(kind, i) for i, kind in enumerate(MechanismKind, start=1)]
    input_hashes = {record.normal_manifest_sha256 for _, record in built}
    objective_hashes = {record.objective_sha256 for _, record in built}
    assert len(input_hashes) == 1
    assert len(objective_hashes) == 1


def test_b_downstream_key_ignores_authority_identity():
    artifact, _ = build(MechanismKind.B, 1)
    assert downstream_matches(artifact, OMEGA_STAR, AuthorityStatus.BASE_AUTH.value)
    assert downstream_matches(artifact, OMEGA_STAR, "SYNTHETIC_OTHER_AUTHORITY")


def test_p_downstream_key_requires_observed_authority_and_generic_mismatch_falls_back():
    artifact, _ = build(MechanismKind.P, 2)
    assert downstream_matches(artifact, OMEGA_STAR, AuthorityStatus.BASE_AUTH.value)
    assert not downstream_matches(artifact, OMEGA_STAR, "SYNTHETIC_OTHER_AUTHORITY")


def test_t_upstream_key_is_normal_world_context_and_protects_authority_state_class():
    artifact, _ = build(MechanismKind.T, 3)
    assert upstream_matches(artifact, W_N, OMEGA_STAR)
    assert not upstream_matches(artifact, "synthetic_other_world", OMEGA_STAR)
    assert artifact.protected_semantic_classes == ("AUTHORITY_TO_CONSEQUENTIAL_STATE",)


def test_each_artifact_passes_custody_without_corrective_inputs():
    for sequence, kind in enumerate(MechanismKind, start=1):
        artifact, record = build(kind, sequence)
        check = validate_mechanism_custody(record, artifact)
        assert check.passed
        assert artifact.normal_action == A0


def test_installation_changes_only_compiled_mode():
    artifact, _ = build(MechanismKind.B, 1)
    before = initial_state()
    after = install_mechanism(before, artifact)
    assert after == replace(before, compiled_mode=1)


def test_custody_detects_finalized_artifact_hash_mutation():
    artifact, record = build(MechanismKind.B, 1)
    mutated = replace(record, finalized_artifact_sha256="0" * 64)
    check = validate_mechanism_custody(mutated, artifact)
    assert not check.passed
    assert check.reason == "OPTIMIZATION_LEAKAGE"
