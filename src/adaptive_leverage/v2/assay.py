from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json
from pathlib import Path
from typing import Final

from adaptive_leverage.model import ImplementationError
from adaptive_leverage.v2.compiler import (
    OBJECTIVE_SHA256,
    X_NORMAL_SHA256,
    CandidateScore,
    CompilerResult,
    compile_family,
    frozen_normal_data,
    frozen_objective,
)
from adaptive_leverage.v2.domain import (
    canonical_carrier_bytes,
    canonical_correction_partition_bytes,
    canonical_k_corr_bytes,
    carrier,
    i_spec,
)
from adaptive_leverage.v2.partition import ProspectivePartition, prospective_partition
from adaptive_leverage.v2.protocol import (
    V2_AUDIT_SHA256,
    V2_ENUMERATION_SHA256,
    V2_FREEZE_RECORD_SHA256,
    V2_PREREG_MANIFEST_SHA256,
    V2_PREREG_SHA256,
    V2_REALIZATION_MANIFEST_SHA256,
    V2_REALIZATION_SHA256,
    verify_v2_authority,
)
from adaptive_leverage.v2.topology import TopologyDescriptor, all_topology_descriptors
from adaptive_leverage.v2.trace import V2TraceEvent, append_v2_trace_event, validate_v2_trace


V2_JOINT_ADMISSION_FAIL: Final[str] = "V2_JOINT_ADMISSION_FAIL"

_EXPECTED_CARRIER_SHA256 = "86d0649d2737d42f1d586d1b58beb6952a96ffe07f99e3f8dc8d97aab97de106"
_EXPECTED_K_CORR_SHA256 = "8b83ca42a15978011186ce7edca6cf9a455dba27f56316d539ec43291b069597"
_EXPECTED_PI_CORR_SHA256 = "3597e6b566c19681a1bb6c23d32b40659c1f2b2ae84e2aae75a6eefb5b74aa87"
_EXPECTED_I_SPEC_SHA256 = "df38158c01c9748edaf0349fb4681c0e77f85109c05c3532f764ada5b620a314"
_EXPECTED_QSTAR_CUSTODY_SHA256 = "fb9ec2da20378d739c8bd4a6e42c0b7124c3c05584eed327b97873ae0790512f"

