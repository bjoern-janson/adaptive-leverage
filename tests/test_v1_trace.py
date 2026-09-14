from dataclasses import replace

import pytest

from adaptive_leverage.model import initial_state
from adaptive_leverage.v1.episodes import run_v1_normal_episode
from adaptive_leverage.v1.mechanisms import (
    MechanismKind,
    construct_mechanism,
    frozen_normal_transcript,
    frozen_objective,
    install_mechanism,
)
from adaptive_leverage.v1.trace import (
    V1TraceValidationError,
    build_v1_trace,
    validate_v1_trace,
)


def built_b():
    return construct_mechanism(
        MechanismKind.B,
        frozen_normal_transcript(),
        frozen_objective(),
        finalization_sequence=1,
    )


def test_v1_trace_is_hash_chained_and_binds_mechanism_hash():
    artifact, custody = built_b()
    state = install_mechanism(initial_state(), artifact)
    episode = run_v1_normal_episode(state, artifact)
    trace = build_v1_trace(
        episode,
        arm="B",
        run_id="software-normal-b",
        mechanism_artifact_sha256=custody.finalized_artifact_sha256,
    )
    validate_v1_trace(trace)
    assert {e.mechanism_artifact_sha256 for e in trace} == {custody.finalized_artifact_sha256}
    assert all(e.protocol_id == "ALCF-V1" for e in trace)


def test_compiled_trace_uses_diagnostic_edge_and_records_source_edges():
    artifact, custody = built_b()
    state = install_mechanism(initial_state(), artifact)
    episode = run_v1_normal_episode(state, artifact)
    trace = build_v1_trace(
        episode,
        arm="B",
        run_id="software-normal-b",
        mechanism_artifact_sha256=custody.finalized_artifact_sha256,
    )
    assert trace[-1].edge_id == "E5_E6_COMPILED"
    assert trace[-1].represented_source_edges == ("E5", "E6")


def test_v1_trace_rejects_mechanism_hash_mutation():
    artifact, custody = built_b()
    state = install_mechanism(initial_state(), artifact)
    episode = run_v1_normal_episode(state, artifact)
    events = list(build_v1_trace(
        episode,
        arm="B",
        run_id="software-normal-b",
        mechanism_artifact_sha256=custody.finalized_artifact_sha256,
    ))
    events[0] = replace(events[0], mechanism_artifact_sha256="0" * 64)
    with pytest.raises(V1TraceValidationError):
        validate_v1_trace(tuple(events))
