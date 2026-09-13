from __future__ import annotations

from pathlib import Path

import pytest

from adaptive_leverage.model import ImplementationError
from adaptive_leverage.v2.assay import CorrectiveReleaseToken, prepare_v2
from adaptive_leverage.v2.compiler import CompiledArtifact
from adaptive_leverage.v2 import replay
from adaptive_leverage.v2.replay import (
    CandidateReference,
    ReferenceConsequence,
    replay_predicate,
    execute_real_arm_replay,
    release_real_challenge_reference,
)
from adaptive_leverage.v2.topology import RefinementMode, WriteMode


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def software_release_token() -> CorrectiveReleaseToken:
    prepared = prepare_v2(repo_root(), run_id="software-task7-synthetic")
    admission = prepared.joint_admission
    assert admission is not None
    assert admission.passed is True
    assert admission.release_token is not None
    return admission.release_token


def consequence(label: str) -> ReferenceConsequence:
    return ReferenceConsequence(
        label=label,
        state_update=f"set-{label}",
        terminal_action=f"act-{label}",
    )


def synthetic_rows(*rows: tuple[str, str, str]) -> tuple[CandidateReference, ...]:
    return tuple(
        CandidateReference(candidate_id=candidate, admissible_token=token, consequence=consequence(label))
        for candidate, token, label in rows
    )


def synthetic_reader(tokens: dict[str, str]):
    def read(candidate_id: str) -> str:
        return tokens[candidate_id]

    return read


def test_pure_class_live_has_qualified_route():
    token = software_release_token()
    rows = synthetic_rows(("a", "u", "left"), ("b", "v", "left"))

    result = replay_predicate(
        token,
        challenged_id="a",
        dispatch_candidates=("a", "b"),
        references=rows,
        refinement=RefinementMode.NO_REFINE,
        write=WriteMode.LIVE,
        challenge_reader=synthetic_reader({"a": "u", "b": "v"}),
    )

    assert result.pre_candidates == ("a", "b")
    assert result.post_candidates == ("a", "b")
    assert result.resolved_consequence == consequence("left")
    assert result.state_write_realized is True
    assert result.terminal_action == "act-left"
    assert result.qualified_route is True


def test_mixed_class_no_refine_live_is_unresolved_without_qualified_route():
    token = software_release_token()
    rows = synthetic_rows(("a", "u", "left"), ("b", "v", "right"))

    result = replay_predicate(
        token,
        challenged_id="a",
        dispatch_candidates=("a", "b"),
        references=rows,
        refinement=RefinementMode.NO_REFINE,
        write=WriteMode.LIVE,
        challenge_reader=synthetic_reader({"a": "u", "b": "v"}),
    )

    assert result.post_candidates == ("a", "b")
    assert result.resolved_consequence is None
    assert result.state_write_realized is False
    assert result.terminal_action is None
    assert result.qualified_route is False


def test_mixed_class_refine_live_recovers_when_token_makes_survivor_pure():
    token = software_release_token()
    rows = synthetic_rows(("a", "u", "left"), ("b", "v", "right"))

    result = replay_predicate(
        token,
        challenged_id="a",
        dispatch_candidates=("a", "b"),
        references=rows,
        refinement=RefinementMode.REFINE,
        write=WriteMode.LIVE,
        challenge_reader=synthetic_reader({"a": "u", "b": "v"}),
    )

    assert result.post_candidates == ("a",)
    assert result.resolved_consequence == consequence("left")
    assert result.state_write_realized is True
    assert result.terminal_action == "act-left"
    assert result.qualified_route is True


def test_resolved_class_blocked_has_no_qualified_route():
    token = software_release_token()
    rows = synthetic_rows(("a", "u", "left"), ("b", "v", "left"))

    result = replay_predicate(
        token,
        challenged_id="a",
        dispatch_candidates=("a", "b"),
        references=rows,
        refinement=RefinementMode.NO_REFINE,
        write=WriteMode.BLOCKED,
        challenge_reader=synthetic_reader({"a": "u", "b": "v"}),
    )

    assert result.resolved_consequence == consequence("left")
    assert result.state_write_realized is False
    assert result.terminal_action is None
    assert result.qualified_route is False


