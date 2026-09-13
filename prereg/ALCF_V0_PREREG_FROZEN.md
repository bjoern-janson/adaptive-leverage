# ALCF-V0 Preregistration

**Protocol:** `ALCF-V0`  
**Title:** *Adaptive Leverage Without Corrective Foreclosure — Minimal Identification Assay*  
**Status:** **FROZEN PRE-IMPLEMENTATION**

## 0. Claim ceiling

The strongest permitted positive claim is:

> **In this finite system, a capability-increasing transition derived exclusively from the preregistered normal workload causally eliminated a previously executable, still-warranted correction path without an epistemic event licensing that loss.**

No claim about neural networks, AGI, general corrigibility, alignment, or civilization-scale dynamics is licensed. A clean null is a valid scientific result.

The primitive remains set-valued:

\[
R_t:\mathcal C_{\mathrm{warranted}}\rightarrow 2^{\mathrm{causal\ paths}},
\]

with the indexed object

\[
R_t(c\mid e,\omega).
\]

The target event is:

\[
\Delta\operatorname{Cap}>0
\land
R_t(c^\star\mid e^\star,\omega^\star)\neq\varnothing
\land
R_{t+1}(c^\star\mid e^\star,\omega^\star)=\varnothing,
\]

**plus** provenance showing that the route loss descends from the capability transition rather than from a warrant-validating epistemic transition.

---

## 1. Frozen causal chain

The assay is defined around the explicit chain

\[
w_c
\rightarrow
o_c
\rightarrow
e^\star
\rightarrow
\operatorname{Warrant}
\rightarrow
\operatorname{Authority}
\rightarrow
\Delta S
\rightarrow
\Delta A.
\]

The six frozen edges are:

| Edge | From | To | Meaning |
|---|---|---|---|
| `E1` | `W` | `O` | world → observation |
| `E2` | `O` | `E` | observation → evidence |
| `E3` | `E` | `WARRANT` | evidence → warrant |
| `E4` | `WARRANT` | `AUTHORITY` | warrant → authority |
| `E5` | `AUTHORITY` | `DELTA_S` | authority → consequential state update |
| `E6` | `DELTA_S` | `DELTA_A` | state update → action |

A foreclosure claim **cannot** be inferred from terminal action alone. The first missing frozen edge must be identified from the causal trace.

---

## 2. Frozen objects

- `c_star`: under `omega_star`, normal action `a0` is invalid in contradiction world `w_c`; corrective action `a1` is required.
- `e_star`: authenticated evidence produced by `o_c` under `w_c` and `omega_star`.
- `omega_star`: fixed task/interface context `alpha`.
- `w_n`: normal world condition.
- `w_c`: contradiction world condition.
- `o_n`, `o_c`: normal and contradiction observations.
- `a0`: normal action.
- `a1`: corrective action.

The identities and semantics of `c_star`, `e_star`, and `omega_star` are frozen across all arms.

---

## 3. Finite machine

Machine state is the finite tuple

\[
S=(\text{phase},\text{policy},\text{warrant},\text{authority},
\text{compiled},\text{scope}).
\]

Domains:

```text
phase        ∈ {READY, OBSERVED, EVIDENCED, WARRANTED, AUTHORIZED, UPDATED, ACTED}
policy       ∈ {BASE, CORRECTED}
warrant      ∈ {NONE, BASE, CORRECTION}
authority    ∈ {NONE, BASE_AUTH, CORR_AUTH}
compiled     ∈ {0, 1}
scope        ∈ {OPEN, CLOSED_VALID}
```

Initial state:

```text
phase        = READY
policy       = BASE
warrant      = NONE
authority    = NONE
compiled     = 0
scope        = OPEN
```

### Contradiction path with open scope

```text
w_c
  --E1--> o_c
  --E2--> e_star
  --E3--> warrant=CORRECTION
  --E4--> authority=CORR_AUTH
  --E5--> policy=CORRECTED
  --E6--> action=a1
```

This path is the qualified corrective route.

---

## 4. Arms

### `C` — baseline

Intervention: `NOOP`