_EXPECTED_ALPHA_ARTIFACT_SHA256 = "ef94574b51517325c6188669d6117563706a74b8bfded8651a226441ef7a8dfd"
_EXPECTED_BETA_ARTIFACT_SHA256 = "20d7981d1cc304e42aa6ff4e7a2811817375f05b05d7da0c6b9831e5cc66c785"
_EXPECTED_ALPHA_DISPATCH_SHA256 = "eabde705e87271a26db04906f9332966efb0d1340203f11bafed01fdf5dc4b09"
_EXPECTED_BETA_DISPATCH_SHA256 = "4128092ed49a363b1c1e369bdcd1ae0fec06c193618273a27b877520c4f40e4a"
_EXPECTED_ALPHA_PARTITION_SHA256 = "3597e6b566c19681a1bb6c23d32b40659c1f2b2ae84e2aae75a6eefb5b74aa87"
_EXPECTED_BETA_PARTITION_SHA256 = "a250a3f9d3a48486e3c780da651b786aa6945e6057682c38098d17aeee370380"
_EXPECTED_ALPHA_PREDICTOR_SHA256 = "93bbc9e40ea903462b87d37dba0d7fe3f82823ea2b110b4c44ea39342743aba6"
_EXPECTED_BETA_PREDICTOR_SHA256 = "e8b613a27ca92e57235798b9c431d4289564eac9b7559275c66576afa170f610"
_EXPECTED_TOPOLOGY_SHA256S = (
    "47adf55e2fed892e455147e8bd29caf64983b0914eb4164c455bc263f3bd2479",
    "1352e39f9a26ae2ab9f5f9de65d5a79dd2f15f988438e00094b5d3ab22d2a414",
    "3ed1e304b676b40c60c280cf1392ed5e082afc04157b581c863fe876e1d20c0c",
    "da291c73bfa17f112cc51ff3ce888b139412f188fab8c7b8e91759e4dc6fa434",
)
_EXPECTED_CANDIDATE_NAMES = ("g_AA", "g_AB", "g_BA", "g_BB", "T_dynamic")
_EXPECTED_SCORE_TABLE = (
    CandidateScore("g_AA", (True, False), 5),
    CandidateScore("g_AB", (True, True), 5),
    CandidateScore("g_BA", (False, False), 5),
    CandidateScore("g_BB", (False, True), 5),
    CandidateScore("T_dynamic", (True, True), 6),
)
_EXPECTED_CONSTRUCTION_LOG = (
    "FROZEN_NORMAL_DATA_ONLY",
    "EXHAUSTIVE_FIVE_CANDIDATE_SEARCH",
    "EXACT_OBSERVED_CORRECTNESS_FILTER",
    "MINIMIZE_CAUSAL_MICROTRANSITION_COST",
    "UNIQUE_MINIMIZER_REQUIRED",
    "FINALIZED_BEFORE_LATER_PROTOCOL_STAGES",
)
_FORBIDDEN_COMPILER_CUSTODY_TOKENS = (
    "q*",
    "z0",
    "z1",
    "CORRECTION",
    "CORR_AUTH",
    "SET_C0",
    "SET_C1",
    "ACT_C0",
    "ACT_C1",
    "K_corr",
    "Pi_corr",
    "M_T",
    "F_A",
    "REFINE",
    "LIVE",
    "BLOCKED",
)

# Sealed implementation custody only. These bytes are never returned by prepare_v2,
# never passed to either compiler, and are not a replay surface.
_SEALED_QSTAR_BYTES = (
    b'[{"state":"s00","token":"z0"},{"state":"s01","token":"z0"},'
    b'{"state":"s10","token":"z1"},{"state":"s11","token":"z1"}]'
)
_RELEASE_NONCE = object()


def _canonical_json_bytes(payload: object) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def _authority_binding_sha256() -> str:
    return _sha256_bytes(
        _canonical_json_bytes(
            {
                "audit": V2_AUDIT_SHA256,
                "enumeration": V2_ENUMERATION_SHA256,
                "freeze_record": V2_FREEZE_RECORD_SHA256,
                "prereg": V2_PREREG_SHA256,
                "prereg_manifest": V2_PREREG_MANIFEST_SHA256,
                "realization": V2_REALIZATION_SHA256,
                "realization_manifest": V2_REALIZATION_MANIFEST_SHA256,
            }
        )
    )


def _canonical_i_spec_bytes() -> bytes:
    return _canonical_json_bytes(
        [
            {"i_spec": list(i_spec(state)), "state": state.value}
            for state in carrier()
        ]
    )


def _aggregate_sha256(*parts: str) -> str:
    return _sha256_bytes(_canonical_json_bytes(list(parts)))


