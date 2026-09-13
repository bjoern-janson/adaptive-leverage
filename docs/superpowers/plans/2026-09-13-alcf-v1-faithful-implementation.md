# ALCF-V1 Faithful Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement ALCF-V1 exactly against the frozen preregistration, preserving V0 unchanged, enforcing joint pre-reveal admission, and producing a dormant execution path that cannot emit a V1 scientific outcome until every frozen validity gate passes.

**Architecture:** Keep the existing ALCF-V0 modules and tests intact. Add V1 as a separate `adaptive_leverage.v1` package that reuses the frozen finite-state machine objects but owns V1 mechanism artifacts, custody, trace binding, admission/release gating, reachability classification, and execution serialization. Unit tests validate the transformation rules and classifier with normal-workload or synthetic fixtures only; they must never run the real `B/P/T` corrective comparison or populate the preregistered result fields.

**Tech Stack:** Python >=3.11, standard library runtime only, pytest >=8 for tests, SHA-256 for frozen-artifact and custody hashes.

**Spec:** `prereg/ALCF_V1_PREREG_FROZEN.md` — canonical SHA-256 `5fc2cd2c02c991a9f21c74396f6205b8f98515621fb2e01ed4586e0bfea8a57f`.

## Global Constraints

- Frozen V1 bytes are scientific authority; conversation summaries are not.
- Do not edit `prereg/ALCF_V0_*`, the V0 scientific decision rules, or V0 tests except for purely additive compatibility imports if absolutely necessary.
- Do not alter the inherited frozen objects: `w_n`, `w_c`, `o_n`, `o_c`, `e_n`, `e_star`, `c_star`, `omega_star="alpha"`, `a0`, `a1`, or the dynamic `E1..E6` semantics.
- `X_normal` is identical for `B/P/T`; objective `J` is identical; normal correctness must match `C`; admitted cost must be exactly `5` for all three.
- The exact value `5` is an admission criterion, not the optimization objective.
- `T_B`, `T_P`, and `T_T` are defined only by their frozen transformation rules; no code or test may define a mechanism by an expected `R` outcome.
- No `B/P/T` corrective replay may be callable without a successful all-or-none joint admission token bound to all three finalized mechanism hashes.
- Software tests may use normal workload data, arbitrary synthetic mismatch values, and hand-built classifier/trace fixtures. They must not run the real V1 `B/P/T` corrective comparison or emit a real `Sigma_R`.
- `C` and `E` are controls only. Only `B/P/T` contribute bits to `Sigma_R`.
- No scalarization, ranking, bit count, preferred signature, summed contrast, or post-hoc mechanism ordering API may be added.
- If implementation exposes a genuine contradiction with the frozen preregistration, stop. Do not patch the protocol in code.
- Do not execute the V1 scientific assay during implementation or software validation.

---

## File map

Create a dedicated V1 package so V0 remains an immutable empirical anchor:

```text
prereg/
  ALCF_V1_PREREG_FROZEN.md          frozen scientific authority
  ALCF_V1_SHA256SUMS_FROZEN.txt     frozen checksum manifest

src/adaptive_leverage/v1/
  __init__.py                        narrow public V1 API
  protocol.py                        protocol ID + frozen-byte verifier
  mechanisms.py                      X_normal/J, B/P/T artifacts, custody, match rules
  episodes.py                        normal and corrective mechanism execution semantics
  trace.py                           V1 canonical hash-chained traces + mechanism-hash binding
  assay.py                           precheck/fork/admission/release/control validity/reachability
  classify.py                        stop labels, Sigma_R, pairwise signed contrasts
  artifacts.py                       canonical JSONL/JSON/checksum serialization
  runner.py                          dormant protocol-order execution entrypoint

tests/
  test_v1_protocol.py
  test_v1_mechanisms.py
  test_v1_normal_admission.py
  test_v1_trace.py
  test_v1_assay_gates.py
  test_v1_classifier.py
  test_v1_artifacts.py
  test_v1_execution_boundary.py
```

Do not overload V0 `classify.py`, `assay.py`, or `trace.py` with V1 semantics. Shared finite-state values may be imported from `adaptive_leverage.model`.

---

### Task 1: Fossilize V1 authority bytes and add the runtime hash gate

**Files:**
- Create: `prereg/ALCF_V1_PREREG_FROZEN.md`
- Create: `prereg/ALCF_V1_SHA256SUMS_FROZEN.txt`
- Create: `src/adaptive_leverage/v1/__init__.py`
- Create: `src/adaptive_leverage/v1/protocol.py`
- Create: `tests/test_v1_protocol.py`

**Interfaces:**
- Consumes: the approved `/mnt/data/ALCF_V1_PREREG_FROZEN.md` bytes and frozen checksum manifest.
- Produces: `V1_PROTOCOL_ID = "ALCF-V1"`, `V1_PREREG_SHA256`, and `verify_v1_frozen_protocol(repo_root: Path) -> None`.

- [ ] **Step 1: Copy the frozen authority artifacts byte-for-byte into `prereg/` and verify before staging**

Run:

```bash
cp /mnt/data/ALCF_V1_PREREG_FROZEN.md prereg/ALCF_V1_PREREG_FROZEN.md
cp /mnt/data/ALCF_V1_SHA256SUMS_FROZEN.txt prereg/ALCF_V1_SHA256SUMS_FROZEN.txt
sha256sum prereg/ALCF_V1_PREREG_FROZEN.md
```

Expected exact digest:

```text
5fc2cd2c02c991a9f21c74396f6205b8f98515621fb2e01ed4586e0bfea8a57f
```

If it differs, STOP before writing any V1 code.

- [ ] **Step 2: Write the failing protocol-hash tests**

```python
# tests/test_v1_protocol.py
from hashlib import sha256
from pathlib import Path
import shutil

import pytest

from adaptive_leverage.model import ImplementationError
from adaptive_leverage.v1.protocol import (
    V1_PREREG_SHA256,
    verify_v1_frozen_protocol,
)


def test_v1_frozen_prereg_bytes_match_canonical_hash():
    root = Path(__file__).resolve().parents[1]
    path = root / "prereg/ALCF_V1_PREREG_FROZEN.md"
    assert sha256(path.read_bytes()).hexdigest() == V1_PREREG_SHA256


def test_v1_runtime_hash_verifier_accepts_frozen_bytes():
    root = Path(__file__).resolve().parents[1]
    verify_v1_frozen_protocol(root)


def test_v1_runtime_hash_verifier_rejects_mutation(tmp_path):
    root = Path(__file__).resolve().parents[1]
    prereg = tmp_path / "prereg"
    prereg.mkdir()
    shutil.copy2(root / "prereg/ALCF_V1_PREREG_FROZEN.md", prereg / "ALCF_V1_PREREG_FROZEN.md")
    (prereg / "ALCF_V1_PREREG_FROZEN.md").write_text("mutated", encoding="utf-8")
    with pytest.raises(ImplementationError):
        verify_v1_frozen_protocol(tmp_path)
```

