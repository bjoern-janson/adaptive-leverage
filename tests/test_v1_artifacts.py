import json
from pathlib import Path

import pytest

from adaptive_leverage.model import ImplementationError, initial_state
from adaptive_leverage.v1.artifacts import (
    write_decision_json,
    write_json,
    write_sha256_manifest,
    write_trace_jsonl,
)
from adaptive_leverage.v1.classify import V1ValidityFacts, classify_v1
from adaptive_leverage.v1.episodes import run_v1_normal_episode
from adaptive_leverage.v1.mechanisms import (
    MechanismKind,
    construct_mechanism,
    frozen_normal_transcript,
    frozen_objective,
    install_mechanism,
)
from adaptive_leverage.v1.trace import build_v1_trace


def fixture_decision(*, valid=True):
    facts = V1ValidityFacts(
        precheck_passed=valid,
        identity_matched=True,
        joint_admission_passed=True,
        joint_admission_reason=None,
        warrant_drift=False,
        control_route_nonempty=True,
        positive_control_valid=True,
        trace_ambiguous=False,
        b_route_nonempty=False,
        p_route_nonempty=True,
        t_route_nonempty=False,
    )
    return classify_v1(facts)


def fixture_trace():
    artifact, record = construct_mechanism(
        MechanismKind.B,
        frozen_normal_transcript(),
        frozen_objective(),
        finalization_sequence=1,
    )
    state = install_mechanism(initial_state(), artifact)
    episode = run_v1_normal_episode(state, artifact)
    return build_v1_trace(
        episode,
        arm="B",
        run_id="software-fixture-artifact",
        mechanism_artifact_sha256=record.finalized_artifact_sha256,
    )


def test_json_writer_is_canonical_and_newline_terminated(tmp_path):
    path = tmp_path / "record.json"
    write_json(path, {"z": 1, "a": 2})
    assert path.read_text(encoding="utf-8") == '{"a":2,"z":1}\n'


def test_trace_jsonl_round_trips_and_ends_with_newline(tmp_path):
    path = tmp_path / "trace.jsonl"
    trace = fixture_trace()
    write_trace_jsonl(path, trace)
    raw = path.read_text(encoding="utf-8")
    assert raw.endswith("\n")
    rows = [json.loads(line) for line in raw.splitlines()]
    assert len(rows) == len(trace)
    assert rows[0]["run_id"] == "software-fixture-artifact"


def test_stopped_decision_cannot_be_serialized_as_scientific_classification(tmp_path):
    with pytest.raises(ImplementationError):
        write_decision_json(tmp_path / "classification.json", fixture_decision(valid=False))


def test_manifest_hashes_written_files_in_stable_name_order(tmp_path):
    write_json(tmp_path / "b.json", {"b": 2})
    write_json(tmp_path / "a.json", {"a": 1})
    manifest = write_sha256_manifest(tmp_path)
    lines = manifest.read_text(encoding="utf-8").splitlines()
    assert lines[0].endswith("  a.json")
    assert lines[1].endswith("  b.json")
    assert all(len(line.split()[0]) == 64 for line in lines)


def test_valid_synthetic_decision_serializes_signature_and_contrasts(tmp_path):
    path = tmp_path / "classification.json"
    write_decision_json(path, fixture_decision())
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["scientific_outcome"]["signature"]["text"] == "010"
    assert payload["scientific_outcome"]["d_bp"] == 1
