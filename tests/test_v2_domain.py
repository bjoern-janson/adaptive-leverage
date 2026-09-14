import pytest

from adaptive_leverage.model import ImplementationError
from adaptive_leverage.v2.domain import (
    KAPPA0,
    KAPPA1,
    S00,
    S01,
    S10,
    S11,
    canonical_carrier_bytes,
    canonical_correction_partition_bytes,
    canonical_k_corr_bytes,
    carrier,
    correction_blocks,
    i_spec,
    k_corr,
    semantic_alias,
)


def test_carrier_and_canonical_order_are_exact():
    assert carrier() == (S00, S01, S10, S11)
    assert [state.value for state in carrier()] == ["s00", "s01", "s10", "s11"]
    assert [semantic_alias(state) for state in carrier()] == [
        ("r0", "n0"),
        ("r0", "n1"),
        ("r1", "n0"),
        ("r1", "n1"),
    ]


def test_specialization_interface_is_exact_two_bit_square():
    assert [i_spec(state) for state in carrier()] == [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    ]


def test_reference_signatures_and_partition_are_exact():
    assert KAPPA0.as_tuple() == (
        "CORRECTION",
        "CORR_AUTH",
        "SET_C0",
        "ACT_C0",
        "OPEN",
    )
    assert KAPPA1.as_tuple() == (
        "CORRECTION",
        "CORR_AUTH",
        "SET_C1",
        "ACT_C1",
        "OPEN",
    )
    assert correction_blocks() == ((S00, S01), (S10, S11))
    assert k_corr(S00) == k_corr(S01) == KAPPA0
    assert k_corr(S10) == k_corr(S11) == KAPPA1
    assert k_corr(S00) != k_corr(S10)


def test_domain_canonical_serialization_is_deterministic_and_explicit():
    assert canonical_carrier_bytes() == b'["s00","s01","s10","s11"]'
    assert canonical_k_corr_bytes() == (
        b'[{"signature":["CORRECTION","CORR_AUTH","SET_C0","ACT_C0","OPEN"],"state":"s00"},'
        b'{"signature":["CORRECTION","CORR_AUTH","SET_C0","ACT_C0","OPEN"],"state":"s01"},'
        b'{"signature":["CORRECTION","CORR_AUTH","SET_C1","ACT_C1","OPEN"],"state":"s10"},'
        b'{"signature":["CORRECTION","CORR_AUTH","SET_C1","ACT_C1","OPEN"],"state":"s11"}]'
    )
    assert canonical_correction_partition_bytes() == (
        b'{"blocks":[["s00","s01"],["s10","s11"]]}'
    )


def test_domain_rejects_unknown_state_instead_of_coercing_it():
    with pytest.raises(ImplementationError):
        i_spec("s00")  # type: ignore[arg-type]