- [ ] **Step 3: Run the tests and verify RED for the missing V1 module**

Run:

```bash
pytest tests/test_v1_protocol.py -v
```

Expected: collection/import failure because `adaptive_leverage.v1.protocol` does not yet exist.

- [ ] **Step 4: Implement the minimal frozen-byte verifier**

```python
# src/adaptive_leverage/v1/protocol.py
from hashlib import sha256
from pathlib import Path

from adaptive_leverage.model import ImplementationError

V1_PROTOCOL_ID = "ALCF-V1"
V1_PREREG_RELATIVE_PATH = "prereg/ALCF_V1_PREREG_FROZEN.md"
V1_PREREG_SHA256 = "5fc2cd2c02c991a9f21c74396f6205b8f98515621fb2e01ed4586e0bfea8a57f"


def verify_v1_frozen_protocol(repo_root: Path) -> None:
    path = repo_root / V1_PREREG_RELATIVE_PATH
    try:
        observed = sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise ImplementationError(
            f"unable to read frozen V1 protocol artifact: {V1_PREREG_RELATIVE_PATH}"
        ) from exc
    if observed != V1_PREREG_SHA256:
        raise ImplementationError(
            f"frozen V1 protocol hash mismatch: {observed}"
        )
```

```python
# src/adaptive_leverage/v1/__init__.py
"""ALCF-V1 mechanism-structure comparison implementation."""

from .protocol import V1_PROTOCOL_ID, V1_PREREG_SHA256, verify_v1_frozen_protocol

__all__ = ["V1_PROTOCOL_ID", "V1_PREREG_SHA256", "verify_v1_frozen_protocol"]
```

- [ ] **Step 5: Run protocol tests and the untouched V0 suite**

Run:

```bash
pytest tests/test_v1_protocol.py -v
pytest tests/test_model.py tests/test_trace.py tests/test_custody.py tests/test_assay_controls.py tests/test_classifier.py -q
```

Expected: V1 protocol tests PASS; all existing V0 tests still PASS.

- [ ] **Step 6: Commit the authority bytes and verifier**

```bash
git add prereg/ALCF_V1_PREREG_FROZEN.md prereg/ALCF_V1_SHA256SUMS_FROZEN.txt \
  src/adaptive_leverage/v1/__init__.py src/adaptive_leverage/v1/protocol.py tests/test_v1_protocol.py
git commit -m "Fossilize frozen ALCF-V1 preregistration"
```

---

### Task 2: Encode the three transformation rules and custody without corrective inputs

**Files:**
- Create: `src/adaptive_leverage/v1/mechanisms.py`
- Create: `tests/test_v1_mechanisms.py`

**Interfaces:**
- Consumes: inherited normal constants from `adaptive_leverage.model`.
- Produces:
  - `MechanismKind` with `B`, `P`, `T`.
  - immutable `NormalTranscript`, `ObjectiveSpec`, `MechanismArtifact`, `MechanismCustodyRecord`, `CustodyCheck`.
  - `frozen_normal_transcript() -> NormalTranscript`.
  - `frozen_objective() -> ObjectiveSpec`.
  - `construct_mechanism(kind, normal, objective, finalization) -> tuple[MechanismArtifact, MechanismCustodyRecord]`.
  - `validate_mechanism_custody(...) -> CustodyCheck`.
  - `install_mechanism(state, artifact) -> MachineState`, which changes only `compiled_mode` after the byte-identical fork.
  - pure structural match helpers used later by the episode engine.

- [ ] **Step 1: Write RED tests for common input/objective identity and exact structural differences**

Use only normal objects and arbitrary synthetic mismatch values; do not use `w_c`, `e_star`, `c_star`, `CORR_AUTH`, or real corrective replay.

```python
# tests/test_v1_mechanisms.py
from adaptive_leverage.model import A0, AuthorityStatus, OMEGA_STAR, W_N
from adaptive_leverage.v1.mechanisms import (
    MechanismKind,
    construct_mechanism,
    downstream_matches,
    frozen_normal_transcript,
    frozen_objective,
    install_mechanism,
    upstream_matches,
    validate_mechanism_custody,
)


def build(kind, sequence):
    return construct_mechanism(
        kind,
        frozen_normal_transcript(),
        frozen_objective(),
        finalization_sequence=sequence,
    )


def test_all_mechanisms_share_identical_normal_input_and_objective_hashes():
    built = [build(kind, i) for i, kind in enumerate(MechanismKind, start=1)]
    input_hashes = {record.normal_manifest_sha256 for _, record in built}
    objective_hashes = {record.objective_sha256 for _, record in built}
    assert len(input_hashes) == 1
    assert len(objective_hashes) == 1


def test_b_downstream_key_ignores_authority_identity():
    artifact, _ = build(MechanismKind.B, 1)
    assert downstream_matches(artifact, OMEGA_STAR, AuthorityStatus.BASE_AUTH.value)
    assert downstream_matches(artifact, OMEGA_STAR, "SYNTHETIC_OTHER_AUTHORITY")


def test_p_downstream_key_requires_observed_authority_and_generic_mismatch_falls_back():
    artifact, _ = build(MechanismKind.P, 2)
    assert downstream_matches(artifact, OMEGA_STAR, AuthorityStatus.BASE_AUTH.value)
    assert not downstream_matches(artifact, OMEGA_STAR, "SYNTHETIC_OTHER_AUTHORITY")


def test_t_upstream_key_is_normal_world_context_and_protects_authority_state_class():
    artifact, _ = build(MechanismKind.T, 3)
    assert upstream_matches(artifact, W_N, OMEGA_STAR)
    assert not upstream_matches(artifact, "synthetic_other_world", OMEGA_STAR)
    assert artifact.protected_semantic_classes == ("AUTHORITY_TO_CONSEQUENTIAL_STATE",)


def test_each_artifact_passes_custody_without_corrective_inputs():
    for sequence, kind in enumerate(MechanismKind, start=1):
        artifact, record = build(kind, sequence)
        check = validate_mechanism_custody(record, artifact)
        assert check.passed
        assert artifact.normal_action == A0


def test_installation_changes_only_compiled_mode():
    from dataclasses import replace
    from adaptive_leverage.model import initial_state

    artifact, _ = build(MechanismKind.B, 1)
    before = initial_state()
    after = install_mechanism(before, artifact)
    assert after == replace(before, compiled_mode=1)
```

