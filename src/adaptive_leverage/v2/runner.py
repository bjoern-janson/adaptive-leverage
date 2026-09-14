from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from adaptive_leverage.model import ImplementationError
from adaptive_leverage.v2.artifacts import (
    ValidityRecord,
    write_arm_trace,
    write_json,
    write_pre_replay_custody,
    write_scientific_results,
    write_sha256_manifest,
)
from adaptive_leverage.v2.assay import (
    PreparedV2Run,
    joint_admit,
    prepare_v2 as _prepare_v2,
)
from adaptive_leverage.v2.classify import (
    ArmKey,
    ArmReachability,
    V2Decision,
    classify_v2,
    raw_reachability_matrix,
)
from adaptive_leverage.v2.domain import carrier
from adaptive_leverage.v2.protocol import verify_v2_authority
from adaptive_leverage.v2.replay import ReplayPredicateResult, execute_real_arm_replay
from adaptive_leverage.v2.trace import validate_v2_trace


def prepare_v2(repo_root: Path, run_id: str) -> PreparedV2Run:
    """Prepare V2 through joint admission without consuming corrective authorization."""
    return _prepare_v2(Path(repo_root), run_id=run_id)


def _require_reverified_admission(prepared: PreparedV2Run):
    if not isinstance(prepared, PreparedV2Run):
        raise ImplementationError("corrective execution requires a PreparedV2Run")
    admission = prepared.joint_admission
    if admission is None or not admission.passed or admission.release_token is None:
        raise ImplementationError("corrective execution requires passing joint admission")

    verify_v2_authority(Path(prepared.repo_root))
    validate_v2_trace(prepared.trace)
    if not prepared.trace or prepared.trace[-1].stage != "JOINT_PRE_REPLAY_ADMISSION_PASS":
        raise ImplementationError("prepared V2 trace does not terminate at joint admission")

    fresh = joint_admit(replace(prepared, joint_admission=None))
    if not fresh.passed or fresh.release_token is None:
        raise ImplementationError("corrective execution failed fresh joint admission")
    if fresh.admission_sha256 != admission.admission_sha256:
        raise ImplementationError("joint admission identity changed before corrective execution")
    if fresh.release_token != admission.release_token:
        raise ImplementationError("corrective release-token binding changed before execution")
    return admission.release_token


def _validate_replay_result(
    result: ReplayPredicateResult,
    *,
    state: str,
) -> None:
    if not isinstance(result, ReplayPredicateResult):
        raise ImplementationError("real replay returned an invalid trace record")
    if result.challenged_id != state:
        raise ImplementationError("real replay trace challenged the wrong carrier state")
    if not result.challenge_token:
        raise ImplementationError("real replay trace is missing its authenticated challenge token")
    if len(set(result.pre_candidates)) != len(result.pre_candidates):
        raise ImplementationError("real replay trace contains duplicate pre-candidates")
    if state not in result.pre_candidates:
        raise ImplementationError("real replay trace omits the challenged pre-candidate")
    if len(set(result.post_candidates)) != len(result.post_candidates):
        raise ImplementationError("real replay trace contains duplicate post-candidates")
    if any(candidate not in result.pre_candidates for candidate in result.post_candidates):
        raise ImplementationError("real replay trace introduces a new post-candidate")
    if state not in result.post_candidates:
        raise ImplementationError("real replay trace removes the challenged candidate")

    if result.resolved_consequence is None:
        if result.state_write_realized or result.terminal_action is not None or result.qualified_route:
            raise ImplementationError("unresolved replay trace claims a realized corrective route")
        return

    if result.state_write_realized:
        if result.terminal_action != result.resolved_consequence.terminal_action:
            raise ImplementationError("real replay terminal action disagrees with resolved consequence")
    elif result.terminal_action is not None:
        raise ImplementationError("blocked replay trace contains a terminal action")

    qualified = bool(result.state_write_realized and result.terminal_action is not None)
    if result.qualified_route is not qualified:
        raise ImplementationError("real replay qualified-route predicate is internally inconsistent")


def execute_v2_corrective(prepared: PreparedV2Run, output_dir: Path) -> V2Decision:
    """Sole protocol-order surface for a separately authorized real corrective execution.

    Software validation must never call this function. It re-verifies frozen authority and
    admission custody before the first real replay access, records all 32 isolated replay
    traces, emits the complete raw reachability matrix, then mechanically derives and
    serializes the frozen scientific outputs.
    """
    release_token = _require_reverified_admission(prepared)
    output_dir = Path(output_dir)

    written = list(write_pre_replay_custody(output_dir, prepared))

    rows: list[ArmReachability] = []
    transformations = (
        ("T_ALPHA", prepared.alpha.artifact),
        ("T_BETA", prepared.beta.artifact),
    )

    for transformation, artifact in transformations:
        for topology in prepared.topologies:
            route_nonempty: list[tuple[str, bool]] = []
            for state in carrier():
                result = execute_real_arm_replay(
                    release_token,
                    artifact=artifact,
                    state=state,
                    topology=topology,
                )
                _validate_replay_result(result, state=state.value)
                written.append(
                    write_arm_trace(
                        output_dir,
                        transformation=transformation,
                        refinement=topology.refinement,
                        write=topology.write,
                        state=state.value,
                        records=(result,),
                    )
                )
                route_nonempty.append((state.value, result.qualified_route))

            rows.append(
                ArmReachability(
                    arm=ArmKey(
                        transformation=transformation,
                        refinement=topology.refinement,
                        write=topology.write,
                    ),
                    route_nonempty=tuple(route_nonempty),
                )
            )

    raw_matrix = raw_reachability_matrix(tuple(rows))

    # Raw R is persisted before any F/D/C_MF_obs derivation.
    raw_path = write_json(output_dir / "raw_R_matrix.json", {"rows": raw_matrix.rows})
    written.append(raw_path)

    decision = classify_v2(raw_matrix, validity_passed=True)
    validity = ValidityRecord(validity_passed=True, reason=None)
    result_paths = write_scientific_results(
        output_dir,
        raw_matrix=raw_matrix,
        decision=decision,
        validity=validity,
    )
    written.extend(path for path in result_paths if path not in written)

    filenames = tuple(dict.fromkeys(path.name for path in written))
    write_sha256_manifest(output_dir, filenames)
    return decision
