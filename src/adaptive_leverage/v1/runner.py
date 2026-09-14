from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from adaptive_leverage.model import (
    A1,
    C_STAR,
    E_STAR,
    OMEGA_STAR,
    O_C,
    W_C,
    AuthorityStatus,
    ImplementationError,
    Provenance,
    ScopeStatus,
    WarrantStatus,
    initial_state,
    run_dynamic_episode,
)
from adaptive_leverage.v1.artifacts import (
    write_decision_json,
    write_json,
    write_sha256_manifest,
    write_trace_jsonl,
)
from adaptive_leverage.v1.assay import (
    CorrectionObservation,
    CorrectiveReleaseToken,
    JointAdmission,
    NormalObservation,
    V1ArmBundle,
    correction_identity_valid,
    fork_v1_arms,
    joint_admit,
    measure_v1_normal,
    qualified_v1_route,
    replay_v1_correction,
    require_corrective_release,
)
from adaptive_leverage.v1.classify import V1Decision, V1ValidityFacts, classify_v1
from adaptive_leverage.v1.mechanisms import (
    CustodyCheck,
    MechanismArtifact,
    MechanismCustodyRecord,
    MechanismKind,
    construct_mechanism,
    frozen_normal_transcript,
    frozen_objective,
    validate_mechanism_custody,
)
from adaptive_leverage.v1.protocol import (
    V1_PREREG_SHA256,
    V1_PROTOCOL_ID,
    verify_v1_frozen_protocol,
)
from adaptive_leverage.v1.trace import V1TraceEvent, validate_v1_trace, build_v1_trace


@dataclass(frozen=True)
class PrecheckResult:
    passed: bool
    action: str
    route_nonempty: bool
    trace: tuple[V1TraceEvent, ...]


@dataclass(frozen=True)
class PreparedV1Run:
    repo_root: Path
    run_id: str
    precheck: PrecheckResult
    arms: V1ArmBundle
    b_artifact: MechanismArtifact
    p_artifact: MechanismArtifact
    t_artifact: MechanismArtifact
    b_custody: MechanismCustodyRecord
    p_custody: MechanismCustodyRecord
    t_custody: MechanismCustodyRecord
    b_custody_check: CustodyCheck
    p_custody_check: CustodyCheck
    t_custody_check: CustodyCheck
    c_normal: NormalObservation
    b_normal: NormalObservation
    p_normal: NormalObservation
    t_normal: NormalObservation
    e_normal: NormalObservation
    joint_admission: JointAdmission
    release_token: CorrectiveReleaseToken | None


def run_sacrificial_precheck(state, *, run_id: str) -> PrecheckResult:
    episode = run_dynamic_episode(W_C, state)
    trace = build_v1_trace(
        episode,
        arm="PRECHECK",
        run_id=f"{run_id}-precheck",
        mechanism_artifact_sha256=None,
    )
    validate_v1_trace(trace)
    route = qualified_v1_route(trace)
    return PrecheckResult(
        passed=route and episode.action == A1,
        action=episode.action,
        route_nonempty=route,
        trace=trace,
    )


def _built(prepared: PreparedV1Run):
    return {
        MechanismKind.B: (prepared.b_artifact, prepared.b_custody),
        MechanismKind.P: (prepared.p_artifact, prepared.p_custody),
        MechanismKind.T: (prepared.t_artifact, prepared.t_custody),
    }