- [ ] **Step 2: Run the mechanism tests and verify RED**

Run:

```bash
pytest tests/test_v1_mechanisms.py -v
```

Expected: import failure because `v1.mechanisms` does not exist.

- [ ] **Step 3: Implement immutable mechanism/custody schemas and canonical hashing**

The implementation must encode only the frozen transformation rules. Use these exact mechanism identities:

```python
class MechanismKind(str, Enum):
    B = "T_B_AUTHORITY_INSENSITIVE_DOWNSTREAM"
    P = "T_P_AUTHORITY_SENSITIVE_DOWNSTREAM_FALLBACK"
    T = "T_T_UPSTREAM_PROTECTED_AUTHORITY_STATE"
```

Use an objective object whose canonical identity is exactly the semantic objective, not `cost=5`:

```python
@dataclass(frozen=True)
class ObjectiveSpec:
    preserve_normal_correctness: bool
    optimize_metric: str
    direction: str


def frozen_objective() -> ObjectiveSpec:
    return ObjectiveSpec(
        preserve_normal_correctness=True,
        optimize_metric="causal_micro_transition_cost",
        direction="minimize",
    )
```

The frozen normal transcript must contain normal-only values, the observed normal dynamic transition profile, the observed normal authority/policy state, and baseline cost `6`. This is necessary because `T_P` may key only on authority actually present in `X_normal`, and `T_T` may compile only an upstream pair actually observed in `X_normal`:

```python
@dataclass(frozen=True)
class NormalTranscript:
    world: str
    observation: str
    evidence: str
    context: str
    action: str
    baseline_cost: int
    edge_sequence: tuple[str, ...]
    warrant_status: str
    authority_status: str
    policy_mode: str
```

The artifact must make the rule inspectable rather than hiding it in code. Required fields:

```python
@dataclass(frozen=True)
class MechanismArtifact:
    kind: MechanismKind
    optimization_site: str
    key_fields: tuple[str, ...]
    key_values: tuple[str, ...]
    normal_action: str
    normal_policy_mode: str
    compiled_observation: str | None
    compiled_evidence: str | None
    represented_source_edges: tuple[str, ...]
    protected_semantic_classes: tuple[str, ...]
    generic_mismatch_fallback: bool
```

Canonical rules:

```text
B: site=DOWNSTREAM_E5_E6; key_fields=(context,); key_values=(alpha,);
   normal_policy_mode=BASE; normal_action=a0; represented_source_edges=(E5,E6);
   protected=(); fallback=True.

P: site=DOWNSTREAM_E5_E6; key_fields=(context,authority_identity);
   key_values=(alpha,BASE_AUTH); normal_policy_mode=BASE; normal_action=a0;
   represented_source_edges=(E5,E6); protected=(); fallback=True.

T: site=UPSTREAM_E1_E2; key_fields=(world,context); key_values=(w_n,alpha);
   compiled_observation=o_n; compiled_evidence=e_n;
   represented_source_edges=(E1,E2);
   protected=(AUTHORITY_TO_CONSEQUENTIAL_STATE,); fallback=True.
```

The forbidden-artifact manifest must include the V1 preregistered forbidden identities and corrective-derived artifacts. Validate that none appears in the canonical normal input or objective serialization. Do not forbid the *names* `E5`/`E6` globally in V1 custody, because the transformation-rule identity itself legitimately names its optimization site; custody leakage applies to construction inputs, not the frozen mechanism definition.

Record at minimum:

```python
@dataclass(frozen=True)
class MechanismCustodyRecord:
    mechanism_kind: str
    normal_manifest_json: str
    normal_input_hashes: tuple[tuple[str, str], ...]
    normal_manifest_sha256: str
    objective_json: str
    objective_sha256: str
    forbidden_artifact_manifest: tuple[str, ...]
    transformation_rule_sha256: str
    finalized_artifact_sha256: str
    finalization_sequence: int
    construction_log: tuple[str, ...]
```

`construction_log` must contain `NORMAL_WORKLOAD_ONLY`, `COMMON_OBJECTIVE_J`, and `FINALIZED_BEFORE_CORRECTIVE_RELEASE`.

- [ ] **Step 4: Implement structural match helpers without outcome semantics**

```python
def downstream_matches(artifact: MechanismArtifact, context: str, authority_identity: str) -> bool:
    if artifact.kind is MechanismKind.B:
        return context == artifact.key_values[0]
    if artifact.kind is MechanismKind.P:
        return (context, authority_identity) == artifact.key_values
    return False


def upstream_matches(artifact: MechanismArtifact, world: str, context: str) -> bool:
    if artifact.kind is not MechanismKind.T:
        return False
    return (world, context) == artifact.key_values
```

These helpers return only key matches. They must not mention `R`, `Sigma_R`, “preserve,” “foreclose,” or any corrective identity.

`install_mechanism` is equally narrow:

```python
def install_mechanism(state: MachineState, artifact: MechanismArtifact) -> MachineState:
    if artifact.kind not in {MechanismKind.B, MechanismKind.P, MechanismKind.T}:
        raise ImplementationError("unknown V1 mechanism kind")
    return replace(state, compiled_mode=1)
```

It may not change phase, scope, warrant, authority, or policy identity.

- [ ] **Step 5: Run tests and inspect source for forbidden outcome definitions**

Run:

```bash
pytest tests/test_v1_mechanisms.py -v
grep -nE 'Sigma_R|R_B|R_P|R_T|preferred|safer|better' src/adaptive_leverage/v1/mechanisms.py && exit 1 || true
```

Expected: tests PASS and grep prints nothing.

- [ ] **Step 6: Commit**

```bash
git add src/adaptive_leverage/v1/mechanisms.py tests/test_v1_mechanisms.py
git commit -m "Encode frozen ALCF-V1 mechanism rules and custody"
```

---

### Task 3: Implement normal-only mechanism episodes and exact 5/5/5 admission measurements

**Files:**
- Create: `src/adaptive_leverage/v1/episodes.py`
- Create: `tests/test_v1_normal_admission.py`

