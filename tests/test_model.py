from adaptive_leverage.model import (
    A0,
    A1,
    E_STAR,
    Edge,
    PolicyMode,
    W_C,
    W_N,
    WarrantStatus,
    AuthorityStatus,
    canonical_state_bytes,
    initial_state,
    run_dynamic_episode,
)


def test_initial_state_serialization_is_stable():
    a = canonical_state_bytes(initial_state())
    b = canonical_state_bytes(initial_state())
    assert a == b


def test_baseline_contradiction_route_is_exact_e1_to_e6_and_a1():
    episode = run_dynamic_episode(W_C, initial_state())
    assert [step.edge for step in episode.steps] == [
        Edge.E1,
        Edge.E2,
        Edge.E3,
        Edge.E4,
        Edge.E5,
        Edge.E6,
    ]
    assert episode.action == A1
    assert episode.evidence == E_STAR
    assert episode.terminal_state.warrant_status is WarrantStatus.CORRECTION
    assert episode.terminal_state.authority_status is AuthorityStatus.CORR_AUTH
    assert episode.terminal_state.policy_mode is PolicyMode.CORRECTED


def test_normal_dynamic_route_returns_a0():
    episode = run_dynamic_episode(W_N, initial_state())
    assert episode.action == A0
    assert len(episode.steps) == 6
