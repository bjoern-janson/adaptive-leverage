from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json

from adaptive_leverage.model import ImplementationError


class CarrierState(str, Enum):
    S00 = "s00"
    S01 = "s01"
    S10 = "s10"
    S11 = "s11"


S00 = CarrierState.S00
S01 = CarrierState.S01
S10 = CarrierState.S10
S11 = CarrierState.S11

_CANONICAL_CARRIER = (S00, S01, S10, S11)

_SEMANTIC_ALIASES = {
    S00: ("r0", "n0"),
    S01: ("r0", "n1"),
    S10: ("r1", "n0"),
    S11: ("r1", "n1"),
}

_I_SPEC = {
    S00: (0, 0),
    S01: (0, 1),
    S10: (1, 0),
    S11: (1, 1),
}


@dataclass(frozen=True)
class ConsequenceSignature:
    warrant: str
    authority: str
    state_update: str
    terminal_action: str
    scope: str

    def as_tuple(self) -> tuple[str, str, str, str, str]:
        return (
            self.warrant,
            self.authority,
            self.state_update,
            self.terminal_action,
            self.scope,
        )


KAPPA0 = ConsequenceSignature(
    warrant="CORRECTION",
    authority="CORR_AUTH",
    state_update="SET_C0",
    terminal_action="ACT_C0",
    scope="OPEN",
)
KAPPA1 = ConsequenceSignature(
    warrant="CORRECTION",
    authority="CORR_AUTH",
    state_update="SET_C1",
    terminal_action="ACT_C1",
    scope="OPEN",
)

_K_CORR = {
    S00: KAPPA0,
    S01: KAPPA0,
    S10: KAPPA1,
    S11: KAPPA1,
}

_CORRECTION_BLOCKS = ((S00, S01), (S10, S11))


def _require_state(state: CarrierState) -> CarrierState:
    if not isinstance(state, CarrierState):
        raise ImplementationError(f"unknown V2 carrier state: {state!r}")
    return state


def carrier() -> tuple[CarrierState, CarrierState, CarrierState, CarrierState]:
    return _CANONICAL_CARRIER


def semantic_alias(state: CarrierState) -> tuple[str, str]:
    return _SEMANTIC_ALIASES[_require_state(state)]


def i_spec(state: CarrierState) -> tuple[int, int]:
    return _I_SPEC[_require_state(state)]


def k_corr(state: CarrierState) -> ConsequenceSignature:
    return _K_CORR[_require_state(state)]


def correction_blocks() -> tuple[tuple[CarrierState, ...], ...]:
    return _CORRECTION_BLOCKS


def _canonical_json_bytes(payload: object) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_carrier_bytes() -> bytes:
    return _canonical_json_bytes([state.value for state in carrier()])


def canonical_k_corr_bytes() -> bytes:
    return _canonical_json_bytes(
        [
            {
                "state": state.value,
                "signature": list(k_corr(state).as_tuple()),
            }
            for state in carrier()
        ]
    )


def canonical_correction_partition_bytes() -> bytes:
    return _canonical_json_bytes(
        {
            "blocks": [
                [state.value for state in block]
                for block in correction_blocks()
            ]
        }
    )