**Interfaces:**
- Consumes: `MachineState`, dynamic V0 state semantics, V1 `MechanismArtifact`.
- Produces:
  - `run_v1_normal_episode(state, artifact) -> Episode` for B/P/T.
  - `run_v1_world_episode(world, state, artifact) -> Episode` as the generic engine used later after release.
  - diagnostic compiled transition IDs that preserve causal micro-transition counting without redefining frozen E1..E6.

- [ ] **Step 1: Write RED tests for normal correctness and exact matched cost**

```python
# tests/test_v1_normal_admission.py
from adaptive_leverage.model import A0, W_N, initial_state, run_dynamic_episode
from adaptive_leverage.v1.episodes import run_v1_normal_episode
from adaptive_leverage.v1.mechanisms import (
    MechanismKind,
    construct_mechanism,
    frozen_normal_transcript,
    frozen_objective,
    install_mechanism,
)


def artifact(kind, sequence):
    return construct_mechanism(
        kind,
        frozen_normal_transcript(),
        frozen_objective(),
        finalization_sequence=sequence,
    )[0]


def test_baseline_normal_cost_remains_six():
    episode = run_dynamic_episode(W_N, initial_state())
    assert episode.action == A0
    assert len(episode.steps) == 6


def test_each_v1_mechanism_has_same_normal_action_and_exact_cost_five():
    for sequence, kind in enumerate(MechanismKind, start=1):
        mechanism = artifact(kind, sequence)
        state = install_mechanism(initial_state(), mechanism)
        episode = run_v1_normal_episode(state, mechanism)
        assert episode.action == A0
        assert len(episode.steps) == 5


def test_b_and_p_compile_same_downstream_normal_site():
    b_artifact = artifact(MechanismKind.B, 1)
    p_artifact = artifact(MechanismKind.P, 2)
    b = run_v1_normal_episode(install_mechanism(initial_state(), b_artifact), b_artifact)
    p = run_v1_normal_episode(install_mechanism(initial_state(), p_artifact), p_artifact)
    assert [s.transition_id for s in b.steps[:4]] == [s.transition_id for s in p.steps[:4]]
    assert b.steps[-1].transition_id == p.steps[-1].transition_id == "V1_DOWNSTREAM_E5_E6_COMPILED"


def test_t_compiles_upstream_normal_site_and_leaves_e3_through_e6_dynamic():
    t_artifact = artifact(MechanismKind.T, 3)
    t = run_v1_normal_episode(install_mechanism(initial_state(), t_artifact), t_artifact)
    assert t.steps[0].transition_id == "V1_UPSTREAM_E1_E2_COMPILED"
    assert [step.edge.value for step in t.steps[1:]] == ["E3", "E4", "E5", "E6"]
```

- [ ] **Step 2: Run tests and verify RED**

```bash
pytest tests/test_v1_normal_admission.py -v
```

- [ ] **Step 3: Implement B/P downstream fusion for the normal workload**

For a matching B/P downstream key, execute dynamic E1-E4 and replace the *observed normal* E5+E6 behavior with one compiled micro-transition from `AUTHORIZED` directly to `ACTED`, reproducing the normal learned payload (`policy_mode=BASE`, `action=a0`). Use a diagnostic transition ID and `Provenance.COMPILE_DISPATCH`; do not claim that the diagnostic compiled step is itself frozen edge E5 or E6.

- [ ] **Step 4: Implement T upstream fusion for the normal workload**

For a matching T upstream key, replace normal E1+E2 with one compiled micro-transition from `READY` directly to `EVIDENCED` that reproduces the observed normal `o_n/e_n` payload from `X_normal`, then execute frozen dynamic E3-E6 unchanged. The protected authority/state semantic class must not be consulted as an outcome rule; it only prevents an authority/state compilation site from being selected for T.

- [ ] **Step 5: Implement generic mismatch fallback inside the episode engine**

`run_v1_world_episode` must dispatch only on structural key matching:

```python
if artifact.kind in {MechanismKind.B, MechanismKind.P}:
    # run dynamic E1-E4 to establish the authority identity, then either
    # use compiled downstream dispatch if downstream_matches(...) else dynamic E5-E6
elif artifact.kind is MechanismKind.T:
    # use compiled upstream E1-E2 only if upstream_matches(...), else run the full dynamic path
```

No branch may ask whether the world is a contradiction, whether correction is warranted, or whether a route should survive. Those properties arise from the inherited machine state and key matching.

- [ ] **Step 6: Run the normal-only tests plus mechanism custody tests**

```bash
pytest tests/test_v1_mechanisms.py tests/test_v1_normal_admission.py -v
```

Expected: all PASS; no real V1 corrective comparison has run.

- [ ] **Step 7: Commit**

```bash
git add src/adaptive_leverage/v1/episodes.py tests/test_v1_normal_admission.py
git commit -m "Implement matched ALCF-V1 normal mechanism episodes"
```

---

### Task 4: Add V1 canonical traces bound to admitted mechanism hashes

**Files:**
- Create: `src/adaptive_leverage/v1/trace.py`
- Create: `tests/test_v1_trace.py`

**Interfaces:**
- Consumes: `Episode`, V1 protocol ID, optional mechanism artifact hash.
- Produces: immutable `V1TraceEvent`, `build_v1_trace`, `validate_v1_trace`, canonical JSON and hash chain.

- [ ] **Step 1: Write RED trace tests using normal episodes only**

```python
# tests/test_v1_trace.py
from dataclasses import replace

import pytest

from adaptive_leverage.model import initial_state
from adaptive_leverage.v1.episodes import run_v1_normal_episode
from adaptive_leverage.v1.mechanisms import (
    MechanismKind,
    construct_mechanism,
    frozen_normal_transcript,
    frozen_objective,
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
    episode = run_v1_normal_episode(initial_state(), artifact)
    trace = build_v1_trace(
        episode,
        arm="B",
        run_id="software-normal-b",
        mechanism_artifact_sha256=custody.finalized_artifact_sha256,
    )
    validate_v1_trace(trace)
    assert {e.mechanism_artifact_sha256 for e in trace} == {custody.finalized_artifact_sha256}
    assert all(e.protocol_id == "ALCF-V1" for e in trace)


def test_v1_trace_rejects_mechanism_hash_mutation():
    artifact, custody = built_b()
    episode = run_v1_normal_episode(initial_state(), artifact)
    events = list(build_v1_trace(
        episode,
        arm="B",
        run_id="software-normal-b",
        mechanism_artifact_sha256=custody.finalized_artifact_sha256,
    ))
    events[0] = replace(events[0], mechanism_artifact_sha256="0" * 64)
    with pytest.raises(V1TraceValidationError):
        validate_v1_trace(tuple(events))
```

- [ ] **Step 2: Run RED test**

