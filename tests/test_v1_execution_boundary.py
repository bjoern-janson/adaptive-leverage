from dataclasses import replace
from pathlib import Path

import pytest

from adaptive_leverage.model import A1, ImplementationError
from adaptive_leverage.v1.runner import (
    PrecheckResult,
    execute_v1_corrective,
    prepare_v1,
)


def synthetic_passing_precheck_fixture():
    return PrecheckResult(
        passed=True,
        action=A1,
        route_nonempty=True,
        trace=(),
    )


def test_prepare_v1_never_releases_corrective_condition(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    called = False

    monkeypatch.setattr(
        "adaptive_leverage.v1.runner.run_sacrificial_precheck",
        lambda *args, **kwargs: synthetic_passing_precheck_fixture(),
    )

    def forbidden(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("corrective replay reached during preparation")

    monkeypatch.setattr("adaptive_leverage.v1.runner.replay_v1_correction", forbidden)
    prepared = prepare_v1(root, run_id="software-prepare-fixture")
    assert prepared.joint_admission.passed
    assert prepared.release_token is not None
    assert not called
    assert prepared.c_normal.cost == 6
    assert prepared.e_normal.cost == 6
    assert (prepared.b_normal.cost, prepared.p_normal.cost, prepared.t_normal.cost) == (5, 5, 5)


def test_prepare_v1_binds_normal_traces_to_requested_run_id(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.setattr(
        "adaptive_leverage.v1.runner.run_sacrificial_precheck",
        lambda *args, **kwargs: synthetic_passing_precheck_fixture(),
    )
    prepared = prepare_v1(root, run_id="software-run-binding")
    for observation in (
        prepared.c_normal,
        prepared.b_normal,
        prepared.p_normal,
        prepared.t_normal,
        prepared.e_normal,
    ):
        assert all(event.run_id.startswith("software-run-binding-") for event in observation.trace)


def test_execute_refuses_missing_release_before_corrective_replay(monkeypatch, tmp_path):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.setattr(
        "adaptive_leverage.v1.runner.run_sacrificial_precheck",
        lambda *args, **kwargs: synthetic_passing_precheck_fixture(),
    )
    prepared = prepare_v1(root, run_id="software-no-release")
    prepared = replace(prepared, release_token=None)

    called = False

    def forbidden(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("corrective replay reached without release token")

    monkeypatch.setattr("adaptive_leverage.v1.runner.replay_v1_correction", forbidden)
    with pytest.raises(ImplementationError):
        execute_v1_corrective(prepared, tmp_path / "must-not-run")
    assert not called
