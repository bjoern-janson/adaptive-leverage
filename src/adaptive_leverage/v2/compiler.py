from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterator

from adaptive_leverage.model import ImplementationError
from adaptive_leverage.v2.domain import S00, S11, i_spec


X_NORMAL_SHA256 = "d477bfb12d9e97f5bc90502530a8d5e25b8a8ed281de22bd15c32b0df0559e84"
OBJECTIVE_SHA256 = "b2be6744a89f0a81d1e043fa60f1bd11b0f8dbe38efeafb981d26808877adb5b"

_ACTION_A = "ACT_NA"
_ACTION_B = "ACT_NB"
_COMPILED_COST = 5
_DYNAMIC_COST = 6


@dataclass(frozen=True)
class NormalExample:
    state: str
    i_spec: tuple[int, int]
    target: str
    baseline_cost: int


@dataclass(frozen=True)
class NormalData:
    examples: tuple[NormalExample, ...]

    @property
    def canonical_json(self) -> str:
        payload = [
            {
                "baseline_cost": example.baseline_cost,
                "i_spec": list(example.i_spec),
                "state": example.state,
                "target": example.target,
            }
            for example in self.examples
        ]
        return _canonical_json(payload)

    @property
    def sha256(self) -> str:
        return _sha256_text(self.canonical_json)


@dataclass(frozen=True)
class ObjectiveSpec:
    minimize: str
    preserve_observed_normal_correctness: bool

    @property
    def canonical_json(self) -> str:
        return _canonical_json(
            {
                "minimize": self.minimize,
                "preserve_observed_normal_correctness": self.preserve_observed_normal_correctness,
            }
        )

    @property
    def sha256(self) -> str:
        return _sha256_text(self.canonical_json)


@dataclass(frozen=True)
class CandidateSpec:
    name: str
    output_for_zero: str | None
    output_for_one: str | None
    observed_cost: int
    compiled: bool


@dataclass(frozen=True)
class HypothesisFamily:
    coordinate_index: int
    name: str
    candidates: tuple[CandidateSpec, ...]

    def __iter__(self) -> Iterator[CandidateSpec]:
        return iter(self.candidates)


@dataclass(frozen=True)
class CandidateScore:
    candidate_name: str
    observed_correctness: tuple[bool, ...]
    observed_cost: int

    @property
    def exactly_correct(self) -> bool:
        return all(self.observed_correctness)


@dataclass(frozen=True)
class CompiledArtifact:
    family_name: str
    coordinate_index: int
    selected_candidate: str
    output_for_zero: str
    output_for_one: str
    observed_cost: int


@dataclass(frozen=True)
class CompilerCustody:
    family_name: str
    coordinate_index: int
    normal_data_sha256: str
    objective_sha256: str
    candidate_names: tuple[str, ...]
    candidate_scores: tuple[CandidateScore, ...]
    selected_candidate: str
    selected_candidate_json: str
    hypothesis_descriptor_sha256: str
    finalized_artifact_sha256: str
    construction_log: tuple[str, ...]


@dataclass(frozen=True)
class CompilerResult:
    selected_candidate: str
    observed_correctness: tuple[bool, ...]
    observed_cost: int
    artifact: CompiledArtifact
    custody: CompilerCustody


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def frozen_normal_data() -> NormalData:
    return NormalData(
        examples=(
            NormalExample(
                state=S00.value,
                i_spec=i_spec(S00),
                target=_ACTION_A,
                baseline_cost=_DYNAMIC_COST,
            ),
            NormalExample(
                state=S11.value,
                i_spec=i_spec(S11),
                target=_ACTION_B,
                baseline_cost=_DYNAMIC_COST,
            ),
        )
    )


def frozen_objective() -> ObjectiveSpec:
    return ObjectiveSpec(
        minimize="causal_microtransition_cost",
        preserve_observed_normal_correctness=True,
    )


def _candidate_specs() -> tuple[CandidateSpec, ...]:
    return (
        CandidateSpec("g_AA", _ACTION_A, _ACTION_A, _COMPILED_COST, True),
        CandidateSpec("g_AB", _ACTION_A, _ACTION_B, _COMPILED_COST, True),
        CandidateSpec("g_BA", _ACTION_B, _ACTION_A, _COMPILED_COST, True),
        CandidateSpec("g_BB", _ACTION_B, _ACTION_B, _COMPILED_COST, True),
        CandidateSpec("T_dynamic", None, None, _DYNAMIC_COST, False),
    )


def _require_coordinate_index(coordinate_index: int) -> int:
    if coordinate_index not in (0, 1):
        raise ImplementationError(f"unknown compiler coordinate index: {coordinate_index!r}")
    return coordinate_index


def candidate_family(coordinate_index: int) -> HypothesisFamily:
    coordinate_index = _require_coordinate_index(coordinate_index)
    return HypothesisFamily(
        coordinate_index=coordinate_index,
        name=f"H_{coordinate_index}",
        candidates=_candidate_specs(),
    )