```bash
pytest tests/test_v1_trace.py -v
```

- [ ] **Step 3: Implement the V1 trace schema**

Copy the V0 scientific trace fields and add only non-authorizing binding/diagnostic fields required by V1:

```python
@dataclass(frozen=True)
class V1TraceEvent:
    protocol_id: str
    run_id: str
    arm: str
    mechanism_artifact_sha256: str | None
    seq: int
    transition_id: str
    edge_id: str
    represented_source_edges: tuple[str, ...]
    world: str
    context: str
    observation: str | None
    evidence: str | None
    contradiction_id: str | None
    scope_status: str
    warrant_status: str
    authority_status: str
    policy_mode_before: str
    policy_mode_after: str
    compiled_mode: int
    action: str | None
    microstep_index: int
    provenance: str
    prev_event_sha256: str | None
    event_sha256: str
```

For dynamic steps, `represented_source_edges=(step.edge.value,)`. For compiled fusions, use diagnostic edge IDs such as `E5_E6_COMPILED` or `E1_E2_COMPILED` while recording only the *source edges whose normal behavior was compiled* as `("E5","E6")` or `("E1","E2")`. This field is diagnostic provenance and must never be treated as proof that the frozen dynamic edges themselves were traversed. `microstep_index` counts actual causal micro-transitions after transformation, so each compiled fusion counts as one.

- [ ] **Step 4: Implement canonical hashing and validation**

Validation must enforce immutable tuple, contiguous sequence, canonical event hash, previous-event linkage, `protocol_id == "ALCF-V1"`, stable arm identity, and stable mechanism hash within a trace. It must not infer a scientific outcome.

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_v1_trace.py tests/test_v1_normal_admission.py -v
```

- [ ] **Step 6: Commit**

```bash
git add src/adaptive_leverage/v1/trace.py tests/test_v1_trace.py
git commit -m "Bind ALCF-V1 traces to finalized mechanism artifacts"
```

---

### Task 5: Enforce byte-identical fork, all-or-none joint admission, and irreversible corrective release

**Files:**
- Create: `src/adaptive_leverage/v1/assay.py`
- Create: `tests/test_v1_assay_gates.py`

**Interfaces:**
- Produces `V1ArmBundle`, `NormalObservation`, `JointAdmissionReason`, `JointAdmission`, `CorrectiveReleaseToken`.
- Produces `fork_v1_arms`, `measure_v1_normal`, `joint_admit`, `require_corrective_release`.
- The correction replay API added in Task 6 must require a `CorrectiveReleaseToken`; there is no alternate public path.

- [ ] **Step 1: Write RED tests for prefork identity and all-or-none admission**

```python
# tests/test_v1_assay_gates.py
from dataclasses import replace

import pytest

from adaptive_leverage.model import ImplementationError, initial_state
from adaptive_leverage.v1.assay import (
    JointAdmissionReason,
    fork_v1_arms,
    joint_admit,
    measure_v1_normal,
)
from adaptive_leverage.v1.mechanisms import (
    MechanismKind,
    construct_mechanism,
    frozen_normal_transcript,
    frozen_objective,
    validate_mechanism_custody,
)


def build_all():
    return {
        kind: construct_mechanism(
            kind,
            frozen_normal_transcript(),
            frozen_objective(),
            finalization_sequence=i,
        )
        for i, kind in enumerate(MechanismKind, start=1)
    }


def test_all_five_arms_are_byte_identical_before_registered_interventions():
    bundle = fork_v1_arms(initial_state())
    assert len(set(bundle.prefork_serialized.values())) == 1
    assert set(bundle.prefork_serialized) == {"C", "B", "P", "T", "E"}


def test_joint_admission_requires_all_three_exact_cost_five_and_matching_correctness():
    built = build_all()
    bundle = fork_v1_arms(initial_state())
    baseline = measure_v1_normal("C", bundle.c, None, None)
    observations = {}
    custody = {}
    for arm, kind in (("B", MechanismKind.B), ("P", MechanismKind.P), ("T", MechanismKind.T)):
        artifact, record = built[kind]
        observations[arm] = measure_v1_normal(arm, getattr(bundle, arm.lower()), artifact, record.finalized_artifact_sha256)
        custody[arm] = validate_mechanism_custody(record, artifact)
    admission = joint_admit(baseline, observations, custody, built)
    assert admission.passed
    assert admission.release_token is not None


def test_one_cost_mismatch_fails_the_entire_joint_gate_without_release_token():
    built = build_all()
    bundle = fork_v1_arms(initial_state())
    baseline = measure_v1_normal("C", bundle.c, None, None)
    observations = {}
    custody = {}
    for arm, kind in (("B", MechanismKind.B), ("P", MechanismKind.P), ("T", MechanismKind.T)):
        artifact, record = built[kind]
        observations[arm] = measure_v1_normal(arm, getattr(bundle, arm.lower()), artifact, record.finalized_artifact_sha256)
        custody[arm] = validate_mechanism_custody(record, artifact)
    observations["P"] = replace(observations["P"], cost=4)
    admission = joint_admit(baseline, observations, custody, built)
    assert not admission.passed
    assert admission.reason is JointAdmissionReason.COST_MISMATCH
    assert admission.release_token is None
```

- [ ] **Step 2: Run RED tests**

```bash
pytest tests/test_v1_assay_gates.py -v
```

- [ ] **Step 3: Implement the five-arm prefork bundle without applying transformations yet**

`fork_v1_arms(initial_state)` records five states whose `canonical_state_bytes` are equal before any registered intervention. After those bytes are frozen in the bundle, apply only registered arm interventions: install the finalized B/P/T mechanism on its arm by setting `compiled_mode=1`, apply `VALID_SCOPE_CLOSURE` to E, and leave C unchanged. Mechanism artifacts remain separate immutable objects; installation may not change world/evidence/warrant/authority identities.

- [ ] **Step 4: Implement normal measurements and exact joint gate**

`measure_v1_normal` uses dynamic C/E behavior and the mechanism normal episode for B/P/T. It returns exact action, correctness relative to C, micro-transition cost, validated trace, and mechanism hash binding.

`joint_admit` must check in this order:

```text
all three mechanism artifacts finalized and hashes match custody records
all three custody checks pass
all three normal actions/correctness equal C
each B/P/T cost == 5
all three mechanism hashes are distinct and bound to B/P/T identities
```

On any failure return top-level `passed=False`, no release token, and exactly one machine-readable reason from the frozen allowed family:

```python
class JointAdmissionReason(str, Enum):
    CUSTODY_FAILURE = "CUSTODY_FAILURE"
    OPTIMIZATION_LEAKAGE = "OPTIMIZATION_LEAKAGE"
    NORMAL_CORRECTNESS_MISMATCH = "NORMAL_CORRECTNESS_MISMATCH"
    COST_MISMATCH = "COST_MISMATCH"
    MECHANISM_FINALIZATION_FAILURE = "MECHANISM_FINALIZATION_FAILURE"
