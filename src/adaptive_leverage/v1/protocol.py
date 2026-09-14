from hashlib import sha256
from pathlib import Path

from adaptive_leverage.model import ImplementationError

V1_PROTOCOL_ID = "ALCF-V1"
V1_PREREG_RELATIVE_PATH = "prereg/ALCF_V1_PREREG_FROZEN.md"
V1_PREREG_SHA256 = "5fc2cd2c02c991a9f21c74396f6205b8f98515621fb2e01ed4586e0bfea8a57f"


def verify_v1_frozen_protocol(repo_root: Path) -> None:
    path = repo_root / V1_PREREG_RELATIVE_PATH
    try:
        observed = sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise ImplementationError(
            f"unable to read frozen V1 protocol artifact: {V1_PREREG_RELATIVE_PATH}"
        ) from exc
    if observed != V1_PREREG_SHA256:
        raise ImplementationError(f"frozen V1 protocol hash mismatch: {observed}")
