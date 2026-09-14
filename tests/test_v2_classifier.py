from __future__ import annotations

from dataclasses import fields
import inspect
import itertools

import pytest

from adaptive_leverage.model import ImplementationError
from adaptive_leverage.v2.classify import (
    ArmKey,
    ArmReachability,
    V2Stop,
    classify_v2,
    raw_reachability_matrix,
)
from adaptive_leverage.v2.domain import carrier
from adaptive_leverage.v2.topology import RefinementMode, WriteMode


TRANSFORMATIONS = ("T_ALPHA", "T_BETA")
TOPOLOGIES = tuple(
    (refinement, write)
    for refinement in (RefinementMode.REFINE, RefinementMode.NO_REFINE)
    for write in (WriteMode.LIVE, WriteMode.BLOCKED)
)


def arm_key(
    transformation: str,
    refinement: RefinementMode,
    write: WriteMode,
) -> ArmKey:
    return ArmKey(
        transformation=transformation,
        refinement=refinement,
        write=write,
    )


def matrix_from_f_vector(
    f_by_arm: dict[ArmKey, int],
):
    state_ids = tuple(state.value for state in carrier())
    rows = []
    for transformation in TRANSFORMATIONS:
        for refinement, write in TOPOLOGIES:
            key = arm_key(transformation, refinement, write)
            f_value = f_by_arm[key]
            routes = tuple(True for _ in state_ids)
            if f_value == 1:
                routes = (False, *routes[1:])
            rows.append(
                ArmReachability(
                    arm=key,
                    route_nonempty=tuple(zip(state_ids, routes, strict=True)),
                )
            )
    return raw_reachability_matrix(tuple(rows))


def constant_f_vector(value: int) -> dict[ArmKey, int]:
    return {
        arm_key(transformation, refinement, write): value
        for transformation in TRANSFORMATIONS
        for refinement, write in TOPOLOGIES
    }


def test_f_is_one_iff_any_state_route_is_empty():
    f_by_arm = constant_f_vector(0)
    target = arm_key("T_ALPHA", RefinementMode.NO_REFINE, WriteMode.LIVE)
    f_by_arm[target] = 1

    decision = classify_v2(matrix_from_f_vector(f_by_arm), validity_passed=True)

    assert decision.stop is None
    assert decision.scientific_outcome is not None
    observed = {entry.arm: entry.f for entry in decision.scientific_outcome.f_vector}
    assert observed == f_by_arm


def test_d_is_signed_beta_minus_alpha_with_topology_fixed():
    f_by_arm = constant_f_vector(0)
    f_by_arm[arm_key("T_BETA", RefinementMode.REFINE, WriteMode.LIVE)] = 1
    f_by_arm[arm_key("T_ALPHA", RefinementMode.REFINE, WriteMode.BLOCKED)] = 1

    decision = classify_v2(matrix_from_f_vector(f_by_arm), validity_passed=True)

    assert decision.scientific_outcome is not None
    contrasts = {
        (entry.refinement, entry.write): entry.d
        for entry in decision.scientific_outcome.d_contrasts
    }
    assert contrasts == {
        (RefinementMode.REFINE, WriteMode.LIVE): 1,
        (RefinementMode.REFINE, WriteMode.BLOCKED): -1,
        (RefinementMode.NO_REFINE, WriteMode.LIVE): 0,
        (RefinementMode.NO_REFINE, WriteMode.BLOCKED): 0,
    }


def test_all_logical_mf_cells_are_accepted_without_ranking():
    f_by_arm = constant_f_vector(0)
    f_by_arm[arm_key("T_ALPHA", RefinementMode.REFINE, WriteMode.BLOCKED)] = 1
    f_by_arm[arm_key("T_BETA", RefinementMode.NO_REFINE, WriteMode.BLOCKED)] = 1

    outcome = classify_v2(
        matrix_from_f_vector(f_by_arm),
        validity_passed=True,
    ).scientific_outcome

    assert outcome is not None
    assert outcome.c_mf_obs == frozenset({(0, 0), (0, 1), (1, 0), (1, 1)})
    forbidden = {"score", "rank", "best", "preferred", "success", "aggregate"}
    assert forbidden.isdisjoint(field.name for field in fields(outcome))


def test_every_binary_f_vector_is_accepted_mechanically():
    arm_order = tuple(
        arm_key(transformation, refinement, write)
        for transformation in TRANSFORMATIONS
        for refinement, write in TOPOLOGIES
    )
    for bits in itertools.product((0, 1), repeat=8):
        f_by_arm = dict(zip(arm_order, bits, strict=True))
        decision = classify_v2(matrix_from_f_vector(f_by_arm), validity_passed=True)
        assert decision.stop is None
        assert decision.scientific_outcome is not None


def test_invalidity_emits_no_scientific_outcome():
    decision = classify_v2(
        None,
        validity_passed=False,
        invalid_reason="trace-integrity failure",
    )
    assert decision.stop is V2Stop.INVALID_EXECUTION
    assert decision.stop_detail == "trace-integrity failure"
    assert decision.scientific_outcome is None


def test_validity_cannot_encode_missing_raw_matrix_as_a_scientific_null():
    with pytest.raises(ImplementationError, match="raw reachability matrix"):
        classify_v2(None, validity_passed=True)


def test_raw_matrix_requires_exact_eight_arm_identity_set():
    matrix = matrix_from_f_vector(constant_f_vector(0))
    with pytest.raises(ImplementationError, match="exactly the eight frozen arms"):
        raw_reachability_matrix(matrix.rows[:-1])


def test_each_arm_requires_exact_carrier_state_identity_set():
    key = arm_key("T_ALPHA", RefinementMode.REFINE, WriteMode.LIVE)
    with pytest.raises(ImplementationError, match="exact carrier states"):
        ArmReachability(
            arm=key,
            route_nonempty=(("s00", True), ("s01", True), ("s10", True)),
        )


def test_arm_identities_are_not_orderable_or_rankable():
    alpha = arm_key("T_ALPHA", RefinementMode.REFINE, WriteMode.LIVE)
    beta = arm_key("T_BETA", RefinementMode.REFINE, WriteMode.LIVE)
    with pytest.raises(TypeError):
        _ = alpha < beta


def test_classifier_has_no_replay_dependency_or_scalarization_api():
    import adaptive_leverage.v2.classify as classify_module

    source = inspect.getsource(classify_module)
    assert "adaptive_leverage.v2.replay" not in source
    assert "from adaptive_leverage.v2.replay" not in source
    assert "sum(" not in source
    assert "weighted" not in source.lower()

    forbidden = {"score", "rank", "best", "preferred", "success", "aggregate"}
    public_names = {
        name
        for name in dir(classify_module)
        if not name.startswith("_")
    }
    assert forbidden.isdisjoint(public_names)
