from hashlib import sha256
from pathlib import Path
import shutil

import pytest

from adaptive_leverage.model import ImplementationError
from adaptive_leverage.v1.protocol import (
    V1_PREREG_SHA256,
    verify_v1_frozen_protocol,
)


def test_v1_frozen_prereg_bytes_match_canonical_hash():
    root = Path(__file__).resolve().parents[1]
    path = root / "prereg/ALCF_V1_PREREG_FROZEN.md"
    assert sha256(path.read_bytes()).hexdigest() == V1_PREREG_SHA256


def test_v1_runtime_hash_verifier_accepts_frozen_bytes():
    root = Path(__file__).resolve().parents[1]
    verify_v1_frozen_protocol(root)


def test_v1_runtime_hash_verifier_rejects_mutation(tmp_path):
    root = Path(__file__).resolve().parents[1]
    prereg = tmp_path / "prereg"
    prereg.mkdir()
    shutil.copy2(root / "prereg/ALCF_V1_PREREG_FROZEN.md", prereg / "ALCF_V1_PREREG_FROZEN.md")
    (prereg / "ALCF_V1_PREREG_FROZEN.md").write_text("mutated", encoding="utf-8")
    with pytest.raises(ImplementationError):
        verify_v1_frozen_protocol(tmp_path)
