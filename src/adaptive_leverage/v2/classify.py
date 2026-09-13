from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from adaptive_leverage.model import ImplementationError
from adaptive_leverage.v2.domain import carrier
from adaptive_leverage.v2.topology import RefinementMode, WriteMode


_TRANSFORMATIONS = ("T_ALPHA", "T_BETA")
_MISMATCH_BY_TRANSFORMATION = {"T_ALPHA": 0, "T_BETA": 1}
_TOPOLOGY_ORDER = tuple(
    (refinement, write)
    for refinement in (RefinementMode.REFINE, RefinementMode.NO_REFINE)
    for write in (WriteMode.LIVE, WriteMode.BLOCKED)
)


class V2Stop(str, Enum):
    INVALID_EXECUTION = "INVALID_EXECUTION"


@dataclass(frozen=True)
class ArmKey:
    transformation: str
    refinement: RefinementMode
    write: WriteMode

    def __post_init__(self) -> None:
        if self.transformation not in _TRANSFORMATIONS:
            raise ImplementationError(
                f"unknown V2 transformation arm: {self.transformation!r}"
            )
        if not isinstance(self.refinement, RefinementMode):
            raise ImplementationError(
                f"unknown V2 refinement mode: {self.refinement!r}"
            )
        if not isinstance(self.write, WriteMode):
            raise ImplementationError(f"unknown V2 write mode: {self.write!r}")


@dataclass(frozen=True)
class ArmReachability:
    arm: ArmKey
    route_nonempty: tuple[tuple[str, bool], ...]

    def __post_init__(self) -> None:
        if not isinstance(self.arm, ArmKey):
            raise ImplementationError("reachability row requires a frozen V2 arm identity")
        expected_states = tuple(state.value for state in carrier())
        observed_states = tuple(state for state, _ in self.route_nonempty)
        if observed_states != expected_states:
            raise ImplementationError(
                "reachability row must contain the exact carrier states in canonical order"
            )
        if any(type(route) is not bool for _, route in self.route_nonempty):
            raise ImplementationError("reachability entries must be booleans")


@dataclass(frozen=True)
class RawReachabilityMatrix:
    rows: tuple[ArmReachability, ...]

    def __post_init__(self) -> None:
        expected = _frozen_arm_keys()
        if len(self.rows) != len(expected):
            raise ImplementationError(
                "raw reachability matrix must contain exactly the eight frozen arms"
            )
        if any(not isinstance(row, ArmReachability) for row in self.rows):
            raise ImplementationError("raw reachability matrix contains an invalid row")
        observed = tuple(row.arm for row in self.rows)
        if len(set(observed)) != len(observed) or set(observed) != set(expected):
            raise ImplementationError(
                "raw reachability matrix must contain exactly the eight frozen arms"
            )


@dataclass(frozen=True)
class ArmForeclosure:
    arm: ArmKey
    f: int

    def __post_init__(self) -> None:
        if self.f not in (0, 1):
            raise ImplementationError("F must be a binary indicator")


@dataclass(frozen=True)
class TopologyContrast:
    refinement: RefinementMode
    write: WriteMode
    d: int

    def __post_init__(self) -> None:
        if self.d not in (-1, 0, 1):
            raise ImplementationError("D must be one of -1, 0, +1")


@dataclass(frozen=True)
class V2ScientificOutcome:
    f_vector: tuple[ArmForeclosure, ...]
    d_contrasts: tuple[TopologyContrast, ...]
    c_mf_obs: frozenset[tuple[int, int]]


@dataclass(frozen=True)
class V2Decision:
    stop: V2Stop | None
    stop_detail: str | None
    scientific_outcome: V2ScientificOutcome | None


def _frozen_arm_keys() -> tuple[ArmKey, ...]:
    return tuple(
        ArmKey(
            transformation=transformation,
            refinement=refinement,
            write=write,
        )
        for transformation in _TRANSFORMATIONS
        for refinement, write in _TOPOLOGY_ORDER
    )


def raw_reachability_matrix(
    rows: tuple[ArmReachability, ...],
) -> RawReachabilityMatrix:
    if not isinstance(rows, tuple):
        raise ImplementationError("raw reachability rows must be an immutable tuple")
    matrix = RawReachabilityMatrix(rows=rows)
    by_arm = {row.arm: row for row in matrix.rows}
    return RawReachabilityMatrix(
        rows=tuple(by_arm[arm] for arm in _frozen_arm_keys())
    )


def _derive_f(row: ArmReachability) -> int:
    return int(any(not route_nonempty for _, route_nonempty in row.route_nonempty))


def classify_v2(
    raw_matrix: RawReachabilityMatrix | None,
    *,
    validity_passed: bool,
    invalid_reason: str | None = None,
) -> V2Decision:
    if type(validity_passed) is not bool:
        raise ImplementationError("validity gate must be boolean")
    if not validity_passed:
        return V2Decision(
            stop=V2Stop.INVALID_EXECUTION,
            stop_detail=invalid_reason,
            scientific_outcome=None,
        )
    if raw_matrix is None:
        raise ImplementationError(
            "valid execution requires an observed raw reachability matrix"
        )
    if not isinstance(raw_matrix, RawReachabilityMatrix):
        raise ImplementationError("invalid raw reachability matrix object")

    f_vector = tuple(
        ArmForeclosure(arm=row.arm, f=_derive_f(row))
        for row in raw_matrix.rows
    )
    f_by_arm = {entry.arm: entry.f for entry in f_vector}

    d_contrasts = tuple(
        TopologyContrast(
            refinement=refinement,
            write=write,
            d=(
                f_by_arm[
                    ArmKey(
                        transformation="T_BETA",
                        refinement=refinement,
                        write=write,
                    )
                ]
                - f_by_arm[
                    ArmKey(
                        transformation="T_ALPHA",
                        refinement=refinement,
                        write=write,
                    )
                ]
            ),
        )
        for refinement, write in _TOPOLOGY_ORDER
    )

    c_mf_obs = frozenset(
        (_MISMATCH_BY_TRANSFORMATION[entry.arm.transformation], entry.f)
        for entry in f_vector
    )

    return V2Decision(
        stop=None,
        stop_detail=None,
        scientific_outcome=V2ScientificOutcome(
            f_vector=f_vector,
            d_contrasts=d_contrasts,
            c_mf_obs=c_mf_obs,
        ),
    )
