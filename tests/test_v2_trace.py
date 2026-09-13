from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import sys
import types

import pytest

from adaptive_leverage.model import ImplementationError
from adaptive_leverage.v2.assay import CorrectiveReleaseToken, prepare_v2
from adaptive_leverage.v2.trace import V2TraceValidationError, validate_v2_trace


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_prepare_trace_is_immutable_hash_chained_and_stops_at_admission():
    prepared = prepare_v2(repo_root(), run_id="software-task6")

    assert prepared.joint_admission is not None
    assert prepared.joint_admission.passed is True
    assert prepared.joint_admission.release_token is not None
    assert tuple(event.seq for event in prepared.trace) == tuple(range(len(prepared.trace)))
    assert prepared.trace[-1].stage == "JOINT_PRE_REPLAY_ADMISSION_PASS"
    assert all(event.stage != "CORRECTIVE_REPLAY" for event in prepared.trace)
    assert all("R_OUTCOME" not in event.stage for event in prepared.trace)
    validate_v2_trace(prepared.trace)

    with pytest.raises(FrozenInstanceError):
        prepared.trace[0].status = "MUTATED"  # type: ignore[misc]


def test_trace_validation_rejects_content_or_hash_chain_mutation():
    prepared = prepare_v2(repo_root(), run_id="software-task6-trace-tamper")
    first = prepared.trace[0]
    tampered_first = replace(first, object_sha256="0" * 64)
    tampered = (tampered_first,) + prepared.trace[1:]

    with pytest.raises(V2TraceValidationError, match="hash"):
        validate_v2_trace(tampered)


def test_prepare_never_imports_or_calls_later_replay(monkeypatch):
    fake = types.ModuleType("adaptive_leverage.v2.replay")

    def forbidden(*args, **kwargs):
        raise AssertionError("corrective replay reached during preparation")

    fake.execute_real_arm_replay = forbidden  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "adaptive_leverage.v2.replay", fake)

    prepared = prepare_v2(repo_root(), run_id="software-no-replay")
    assert prepared.joint_admission is not None
    assert prepared.joint_admission.passed is True


def test_release_token_cannot_be_forged_through_public_constructor():
    with pytest.raises(ImplementationError, match="joint admission"):
        CorrectiveReleaseToken(
            alpha_artifact_sha256="a" * 64,
            beta_artifact_sha256="b" * 64,
            correction_partition_sha256="c" * 64,
            alpha_partition_sha256="d" * 64,
            alpha_predictor_sha256="e" * 64,
            beta_partition_sha256="f" * 64,
            beta_predictor_sha256="0" * 64,
            topology_sha256s=("1" * 64,) * 4,
            admission_sha256="2" * 64,
            _nonce=object(),
        )