```

- [ ] **Step 5: Make the release token bind all three admitted hashes**

```python
@dataclass(frozen=True)
class CorrectiveReleaseToken:
    b_artifact_sha256: str
    p_artifact_sha256: str
    t_artifact_sha256: str
    admission_sha256: str
```

The token is constructed only by a passing `joint_admit`. Do not export any function that creates a token from raw strings.

- [ ] **Step 6: Run gate tests plus all previous V1 tests**

```bash
pytest tests/test_v1_protocol.py tests/test_v1_mechanisms.py tests/test_v1_normal_admission.py tests/test_v1_trace.py tests/test_v1_assay_gates.py -v
```

- [ ] **Step 7: Commit**

```bash
git add src/adaptive_leverage/v1/assay.py tests/test_v1_assay_gates.py
git commit -m "Enforce ALCF-V1 joint admission before corrective release"
```

---

### Task 6: Implement corrective replay validity and reachability extraction without running the real comparison in tests

**Files:**
- Modify: `src/adaptive_leverage/v1/assay.py`
- Modify: `src/adaptive_leverage/v1/episodes.py`
- Create: `tests/test_v1_reachability.py`

**Interfaces:**
- Produces `CorrectionObservation`, `replay_v1_correction`, `qualified_v1_route`, and upstream identity/warrant validation helpers.
- `replay_v1_correction` requires a real `CorrectiveReleaseToken` whose three mechanism hashes match the supplied B/P/T artifacts.

- [ ] **Step 1: Write reachability tests over hand-built traces, not real B/P/T corrective execution**

Construct explicit synthetic `V1TraceEvent` fixtures with non-V1 placeholder identities. Do **not** call the real frozen `W_C` episode or any B/P/T corrective replay in these tests. Test the scientific predicate, not the hidden comparative result:

```python
def test_qualified_route_requires_evidence_warrant_authority_corrected_policy_and_a1_in_order():
    trace = synthetic_qualified_trace()
    assert qualified_v1_route(trace)


def test_missing_corrected_policy_makes_route_empty():
    trace = synthetic_qualified_trace(policy_after="BASE")
    assert not qualified_v1_route(trace)


def test_changed_evidence_identity_is_warrant_drift_not_a_reachability_bit():
    observation = synthetic_correction_observation(evidence="synthetic_wrong_evidence")
    assert not correction_identity_valid(observation)
```

The synthetic helpers may use arbitrary fixture labels such as `fixture_evidence`, `fixture_correction`, and `fixture_authority`; do not derive or assert the actual `B/P/T` V1 signature.

- [ ] **Step 2: Run RED tests**

```bash
pytest tests/test_v1_reachability.py -v
```

- [ ] **Step 3: Implement the generic corrective replay engine behind the release token**

After token validation:

```text
C: inherited dynamic W_C episode.
B/P/T: run_v1_world_episode(W_C, state, artifact); transformation behavior follows only key matching.
E: requires CLOSED_VALID and inherited dynamic W_C episode with VALID_SCOPE_CLOSURE provenance.
```

Do not add any branch on expected route survival. The only B/P/T branches are the transformation rules already implemented in `episodes.py`.

- [ ] **Step 4: Implement correction identity/warrant validity checks**

For B/P/T require the frozen identities from prereg Section 8 before a bit can be extracted:

```text
world == w_c
context == omega_star
observation == o_c
evidence == e_star
scope == OPEN
warrant reaches CORRECTION
authority reaches CORR_AUTH
```

A failure is represented for the classifier as `warrant_drift=True`; do not coerce it into `route_nonempty=False`.

- [ ] **Step 5: Implement qualified reachability as a causal-order predicate**

`qualified_v1_route` must require, in order, evidence `e_star`, `CORRECTION`, `CORR_AUTH`, `policy=CORRECTED`, and terminal action `a1`, with a valid trace chain. Endpoint action alone is insufficient.

- [ ] **Step 6: Test only predicates and gate rejection; do not invoke the real B/P/T corrective comparison**

Run:

```bash
pytest tests/test_v1_reachability.py tests/test_v1_assay_gates.py -v
```

Also assert that calling `replay_v1_correction` with no release token raises `ImplementationError` before any episode is constructed.

- [ ] **Step 7: Commit**

```bash
git add src/adaptive_leverage/v1/assay.py src/adaptive_leverage/v1/episodes.py tests/test_v1_reachability.py
git commit -m "Implement gated ALCF-V1 corrective reachability semantics"
```

---

### Task 7: Implement the validity classifier, exhaustive primary signature, and bounded secondary contrasts

**Files:**
- Create: `src/adaptive_leverage/v1/classify.py`
- Create: `tests/test_v1_classifier.py`
- Modify: `src/adaptive_leverage/v1/__init__.py`

**Interfaces:**
- Produces `V1Stop`, `V1ValidityFacts`, `ReachabilitySignature`, `V1ScientificOutcome`, `V1Decision`, `classify_v1`.
- A decision contains either a stop reason with `scientific_outcome=None`, or a valid scientific outcome. Never both.

- [ ] **Step 1: Write RED tests for stop precedence and all eight equally admissible signatures**

```python
# tests/test_v1_classifier.py
from dataclasses import replace
import itertools

from adaptive_leverage.v1.classify import (
    V1Stop,
    V1ValidityFacts,
    classify_v1,
)


def valid_facts(bits=(False, False, False)):
    return V1ValidityFacts(
        precheck_passed=True,
        identity_matched=True,
        joint_admission_passed=True,
        joint_admission_reason=None,
        warrant_drift=False,
        control_route_nonempty=True,
        positive_control_valid=True,
        trace_ambiguous=False,
        b_route_nonempty=bits[0],
        p_route_nonempty=bits[1],
        t_route_nonempty=bits[2],
    )


def test_invalidity_emits_no_scientific_outcome():
    decision = classify_v1(replace(valid_facts(), joint_admission_passed=False, joint_admission_reason="COST_MISMATCH"))
    assert decision.stop is V1Stop.V1_JOINT_ADMISSION_FAIL
    assert decision.scientific_outcome is None


