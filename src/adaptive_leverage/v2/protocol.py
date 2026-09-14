from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

from adaptive_leverage.model import ImplementationError

V2_PROTOCOL_ID = "ALCF-V2-0"

V2_REALIZATION_RELATIVE_PATH = "prereg/ALCF_V2_0_FINITE_REALIZATION_DIAGONAL_FROZEN.md"
V2_ENUMERATION_RELATIVE_PATH = "prereg/ALCF_V2_0_FINITE_REALIZATION_DIAGONAL_ENUMERATION_FROZEN.csv"
V2_AUDIT_RELATIVE_PATH = "prereg/ALCF_V2_0_FINITE_REALIZATION_DIAGONAL_AUDIT.json"
V2_REALIZATION_MANIFEST_RELATIVE_PATH = (
    "prereg/ALCF_V2_0_FINITE_REALIZATION_DIAGONAL_SHA256SUMS_FROZEN.txt"
)
V2_PREREG_RELATIVE_PATH = "prereg/ALCF_V2_0_PREREG_FROZEN.md"
V2_PREREG_MANIFEST_RELATIVE_PATH = "prereg/ALCF_V2_0_PREREG_SHA256SUMS_FROZEN.txt"
V2_FREEZE_RECORD_RELATIVE_PATH = "prereg/ALCF_V2_0_PREREG_FREEZE_RECORD.txt"

V2_REALIZATION_SHA256 = "4b24ce642979112747d987b287618fbf16a77a9c4a66a0f2573c30c69256c5a1"
V2_ENUMERATION_SHA256 = "6392d4d845250edc4d1a059535e84d1e6bb53a35dbf8bda5f243be35cd0d2ab3"
V2_AUDIT_SHA256 = "1cf0cee982c56a9548a4b1d62a54485ddb425c1acad53ca616c5d8d29923c944"
V2_REALIZATION_MANIFEST_SHA256 = "49b1a332293fc1c8386fdb4e06b25b2a53b37c452caba71567bea46cc2cc0ea7"
V2_PREREG_SHA256 = "9a9cb7c074ca7c928f59cc2efa69585b05faa0ffbc128dcf6b0ed699c268d12b"
V2_PREREG_MANIFEST_SHA256 = "74a8fbf45cb861a63d7170d579790173e82c12f147bf41bc3f48f8fabd3c7242"
V2_FREEZE_RECORD_SHA256 = "30596af6b35bbbe566201fd0af6644f4a2db014410e234a28c8ff9ee1585deeb"

_EXPECTED_FILES = {
    V2_REALIZATION_RELATIVE_PATH: V2_REALIZATION_SHA256,
    V2_ENUMERATION_RELATIVE_PATH: V2_ENUMERATION_SHA256,
    V2_AUDIT_RELATIVE_PATH: V2_AUDIT_SHA256,
    V2_REALIZATION_MANIFEST_RELATIVE_PATH: V2_REALIZATION_MANIFEST_SHA256,
    V2_PREREG_RELATIVE_PATH: V2_PREREG_SHA256,
    V2_PREREG_MANIFEST_RELATIVE_PATH: V2_PREREG_MANIFEST_SHA256,
    V2_FREEZE_RECORD_RELATIVE_PATH: V2_FREEZE_RECORD_SHA256,
}

_REALIZATION_MANIFEST_EXPECTED = {
    Path(V2_REALIZATION_RELATIVE_PATH).name: V2_REALIZATION_SHA256,
    Path(V2_ENUMERATION_RELATIVE_PATH).name: V2_ENUMERATION_SHA256,
    Path(V2_AUDIT_RELATIVE_PATH).name: V2_AUDIT_SHA256,
}

_PREREG_MANIFEST_EXPECTED = {
    Path(V2_PREREG_RELATIVE_PATH).name: V2_PREREG_SHA256,
}

_MANIFEST_LINE = re.compile(r"^([0-9a-f]{64})  ([^/\\]+)$")


def _digest(path: Path, relative_path: str) -> str:
    try:
        return sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise ImplementationError(
            f"unable to read frozen V2 authority artifact: {relative_path}"
        ) from exc


def _verify_exact_file(repo_root: Path, relative_path: str, expected_sha256: str) -> None:
    observed = _digest(repo_root / relative_path, relative_path)
    if observed != expected_sha256:
        raise ImplementationError(
            f"frozen V2 authority hash mismatch for {relative_path}: {observed}"
        )


def _verify_checksum_manifest(
    repo_root: Path,
    manifest_relative_path: str,
    expected_entries: dict[str, str],
) -> None:
    manifest_path = repo_root / manifest_relative_path
    try:
        lines = manifest_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ImplementationError(
            f"unable to read frozen V2 checksum manifest: {manifest_relative_path}"
        ) from exc

    parsed: dict[str, str] = {}
    for line in lines:
        match = _MANIFEST_LINE.fullmatch(line)
        if match is None:
            raise ImplementationError(
                f"malformed frozen V2 checksum manifest: {manifest_relative_path}"
            )
        digest, filename = match.groups()
        if filename in parsed:
            raise ImplementationError(
                f"duplicate entry in frozen V2 checksum manifest: {filename}"
            )
        parsed[filename] = digest

    if parsed != expected_entries:
        raise ImplementationError(
            f"frozen V2 checksum manifest entry mismatch: {manifest_relative_path}"
        )

    prereg_dir = manifest_path.parent
    for filename, expected_sha256 in expected_entries.items():
        observed = _digest(prereg_dir / filename, f"prereg/{filename}")
        if observed != expected_sha256:
            raise ImplementationError(
                f"frozen V2 checksum target mismatch for prereg/{filename}: {observed}"
            )


def verify_v2_authority(repo_root: Path) -> None:
    """Fail closed unless every frozen V2 authority/custody byte is exact."""
    for relative_path, expected_sha256 in _EXPECTED_FILES.items():
        _verify_exact_file(repo_root, relative_path, expected_sha256)

    _verify_checksum_manifest(
        repo_root,
        V2_REALIZATION_MANIFEST_RELATIVE_PATH,
        _REALIZATION_MANIFEST_EXPECTED,
    )
    _verify_checksum_manifest(
        repo_root,
        V2_PREREG_MANIFEST_RELATIVE_PATH,
        _PREREG_MANIFEST_EXPECTED,
    )
