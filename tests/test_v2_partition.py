from dataclasses import replace
from hashlib import sha256

import pytest

from adaptive_leverage.model import ImplementationError
from adaptive_leverage.v2.compiler import compile_family, frozen_normal_data, frozen_objective
from adaptive_leverage.v2.partition import (
    DispatchObject,
    canonical_dispatch_bytes,
    canonical_partition_bytes,
    canonical_predictor_bytes,
    dispatch_action,
    extract_dispatch_table,
    prospective_partition,
)


def artifact(coordinate_index: int):
    return compile_family(
        coordinate_index,
        frozen_normal_data(),
        frozen_objective(),
    ).artifact


def test_alpha_and_beta_generalize_differently_only_after_compilation():
    alpha = artifact(0)
    beta = artifact(1)

    assert dispatch_action(alpha, "s01") == "ACT_NA"
    assert dispatch_action(alpha, "s10") == "ACT_NB"
    assert dispatch_action(beta, "s01") == "ACT_NB"
    assert dispatch_action(beta, "s10") == "ACT_NA"


def test_full_dispatch_table_is_canonical_and_uses_full_dispatch_object():
    alpha = extract_dispatch_table(artifact(0))
    beta = extract_dispatch_table(artifact(1))

    d0 = DispatchObject("K0", "FAST_NORMAL", "GENERIC_POST_SPECIALIZATION")
    d1 = DispatchObject("K1", "FAST_NORMAL", "GENERIC_POST_SPECIALIZATION")

    assert tuple((row.state, row.dispatch, row.action) for row in alpha) == (
        ("s00", d0, "ACT_NA"),
        ("s01", d0, "ACT_NA"),
        ("s10", d1, "ACT_NB"),
        ("s11", d1, "ACT_NB"),
    )
    assert tuple((row.state, row.dispatch, row.action) for row in beta) == (
        ("s00", d0, "ACT_NA"),
        ("s01", d1, "ACT_NB"),
        ("s10", d0, "ACT_NA"),
        ("s11", d1, "ACT_NB"),
    )


def test_partition_equality_is_not_terminal_action_equality():
    alpha = artifact(0)
    same_action = replace(alpha, output_for_one="ACT_NA")
    record = prospective_partition(same_action)

    assert record.partition == (("s00", "s01"), ("s10", "s11"))
    assert tuple(row.action for row in record.dispatch_table) == (
        "ACT_NA", "ACT_NA", "ACT_NA", "ACT_NA"
    )


def test_alpha_is_aligned_and_beta_has_exact_two_witnesses():
    alpha = prospective_partition(artifact(0))
    beta = prospective_partition(artifact(1))

    assert alpha.partition == (("s00", "s01"), ("s10", "s11"))
    assert alpha.mismatch == 0
    assert alpha.witnesses == ()

    assert beta.partition == (("s00", "s10"), ("s01", "s11"))
    assert beta.mismatch == 1
    assert beta.witnesses == (("s00", "s10"), ("s01", "s11"))


def test_witnesses_are_canonical_and_serialization_is_hash_stable():
    beta = prospective_partition(artifact(1))
    assert all(("s00", "s01", "s10", "s11").index(x) < ("s00", "s01", "s10", "s11").index(y)
               for x, y in beta.witnesses)

    assert sha256(canonical_dispatch_bytes(beta.dispatch_table)).hexdigest() == beta.dispatch_sha256
    assert sha256(canonical_partition_bytes(beta.partition)).hexdigest() == beta.partition_sha256
    assert sha256(canonical_predictor_bytes(beta.mismatch, beta.witnesses)).hexdigest() == beta.predictor_sha256


def test_partition_extraction_does_not_mutate_finalized_artifact():
    alpha = artifact(0)
    before = alpha
    prospective_partition(alpha)
    assert alpha == before


def test_unknown_state_dispatch_is_rejected():
    with pytest.raises(ImplementationError, match="carrier state"):
        dispatch_action(artifact(0), "s99")
