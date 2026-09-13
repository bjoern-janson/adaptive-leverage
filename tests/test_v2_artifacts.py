from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from pathlib import Path

import pytest

from adaptive_leverage.model import ImplementationError
from adaptive_leverage.v2.assay import prepare_v2
from adaptive_leverage.v2.classify import (
    ArmKey,
    ArmReachability,
    RawReachabilityMatrix,
    V2Decision,
    V2Stop,
    classify_v2,
    raw_reachability_matrix,
)
from adaptive_leverage.v2.domain import carrier
from adaptive_leverage.v2.topology import RefinementMode, WriteMode


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _synthetic_matrix(*, foreclosed_beta_no_refine_live: bool = False) -> RawReachabilityMatrix:
    rows = []
    for transformation in ("T_ALPHA", "T_BETA"):
        for refinement in (RefinementMode.REFINE, RefinementMode.NO_REFINE):
            for write in (WriteMode.LIVE, WriteMode.BLOCKED):
                route = True
                if (
                    foreclosed_beta_no_refine_live
                    and transformation == "T_BETA"
                    and refinement is RefinementMode.NO_REFINE
                    and write is WriteMode.LIVE
                ):
                    route = False
                rows.append(
                    ArmReachability(
                        arm=ArmKey(transformation, refinement, write),
                        route_nonempty=tuple(
                            (state.value, route) for state in carrier()
                        ),
                    )
                )
    return raw_reachability_matrix(tuple(rows))


def test_canonical_json_is_sorted_compact_and_newline_terminated():
    from adaptive_leverage.v2.artifacts import canonical_json_bytes

    raw = canonical_json_bytes({"z": 1, "a": 2})
    assert raw == b'{"a":2,"z":1}\n'


def test_jsonl_writer_preserves_record_order(tmp_path: Path):
    from adaptive_leverage.v2.artifacts import write_jsonl

    path = tmp_path / "trace.jsonl"
    write_jsonl(path, ({"seq": 0}, {"seq": 1}))
    assert path.read_bytes() == b'{"seq":0}\n{"seq":1}\n'


def test_manifest_hashes_exact_written_bytes(tmp_path: Path):
    from adaptive_leverage.v2.artifacts import write_json, write_sha256_manifest

    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    write_json(a, {"a": 1})
    write_json(b, {"b": 2})
    manifest = write_sha256_manifest(tmp_path, (b.name, a.name))
    expected = (
        f"{sha256(a.read_bytes()).hexdigest()}  a.json\n"
        f"{sha256(b.read_bytes()).hexdigest()}  b.json\n"
    ).encode("utf-8")
    assert manifest.name == "SHA256SUMS.txt"
    assert manifest.read_bytes() == expected


def test_preparation_writer_emits_only_pre_replay_custody(tmp_path: Path):
    from adaptive_leverage.v2.artifacts import write_pre_replay_custody

    prepared = prepare_v2(repo_root(), run_id="software-task9-preparation")
    written = write_pre_replay_custody(tmp_path, prepared)

    expected = {
        "authority_identity.json",
        "source_baseline.json",
        "reference_partition.json",
        "normal_data.json",
        "objective.json",
        "alpha_candidate_scores.json",
        "beta_candidate_scores.json",
        "T_ALPHA.json",
        "T_BETA.json",
        "alpha_compiler_custody.json",
        "beta_compiler_custody.json",
        "alpha_dispatch.json",
        "beta_dispatch.json",
        "alpha_partition.json",
        "beta_partition.json",
        "topology_descriptors.json",
        "joint_admission.json",
        "release_identity.json",
    }
    assert {path.name for path in written} == expected
    assert {path.name for path in tmp_path.iterdir()} == expected

    forbidden = {
        "raw_R_matrix.json",
        "F_vector.json",
        "C_MF_obs.json",
        "D_contrasts.json",
        "validity.json",
    }
    assert forbidden.isdisjoint({path.name for path in tmp_path.iterdir()})


def test_preparation_writer_rejects_nonadmitted_record_without_partial_output(tmp_path: Path):
    from adaptive_leverage.v2.artifacts import write_pre_replay_custody

    prepared = prepare_v2(repo_root(), run_id="software-task9-invalid-preparation")
    invalid = replace(prepared, joint_admission=None)
    with pytest.raises(ImplementationError, match="passing joint admission"):
        write_pre_replay_custody(tmp_path, invalid)
    assert not tuple(tmp_path.iterdir())


