from dataclasses import FrozenInstanceError

import pytest

from adaptive_leverage.v2.topology import (
    RefinementMode,
    TopologyDescriptor,
    WriteMode,
    all_topology_descriptors,
    no_refine,
    refine_candidates,
    topology_descriptor,
    write_permitted,
)


def test_refine_splits_by_any_admissible_token():
    candidates = (("u", "left"), ("v", "right"))
    assert refine_candidates(candidates, token="left") == ("u",)
    assert refine_candidates(candidates, token="right") == ("v",)


def test_no_refine_leaves_candidate_set_unchanged():
    assert no_refine(("u", "v"), token="anything") == ("u", "v")


def test_live_and_blocked_are_independent_of_refinement():
    assert write_permitted(WriteMode.LIVE)
    assert not write_permitted(WriteMode.BLOCKED)


def test_topology_descriptor_is_immutable_and_canonical():
    descriptor = topology_descriptor(RefinementMode.REFINE, WriteMode.LIVE)
    assert descriptor == TopologyDescriptor(
        refinement=RefinementMode.REFINE,
        write=WriteMode.LIVE,
    )
    assert descriptor.canonical_json == '{"refinement":"REFINE","write":"LIVE"}'
    assert len(descriptor.sha256) == 64
    with pytest.raises(FrozenInstanceError):
        descriptor.write = WriteMode.BLOCKED  # type: ignore[misc]


def test_all_four_topology_descriptors_are_distinct_and_deterministic():
    descriptors = all_topology_descriptors()
    assert tuple((d.refinement.value, d.write.value) for d in descriptors) == (
        ("REFINE", "LIVE"),
        ("REFINE", "BLOCKED"),
        ("NO_REFINE", "LIVE"),
        ("NO_REFINE", "BLOCKED"),
    )
    assert len({d.sha256 for d in descriptors}) == 4
