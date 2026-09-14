from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from itertools import combinations

from adaptive_leverage.model import ImplementationError
from adaptive_leverage.v2.compiler import CompiledArtifact
from adaptive_leverage.v2.domain import CarrierState, carrier, i_spec, k_corr


_COMPILED_TRANSITION_CLASS = "FAST_NORMAL"
_FALLBACK_CLASS = "GENERIC_POST_SPECIALIZATION"


@dataclass(frozen=True)
class DispatchObject:
    key_class: str
    compiled_transition_class: str
    fallback_class: str

    def as_tuple(self) -> tuple[str, str, str]:
        return (
            self.key_class,
            self.compiled_transition_class,
            self.fallback_class,
        )


@dataclass(frozen=True)
class DispatchRow:
    state: str
    dispatch: DispatchObject
    action: str


@dataclass(frozen=True)
class ProspectivePartition:
    family_name: str
    coordinate_index: int
    dispatch_table: tuple[DispatchRow, ...]
    partition: tuple[tuple[str, ...], ...]
    mismatch: int
    witnesses: tuple[tuple[str, str], ...]
    dispatch_sha256: str
    partition_sha256: str
    predictor_sha256: str


def _canonical_json_bytes(payload: object) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _coerce_state(state: CarrierState | str) -> CarrierState:
    if isinstance(state, CarrierState):
        return state
    if isinstance(state, str):
        try:
            return CarrierState(state)
        except ValueError as exc:
            raise ImplementationError(f"unknown V2 carrier state: {state!r}") from exc
    raise ImplementationError(f"unknown V2 carrier state: {state!r}")


def _require_artifact(artifact: CompiledArtifact) -> CompiledArtifact:
    if not isinstance(artifact, CompiledArtifact):
        raise ImplementationError("partition extraction requires a finalized CompiledArtifact")
    if artifact.coordinate_index not in (0, 1):
        raise ImplementationError("compiled artifact has unknown coordinate index")
    if not artifact.output_for_zero or not artifact.output_for_one:
        raise ImplementationError("compiled artifact has incomplete dispatch outputs")
    return artifact


def _dispatch_for_state(artifact: CompiledArtifact, state: CarrierState) -> DispatchRow:
    artifact = _require_artifact(artifact)
    coordinate_value = i_spec(state)[artifact.coordinate_index]
    if coordinate_value == 0:
        key_class = "K0"
        action = artifact.output_for_zero
    elif coordinate_value == 1:
        key_class = "K1"
        action = artifact.output_for_one
    else:  # pragma: no cover - frozen I_spec is binary; fail closed if changed.
        raise ImplementationError("specialization coordinate is not binary")

    return DispatchRow(
        state=state.value,
        dispatch=DispatchObject(
            key_class=key_class,
            compiled_transition_class=_COMPILED_TRANSITION_CLASS,
            fallback_class=_FALLBACK_CLASS,
        ),
        action=action,
    )


def dispatch_action(artifact: CompiledArtifact, state: CarrierState | str) -> str:
    return _dispatch_for_state(_require_artifact(artifact), _coerce_state(state)).action


def extract_dispatch_table(artifact: CompiledArtifact) -> tuple[DispatchRow, ...]:
    artifact = _require_artifact(artifact)
    return tuple(_dispatch_for_state(artifact, state) for state in carrier())


def _partition_from_dispatch(
    dispatch_table: tuple[DispatchRow, ...],
) -> tuple[tuple[str, ...], ...]:
    blocks: list[list[str]] = []
    block_keys: list[DispatchObject] = []
    for row in dispatch_table:
        try:
            index = block_keys.index(row.dispatch)
        except ValueError:
            block_keys.append(row.dispatch)
            blocks.append([row.state])
        else:
            blocks[index].append(row.state)
    return tuple(tuple(block) for block in blocks)


def _witnesses_for_dispatch(
    dispatch_table: tuple[DispatchRow, ...],
) -> tuple[tuple[str, str], ...]:
    dispatch_by_state = {row.state: row.dispatch for row in dispatch_table}
    state_by_id = {state.value: state for state in carrier()}
    witnesses: list[tuple[str, str]] = []
    ordered_ids = tuple(state.value for state in carrier())
    for left, right in combinations(ordered_ids, 2):
        if dispatch_by_state[left] != dispatch_by_state[right]:
            continue
        if k_corr(state_by_id[left]) == k_corr(state_by_id[right]):
            continue
        witnesses.append((left, right))
    return tuple(witnesses)


def canonical_dispatch_bytes(dispatch_table: tuple[DispatchRow, ...]) -> bytes:
    return _canonical_json_bytes(
        [
            {
                "action": row.action,
                "dispatch": list(row.dispatch.as_tuple()),
                "state": row.state,
            }
            for row in dispatch_table
        ]
    )


def canonical_partition_bytes(partition: tuple[tuple[str, ...], ...]) -> bytes:
    return _canonical_json_bytes({"blocks": [list(block) for block in partition]})


def canonical_predictor_bytes(
    mismatch: int,
    witnesses: tuple[tuple[str, str], ...],
) -> bytes:
    if mismatch not in (0, 1):
        raise ImplementationError("mismatch must be a binary indicator")
    return _canonical_json_bytes(
        {
            "mismatch": mismatch,
            "witnesses": [list(pair) for pair in witnesses],
        }
    )


def prospective_partition(artifact: CompiledArtifact) -> ProspectivePartition:
    artifact = _require_artifact(artifact)
    dispatch_table = extract_dispatch_table(artifact)
    partition = _partition_from_dispatch(dispatch_table)
    witnesses = _witnesses_for_dispatch(dispatch_table)
    mismatch = int(bool(witnesses))

    dispatch_bytes = canonical_dispatch_bytes(dispatch_table)
    partition_bytes = canonical_partition_bytes(partition)
    predictor_bytes = canonical_predictor_bytes(mismatch, witnesses)

    return ProspectivePartition(
        family_name=artifact.family_name,
        coordinate_index=artifact.coordinate_index,
        dispatch_table=dispatch_table,
        partition=partition,
        mismatch=mismatch,
        witnesses=witnesses,
        dispatch_sha256=sha256(dispatch_bytes).hexdigest(),
        partition_sha256=sha256(partition_bytes).hexdigest(),
        predictor_sha256=sha256(predictor_bytes).hexdigest(),
    )