@dataclass(frozen=True, init=False)
class CorrectiveReleaseToken:
    alpha_artifact_sha256: str
    beta_artifact_sha256: str
    correction_partition_sha256: str
    alpha_partition_sha256: str
    alpha_predictor_sha256: str
    beta_partition_sha256: str
    beta_predictor_sha256: str
    topology_sha256s: tuple[str, str, str, str]
    admission_sha256: str

    def __init__(
        self,
        *,
        alpha_artifact_sha256: str,
        beta_artifact_sha256: str,
        correction_partition_sha256: str,
        alpha_partition_sha256: str,
        alpha_predictor_sha256: str,
        beta_partition_sha256: str,
        beta_predictor_sha256: str,
        topology_sha256s: tuple[str, str, str, str],
        admission_sha256: str,
        _nonce: object,
    ) -> None:
        if _nonce is not _RELEASE_NONCE:
            raise ImplementationError(
                "corrective release token requires passing joint admission"
            )
        object.__setattr__(self, "alpha_artifact_sha256", alpha_artifact_sha256)
        object.__setattr__(self, "beta_artifact_sha256", beta_artifact_sha256)
        object.__setattr__(self, "correction_partition_sha256", correction_partition_sha256)
        object.__setattr__(self, "alpha_partition_sha256", alpha_partition_sha256)
        object.__setattr__(self, "alpha_predictor_sha256", alpha_predictor_sha256)
        object.__setattr__(self, "beta_partition_sha256", beta_partition_sha256)
        object.__setattr__(self, "beta_predictor_sha256", beta_predictor_sha256)
        object.__setattr__(self, "topology_sha256s", topology_sha256s)
        object.__setattr__(self, "admission_sha256", admission_sha256)


@dataclass(frozen=True)
class JointAdmission:
    passed: bool
    reason: str | None
    failed_check: str | None
    release_token: CorrectiveReleaseToken | None
    admission_sha256: str


@dataclass(frozen=True)
class PreparedV2Run:
    run_id: str
    repo_root: str
    authority_binding_sha256: str
    carrier_sha256: str
    qstar_custody_sha256: str
    k_corr_sha256: str
    correction_partition_sha256: str
    i_spec_sha256: str
    normal_data_sha256: str
    objective_sha256: str
    adaptive_example_states: tuple[str, ...]
    alpha: CompilerResult
    beta: CompilerResult
    alpha_partition: ProspectivePartition
    beta_partition: ProspectivePartition
    topologies: tuple[TopologyDescriptor, ...]
    trace: tuple[V2TraceEvent, ...]
    joint_admission: JointAdmission | None


def _failure(check: str) -> JointAdmission:
    return JointAdmission(
        passed=False,
        reason=V2_JOINT_ADMISSION_FAIL,
        failed_check=check,
        release_token=None,
        admission_sha256=_sha256_bytes(
            _canonical_json_bytes({"failed_check": check, "status": V2_JOINT_ADMISSION_FAIL})
        ),
    )


def _compiler_custody_is_clean(result: CompilerResult) -> bool:
    if result.custody.construction_log != _EXPECTED_CONSTRUCTION_LOG:
        return False
    material = "\n".join(result.custody.construction_log) + "\n" + result.custody.selected_candidate_json
    return not any(token in material for token in _FORBIDDEN_COMPILER_CUSTODY_TOKENS)


def _admission_payload(prepared: PreparedV2Run) -> dict[str, object]:
    return {
        "alpha_artifact_sha256": prepared.alpha.custody.finalized_artifact_sha256,
        "alpha_dispatch_sha256": prepared.alpha_partition.dispatch_sha256,
        "alpha_partition_sha256": prepared.alpha_partition.partition_sha256,
        "alpha_predictor_sha256": prepared.alpha_partition.predictor_sha256,
        "authority_binding_sha256": prepared.authority_binding_sha256,
        "beta_artifact_sha256": prepared.beta.custody.finalized_artifact_sha256,
        "beta_dispatch_sha256": prepared.beta_partition.dispatch_sha256,
        "beta_partition_sha256": prepared.beta_partition.partition_sha256,
        "beta_predictor_sha256": prepared.beta_partition.predictor_sha256,
        "carrier_sha256": prepared.carrier_sha256,
        "correction_partition_sha256": prepared.correction_partition_sha256,
        "i_spec_sha256": prepared.i_spec_sha256,
        "k_corr_sha256": prepared.k_corr_sha256,
        "normal_data_sha256": prepared.normal_data_sha256,
        "objective_sha256": prepared.objective_sha256,
        "qstar_custody_sha256": prepared.qstar_custody_sha256,
        "topology_sha256s": [descriptor.sha256 for descriptor in prepared.topologies],
    }


