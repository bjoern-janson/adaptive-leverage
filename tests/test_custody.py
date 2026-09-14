import inspect
from dataclasses import replace

from adaptive_leverage.interventions import (
    NormalWorkloadInput,
    compile_dispatch,
    validate_custody,
)
from adaptive_leverage.model import A0, O_N, OMEGA_STAR, W_N


def frozen_normal_input():
    return NormalWorkloadInput(
        world=W_N,
        observation=O_N,
        context=OMEGA_STAR,
        expected_action=A0,
        baseline_cost=6,
    )


def test_compile_api_accepts_only_normal_workload():
    params = tuple(inspect.signature(compile_dispatch).parameters)
    assert params == ("normal",)


def test_compiler_finalizes_artifact_from_normal_inputs_only():
    artifact, record = compile_dispatch(frozen_normal_input())
    check = validate_custody(record, artifact)
    assert check.passed
    assert artifact.action == A0
    assert artifact.context == OMEGA_STAR
    assert record.finalized_artifact_sha256


def test_corrective_symbol_contamination_fails_custody():
    artifact, record = compile_dispatch(frozen_normal_input())
    contaminated = replace(
        record, optimization_inputs=record.optimization_inputs + ("e_star",)
    )
    check = validate_custody(contaminated, artifact)
    assert not check.passed
    assert check.reason == "OPTIMIZATION_LEAKAGE"


def test_custody_records_per_input_hashes_and_forbidden_manifest():
    artifact, record = compile_dispatch(frozen_normal_input())
    assert {name for name, _ in record.optimization_input_hashes} == {
        "baseline_cost",
        "context",
        "expected_action",
        "observation",
        "world",
    }
    assert all(len(digest) == 64 for _, digest in record.optimization_input_hashes)
    assert {"w_c", "o_c", "e_star", "c_star", "a1"}.issubset(
        set(record.forbidden_artifact_manifest)
    )
    assert validate_custody(record, artifact).passed
