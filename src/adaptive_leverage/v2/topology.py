from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Hashable, TypeVar

from adaptive_leverage.model import ImplementationError


CandidateId = TypeVar("CandidateId", bound=Hashable)
Token = TypeVar("Token", bound=Hashable)


class RefinementMode(str, Enum):
    REFINE = "REFINE"
    NO_REFINE = "NO_REFINE"


class WriteMode(str, Enum):
    LIVE = "LIVE"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class TopologyDescriptor:
    refinement: RefinementMode
    write: WriteMode

    @property
    def canonical_json(self) -> str:
        return json.dumps(
            {
                "refinement": self.refinement.value,
                "write": self.write.value,
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    @property
    def sha256(self) -> str:
        return sha256(self.canonical_json.encode("utf-8")).hexdigest()


def _require_refinement_mode(mode: RefinementMode) -> RefinementMode:
    if not isinstance(mode, RefinementMode):
        raise ImplementationError(f"unknown refinement mode: {mode!r}")
    return mode


def _require_write_mode(mode: WriteMode) -> WriteMode:
    if not isinstance(mode, WriteMode):
        raise ImplementationError(f"unknown write mode: {mode!r}")
    return mode


def refine_candidates(
    candidates: tuple[tuple[CandidateId, Token], ...],
    *,
    token: Token,
) -> tuple[CandidateId, ...]:
    return tuple(candidate_id for candidate_id, candidate_token in candidates if candidate_token == token)


def no_refine(
    candidates: tuple[CandidateId, ...],
    *,
    token: Token,
) -> tuple[CandidateId, ...]:
    del token
    return candidates


def write_permitted(mode: WriteMode) -> bool:
    mode = _require_write_mode(mode)
    return mode is WriteMode.LIVE


def topology_descriptor(
    refinement: RefinementMode,
    write: WriteMode,
) -> TopologyDescriptor:
    return TopologyDescriptor(
        refinement=_require_refinement_mode(refinement),
        write=_require_write_mode(write),
    )


def all_topology_descriptors() -> tuple[TopologyDescriptor, ...]:
    return tuple(
        topology_descriptor(refinement, write)
        for refinement in (RefinementMode.REFINE, RefinementMode.NO_REFINE)
        for write in (WriteMode.LIVE, WriteMode.BLOCKED)
    )