def _compiled_prediction(candidate: CandidateSpec, coordinate_value: int) -> str:
    if coordinate_value == 0 and candidate.output_for_zero is not None:
        return candidate.output_for_zero
    if coordinate_value == 1 and candidate.output_for_one is not None:
        return candidate.output_for_one
    raise ImplementationError("compiled candidate mapping is incomplete")


def score_candidate(
    candidate: CandidateSpec,
    data: NormalData,
    *,
    coordinate_index: int,
) -> CandidateScore:
    coordinate_index = _require_coordinate_index(coordinate_index)
    if data != frozen_normal_data():
        raise ImplementationError("compiler input must equal frozen X_normal")
    if candidate not in _candidate_specs():
        raise ImplementationError("candidate is not a member of the frozen family")

    correctness: list[bool] = []
    for example in data.examples:
        if candidate.compiled:
            predicted = _compiled_prediction(candidate, example.i_spec[coordinate_index])
        else:
            predicted = example.target
        correctness.append(predicted == example.target)

    return CandidateScore(
        candidate_name=candidate.name,
        observed_correctness=tuple(correctness),
        observed_cost=candidate.observed_cost,
    )


def _candidate_payload(candidate: CandidateSpec) -> dict[str, object]:
    return {
        "compiled": candidate.compiled,
        "name": candidate.name,
        "observed_cost": candidate.observed_cost,
        "output_for_one": candidate.output_for_one,
        "output_for_zero": candidate.output_for_zero,
    }


def _family_payload(family: HypothesisFamily) -> dict[str, object]:
    return {
        "candidate_family": [_candidate_payload(candidate) for candidate in family.candidates],
        "coordinate_index": family.coordinate_index,
        "name": family.name,
    }


def _artifact_payload(artifact: CompiledArtifact) -> dict[str, object]:
    return {
        "coordinate_index": artifact.coordinate_index,
        "family_name": artifact.family_name,
        "observed_cost": artifact.observed_cost,
        "output_for_one": artifact.output_for_one,
        "output_for_zero": artifact.output_for_zero,
        "selected_candidate": artifact.selected_candidate,
    }


def compile_family(
    coordinate_index: int,
    data: NormalData,
    objective: ObjectiveSpec,
) -> CompilerResult:
    coordinate_index = _require_coordinate_index(coordinate_index)
    if data != frozen_normal_data() or data.sha256 != X_NORMAL_SHA256:
        raise ImplementationError("compiler input must equal frozen X_normal")
    if objective != frozen_objective() or objective.sha256 != OBJECTIVE_SHA256:
        raise ImplementationError("compiler objective must equal frozen objective J")

    family = candidate_family(coordinate_index)
    scores = tuple(
        score_candidate(candidate, data, coordinate_index=coordinate_index)
        for candidate in family
    )
    correct_scores = tuple(score for score in scores if score.exactly_correct)
    if not correct_scores:
        raise ImplementationError("no exactly correct candidate in frozen family")

    minimum_cost = min(score.observed_cost for score in correct_scores)
    minimizers = tuple(score for score in correct_scores if score.observed_cost == minimum_cost)
    if len(minimizers) != 1:
        raise ImplementationError("frozen compiler search did not yield a unique minimizer")

    selected_score = minimizers[0]
    selected = next(candidate for candidate in family if candidate.name == selected_score.candidate_name)
    if not selected.compiled or selected.output_for_zero is None or selected.output_for_one is None:
        raise ImplementationError("unique minimizer is not an admissible compiled candidate")
    if selected.observed_cost != _COMPILED_COST:
        raise ImplementationError("unique minimizer does not have frozen compiled cost")

    artifact = CompiledArtifact(
        family_name=family.name,
        coordinate_index=coordinate_index,
        selected_candidate=selected.name,
        output_for_zero=selected.output_for_zero,
        output_for_one=selected.output_for_one,
        observed_cost=selected.observed_cost,
    )
    selected_json = _canonical_json(_candidate_payload(selected))
    family_json = _canonical_json(_family_payload(family))
    artifact_json = _canonical_json(_artifact_payload(artifact))
    custody = CompilerCustody(
        family_name=family.name,
        coordinate_index=coordinate_index,
        normal_data_sha256=data.sha256,
        objective_sha256=objective.sha256,
        candidate_names=tuple(candidate.name for candidate in family),
        candidate_scores=scores,
        selected_candidate=selected.name,
        selected_candidate_json=selected_json,
        hypothesis_descriptor_sha256=_sha256_text(family_json),
        finalized_artifact_sha256=_sha256_text(artifact_json),
        construction_log=(
            "FROZEN_NORMAL_DATA_ONLY",
            "EXHAUSTIVE_FIVE_CANDIDATE_SEARCH",
            "EXACT_OBSERVED_CORRECTNESS_FILTER",
            "MINIMIZE_CAUSAL_MICROTRANSITION_COST",
            "UNIQUE_MINIMIZER_REQUIRED",
            "FINALIZED_BEFORE_LATER_PROTOCOL_STAGES",
        ),
    )
    return CompilerResult(
        selected_candidate=selected.name,
        observed_correctness=selected_score.observed_correctness,
        observed_cost=selected_score.observed_cost,
        artifact=artifact,
        custody=custody,
    )
