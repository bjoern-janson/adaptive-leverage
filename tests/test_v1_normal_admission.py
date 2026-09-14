from adaptive_leverage.model import A0, W_N, initial_state, run_dynamic_episode
from adaptive_leverage.v1.episodes import run_v1_normal_episode
from adaptive_leverage.v1.mechanisms import (
    MechanismKind,
    construct_mechanism,
    frozen_normal_transcript,
    frozen_objective,
    install_mechanism,
)


def artifact(kind, sequence):
    return construct_mechanism(
        kind,
        frozen_normal_transcript(),
        frozen_objective(),
        finalization_sequence=sequence,
    )[0]


def test_baseline_normal_cost_remains_six():
    episode = run_dynamic_episode(W_N, initial_state())
    assert episode.action == A0
    assert len(episode.steps) == 6


def test_each_v1_mechanism_has_same_normal_action_and_exact_cost_five():
    for sequence, kind in enumerate(MechanismKind, start=1):
        mechanism = artifact(kind, sequence)
        state = install_mechanism(initial_state(), mechanism)
        episode = run_v1_normal_episode(state, mechanism)
        assert episode.action == A0
        assert len(episode.steps) == 5


def test_b_and_p_compile_same_downstream_normal_site():
    b_artifact = artifact(MechanismKind.B, 1)
    p_artifact = artifact(MechanismKind.P, 2)
    b = run_v1_normal_episode(install_mechanism(initial_state(), b_artifact), b_artifact)
    p = run_v1_normal_episode(install_mechanism(initial_state(), p_artifact), p_artifact)
    assert [s.transition_id for s in b.steps[:4]] == [s.transition_id for s in p.steps[:4]]
    assert b.steps[-1].transition_id == p.steps[-1].transition_id == "V1_DOWNSTREAM_E5_E6_COMPILED"


def test_t_compiles_upstream_normal_site_and_leaves_e3_through_e6_dynamic():
    t_artifact = artifact(MechanismKind.T, 3)
    t = run_v1_normal_episode(install_mechanism(initial_state(), t_artifact), t_artifact)
    assert t.steps[0].transition_id == "V1_UPSTREAM_E1_E2_COMPILED"
    assert [step.edge.value for step in t.steps[1:]] == ["E3", "E4", "E5", "E6"]