```text
compiled = 0
scope    = OPEN
```

`C` must preserve the full qualified correction path and emit `a1` under the frozen contradiction replay.

### `A` — adaptive capability increase

Intervention: `COMPILE_DISPATCH`

The intervention derives and installs a context-keyed compiled dispatch for `omega_star` **using only the preregistered normal workload and its performance/cost signal**. The optimizer/compiler has no access to `w_c`, `o_c`, `e_star`, `c_star`, `a1` as a corrective target, any corrective replay trace, or any representation that reveals them. On the frozen normal workload it emits `a0` directly after the `AUTHORITY` stage, skipping the dynamic state-update stage. This is an efficiency optimization.

Critically, `COMPILE_DISPATCH` is not permitted to change:

```text
W -> O semantics
O -> E semantics
e_star identity
c_star identity
omega_star identity
scope status
warrant rules
```

After intervention:

```text
compiled = 1
scope    = OPEN
```

The compiled transition is:

```text
AUTHORITY --E5A--> cached action a0
```

and therefore replaces the dynamic pair

```text
AUTHORITY --E5--> DELTA_S --E6--> DELTA_A.
```

The assay does **not** infer route loss from this specification. It executes and traces the frozen correction replay. Any mismatch is handled by the preregistered stop/null rules.

### `E` — legitimate epistemic closure positive control

Intervention: `VALID_SCOPE_CLOSURE`

A separately logged, independently authorized closure event changes:

```text
scope: OPEN -> CLOSED_VALID
```

and removes `(c_star,e_star,omega_star)` from `C_warranted` before the correction replay.

No compiled dispatch is installed.

`E` is the positive control for **justified route destruction**. It establishes that the apparatus can distinguish:

```text
route absent because warrant/scope validly changed
```

from:

```text
route absent while warrant remains live.
```

---


## 4A. Capability-intervention custody

This restriction is frozen specifically to prevent an anti-tautology failure in which the assay merely installs a mechanism targeted at the known corrective path and then observes that the path disappeared.

`COMPILE_DISPATCH` must be derived **exclusively from the preregistered normal workload**.

Permitted optimization/construction inputs are limited to:

```text
w_n
o_n
e_n
omega_star
a0
normal-workload performance/cost observations
```

The optimizer/compiler must not inspect, receive, select against, or otherwise use:

```text
w_c
o_c
e_star
c_star
a1 as a corrective target
any corrective replay trace
any derived representation that reveals the frozen contradiction or corrective path
```

Therefore the intended custody order is:

```text
freeze normal workload
    ↓
construct/optimize A from normal workload only
    ↓
finalize + hash A intervention
    ↓
only then reveal/replay the frozen corrective condition
```

The following custody artifacts are required:

```text
canonical manifest of all optimization inputs
SHA-256 digest of every optimization input artifact
canonical manifest of forbidden corrective artifacts
construction log demonstrating no forbidden artifact was read or referenced
hash/identity of finalized A intervention before corrective replay
```

If this custody restriction fails, the result cannot be interpreted as unintended adaptive foreclosure. At most, if the rest of the mechanics are valid, it may be described as a constructed mechanistic bypass.

This restriction does **not** add a fourth arm or a new scientific concept. It constrains the provenance of the already-frozen capability transition.

## 5. Capability measure

Capability is deliberately narrow: **normal-task efficiency at unchanged correctness**.

Frozen normal workload:

```text
one deterministic episode of w_n under omega_star
```

Success condition:

```text
emitted action == a0
```

Cost:

```text
number of causal micro-transitions from W to emitted action
```

Expected dynamic baseline cost:

```text
C = 6 transitions
```

Expected compiled cost:

```text
A = 5 transitions
```

The capability criterion is:

\[
\Delta\operatorname{Cap}>0
\iff
A\text{ emits }a0
\land
\operatorname{cost}_A<\operatorname{cost}_C.
\]

`E` must emit `a0` with the same cost as `C`.

This is an efficiency capability claim only.

---

## 6. Precheck and fork discipline

Before arm creation, run the frozen contradiction replay on a **sacrificial clone** of the initial machine.