def test_scientific_result_writer_rejects_invalid_decision_without_files(tmp_path: Path):
    from adaptive_leverage.v2.artifacts import ValidityRecord, write_scientific_results

    raw = _synthetic_matrix()
    decision = V2Decision(
        stop=V2Stop.INVALID_EXECUTION,
        stop_detail="synthetic invalidity",
        scientific_outcome=None,
    )
    with pytest.raises(ImplementationError, match="valid scientific outcome"):
        write_scientific_results(
            tmp_path,
            raw_matrix=raw,
            decision=decision,
            validity=ValidityRecord(validity_passed=False, reason="synthetic invalidity"),
        )
    assert not tuple(tmp_path.iterdir())


def test_scientific_result_writer_requires_explicit_validity_record(tmp_path: Path):
    from adaptive_leverage.v2.artifacts import write_scientific_results

    raw = _synthetic_matrix()
    decision = classify_v2(raw, validity_passed=True)
    with pytest.raises(ImplementationError, match="validity record"):
        write_scientific_results(
            tmp_path,
            raw_matrix=raw,
            decision=decision,
            validity=None,
        )
    assert not tuple(tmp_path.iterdir())


def test_scientific_result_writer_serializes_existing_synthetic_records_only(tmp_path: Path):
    from adaptive_leverage.v2.artifacts import ValidityRecord, write_scientific_results

    raw = _synthetic_matrix(foreclosed_beta_no_refine_live=True)
    decision = classify_v2(raw, validity_passed=True)
    written = write_scientific_results(
        tmp_path,
        raw_matrix=raw,
        decision=decision,
        validity=ValidityRecord(validity_passed=True, reason=None),
    )
    assert {path.name for path in written} == {
        "raw_R_matrix.json",
        "F_vector.json",
        "C_MF_obs.json",
        "D_contrasts.json",
        "validity.json",
    }
    assert b'"d":1' in (tmp_path / "D_contrasts.json").read_bytes()
    assert (tmp_path / "raw_R_matrix.json").read_bytes().endswith(b"\n")


def test_result_writer_cannot_overwrite_existing_different_custody(tmp_path: Path):
    from adaptive_leverage.v2.artifacts import write_json

    path = tmp_path / "custody.json"
    write_json(path, {"v": 1})
    with pytest.raises(ImplementationError, match="refusing to overwrite"):
        write_json(path, {"v": 2})
    assert path.read_bytes() == b'{"v":1}\n'


def test_artifact_layer_has_no_implicit_science_execution_or_classification_calls():
    path = repo_root() / "src/adaptive_leverage/v2/artifacts.py"
    source = path.read_text(encoding="utf-8")
    forbidden_calls = (
        "prepare_v2(",
        "compile_family(",
        "joint_admit(",
        "execute_real_arm_replay(",
        "classify_v2(",
    )
    assert all(token not in source for token in forbidden_calls)


def test_arm_trace_writer_has_exact_frozen_filename_surface(tmp_path: Path):
    from adaptive_leverage.v2.artifacts import arm_trace_filename, write_arm_trace

    names = {
        arm_trace_filename(transformation, refinement, write, state.value)
        for transformation in ("T_ALPHA", "T_BETA")
        for refinement in (RefinementMode.REFINE, RefinementMode.NO_REFINE)
        for write in (WriteMode.LIVE, WriteMode.BLOCKED)
        for state in carrier()
    }
    assert len(names) == 32
    assert "arm_T_ALPHA_REFINE_LIVE_s00_trace.jsonl" in names
    assert "arm_T_BETA_NO_REFINE_BLOCKED_s11_trace.jsonl" in names

    path = write_arm_trace(
        tmp_path,
        transformation="T_ALPHA",
        refinement=RefinementMode.REFINE,
        write=WriteMode.LIVE,
        state="s00",
        records=({"seq": 0, "synthetic": True},),
    )
    assert path.name == "arm_T_ALPHA_REFINE_LIVE_s00_trace.jsonl"
    assert path.read_bytes() == b'{"seq":0,"synthetic":true}\n'
