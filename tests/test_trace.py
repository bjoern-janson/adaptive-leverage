from dataclasses import replace

import pytest

from adaptive_leverage.model import W_C, initial_state, run_dynamic_episode
from adaptive_leverage.trace import TraceValidationError, build_trace, validate_trace


def test_trace_is_hash_chained_and_valid():
    events = build_trace(
        run_dynamic_episode(W_C, initial_state()), arm="C", run_id="fixture-c"
    )
    validate_trace(events)
    assert events[0].prev_event_sha256 is None
    for left, right in zip(events, events[1:]):
        assert right.prev_event_sha256 == left.event_sha256


def test_trace_detects_mutation():
    events = list(
        build_trace(run_dynamic_episode(W_C, initial_state()), arm="C", run_id="fixture-c")
    )
    events[2] = replace(events[2], evidence="mutated")
    with pytest.raises(TraceValidationError):
        validate_trace(tuple(events))


def test_trace_detects_deletion():
    events = build_trace(
        run_dynamic_episode(W_C, initial_state()), arm="C", run_id="fixture-c"
    )
    with pytest.raises(TraceValidationError):
        validate_trace(events[:2] + events[3:])