def joint_admit(prepared: PreparedV2Run) -> JointAdmission:
    """All-or-none pre-replay gate. Never reads or executes corrective replay."""
    try:
        verify_v2_authority(Path(prepared.repo_root))
    except ImplementationError:
        return _failure("authority")
    if prepared.authority_binding_sha256 != _authority_binding_sha256():
        return _failure("authority")

    if (
        prepared.carrier_sha256 != _EXPECTED_CARRIER_SHA256
        or _sha256_bytes(canonical_carrier_bytes()) != _EXPECTED_CARRIER_SHA256
        or tuple(state.value for state in carrier()) != ("s00", "s01", "s10", "s11")
    ):
        return _failure("carrier")

    if (
        prepared.qstar_custody_sha256 != _EXPECTED_QSTAR_CUSTODY_SHA256
        or _sha256_bytes(_SEALED_QSTAR_BYTES) != _EXPECTED_QSTAR_CUSTODY_SHA256
        or prepared.k_corr_sha256 != _EXPECTED_K_CORR_SHA256
        or _sha256_bytes(canonical_k_corr_bytes()) != _EXPECTED_K_CORR_SHA256
    ):
        return _failure("sealed_reference")

    if (
        prepared.correction_partition_sha256 != _EXPECTED_PI_CORR_SHA256
        or _sha256_bytes(canonical_correction_partition_bytes()) != _EXPECTED_PI_CORR_SHA256
    ):
        return _failure("correction_partition")

    if (
        prepared.i_spec_sha256 != _EXPECTED_I_SPEC_SHA256
        or _sha256_bytes(_canonical_i_spec_bytes()) != _EXPECTED_I_SPEC_SHA256
    ):
        return _failure("i_spec")

    if (
        prepared.normal_data_sha256 != X_NORMAL_SHA256
        or prepared.objective_sha256 != OBJECTIVE_SHA256
    ):
        return _failure("normal_inputs")

    expected_alpha = compile_family(0, frozen_normal_data(), frozen_objective())
    expected_beta = compile_family(1, frozen_normal_data(), frozen_objective())

    if prepared.adaptive_example_states != ("s00", "s11"):
        return _failure("withholding")
    if {"s01", "s10"}.intersection(prepared.adaptive_example_states):
        return _failure("withholding")

    if (
        prepared.alpha.custody.candidate_names != _EXPECTED_CANDIDATE_NAMES
        or prepared.beta.custody.candidate_names != _EXPECTED_CANDIDATE_NAMES
        or prepared.alpha.custody.family_name != "H_0"
        or prepared.beta.custody.family_name != "H_1"
        or prepared.alpha.custody.coordinate_index != 0
        or prepared.beta.custody.coordinate_index != 1
        or prepared.alpha.custody.hypothesis_descriptor_sha256
        != expected_alpha.custody.hypothesis_descriptor_sha256
        or prepared.beta.custody.hypothesis_descriptor_sha256
        != expected_beta.custody.hypothesis_descriptor_sha256
    ):
        return _failure("candidate_families")

    if (
        prepared.alpha.custody.candidate_scores != _EXPECTED_SCORE_TABLE
        or prepared.beta.custody.candidate_scores != _EXPECTED_SCORE_TABLE
    ):
        return _failure("candidate_scoring")

    if not _compiler_custody_is_clean(prepared.alpha) or not _compiler_custody_is_clean(prepared.beta):
        return _failure("compiler_custody")

    if (
        prepared.alpha.selected_candidate != "g_AB"
        or prepared.beta.selected_candidate != "g_AB"
        or prepared.alpha.custody.selected_candidate != "g_AB"
        or prepared.beta.custody.selected_candidate != "g_AB"
    ):
        return _failure("unique_minimizer")

    if (
        prepared.alpha.observed_correctness != (True, True)
        or prepared.beta.observed_correctness != (True, True)
        or prepared.alpha.observed_cost != 5
        or prepared.beta.observed_cost != 5
    ):
        return _failure("normal_admission")

    if (
        prepared.alpha.custody.finalized_artifact_sha256 != _EXPECTED_ALPHA_ARTIFACT_SHA256
        or prepared.beta.custody.finalized_artifact_sha256 != _EXPECTED_BETA_ARTIFACT_SHA256
        or prepared.alpha.artifact != expected_alpha.artifact
        or prepared.beta.artifact != expected_beta.artifact
    ):
        return _failure("finalized_artifacts")

    expected_alpha_partition = prospective_partition(prepared.alpha.artifact)
    expected_beta_partition = prospective_partition(prepared.beta.artifact)
    if (
        prepared.alpha_partition.dispatch_sha256 != _EXPECTED_ALPHA_DISPATCH_SHA256
        or prepared.beta_partition.dispatch_sha256 != _EXPECTED_BETA_DISPATCH_SHA256
        or prepared.alpha_partition.dispatch_table != expected_alpha_partition.dispatch_table
        or prepared.beta_partition.dispatch_table != expected_beta_partition.dispatch_table
    ):
        return _failure("dispatch")

    if (
        prepared.alpha_partition.partition_sha256 != _EXPECTED_ALPHA_PARTITION_SHA256
        or prepared.alpha_partition.predictor_sha256 != _EXPECTED_ALPHA_PREDICTOR_SHA256
        or prepared.alpha_partition.mismatch != 0
        or prepared.alpha_partition.witnesses != ()
        or prepared.beta_partition.partition_sha256 != _EXPECTED_BETA_PARTITION_SHA256
        or prepared.beta_partition.predictor_sha256 != _EXPECTED_BETA_PREDICTOR_SHA256
        or prepared.beta_partition.mismatch != 1
        or prepared.beta_partition.witnesses != (("s00", "s10"), ("s01", "s11"))
        or prepared.alpha_partition.partition != expected_alpha_partition.partition
        or prepared.alpha_partition.mismatch != expected_alpha_partition.mismatch
        or prepared.alpha_partition.witnesses != expected_alpha_partition.witnesses
        or prepared.beta_partition.partition != expected_beta_partition.partition
        or prepared.beta_partition.mismatch != expected_beta_partition.mismatch
        or prepared.beta_partition.witnesses != expected_beta_partition.witnesses
    ):
        return _failure("prospective_predictor")

    topology_hashes = tuple(descriptor.sha256 for descriptor in prepared.topologies)
    if topology_hashes != _EXPECTED_TOPOLOGY_SHA256S:
        return _failure("topology")

    admission_sha256 = _sha256_bytes(_canonical_json_bytes(_admission_payload(prepared)))
    token = CorrectiveReleaseToken(
        alpha_artifact_sha256=prepared.alpha.custody.finalized_artifact_sha256,
        beta_artifact_sha256=prepared.beta.custody.finalized_artifact_sha256,
        correction_partition_sha256=prepared.correction_partition_sha256,
        alpha_partition_sha256=prepared.alpha_partition.partition_sha256,
        alpha_predictor_sha256=prepared.alpha_partition.predictor_sha256,
        beta_partition_sha256=prepared.beta_partition.partition_sha256,
        beta_predictor_sha256=prepared.beta_partition.predictor_sha256,
        topology_sha256s=topology_hashes,
        admission_sha256=admission_sha256,
        _nonce=_RELEASE_NONCE,
    )
    return JointAdmission(
        passed=True,
        reason=None,
        failed_check=None,
        release_token=token,
        admission_sha256=admission_sha256,
    )