def prepare_v1(repo_root: Path, run_id: str) -> PreparedV1Run:
    verify_v1_frozen_protocol(repo_root)
    m0 = initial_state()
    precheck = run_sacrificial_precheck(m0, run_id=run_id)
    if not precheck.passed:
        raise ImplementationError("PRECHECK_FAIL: sacrificial V1 precheck did not preserve full correction route")

    arms = fork_v1_arms(m0)
    normal = frozen_normal_transcript()
    objective = frozen_objective()

    b_artifact, b_custody = construct_mechanism(
        MechanismKind.B, normal, objective, finalization_sequence=1
    )
    p_artifact, p_custody = construct_mechanism(
        MechanismKind.P, normal, objective, finalization_sequence=2
    )
    t_artifact, t_custody = construct_mechanism(
        MechanismKind.T, normal, objective, finalization_sequence=3
    )
    b_check = validate_mechanism_custody(b_custody, b_artifact)
    p_check = validate_mechanism_custody(p_custody, p_artifact)
    t_check = validate_mechanism_custody(t_custody, t_artifact)

    c_normal = measure_v1_normal(
        "C", arms.c, None, None, run_id=f"{run_id}-normal-c"
    )
    b_normal = measure_v1_normal(
        "B", arms.b, b_artifact, b_custody.finalized_artifact_sha256,
        run_id=f"{run_id}-normal-b",
    )
    p_normal = measure_v1_normal(
        "P", arms.p, p_artifact, p_custody.finalized_artifact_sha256,
        run_id=f"{run_id}-normal-p",
    )
    t_normal = measure_v1_normal(
        "T", arms.t, t_artifact, t_custody.finalized_artifact_sha256,
        run_id=f"{run_id}-normal-t",
    )
    e_normal = measure_v1_normal(
        "E", arms.e, None, None, run_id=f"{run_id}-normal-e"
    )

    built = {
        MechanismKind.B: (b_artifact, b_custody),
        MechanismKind.P: (p_artifact, p_custody),
        MechanismKind.T: (t_artifact, t_custody),
    }
    admission = joint_admit(
        c_normal,
        {"B": b_normal, "P": p_normal, "T": t_normal},
        {"B": b_check, "P": p_check, "T": t_check},
        built,
    )
    return PreparedV1Run(
        repo_root=repo_root,
        run_id=run_id,
        precheck=precheck,
        arms=arms,
        b_artifact=b_artifact,
        p_artifact=p_artifact,
        t_artifact=t_artifact,
        b_custody=b_custody,
        p_custody=p_custody,
        t_custody=t_custody,
        b_custody_check=b_check,
        p_custody_check=p_check,
        t_custody_check=t_check,
        c_normal=c_normal,
        b_normal=b_normal,
        p_normal=p_normal,
        t_normal=t_normal,
        e_normal=e_normal,
        joint_admission=admission,
        release_token=admission.release_token,
    )


def _ensure_new_output_dir(output_dir: Path) -> None:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ImplementationError("V1 execution output directory must be new or empty")
    output_dir.mkdir(parents=True, exist_ok=True)


def _write_pre_reveal_artifacts(prepared: PreparedV1Run, output_dir: Path) -> None:
    write_json(
        output_dir / "protocol_identity.json",
        {
            "protocol_id": V1_PROTOCOL_ID,
            "prereg_sha256": V1_PREREG_SHA256,
            "run_id": prepared.run_id,
        },
    )
    write_json(
        output_dir / "prefork_identity.json",
        {
            "arm_state_hex": {
                arm: raw.hex() for arm, raw in prepared.arms.prefork_serialized.items()
            },
            "byte_identical": len(set(prepared.arms.prefork_serialized.values())) == 1,
        },
    )
    for arm, artifact, custody in (
        ("B", prepared.b_artifact, prepared.b_custody),
        ("P", prepared.p_artifact, prepared.p_custody),
        ("T", prepared.t_artifact, prepared.t_custody),
    ):
        write_json(output_dir / f"{arm}_mechanism.json", artifact)
        write_json(output_dir / f"{arm}_custody.json", custody)
    for arm, observation in (
        ("C", prepared.c_normal),
        ("B", prepared.b_normal),
        ("P", prepared.p_normal),
        ("T", prepared.t_normal),
        ("E", prepared.e_normal),
    ):
        write_trace_jsonl(output_dir / f"{arm}_normal_trace.jsonl", observation.trace)
    write_json(output_dir / "joint_admission.json", prepared.joint_admission)


def _fixed_replay_identity(observation: CorrectionObservation) -> tuple[str, str, str, str, str | None]:
    return (
        observation.world,
        observation.context,
        observation.observation,
        observation.evidence,
        observation.contradiction_id,
    )


