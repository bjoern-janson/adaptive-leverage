from dataclasses import replace
from hashlib import sha256

import pytest

from adaptive_leverage.model import ImplementationError
from adaptive_leverage.v2.compiler import (
    X_NORMAL_SHA256,
    OBJECTIVE_SHA256,
    candidate_family,
    compile_family,
    frozen_normal_data,
    frozen_objective,
    score_candidate,
)


def test_normal_data_contains_exactly_diagonal_states():
    data = frozen_normal_data()
    assert tuple(x.state for x in data.examples) == ("s00", "s11")
    assert tuple(x.target for x in data.examples) == ("ACT_NA", "ACT_NB")
    assert data.canonical_json == (
        '[{"baseline_cost":6,"i_spec":[0,0],"state":"s00","target":"ACT_NA"},'
        '{"baseline_cost":6,"i_spec":[1,1],"state":"s11","target":"ACT_NB"}]'
    )
    assert "s01" not in data.canonical_json
    assert "s10" not in data.canonical_json
    assert sha256(data.canonical_json.encode("utf-8")).hexdigest() == X_NORMAL_SHA256
    assert X_NORMAL_SHA256 == "d477bfb12d9e97f5bc90502530a8d5e25b8a8ed281de22bd15c32b0df0559e84"


def test_objective_bytes_are_exact_frozen_j():
    objective = frozen_objective()
    assert objective.canonical_json == (
        '{"minimize":"causal_microtransition_cost",'
        '"preserve_observed_normal_correctness":true}'
    )
    assert sha256(objective.canonical_json.encode("utf-8")).hexdigest() == OBJECTIVE_SHA256
    assert OBJECTIVE_SHA256 == "b2be6744a89f0a81d1e043fa60f1bd11b0f8dbe38efeafb981d26808877adb5b"


def test_each_family_has_four_compiled_maps_plus_dynamic():
    for j in (0, 1):
        family = candidate_family(j)
        assert family.coordinate_index == j
        assert tuple(c.name for c in family) == (
            "g_AA", "g_AB", "g_BA", "g_BB", "T_dynamic"
        )


def test_candidate_scoring_table_is_exact_and_identical_across_families():
    expected = {
        "g_AA": ((True, False), 5),
        "g_AB": ((True, True), 5),
        "g_BA": ((False, False), 5),
        "g_BB": ((False, True), 5),
        "T_dynamic": ((True, True), 6),
    }
    data = frozen_normal_data()
    for j in (0, 1):
        observed = {
            candidate.name: (
                score_candidate(candidate, data, coordinate_index=j).observed_correctness,
                score_candidate(candidate, data, coordinate_index=j).observed_cost,
            )
            for candidate in candidate_family(j)
        }
        assert observed == expected


def test_same_data_uniquely_selects_g_ab_in_both_families():
    for j in (0, 1):
        result = compile_family(j, frozen_normal_data(), frozen_objective())
        assert result.selected_candidate == "g_AB"
        assert result.observed_cost == 5
        assert result.observed_correctness == (True, True)
        assert result.artifact.coordinate_index == j
        assert result.artifact.output_for_zero == "ACT_NA"
        assert result.artifact.output_for_one == "ACT_NB"
        assert result.custody.normal_data_sha256 == X_NORMAL_SHA256
        assert result.custody.objective_sha256 == OBJECTIVE_SHA256
        assert result.custody.selected_candidate == "g_AB"
        assert tuple(score.candidate_name for score in result.custody.candidate_scores) == (
            "g_AA", "g_AB", "g_BA", "g_BB", "T_dynamic"
        )


def test_compile_rejects_nonfrozen_data_or_objective():
    data = frozen_normal_data()
    objective = frozen_objective()
    bad_example = replace(data.examples[0], target="ACT_NB")
    bad_data = replace(data, examples=(bad_example, data.examples[1]))
    bad_objective = replace(objective, minimize="other_metric")

    with pytest.raises(ImplementationError, match="X_normal"):
        compile_family(0, bad_data, objective)
    with pytest.raises(ImplementationError, match="objective"):
        compile_family(0, data, bad_objective)


def test_unknown_coordinate_family_is_rejected():
    with pytest.raises(ImplementationError, match="coordinate"):
        candidate_family(2)
    with pytest.raises(ImplementationError, match="coordinate"):
        compile_family(2, frozen_normal_data(), frozen_objective())
