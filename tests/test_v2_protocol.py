from hashlib import sha256
from pathlib import Path
import shutil

import pytest

from adaptive_leverage.model import ImplementationError
from adaptive_leverage.v2.protocol import (
    V2_AUDIT_SHA256,
    V2_ENUMERATION_SHA256,
    V2_FREEZE_RECORD_SHA256,
    V2_PREREG_MANIFEST_SHA256,
    V2_PREREG_SHA256,
    V2_REALIZATION_MANIFEST_SHA256,
    V2_REALIZATION_SHA256,
    verify_v2_authority,
)


V2_AUTHORITY_FILES = (
    "ALCF_V2_0_FINITE_REALIZATION_DIAGONAL_FROZEN.md",
    "ALCF_V2_0_FINITE_REALIZATION_DIAGONAL_ENUMERATION_FROZEN.csv",
    "ALCF_V2_0_FINITE_REALIZATION_DIAGONAL_AUDIT.json",
    "ALCF_V2_0_FINITE_REALIZATION_DIAGONAL_SHA256SUMS_FROZEN.txt",
    "ALCF_V2_0_PREREG_FROZEN.md",
    "ALCF_V2_0_PREREG_SHA256SUMS_FROZEN.txt",
    "ALCF_V2_0_PREREG_FREEZE_RECORD.txt",
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def copy_v2_authority(tmp_path: Path) -> Path:
    source = repo_root() / "prereg"
    target = tmp_path / "prereg"
    target.mkdir()
    for name in V2_AUTHORITY_FILES:
        shutil.copy2(source / name, target / name)
    return tmp_path


def test_v2_authority_constants_match_exact_frozen_bytes():
    root = repo_root() / "prereg"
    expected = {
        "ALCF_V2_0_FINITE_REALIZATION_DIAGONAL_FROZEN.md": V2_REALIZATION_SHA256,
        "ALCF_V2_0_FINITE_REALIZATION_DIAGONAL_ENUMERATION_FROZEN.csv": V2_ENUMERATION_SHA256,
        "ALCF_V2_0_FINITE_REALIZATION_DIAGONAL_AUDIT.json": V2_AUDIT_SHA256,
        "ALCF_V2_0_FINITE_REALIZATION_DIAGONAL_SHA256SUMS_FROZEN.txt": V2_REALIZATION_MANIFEST_SHA256,
        "ALCF_V2_0_PREREG_FROZEN.md": V2_PREREG_SHA256,
        "ALCF_V2_0_PREREG_SHA256SUMS_FROZEN.txt": V2_PREREG_MANIFEST_SHA256,
        "ALCF_V2_0_PREREG_FREEZE_RECORD.txt": V2_FREEZE_RECORD_SHA256,
    }
    for name, digest in expected.items():
        assert sha256((root / name).read_bytes()).hexdigest() == digest


def test_v2_authority_accepts_exact_frozen_bytes():
    verify_v2_authority(repo_root())


def test_v2_authority_rejects_prereg_mutation(tmp_path):
    root = copy_v2_authority(tmp_path)
    path = root / "prereg/ALCF_V2_0_PREREG_FROZEN.md"
    path.write_bytes(path.read_bytes() + b"\nMUTATED")
    with pytest.raises(ImplementationError):
        verify_v2_authority(root)


def test_v2_authority_rejects_custody_manifest_mutation(tmp_path):
    root = copy_v2_authority(tmp_path)
    path = root / "prereg/ALCF_V2_0_PREREG_SHA256SUMS_FROZEN.txt"
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ImplementationError):
        verify_v2_authority(root)


def test_v2_authority_rejects_missing_frozen_artifact(tmp_path):
    root = copy_v2_authority(tmp_path)
    (root / "prereg/ALCF_V2_0_FINITE_REALIZATION_DIAGONAL_AUDIT.json").unlink()
    with pytest.raises(ImplementationError):
        verify_v2_authority(root)