def _positive_control_valid(observation: CorrectionObservation) -> bool:
    return (
        observation.arm == "E"
        and observation.scope_closed_valid
        and observation.licensing_epistemic_event
        and observation.route_loss_provenance == Provenance.VALID_SCOPE_CLOSURE.value
        and not observation.route_nonempty
        and not any(
            event.warrant_status == WarrantStatus.CORRECTION.value
            or event.authority_status == AuthorityStatus.CORR_AUTH.value
            for event in observation.trace
        )
        and all(event.scope_status == ScopeStatus.CLOSED_VALID.value for event in observation.trace)
    )


def execute_v1_corrective(prepared: PreparedV1Run, output_dir: Path) -> V1Decision:
    if not prepared.joint_admission.passed or prepared.release_token is None:
        raise ImplementationError("V1 corrective execution requires JOINT_ADMISSION_PASS")
    verify_v1_frozen_protocol(prepared.repo_root)
    built = _built(prepared)
    require_corrective_release(prepared.release_token, built)

    _ensure_new_output_dir(output_dir)
    _write_pre_reveal_artifacts(prepared, output_dir)

    c = replay_v1_correction(
        "C", prepared.arms.c,
        artifact=None,
        mechanism_artifact_sha256_value=None,
        release_token=prepared.release_token,
        built=built,
        run_id=f"{prepared.run_id}-correction-c",
    )
    b = replay_v1_correction(
        "B", prepared.arms.b,
        artifact=prepared.b_artifact,
        mechanism_artifact_sha256_value=prepared.b_custody.finalized_artifact_sha256,
        release_token=prepared.release_token,
        built=built,
        run_id=f"{prepared.run_id}-correction-b",
    )
    p = replay_v1_correction(
        "P", prepared.arms.p,
        artifact=prepared.p_artifact,
        mechanism_artifact_sha256_value=prepared.p_custody.finalized_artifact_sha256,
        release_token=prepared.release_token,
        built=built,
        run_id=f"{prepared.run_id}-correction-p",
    )
    t = replay_v1_correction(
        "T", prepared.arms.t,
        artifact=prepared.t_artifact,
        mechanism_artifact_sha256_value=prepared.t_custody.finalized_artifact_sha256,
        release_token=prepared.release_token,
        built=built,
        run_id=f"{prepared.run_id}-correction-t",
    )
    e = replay_v1_correction(
        "E", prepared.arms.e,
        artifact=None,
        mechanism_artifact_sha256_value=None,
        release_token=prepared.release_token,
        built=built,
        run_id=f"{prepared.run_id}-correction-e",
    )

    observations = (c, b, p, t, e)
    for observation in observations:
        validate_v1_trace(observation.trace)
        write_trace_jsonl(
            output_dir / f"{observation.arm}_correction_trace.jsonl",
            observation.trace,
        )

    expected_identity = (W_C, OMEGA_STAR, O_C, E_STAR, C_STAR)
    prefork_identity = len(set(prepared.arms.prefork_serialized.values())) == 1
    replay_identity = all(_fixed_replay_identity(obs) == expected_identity for obs in observations)
    identity_matched = prefork_identity and replay_identity

    control_route_nonempty = c.route_nonempty and c.action == A1
    positive_control_valid = _positive_control_valid(e)
    warrant_drift = any(
        not correction_identity_valid(obs)
        for obs in (b, p, t)
    )

    facts = V1ValidityFacts(
        precheck_passed=prepared.precheck.passed,
        identity_matched=identity_matched,
        joint_admission_passed=prepared.joint_admission.passed,
        joint_admission_reason=(
            prepared.joint_admission.reason.value
            if prepared.joint_admission.reason is not None
            else None
        ),
        warrant_drift=warrant_drift,
        control_route_nonempty=control_route_nonempty,
        positive_control_valid=positive_control_valid,
        trace_ambiguous=False,
        b_route_nonempty=b.route_nonempty,
        p_route_nonempty=p.route_nonempty,
        t_route_nonempty=t.route_nonempty,
    )
    decision = classify_v1(facts)
    write_json(output_dir / "validity_facts.json", facts)
    if decision.stop is None:
        write_decision_json(output_dir / "classification.json", decision)
    else:
        write_json(output_dir / "classification.json", decision)
    write_sha256_manifest(output_dir)
    return decision