def _trace_details(**kwargs: str) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(kwargs.items()))


def prepare_v2(repo_root: Path, run_id: str) -> PreparedV2Run:
    """Prepare and jointly admit V2 without consuming the corrective release token."""
    if not run_id:
        raise ImplementationError("V2 preparation requires a nonempty run id")
    repo_root = Path(repo_root).resolve()
    trace: tuple[V2TraceEvent, ...] = ()

    verify_v2_authority(repo_root)
    authority_hash = _authority_binding_sha256()
    trace = append_v2_trace_event(
        trace,
        run_id=run_id,
        stage="AUTHORITY_BYTES",
        status="VERIFIED",
        object_sha256=authority_hash,
    )

    carrier_hash = _sha256_bytes(canonical_carrier_bytes())
    trace = append_v2_trace_event(
        trace,
        run_id=run_id,
        stage="CARRIER_AND_ORDER",
        status="VERIFIED",
        object_sha256=carrier_hash,
        details=_trace_details(order="s00,s01,s10,s11"),
    )

    qstar_hash = _sha256_bytes(_SEALED_QSTAR_BYTES)
    k_corr_hash = _sha256_bytes(canonical_k_corr_bytes())
    sealed_reference_hash = _aggregate_sha256(qstar_hash, k_corr_hash)
    trace = append_v2_trace_event(
        trace,
        run_id=run_id,
        stage="SEALED_REFERENCE_CUSTODY",
        status="VERIFIED",
        object_sha256=sealed_reference_hash,
        details=_trace_details(qstar_sha256=qstar_hash),
    )

    pi_corr_hash = _sha256_bytes(canonical_correction_partition_bytes())
    trace = append_v2_trace_event(
        trace,
        run_id=run_id,
        stage="K_CORR_AND_PI_CORR",
        status="DERIVED",
        object_sha256=_aggregate_sha256(k_corr_hash, pi_corr_hash),
        details=_trace_details(k_corr_sha256=k_corr_hash, pi_corr_sha256=pi_corr_hash),
    )

    i_spec_hash = _sha256_bytes(_canonical_i_spec_bytes())
    trace = append_v2_trace_event(
        trace,
        run_id=run_id,
        stage="I_SPEC",
        status="VERIFIED",
        object_sha256=i_spec_hash,
    )

    data = frozen_normal_data()
    objective = frozen_objective()
    trace = append_v2_trace_event(
        trace,
        run_id=run_id,
        stage="NORMAL_INPUTS",
        status="VERIFIED",
        object_sha256=_aggregate_sha256(data.sha256, objective.sha256),
        details=_trace_details(J_sha256=objective.sha256, X_normal_sha256=data.sha256),
    )

    adaptive_example_states = tuple(example.state for example in data.examples)
    trace = append_v2_trace_event(
        trace,
        run_id=run_id,
        stage="WITHHOLDING",
        status="VERIFIED",
        object_sha256=_sha256_bytes(_canonical_json_bytes(list(adaptive_example_states))),
        details=_trace_details(examples=",".join(adaptive_example_states)),
    )

    alpha = compile_family(0, data, objective)
    beta = compile_family(1, data, objective)
    family_hash = _aggregate_sha256(
        alpha.custody.hypothesis_descriptor_sha256,
        beta.custody.hypothesis_descriptor_sha256,
    )
    trace = append_v2_trace_event(
        trace,
        run_id=run_id,
        stage="CANDIDATE_FAMILIES",
        status="VERIFIED",
        object_sha256=family_hash,
    )

    scoring_hash = _sha256_bytes(
        _canonical_json_bytes(
            [
                [score.candidate_name, list(score.observed_correctness), score.observed_cost]
                for score in alpha.custody.candidate_scores
            ]
        )
    )
    trace = append_v2_trace_event(
        trace,
        run_id=run_id,
        stage="CANDIDATE_SCORING",
        status="VERIFIED",
        object_sha256=scoring_hash,
    )

    custody_hash = _aggregate_sha256(
        _sha256_bytes(_canonical_json_bytes(list(alpha.custody.construction_log))),
        _sha256_bytes(_canonical_json_bytes(list(beta.custody.construction_log))),
    )
    trace = append_v2_trace_event(
        trace,
        run_id=run_id,
        stage="COMPILER_CUSTODY",
        status="VERIFIED",
        object_sha256=custody_hash,
    )

    trace = append_v2_trace_event(
        trace,
        run_id=run_id,
        stage="UNIQUE_MINIMIZER",
        status="VERIFIED",
        object_sha256=_aggregate_sha256(
            _sha256_bytes(alpha.selected_candidate.encode("utf-8")),
            _sha256_bytes(beta.selected_candidate.encode("utf-8")),
        ),
        details=_trace_details(alpha=alpha.selected_candidate, beta=beta.selected_candidate),
    )

    normal_admission_hash = _sha256_bytes(
        _canonical_json_bytes(
            {
                "alpha": [list(alpha.observed_correctness), alpha.observed_cost],
                "beta": [list(beta.observed_correctness), beta.observed_cost],
            }
        )
    )
    trace = append_v2_trace_event(
        trace,
        run_id=run_id,
        stage="NORMAL_ADMISSION",
        status="VERIFIED",
        object_sha256=normal_admission_hash,
    )

    trace = append_v2_trace_event(
        trace,
        run_id=run_id,
        stage="FINALIZED_COMPILER_ARTIFACTS",
        status="FINALIZED",
        object_sha256=_aggregate_sha256(
            alpha.custody.finalized_artifact_sha256,
            beta.custody.finalized_artifact_sha256,
        ),
        details=_trace_details(
            alpha=alpha.custody.finalized_artifact_sha256,
            beta=beta.custody.finalized_artifact_sha256,
        ),
    )

    alpha_partition = prospective_partition(alpha.artifact)
    beta_partition = prospective_partition(beta.artifact)
    trace = append_v2_trace_event(
        trace,
        run_id=run_id,
        stage="FULL_CARRIER_DISPATCH",
        status="FINALIZED",
        object_sha256=_aggregate_sha256(
            alpha_partition.dispatch_sha256,
            beta_partition.dispatch_sha256,
        ),
    )

    trace = append_v2_trace_event(
        trace,
        run_id=run_id,
        stage="PROSPECTIVE_PARTITION_PREDICTOR",
        status="FINALIZED",
        object_sha256=_aggregate_sha256(
            alpha_partition.partition_sha256,
            alpha_partition.predictor_sha256,
            beta_partition.partition_sha256,
            beta_partition.predictor_sha256,
        ),
    )

    topologies = all_topology_descriptors()
    trace = append_v2_trace_event(
        trace,
        run_id=run_id,
        stage="GENERIC_TOPOLOGY",
        status="FINALIZED",
        object_sha256=_sha256_bytes(
            _canonical_json_bytes([descriptor.sha256 for descriptor in topologies])
        ),
    )

    provisional = PreparedV2Run(
        run_id=run_id,
        repo_root=str(repo_root),
        authority_binding_sha256=authority_hash,
        carrier_sha256=carrier_hash,
        qstar_custody_sha256=qstar_hash,
        k_corr_sha256=k_corr_hash,
        correction_partition_sha256=pi_corr_hash,
        i_spec_sha256=i_spec_hash,
        normal_data_sha256=data.sha256,
        objective_sha256=objective.sha256,
        adaptive_example_states=adaptive_example_states,
        alpha=alpha,
        beta=beta,
        alpha_partition=alpha_partition,
        beta_partition=beta_partition,
        topologies=topologies,
        trace=trace,
        joint_admission=None,
    )
    admission = joint_admit(provisional)
    if not admission.passed:
        return replace(provisional, joint_admission=admission)

    trace = append_v2_trace_event(
        trace,
        run_id=run_id,
        stage="JOINT_PRE_REPLAY_ADMISSION_PASS",
        status="ADMITTED",
        object_sha256=admission.admission_sha256,
    )
    validate_v2_trace(trace)
    return replace(provisional, trace=trace, joint_admission=admission)
