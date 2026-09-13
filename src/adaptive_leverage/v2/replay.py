from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Final

from adaptive_leverage.model import ImplementationError
from adaptive_leverage.v2.assay import CorrectiveReleaseToken
from adaptive_leverage.v2.compiler import (
    CompiledArtifact,
    compile_family,
    frozen_normal_data,
    frozen_objective,
)
from adaptive_leverage.v2.domain import CarrierState, carrier, k_corr
from adaptive_leverage.v2.partition import extract_dispatch_table
from adaptive_leverage.v2.topology import (
    RefinementMode,
    TopologyDescriptor,
    WriteMode,
    no_refine,
    refine_candidates,
    write_permitted,
)


_EXPECTED_RELEASE_BINDING: Final[tuple[object, ...]] = (
    "ef94574b51517325c6188669d6117563706a74b8bfded8651a226441ef7a8dfd",
    "20d7981d1cc304e42aa6ff4e7a2811817375f05b05d7da0c6b9831e5cc66c785",
    "3597e6b566c19681a1bb6c23d32b40659c1f2b2ae84e2aae75a6eefb5b74aa87",
    "3597e6b566c19681a1bb6c23d32b40659c1f2b2ae84e2aae75a6eefb5b74aa87",
    "93bbc9e40ea903462b87d37dba0d7fe3f82823ea2b110b4c44ea39342743aba6",
    "a250a3f9d3a48486e3c780da651b786aa6945e6057682c38098d17aeee370380",
    "e8b613a27ca92e57235798b9c431d4289564eac9b7559275c66576afa170f610",
    (
        "47adf55e2fed892e455147e8bd29caf64983b0914eb4164c455bc263f3bd2479",
        "1352e39f9a26ae2ab9f5f9de65d5a79dd2f15f988438e00094b5d3ab22d2a414",
        "3ed1e304b676b40c60c280cf1392ed5e082afc04157b581c863fe876e1d20c0c",
        "da291c73bfa17f112cc51ff3ce888b139412f188fab8c7b8e91759e4dc6fa434",
    ),
    "1fc1f4c166ba87457ffdf4d23229e12742764e3197165dea91218aec57d35f57",
)


@dataclass(frozen=True)
class ReferenceConsequence:
    label: str
    state_update: str
    terminal_action: str
    warrant: str = "SYNTHETIC_WARRANT"
    authority: str = "SYNTHETIC_AUTHORITY"
    scope: str = "OPEN"


@dataclass(frozen=True)
class CandidateReference:
    candidate_id: str
    admissible_token: str
    consequence: ReferenceConsequence


@dataclass(frozen=True)
class ReplayPredicateResult:
    challenged_id: str
    challenge_token: str
    pre_candidates: tuple[str, ...]
    post_candidates: tuple[str, ...]
    resolved_consequence: ReferenceConsequence | None
    state_write_realized: bool
    terminal_action: str | None
    qualified_route: bool


def _require_release_token(token: CorrectiveReleaseToken) -> CorrectiveReleaseToken:
    if not isinstance(token, CorrectiveReleaseToken):
        raise ImplementationError("valid corrective release token required before challenge access")
    try:
        binding = (
            token.alpha_artifact_sha256,
            token.beta_artifact_sha256,
            token.correction_partition_sha256,
            token.alpha_partition_sha256,
            token.alpha_predictor_sha256,
            token.beta_partition_sha256,
            token.beta_predictor_sha256,
            token.topology_sha256s,
            token.admission_sha256,
        )
    except AttributeError as exc:
        raise ImplementationError(
            "valid corrective release token required before challenge access"
        ) from exc
    if binding != _EXPECTED_RELEASE_BINDING:
        raise ImplementationError("corrective release token does not match frozen admission binding")
    return token


def _reference_index(
    references: tuple[CandidateReference, ...],
) -> dict[str, CandidateReference]:
    index: dict[str, CandidateReference] = {}
    for reference in references:
        if not isinstance(reference, CandidateReference):
            raise ImplementationError("replay references must be CandidateReference records")
        if not reference.candidate_id:
            raise ImplementationError("replay candidate id must be nonempty")
        if reference.candidate_id in index:
            raise ImplementationError("replay candidate ids must be unique")
        index[reference.candidate_id] = reference
    return index


def _resolve_consequence(
    candidate_ids: tuple[str, ...],
    references: dict[str, CandidateReference],
) -> ReferenceConsequence | None:
    if not candidate_ids:
        return None
    consequences = {references[candidate_id].consequence for candidate_id in candidate_ids}
    if len(consequences) != 1:
        return None
    return next(iter(consequences))