@pytest.mark.parametrize("bad_token", [None, object()])
def test_replay_rejects_missing_or_invalid_token_before_reading_challenge(bad_token):
    reads = 0

    def forbidden_reader(candidate_id: str) -> str:
        nonlocal reads
        reads += 1
        raise AssertionError(f"challenge data read for {candidate_id}")

    rows = synthetic_rows(("a", "u", "left"),)
    with pytest.raises(ImplementationError, match="release token"):
        replay_predicate(
            bad_token,  # type: ignore[arg-type]
            challenged_id="a",
            dispatch_candidates=("a",),
            references=rows,
            refinement=RefinementMode.NO_REFINE,
            write=WriteMode.LIVE,
            challenge_reader=forbidden_reader,
        )
    assert reads == 0


def test_forged_token_instance_is_rejected_before_reading_challenge():
    forged = object.__new__(CorrectiveReleaseToken)
    reads = 0

    def forbidden_reader(candidate_id: str) -> str:
        nonlocal reads
        reads += 1
        raise AssertionError(f"challenge data read for {candidate_id}")

    with pytest.raises(ImplementationError, match="release token"):
        replay_predicate(
            forged,
            challenged_id="a",
            dispatch_candidates=("a",),
            references=synthetic_rows(("a", "u", "left")),
            refinement=RefinementMode.NO_REFINE,
            write=WriteMode.LIVE,
            challenge_reader=forbidden_reader,
        )
    assert reads == 0


def test_real_adapter_rejects_invalid_token_before_opening_sealed_reference(monkeypatch):
    opened = False

    def forbidden_open(state):
        nonlocal opened
        opened = True
        raise AssertionError(f"sealed real reference opened for {state}")

    monkeypatch.setattr(replay, "_sealed_real_reference_for_state", forbidden_open)
    with pytest.raises(ImplementationError, match="release token"):
        release_real_challenge_reference(None, "s00")  # type: ignore[arg-type]
    assert opened is False



def test_real_replay_rejects_unbound_artifact_before_opening_sealed_reference(monkeypatch):
    opened = False

    def forbidden_open(state):
        nonlocal opened
        opened = True
        raise AssertionError(f"sealed real reference opened for {state}")

    monkeypatch.setattr(replay, "_sealed_real_reference_for_state", forbidden_open)
    bad_artifact = CompiledArtifact(
        family_name="H_0",
        coordinate_index=0,
        selected_candidate="g_AB",
        output_for_zero="MUTATED",
        output_for_one="ACT_NB",
        observed_cost=5,
    )

    with pytest.raises(ImplementationError, match="artifact"):
        execute_real_arm_replay(
            software_release_token(),
            artifact=bad_artifact,
            state="s00",
            topology=prepare_v2(repo_root(), run_id="software-task7-topology").topologies[0],
        )
    assert opened is False


def test_real_replay_rejects_invalid_topology_before_opening_sealed_reference(monkeypatch):
    opened = False

    def forbidden_open(state):
        nonlocal opened
        opened = True
        raise AssertionError(f"sealed real reference opened for {state}")

    monkeypatch.setattr(replay, "_sealed_real_reference_for_state", forbidden_open)
    prepared = prepare_v2(repo_root(), run_id="software-task7-invalid-topology")
    token = prepared.joint_admission.release_token
    assert token is not None

    with pytest.raises(ImplementationError, match="topology"):
        execute_real_arm_replay(
            token,
            artifact=prepared.alpha.artifact,
            state="s00",
            topology=object(),  # type: ignore[arg-type]
        )
    assert opened is False

def test_synthetic_predicates_never_call_real_replay_or_write_scientific_artifacts(monkeypatch, tmp_path):
    calls = 0

    def forbidden(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise AssertionError("real corrective replay reached during synthetic software validation")

    monkeypatch.setattr(replay, "execute_real_arm_replay", forbidden)
    monkeypatch.setattr(replay, "release_real_challenge_reference", forbidden)

    result = replay_predicate(
        software_release_token(),
        challenged_id="a",
        dispatch_candidates=("a",),
        references=synthetic_rows(("a", "u", "left")),
        refinement=RefinementMode.NO_REFINE,
        write=WriteMode.LIVE,
        challenge_reader=synthetic_reader({"a": "u"}),
    )

    assert result.qualified_route is True
    assert calls == 0
    assert not (tmp_path / "raw_R_matrix.json").exists()
    assert not (tmp_path / "F_vector.json").exists()
    assert not (tmp_path / "D_contrasts.json").exists()
    assert not (tmp_path / "C_MF_obs.json").exists()
    assert not list(tmp_path.glob("arm_*_trace.jsonl"))