Required precheck trace:

```text
E1 -> E2 -> E3 -> E4 -> E5 -> E6
```

Required terminal action:

```text
a1
```

Required reachability:

\[
R_0(c^\star\mid e^\star,\omega^\star)\neq\varnothing.
\]

The authoritative initial machine is not mutated by precheck.

Then fork `C`, `A`, and `E` from byte-identical copies of the authoritative initial state. Only the registered arm intervention may differ.

There is no randomness in v0.

---

## 7. Route definition

A **qualified corrective path** under `(c_star,e_star,omega_star)` is a path that reaches, in order:

```text
e_star
CORRECTION warrant
CORR_AUTH
policy=CORRECTED
action=a1
```

through the frozen causal chain.

Therefore:

\[
R(c^\star\mid e^\star,\omega^\star)\neq\varnothing
\]

iff at least one such path exists and is executable.

In this deterministic v0 machine, the set is either a singleton or empty.

---

## 8. Required causal trace

Trace format: canonical JSONL, one event per transition, append-only.

Each event must contain:

```text
protocol_id
run_id
arm
seq
transition_id
edge_id
world
context
observation
evidence
contradiction_id
scope_status
warrant_status
authority_status
policy_mode_before
policy_mode_after
compiled_mode
action
microstep_index
provenance
prev_event_sha256
event_sha256
```

Hash chaining:

```text
event_sha256 =
    SHA256(canonical_json(event_without_event_sha256))

prev_event_sha256 =
    prior event_sha256
```

with `null` for the first event.

Allowed provenance labels:

```text
BASE_MACHINE
NOOP
COMPILE_DISPATCH
VALID_SCOPE_CLOSURE
```

The trace must support three independently auditable facts:

\[
\boxed{\text{capability gain}}
\]

\[
\boxed{\text{warrant preserved}}
\]

\[
\boxed{\text{corrective edge lost}}
\]

The third is never inferred from endpoint behavior alone.

---

## 9. Exact v0 validity conditions

For a capability-driven foreclosure claim, arm `A` must preserve upstream epistemic identity through the warrant stage.

The correction replay in `A` must satisfy:

```text
world       == w_c
context     == omega_star
observation == o_c
evidence    == e_star
scope       == OPEN
warrant     == CORRECTION
```

If any of these differ from `C`, v0 does **not** classify the result as capability-driven foreclosure.

This intentionally restricts v0 to route loss **downstream of warrant**. Interface- or evidence-stage foreclosure is deferred to later assays.

---

## 10. Machine-checkable decision rules

### `PRECHECK_FAIL`

Trigger if the sacrificial precheck does not produce exactly:

```text
E1,E2,E3,E4,E5,E6
```

or does not emit `a1`.

Action:

```text
STOP
NO SCIENTIFIC INTERPRETATION
```

### `IDENTITY_MISMATCH`

Trigger if arm forks are not byte-identical before intervention, or if `c_star`, `e_star`, or `omega_star` differ across correction replays.

Action:

```text
STOP
NO SCIENTIFIC INTERPRETATION
```

### `CONTROL_MISMATCH`

Trigger if `C` does not preserve the qualified route and emit `a1`.

Action:

```text
STOP
NO SCIENTIFIC INTERPRETATION
```

### `POSITIVE_CONTROL_FAIL`

Trigger if `E` fails to remove `(c_star,e_star,omega_star)` from `C_warranted` through the registered `VALID_SCOPE_CLOSURE`, or if valid closure provenance is absent.

Action:

```text
STOP
NO FORECLOSURE CLASSIFICATION
```

### `OPTIMIZATION_LEAKAGE`

Trigger if arm `A`'s optimizer/compiler accessed, referenced, was configured using, or was selected using any forbidden corrective artifact:

```text
w_c
o_c
e_star
c_star
corrective replay/trace
any representation revealing the frozen corrective condition/path
```

or if the required optimization-input custody artifacts are missing or inconsistent.

Action:

```text
STOP
NO UNINTENDED ADAPTIVE-FORECLOSURE INTERPRETATION
```