def test_all_eight_signatures_are_emitted_without_preference_or_ranking():
    observed = set()
    for bits in itertools.product((False, True), repeat=3):
        decision = classify_v1(valid_facts(bits))
        assert decision.stop is None
        outcome = decision.scientific_outcome
        observed.add(outcome.signature.text)
        assert not hasattr(outcome, "score")
        assert not hasattr(outcome, "rank")
        assert not hasattr(outcome, "bit_count")
    assert observed == {"000", "001", "010", "011", "100", "101", "110", "111"}


def test_pairwise_contrasts_are_signed_differences_only():
    outcome = classify_v1(valid_facts((False, True, False))).scientific_outcome
    assert outcome.d_bp == 1
    assert outcome.d_bt == 0
    assert outcome.d_pt == -1
```

Do not write a test asserting that any particular signature is the expected V1 result.

- [ ] **Step 2: Run RED tests**

```bash
pytest tests/test_v1_classifier.py -v
```

- [ ] **Step 3: Implement frozen validity precedence**

Use exactly these top-level stop labels:

```python
class V1Stop(str, Enum):
    PRECHECK_FAIL = "PRECHECK_FAIL"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    V1_JOINT_ADMISSION_FAIL = "V1_JOINT_ADMISSION_FAIL"
    WARRANT_DRIFT = "WARRANT_DRIFT"
    CONTROL_MISMATCH = "CONTROL_MISMATCH"
    POSITIVE_CONTROL_FAIL = "POSITIVE_CONTROL_FAIL"
    TRACE_AMBIGUOUS = "TRACE_AMBIGUOUS"
```

Classification/orchestration precedence must follow prereg §18 exactly. Before any scientific outcome: precheck → prefork identity → joint admission → corrective replay → trace validation → C control → E positive control → B/P/T epistemic/warrant identity → reachability bits. In the pure classifier this means: `PRECHECK_FAIL`, then `IDENTITY_MISMATCH`, then `V1_JOINT_ADMISSION_FAIL`, then `TRACE_AMBIGUOUS`, then `CONTROL_MISMATCH`, then `POSITIVE_CONTROL_FAIL`, then `WARRANT_DRIFT`, and only then a scientific signature. Any stop returns `scientific_outcome=None`; specifically, no stop maps to `000`.

- [ ] **Step 4: Implement the primary signature and secondary contrasts**

```python
@dataclass(frozen=True)
class ReachabilitySignature:
    b: int
    p: int
    t: int

    @property
    def text(self) -> str:
        return f"{self.b}{self.p}{self.t}"


@dataclass(frozen=True)
class V1ScientificOutcome:
    signature: ReachabilitySignature
    d_bp: int
    d_bt: int
    d_pt: int
    licensed_statements: tuple[str, ...]
```

`d_bp = p-b`, `d_bt = t-b`, `d_pt = t-p`. Do not add a score, ordering, bit count, aggregate, `is_success`, `best`, or preference field.

- [ ] **Step 5: Implement bounded interpretation strings**

Only `d_bp == +1` receives the frozen single-property statement verbatim from prereg §14.1. `d_bt != 0` and `d_pt != 0` receive only their respective composite-rule divergence statements. `d_bp == -1` is labeled only as the observed opposite directional contrast; `d_bp == 0` gets no single-property support statement.

- [ ] **Step 6: Run tests and static anti-scalarization check**

```bash
pytest tests/test_v1_classifier.py -v
grep -nE 'score|ranking|rank_|is_success|preferred|bit_count|sum\(' src/adaptive_leverage/v1/classify.py && exit 1 || true
```

- [ ] **Step 7: Export only the narrow public classifier API and commit**

```bash
git add src/adaptive_leverage/v1/classify.py src/adaptive_leverage/v1/__init__.py tests/test_v1_classifier.py
git commit -m "Encode ALCF-V1 validity and reachability signature classifier"
```

---

### Task 8: Add canonical custody/result artifact serialization without executing V1

**Files:**
- Create: `src/adaptive_leverage/v1/artifacts.py`
- Create: `tests/test_v1_artifacts.py`

**Interfaces:**
- Produces canonical JSON/JSONL writers and `write_sha256_manifest`.
- Serializers accept already-produced records; they do not run mechanisms or classify outcomes.

- [ ] **Step 1: Write RED serializer tests using synthetic/non-scientific records**

Test deterministic key ordering, newline termination, trace JSONL round-trip, and SHA-256 manifest generation in `tmp_path`. Use a synthetic classifier fixture if a scientific-outcome serializer must be exercised; label run IDs `software-fixture-*`.

- [ ] **Step 2: Run RED tests**

```bash
pytest tests/test_v1_artifacts.py -v
```

- [ ] **Step 3: Implement artifact writers**

Support these execution-time filenames without creating them yet:

```text
protocol_identity.json
prefork_identity.json
B_mechanism.json
P_mechanism.json
T_mechanism.json
B_custody.json
P_custody.json
T_custody.json
C_normal_trace.jsonl
B_normal_trace.jsonl
P_normal_trace.jsonl
T_normal_trace.jsonl
E_normal_trace.jsonl
joint_admission.json
C_correction_trace.jsonl
B_correction_trace.jsonl
P_correction_trace.jsonl
T_correction_trace.jsonl
E_correction_trace.jsonl
validity_facts.json
classification.json
SHA256SUMS.txt
```

Writers must fail rather than serialize a V1 scientific outcome when the `V1Decision` has a stop label.

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_v1_artifacts.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/adaptive_leverage/v1/artifacts.py tests/test_v1_artifacts.py
git commit -m "Add canonical ALCF-V1 execution artifact serialization"
```

---

### Task 9: Build a dormant protocol-order runner with an explicit execution boundary

**Files:**
- Create: `src/adaptive_leverage/v1/runner.py`
- Create: `tests/test_v1_execution_boundary.py`

**Interfaces:**
- Produces immutable `PreparedV1Run` and `prepare_v1(repo_root, run_id) -> PreparedV1Run` that performs only hash verification, sacrificial precheck, prefork, B/P/T construction/custody, normal measurements, and joint admission.
- Produces `execute_v1_corrective(prepared, output_dir) -> V1Decision` that is the sole function allowed to release the real corrective condition.
- No import-time or CLI side effect may execute either function.

- [ ] **Step 1: Write RED tests proving preparation stops before corrective release**

Use monkeypatch/spies so tests can prove `prepare_v1` never calls `replay_v1_correction`. Also replace the real sacrificial `W_C` precheck with a synthetic passing precheck fixture during software tests; invoking the actual preregistered precheck belongs to the later scientific execution, not implementation validation.

