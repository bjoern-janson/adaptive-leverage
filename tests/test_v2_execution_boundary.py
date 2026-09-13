from __future__ import annotations

import inspect
import os
from pathlib import Path
import subprocess
import sys


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_prepare_v2_never_releases_real_challenge(monkeypatch):
    from adaptive_leverage.v2 import runner

    called = False

    def forbidden(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("real corrective replay reached")

    monkeypatch.setattr(runner, "execute_real_arm_replay", forbidden)
    prepared = runner.prepare_v2(repo_root(), run_id="software-preparation")
    assert prepared.joint_admission is not None
    assert prepared.joint_admission.passed is True
    assert called is False


def test_runner_exposes_only_explicit_corrective_execution_surface_without_calling_it(monkeypatch):
    from adaptive_leverage.v2 import runner

    called = False

    def forbidden(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("corrective execution reached")

    monkeypatch.setattr(runner, "execute_v2_corrective", forbidden)
    prepared = runner.prepare_v2(repo_root(), run_id="software-runner-surface")
    assert prepared.joint_admission is not None
    assert prepared.joint_admission.release_token is not None
    assert called is False

    signature = inspect.signature(runner.execute_v2_corrective)
    assert tuple(signature.parameters) == ("args", "kwargs") or tuple(signature.parameters) == (
        "prepared",
        "output_dir",
    )


def test_python_m_runner_is_dormant_and_creates_no_scientific_artifacts(tmp_path: Path):
    env = os.environ.copy()
    src = str(repo_root() / "src")
    env["PYTHONPATH"] = src + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    result = subprocess.run(
        [sys.executable, "-m", "adaptive_leverage.v2.runner"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert tuple(tmp_path.iterdir()) == ()


def test_runner_contains_no_expected_scientific_matrix_or_preferred_outcome_logic():
    source = (repo_root() / "src/adaptive_leverage/v2/runner.py").read_text(encoding="utf-8")
    forbidden = (
        "expected_matrix",
        "EXPECTED_MATRIX",
        "preferred_cell",
        "best_cell",
        "is_success",
        "design_time_matrix",
        "T_BETA.*NO_REFINE",
    )
    assert all(token not in source for token in forbidden)


def test_runner_has_no_console_entry_point():
    source = (repo_root() / "src/adaptive_leverage/v2/runner.py").read_text(encoding="utf-8")
    assert "if __name__" not in source
    assert "argparse" not in source