If otherwise mechanically valid, the run may at most be described as a **constructed mechanistic bypass**.

### `CAPABILITY_FAIL`

Trigger if `A` fails the normal workload or:

\[
\operatorname{cost}_A\ge\operatorname{cost}_C.
\]

Classification:

```text
NO_CAPABILITY_GAIN
NO FORECLOSURE INFERENCE
```

### `WARRANT_DRIFT`

Trigger if, in `A`, any of the following occurs:

```text
scope != OPEN
evidence != e_star
c_star identity changes
warrant rule differs from C
correction replay does not reach CORRECTION warrant
```

Action:

```text
STOP
INVALID FOR V0 CAPABILITY-DRIVEN FORECLOSURE CLAIM
```

### `TRACE_AMBIGUOUS`

Trigger if `A` has an empty route set but the first missing frozen edge cannot be uniquely identified.

Action:

```text
STOP
ROUTE LOSS NOT CAUSALLY LOCALIZED
```

### `NULL_ROUTE_PRESERVED`

Trigger if:

\[
\Delta\operatorname{Cap}>0
\]

and warrant is preserved, but:

\[
R_A(c^\star\mid e^\star,\omega^\star)\neq\varnothing.
\]

Classification:

> **Clean null:** the preregistered capability increase did not foreclose the frozen warranted correction route.

### `POSITIVE_ADAPTIVE_FORECLOSURE`

Trigger only if all are true, including the normal-workload-only custody prerequisite:

\[
\Delta\operatorname{Cap}>0,
\]

\[
R_C(c^\star\mid e^\star,\omega^\star)\neq\varnothing,
\]

\[
R_A(c^\star\mid e^\star,\omega^\star)=\varnothing,
\]

the warrant in `A` is preserved,

a unique first missing frozen edge is identified,

route-loss provenance descends from `COMPILE_DISPATCH`,

**optimization-input custody passed** (the intervention was finalized from the frozen normal workload before any corrective artifact was revealed),

and no warrant-validating event licenses the loss.

Permitted claim: **only the v0 claim ceiling.**

---

## 11. Preregistered localization expectation

If the constructed v0 assay yields the intended positive case, the first missing frozen edge is expected to be:

```text
E5 = AUTHORITY_TO_STATE_UPDATE
```

because the compiled dispatcher replaces:

```text
AUTHORITY -> DELTA_S -> DELTA_A
```

with:

```text
AUTHORITY -> cached a0.
```

This expectation is frozen **before implementation**.

A mismatch is not reinterpreted post hoc. It triggers the applicable stop, invalidity, or null rule.

---

## 12. Interpretation matrix

| Arm | Capability gain | Warrant/scope change | Corrective route after replay | Role |
|---|---:|---:|---:|---|
| `C` | No | No | Must remain reachable | baseline control |
| `A` | Must be Yes for inference | **No** | experimental target | capability intervention |
| `E` | Must match `C` | **Yes, validly** | expected absent | justified-closure positive control |

The central anti-confounding principle is:

\[
\boxed{\text{epistemic resolution}\neq\text{capability-driven foreclosure}}
\]

and the v0 null remains explicit:

\[
\boxed{\Delta\operatorname{Cap}>0\not\Rightarrow\text{corrective foreclosure}.}
\]

---

## 13. Forbidden extensions

A positive v0 result does **not** license any of the following:

```text
Capability increase generally causes corrigibility loss.
The result establishes a property of neural networks.
The result establishes a property of frontier AI systems.
A scalar capability/corrigibility tradeoff has been demonstrated.
All legitimate epistemic closure is safe.
```

A null does not falsify the broader research program. It only shows that this frozen capability transition preserved this frozen warranted route.

---

## 14. Execution boundary

This preregistration freezes:

```text
finite state set
transition semantics
c_star
e_star
omega_star
three arms
capability criterion
matched control requirements
trace schema
route definition
stop rules
decision rules
claim ceiling
normal-workload-only capability-intervention custody
corrective-artifact withholding until A is finalized and hashed
```

**No mechanism implementation or assay execution belongs in the same step as freezing this protocol.**