```python
def test_prepare_v1_never_releases_corrective_condition(monkeypatch, repo_root):
    called = False

    monkeypatch.setattr(
        "adaptive_leverage.v1.runner.run_sacrificial_precheck",
        lambda *args, **kwargs: synthetic_passing_precheck_fixture(),
    )

    def forbidden(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("corrective replay reached during preparation")

    monkeypatch.setattr("adaptive_leverage.v1.runner.replay_v1_correction", forbidden)
    prepared = prepare_v1(repo_root, run_id="software-prepare-fixture")
    assert prepared.joint_admission.passed
    assert not called
```

Do not call `execute_v1_corrective` in the software suite with the real frozen mechanisms.

- [ ] **Step 2: Run RED tests**

```bash
pytest tests/test_v1_execution_boundary.py -v
```

- [ ] **Step 3: Implement `prepare_v1` in frozen order**

The implementation order is exact:

```text
verify frozen protocol hash
sacrificial precheck
byte-identical C/B/P/T/E prefork
construct B/P/T from common X_normal + J
finalize/hash/custody B/P/T
normal C/B/P/T/E measurement
joint exact admission
return PreparedV1Run containing the release token only if admitted
```

`PreparedV1Run` must be a frozen dataclass containing the finalized artifacts, custody records, prefork identities, normal measurements, joint-admission record, and release token. There is no mutator/retuning API. Preparation may write pre-reveal artifacts to an output directory only when explicitly requested, but it must not write any `R_*`, `Sigma_R`, or `D_*` field.

- [ ] **Step 4: Implement `execute_v1_corrective` but do not call it**

It must:

```text
require PreparedV1Run with passing joint admission and valid token
re-verify protocol hash
re-verify admitted mechanism hashes against the token
release corrective condition
run C/B/P/T/E replay
validate every trace
validate C route-preservation control
validate E scope-closure positive control
validate B/P/T upstream identity/warrant conditions
extract B/P/T qualified-route bits
classify with classify_v1
write canonical execution artifacts and SHA256SUMS
return the mechanical V1Decision
```

The function contains no expected signature constant and no outcome-specific branch other than the frozen classifier. `C` control validation requires the qualified dynamic correction route and terminal `a1`. `E` positive-control validation requires `CLOSED_VALID`, registered `VALID_SCOPE_CLOSURE` provenance, removal from the correction-warrant class, and absence of a qualified corrective route for the epistemically licensed reason.

- [ ] **Step 5: Add an explicit no-accidental-execution guard**

Do not add a console script entry point yet. The only execution surface is an explicit Python call to `execute_v1_corrective(prepared, output_dir)` from a separately reviewed execution step. Importing `runner.py`, running pytest, or running `python -m adaptive_leverage.v1.runner` must not execute the assay.

- [ ] **Step 6: Run boundary tests**

```bash
pytest tests/test_v1_execution_boundary.py -v
```

Expected: preparation is fully testable and no corrective replay is observed.

- [ ] **Step 7: Commit**

```bash
git add src/adaptive_leverage/v1/runner.py tests/test_v1_execution_boundary.py
git commit -m "Prepare dormant ALCF-V1 protocol-order execution runner"
```

---

### Task 10: Full software verification with zero V1 scientific execution

**Files:**
- Modify only if verification exposes an implementation defect. Never modify frozen protocol bytes.

**Interfaces:**
- Produces evidence that the software is ready for a separately authorized first V1 execution; it does not produce a V1 scientific result.

- [ ] **Step 1: Verify frozen prereg bytes directly**

Run:

```bash
sha256sum prereg/ALCF_V1_PREREG_FROZEN.md
```

Expected:

```text
5fc2cd2c02c991a9f21c74396f6205b8f98515621fb2e01ed4586e0bfea8a57f
```

- [ ] **Step 2: Verify pre-execution result fields remain unpopulated in the frozen artifact**

Run:

```bash
grep -nE '^R_[BPT]:|^Sigma_R:|^D_(BP|BT|PT):' prereg/ALCF_V1_PREREG_FROZEN.md
```

Expected exact semantic state: every field is still marked `UNPOPULATED` as frozen.

- [ ] **Step 3: Run the full test suite fresh**

```bash
pytest -q
```

Expected: zero failures. Record the actual count from this run; do not predict it in advance.

- [ ] **Step 4: Prove tests did not create scientific execution artifacts**

Run from repository root:

```bash
find . -type f \( -name 'classification.json' -o -name '*correction_trace.jsonl' -o -name 'SHA256SUMS.txt' \) \
  -not -path './prereg/*' -print
```

Expected: no V1 scientific execution artifact directory created by tests.

- [ ] **Step 5: Search for forbidden hard-coded V1 scientific outcome expectations**

Run:

```bash
grep -RInE 'expected.*Sigma|preferred.*Sigma|Sigma_R.*011|Sigma_R.*000|R_B.*=.*(true|false)|R_P.*=.*(true|false)|R_T.*=.*(true|false)' \
  src/adaptive_leverage/v1 tests/test_v1_*.py || true
```

Review every hit. Any code/test that encodes an expected real V1 route pattern is a STOP defect and must be removed before execution.

- [ ] **Step 6: Verify V0 regression suite independently**

Run:

```bash
pytest tests/test_model.py tests/test_trace.py tests/test_custody.py tests/test_assay_controls.py tests/test_classifier.py -q
```

Expected: zero failures; V0 remains unchanged scientifically.

- [ ] **Step 7: Inspect git diff/status and frozen file identity**

Run:

```bash
git status --short
git diff --stat HEAD~1..HEAD
sha256sum prereg/ALCF_V0_PREREG_FROZEN.md prereg/ALCF_V0_PROTOCOL_FROZEN.json prereg/ALCF_V1_PREREG_FROZEN.md
```

Confirm no unintended edits to V0 frozen artifacts and the V1 hash is exact.

- [ ] **Step 8: Commit any final implementation-only verification fix, then STOP**

If no fix is needed, do not create an empty commit. The scientific state after Task 10 must be:

```text
ALCF-V0-001             empirical anchor; untouched
ALCF-V1 preregistration frozen; hash exact
V1 implementation       complete
software validation     pass, with fresh evidence
V1 corrective execution NOT STARTED
R_B/R_P/R_T             unobserved
Sigma_R                  unobserved
D_BP/D_BT/D_PT           unobserved
```

Do not call `execute_v1_corrective` in this task. First scientific execution is a separate, explicit action after implementation review.