def replay_predicate(
    release_token: CorrectiveReleaseToken,
    *,
    challenged_id: str,
    dispatch_candidates: tuple[str, ...],
    references: tuple[CandidateReference, ...],
    refinement: RefinementMode,
    write: WriteMode,
    challenge_reader: Callable[[str], str],
) -> ReplayPredicateResult:
    """Evaluate one qualified-route predicate after release, using supplied references.

    The release token is validated before ``challenge_reader`` is invoked. This function
    is generic and is the only replay surface used by software-validation tests.
    """
    _require_release_token(release_token)

    if not challenged_id or challenged_id not in dispatch_candidates:
        raise ImplementationError("challenged candidate must belong to the dispatch class")
    if len(set(dispatch_candidates)) != len(dispatch_candidates):
        raise ImplementationError("dispatch candidate ids must be unique")

    reference_by_id = _reference_index(references)
    if any(candidate_id not in reference_by_id for candidate_id in dispatch_candidates):
        raise ImplementationError("dispatch class contains a candidate without reference data")

    challenge_token = challenge_reader(challenged_id)
    if not isinstance(challenge_token, str) or not challenge_token:
        raise ImplementationError("challenge reader must return a nonempty token")
    if reference_by_id[challenged_id].admissible_token != challenge_token:
        raise ImplementationError("challenge token disagrees with authenticated candidate reference")

    if refinement is RefinementMode.REFINE:
        tokenized = tuple(
            (candidate_id, reference_by_id[candidate_id].admissible_token)
            for candidate_id in dispatch_candidates
        )
        post_candidates = refine_candidates(tokenized, token=challenge_token)
    elif refinement is RefinementMode.NO_REFINE:
        post_candidates = no_refine(dispatch_candidates, token=challenge_token)
    else:
        raise ImplementationError(f"unknown refinement mode: {refinement!r}")

    resolved = _resolve_consequence(post_candidates, reference_by_id)
    state_write_realized = resolved is not None and write_permitted(write)
    terminal_action = resolved.terminal_action if state_write_realized and resolved is not None else None
    qualified_route = bool(state_write_realized and terminal_action is not None)

    return ReplayPredicateResult(
        challenged_id=challenged_id,
        challenge_token=challenge_token,
        pre_candidates=dispatch_candidates,
        post_candidates=post_candidates,
        resolved_consequence=resolved,
        state_write_realized=state_write_realized,
        terminal_action=terminal_action,
        qualified_route=qualified_route,
    )


def _coerce_carrier_state(state: CarrierState | str) -> CarrierState:
    if isinstance(state, CarrierState):
        return state
    if isinstance(state, str):
        try:
            return CarrierState(state)
        except ValueError as exc:
            raise ImplementationError(f"unknown V2 carrier state: {state!r}") from exc
    raise ImplementationError(f"unknown V2 carrier state: {state!r}")


def _sealed_real_reference_for_state(state: CarrierState) -> CandidateReference:
    """Return the frozen real challenge/reference row.

    Callers must validate the corrective release token before entering this function.
    """
    challenge_token = {
        CarrierState.S00: "z0",
        CarrierState.S01: "z0",
        CarrierState.S10: "z1",
        CarrierState.S11: "z1",
    }[state]
    signature = k_corr(state)
    return CandidateReference(
        candidate_id=state.value,
        admissible_token=challenge_token,
        consequence=ReferenceConsequence(
            label=signature.state_update,
            state_update=signature.state_update,
            terminal_action=signature.terminal_action,
            warrant=signature.warrant,
            authority=signature.authority,
            scope=signature.scope,
        ),
    )


def release_real_challenge_reference(
    release_token: CorrectiveReleaseToken,
    state: CarrierState | str,
) -> CandidateReference:
    """Open one real q* challenge/reference row only after release-token validation."""
    _require_release_token(release_token)
    coerced = _coerce_carrier_state(state)
    return _sealed_real_reference_for_state(coerced)


def _require_bound_real_artifact(
    release_token: CorrectiveReleaseToken, artifact: CompiledArtifact
) -> CompiledArtifact:
    if not isinstance(artifact, CompiledArtifact):
        raise ImplementationError("real replay requires a finalized bound compiler artifact")
    expected_alpha = compile_family(0, frozen_normal_data(), frozen_objective())
    expected_beta = compile_family(1, frozen_normal_data(), frozen_objective())
    if artifact == expected_alpha.artifact:
        if release_token.alpha_artifact_sha256 != expected_alpha.custody.finalized_artifact_sha256:
            raise ImplementationError("release token does not bind the alpha artifact")
        return artifact
    if artifact == expected_beta.artifact:
        if release_token.beta_artifact_sha256 != expected_beta.custody.finalized_artifact_sha256:
            raise ImplementationError("release token does not bind the beta artifact")
        return artifact
    raise ImplementationError("real replay artifact is not bound by the corrective release token")


def _require_bound_topology(
    release_token: CorrectiveReleaseToken, topology: TopologyDescriptor
) -> TopologyDescriptor:
    if not isinstance(topology, TopologyDescriptor):
        raise ImplementationError("real replay requires a bound topology descriptor")
    if not isinstance(topology.refinement, RefinementMode) or not isinstance(topology.write, WriteMode):
        raise ImplementationError("real replay topology descriptor is malformed")
    if topology.sha256 not in release_token.topology_sha256s:
        raise ImplementationError("real replay topology is not bound by the corrective release token")
    return topology


def execute_real_arm_replay(
    release_token: CorrectiveReleaseToken,
    *,
    artifact: CompiledArtifact,
    state: CarrierState | str,
    topology: TopologyDescriptor,
) -> ReplayPredicateResult:
    """Dormant single-state real replay surface for the later authorized runner.

    This function performs no file writes, no arm aggregation, and no F/D classification.
    Software-validation tests must not call it with a valid release token.
    """
    _require_release_token(release_token)
    artifact = _require_bound_real_artifact(release_token, artifact)
    topology = _require_bound_topology(release_token, topology)
    challenged_state = _coerce_carrier_state(state)

    dispatch_table = extract_dispatch_table(artifact)
    challenged_row = next(
        (row for row in dispatch_table if row.state == challenged_state.value),
        None,
    )
    if challenged_row is None:
        raise ImplementationError("challenged state is absent from finalized dispatch table")
    dispatch_candidates = tuple(
        row.state for row in dispatch_table if row.dispatch == challenged_row.dispatch
    )

    references = tuple(
        release_real_challenge_reference(release_token, candidate_state)
        for candidate_state in carrier()
    )
    challenged_reference = next(
        reference for reference in references if reference.candidate_id == challenged_state.value
    )

    return replay_predicate(
        release_token,
        challenged_id=challenged_state.value,
        dispatch_candidates=dispatch_candidates,
        references=references,
        refinement=topology.refinement,
        write=topology.write,
        challenge_reader=lambda _candidate_id: challenged_reference.admissible_token,
    )
