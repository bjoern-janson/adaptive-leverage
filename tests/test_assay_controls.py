from adaptive_leverage.assay import (
    first_missing_frozen_edge,
    fork_arms,
    measure_capability,
    precheck,
    qualified_route,
    replay_correction,
)
from adaptive_leverage.interventions import NormalWorkloadInput, compile_dispatch
from adaptive_leverage.model import A0, A1, Edge, O_N, OMEGA_STAR, W_N, initial_state


def normal_input():
    return NormalWorkloadInput(W_N, O_N, OMEGA_STAR, A0, 6)


def test_precheck_has_full_route_and_a1():
    obs = precheck(initial_state())
    assert obs.action == A1
    assert obs.route_nonempty
    assert [e.edge_id for e in obs.trace] == ["E1", "E2", "E3", "E4", "E5", "E6"]


def test_arm_forks_are_byte_identical_before_intervention():
    artifact, _ = compile_dispatch(normal_input())
    bundle = fork_arms(initial_state(), artifact)
    assert (
        bundle.prefork_serialized_c
        == bundle.prefork_serialized_a
        == bundle.prefork_serialized_e
    )


def test_a_capability_is_correct_and_strictly_cheaper():
    artifact, _ = compile_dispatch(normal_input())
    bundle = fork_arms(initial_state(), artifact)
    c = measure_capability("C", bundle.c)
    a = measure_capability("A", bundle.a, artifact)
    e = measure_capability("E", bundle.e)
    assert c.action == a.action == e.action == A0
    assert a.cost < c.cost
    assert a.cost == 5
    assert c.cost == e.cost == 6


def test_c_preserves_route_and_a_preserves_warrant_but_loses_e5():
    artifact, _ = compile_dispatch(normal_input())
    bundle = fork_arms(initial_state(), artifact)
    c = replay_correction("C", bundle.c)
    a = replay_correction("A", bundle.a, artifact)
    assert qualified_route(c.trace)
    assert not qualified_route(a.trace)
    assert a.warrant_preserved
    assert {event.context for event in c.trace} == {OMEGA_STAR}
    assert {event.context for event in a.trace} == {OMEGA_STAR}
    assert {event.contradiction_id for event in c.trace} == {"c_star"}
    assert {event.contradiction_id for event in a.trace} == {"c_star"}
    assert any(event.evidence == "e_star" for event in c.trace)
    assert any(event.evidence == "e_star" for event in a.trace)
    assert first_missing_frozen_edge(a.trace) is Edge.E5
    assert a.trace[-1].edge_id == "E5A"


def test_e_is_justified_scope_closure_not_a_foreclosure_route():
    artifact, _ = compile_dispatch(normal_input())
    bundle = fork_arms(initial_state(), artifact)
    e = replay_correction("E", bundle.e)
    assert not e.route_nonempty
    assert e.scope_closed_valid
    assert e.licensing_epistemic_event
    assert e.route_loss_provenance == "VALID_SCOPE_CLOSURE"


def test_localization_is_ambiguous_if_later_frozen_edge_survives_after_gap():
    c = precheck(initial_state())
    without_e5 = tuple(event for event in c.trace if event.edge_id != "E5")
    assert first_missing_frozen_edge(without_e5) is None


def test_frozen_protocol_bytes_match_preregistered_hashes():
    from hashlib import sha256
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    expected = {
        "prereg/ALCF_V0_PREREG_FROZEN.md": (
            "05e8edd5c9aa7d5e15cf46575eb1efe2c91d1674054e53e6ed3a23a94e7f8192"
        ),
        "prereg/ALCF_V0_PROTOCOL_FROZEN.json": (
            "7b476c5020f0b81e6a1bceb712b877f5d52d0cbf6d99b0e164e7f705f06c1188"
        ),
    }
    for rel, digest in expected.items():
        assert sha256((root / rel).read_bytes()).hexdigest() == digest


def test_runtime_protocol_hash_verifier_accepts_frozen_bytes():
    from pathlib import Path

    from adaptive_leverage.assay import verify_frozen_protocol_hashes

    root = Path(__file__).resolve().parents[1]
    verify_frozen_protocol_hashes(root)


def test_runtime_protocol_hash_verifier_rejects_mutation(tmp_path):
    from pathlib import Path
    import shutil

    import pytest

    from adaptive_leverage.assay import verify_frozen_protocol_hashes
    from adaptive_leverage.model import ImplementationError

    root = Path(__file__).resolve().parents[1]
    prereg = tmp_path / "prereg"
    prereg.mkdir()
    for name in ("ALCF_V0_PREREG_FROZEN.md", "ALCF_V0_PROTOCOL_FROZEN.json"):
        shutil.copy2(root / "prereg" / name, prereg / name)
    (prereg / "ALCF_V0_PROTOCOL_FROZEN.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ImplementationError):
        verify_frozen_protocol_hashes(tmp_path)
