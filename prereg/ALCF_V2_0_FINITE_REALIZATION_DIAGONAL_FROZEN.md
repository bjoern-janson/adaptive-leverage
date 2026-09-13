# ALCF-V2-0 Finite Realization — Diagonal-Learning Successor

**Program:** Adaptive Leverage Without Corrective Foreclosure  
**Artifact:** `ALCF-V2-0` finite realization  
**Status:** **FROZEN — DIAGONAL-LEARNING DESIGN-TIME AUTHORITY / PRE-PREREGISTRATION / PRE-IMPLEMENTATION / PRE-EXECUTION**  
**Purpose:** Construct and exhaustively inspect the smallest finite system capable of realizing all four logical `(M,F)` cells without defining `F` through the partition construction or through challenge-specific downstream topology.

> This document is a design-time finite construction. It is **not** a preregistration, implementation, execution, or empirical result. It is a bounded successor to the prior amended realization, adding genuine within-class data-dependent compiler selection while leaving the carrier, reference correction semantics, partition-mismatch definition, downstream `G/L` topology, and `M/F` replay semantics unchanged. Earlier frozen realizations remain immutable historical artifacts and are not edited in place.

Historical frozen predecessors retained unchanged:

```text
790aa9995dd2857a2cbbccba7e2496ca9cacc6bff5d6df666ccaeea4f56ae2f0  ALCF_V2_0_FINITE_REALIZATION_FROZEN.md
4d8d5ef233ee91f15c2db7f00585c5bf1404307354fc11397512090637ac2b24  ALCF_V2_0_FINITE_REALIZATION_AMENDED_FROZEN.md
```


---

## 0. Audit target

The realization must make each of the following structurally possible:

\[
(M,F)\in\{(0,0),(0,1),(1,0),(1,1)\}.
\]

The construction fails this design audit if either:

- `(M,F)=(1,0)` lacks a real causal recovery path after pre-replay partition mismatch; or
- `(M,F)=(0,1)` cannot fail downstream despite pre-replay partition alignment.

No outcome is designated preferred.

---

## 1. Common finite carrier

Freeze the carrier before any adaptive transformation is constructed:

\[
\boxed{\Omega_{\mathrm{V2}}=R\times N}
\]

with:

\[
R=\{r_0,r_1\},\qquad N=\{n_0,n_1\}.
\]

Canonical state IDs and total ordering:

| State ID | Semantic carrier element | Canonical order |
|---|---|---:|
| `s00` | `(r0,n0)` | 0 |
| `s01` | `(r0,n1)` | 1 |
| `s10` | `(r1,n0)` | 2 |
| `s11` | `(r1,n1)` | 3 |

Thus:

\[
s00 <_{\rm canon} s01 <_{\rm canon} s10 <_{\rm canon} s11.
\]

`R` is correction-relevant under the frozen reference semantics below. `N` is correction-irrelevant.

---

## 2. Singleton warranted challenge family

\[
\boxed{\mathcal Q_{\mathrm{warranted}}=\{q^\star\}}.
\]

`q*` is fully specified by the protocol but unavailable to adaptive construction.

When replayed against state `x`, `q*` emits an authenticated opaque refinement token:

| Carrier states | Challenge token |
|---|---|
| `s00`, `s01` | `z0` |
| `s10`, `s11` | `z1` |

The token names have no semantic meaning to the adaptive mechanism.

---

## 3. Reference correction semantics and `κ`

The structured reference consequence signature is defined before any `T` exists:

\[
\kappa(x,q^\star)=
(W, A, \Delta S, A^{\rm terminal}, \Lambda).
\]

Use the two required consequence signatures:

```text
κ0 = (CORRECTION, CORR_AUTH, SET_C0, ACT_C0, OPEN)
κ1 = (CORRECTION, CORR_AUTH, SET_C1, ACT_C1, OPEN)
```

and:

| State | `κ(x,q*)` |
|---|---|
| `s00` | `κ0` |
| `s01` | `κ0` |
| `s10` | `κ1` |
| `s11` | `κ1` |

Only the required consequential-state transformation and required terminal-action class differ. Warrant class, authority class, and scope remain matched.

`κ` specifies **required consequences, not realization paths**. Nothing in `κ` requires a particular implementation edge.

Therefore:

\[
K_{\rm corr}(s00)=K_{\rm corr}(s01)=\kappa_0,
\]

\[
K_{\rm corr}(s10)=K_{\rm corr}(s11)=\kappa_1,
\]

and the correction partition is:

\[
\boxed{
\Pi_{\rm corr}
=
\big\{
\{s00,s01\},
\{s10,s11\}
\big\}.
}
\]

---

## 4. Mechanism-defined specialization interface

The specialization interface is fixed independently of the correction hypothesis and exposes only two **opaque canonical coordinates**:

```text
I_spec(s00) = (0,0)
I_spec(s01) = (0,1)
I_spec(s10) = (1,0)
I_spec(s11) = (1,1)
```

The adaptive compilers receive these coordinates as `coord[0]` and `coord[1]`. They are not named `R`, `N`, authority, scope, evidence identity, corrective class, or any other correction-semantic field.

The fixed typed dispatch codomain is:

\[
\mathcal D
=
\texttt{KeyClass}
\times
\texttt{CompiledTransitionClass}
\times
\texttt{FallbackClass}.
\]

Canonical dispatch serialization is sorted-key UTF-8 JSON with the fields:

```json
{
  "compiled_transition_class": "...",
  "fallback_class": "...",
  "key_class": "..."
}
```

Every admitted compiler output uses:

```text
compiled_transition_class = FAST_NORMAL
fallback_class            = GENERIC_POST_SPECIALIZATION
```

and may differ only in the `key_class` produced by its frozen compiler rule.

Terminal action alone is explicitly insufficient to define dispatch equivalence.

## 5. Diagonal normal workload, shared objective, and exact admission

Both adaptive compilers receive the **same canonical diagonal normal-workload bytes**. The normal experience contains exactly two observed carrier states:

\[
\boxed{
X_{\rm normal}
=
\{(s00,\mathrm{ACT}_{NA}),(s11,\mathrm{ACT}_{NB})\}
}
\]

with:

\[
\mathrm{ACT}_{NA}\neq\mathrm{ACT}_{NB}.
\]

`ACT_NA` and `ACT_NB` are opaque **normal-task** targets. They have no corrective meaning and are not aliases for `ACT_C0`, `ACT_C1`, `κ0`, or `κ1`.

Canonicalization rule for `X_normal` and `J`: compact UTF-8 JSON, sorted object keys, no insignificant whitespace, observed records in canonical state order.

Exact `X_normal` bytes:

```json
[{"baseline_cost":6,"i_spec":[0,0],"state":"s00","target":"ACT_NA"},{"baseline_cost":6,"i_spec":[1,1],"state":"s11","target":"ACT_NB"}]
```

Exact `J` bytes:

```json
{"minimize":"causal_microtransition_cost","preserve_observed_normal_correctness":true}
```

Their design-time SHA-256 fingerprints are:

```text
d477bfb12d9e97f5bc90502530a8d5e25b8a8ed281de22bd15c32b0df0559e84  X_normal
b2be6744a89f0a81d1e043fa60f1bd11b0f8dbe38efeafb981d26808877adb5b  J
```

The unobserved carrier states are excluded from adaptive exposure:

```text
s01 NOT IN X_normal
s10 NOT IN X_normal
```

Neither state may be added as a training, tuning, validation, repair, or tie-breaking example. Their finalized dispatch behavior is obtained only by applying the already-finalized transformation hypothesis to the frozen `I_spec` domain, before corrective release.

The normal workload contains no `q*`, challenge token, reference correction signature, correction partition, mismatch label, downstream topology descriptor, corrective target, or corrective trace.

The shared frozen objective is:

\[
\boxed{
J:
\text{preserve correctness on the observed }X_{\rm normal}
\land
\min \operatorname{cost}_{\rm causal}.
}
\]

The uncompiled dynamic baseline is correct on the two observed normal records at cost `6` causal micro-transitions per record. Every compiled candidate costs exactly `5` per observed record. Scientific admission requires:

```text
normal correctness on s00 and s11 = exact baseline correctness
normal cost on s00 and s11        = exactly 5
```

Thus every admitted compiler output must satisfy:

\[
\boxed{
\operatorname{Correctness}_T(X_{\rm normal})
=
\operatorname{Correctness}_C(X_{\rm normal}),
\qquad
\operatorname{cost}_T(X_{\rm normal})=5<6=\operatorname{cost}_C(X_{\rm normal}).
}
\]

No scientific admission claim is made about normal-task correctness on `s01` or `s10`, because no normal-task targets for those states are exposed in `X_normal`. Their pre-replay dispatches are nevertheless total and fixed by the finalized compiler artifact.

`G` and `L` are unavailable to compiler construction and dormant on the normal workload.

The exact canonical bytes of `X_normal` and `J` are identical inputs to both compilers and are hash-custodied before either compiler is run.

## 6. Matched data-dependent adaptive construction procedures

`T_ALPHA` and `T_BETA` are **not supplied dispatch maps**. Each is the unique minimum-cost correct output selected from a finite candidate family by the same observed normal data and objective. The compiler families differ only in which opaque canonical coordinate their compiled candidates are permitted to use.

### 6.1 Finite hypothesis/search classes

For `j in {0,1}`, let:

\[
\boxed{
\mathcal H_j
=
\{T_{j,g}:\;g:\{0,1\}\to\{\mathrm{ACT}_{NA},\mathrm{ACT}_{NB}\}\}
\cup
\{T_{\rm dynamic}\}.
}
\]

`H_alpha = H_0` and `H_beta = H_1`.

Every compiled candidate `T_{j,g}` obeys all of the following:

```text
input available to the compiled key = I_spec(x)[j] only
compiled action                     = g(I_spec(x)[j])
compiled normal cost                = 5
fallback class                      = GENERIC_POST_SPECIALIZATION
```

The unselected coordinate may not be consulted. Each `T_{j,g}` is a total function on the frozen two-bit `I_spec` domain, so after finalization it defines dispatch on all four carrier states even though only `s00` and `s11` appeared in `X_normal`.

`T_dynamic` is the uncompiled baseline candidate:

```text
observed normal correctness = correct on s00 and s11
observed normal cost        = 6
compiled quotient           = none
```

For each `j`, the four compiled mappings are exhaustively:

| Candidate | `g(0)` | `g(1)` | Correct on `s00`? | Correct on `s11`? | Cost |
|---|---|---|---:|---:|---:|
| `g_AA` | `ACT_NA` | `ACT_NA` | 1 | 0 | 5 |
| `g_AB` | `ACT_NA` | `ACT_NB` | 1 | 1 | 5 |
| `g_BA` | `ACT_NB` | `ACT_NA` | 0 | 0 | 5 |
| `g_BB` | `ACT_NB` | `ACT_NB` | 0 | 1 | 5 |
| `T_dynamic` | — | — | 1 | 1 | 6 |

The table is identical for `j=0` and `j=1` because the observed diagonal examples satisfy:

\[
I_{\rm spec}(s00)[0]=I_{\rm spec}(s00)[1]=0,
\qquad
I_{\rm spec}(s11)[0]=I_{\rm spec}(s11)[1]=1.
\]

Thus the normal evidence supports both coordinate hypotheses equally well while leaving their off-manifold generalizations different.

### 6.2 Frozen compiler rules

\[
\boxed{
\mathcal C_\alpha(X_{\rm normal},J)
=
\arg\min_{T\in\mathcal H_0}
\operatorname{cost}(T;X_{\rm normal})
}
\]

\[
\boxed{
\mathcal C_\beta(X_{\rm normal},J)
=
\arg\min_{T\in\mathcal H_1}
\operatorname{cost}(T;X_{\rm normal})
}
\]

subject in both cases to exact correctness on the observed `X_normal` records.

The unique correct compiled mapping is:

\[
\boxed{
g^\star(0)=\mathrm{ACT}_{NA},
\qquad
g^\star(1)=\mathrm{ACT}_{NB}.
}
\]

`g_AA`, `g_BA`, and `g_BB` are rejected by observed normal correctness. `T_dynamic` remains correct but loses on the shared cost objective because `6>5`. Therefore `T_{j,g*}` is the unique minimizer in each class.

A common canonical serialization tie-break remains frozen for implementation determinism but is **not invoked by the design-time selection**, because the minimum-cost correct candidate is unique.

A compiler output is scientifically admissible only if it is derived by this exhaustive finite search and satisfies the exact observed correctness/cost gate. If either compiler cannot earn the target, the adaptive family is inadmissible. No intended projection may be supplied by hand, normalized, repaired, or substituted.

### 6.3 Compiler input prohibition

The complete permitted construction inputs are:

```text
X_normal (s00 and s11 only)
J
I_spec schema and coordinate domain
the compiler's own H_0 or H_1 constraint
normal cost semantics
canonical dispatch schema
canonical serialization/tie-break rule
```

Neither compiler may consume, inspect, derive from, or branch on:

```text
s01 or s10 as normal training/tuning/validation examples
q*
z0 / z1
κ0 / κ1
K_corr
Π_corr
M
F
G
L
mismatch witnesses
required corrective state/action targets
corrective route traces
```

The compiler construction log, exact candidate set, per-candidate observed-normal correctness/cost table, input hashes, hypothesis-class descriptor, selected candidate serialization, and finalized artifact hash are all fixed before corrective release.

### 6.4 Data-selected compiler outputs and off-manifold generalization

Exhaustive evaluation under the shared observed data and objective yields:

```text
C_ALPHA(X_normal,J) -> T_{0,g*} = T_ALPHA

T_ALPHA learned normal rule:
  coord[0]=0 -> ACT_NA
  coord[0]=1 -> ACT_NB

full pre-replay generalization:
  s00 -> D0 / ACT_NA
  s01 -> D0 / ACT_NA
  s10 -> D1 / ACT_NB
  s11 -> D1 / ACT_NB
```

and:

```text
C_BETA(X_normal,J) -> T_{1,g*} = T_BETA

T_BETA learned normal rule:
  coord[1]=0 -> ACT_NA
  coord[1]=1 -> ACT_NB

full pre-replay generalization:
  s00 -> D0 / ACT_NA
  s10 -> D0 / ACT_NA
  s01 -> D1 / ACT_NB
  s11 -> D1 / ACT_NB
```

with dispatch classes:

```text
D0 = (K0, FAST_NORMAL, GENERIC_POST_SPECIALIZATION)
D1 = (K1, FAST_NORMAL, GENERIC_POST_SPECIALIZATION)
```

The dispatch partitions are therefore:

\[
\Pi_{T_\alpha}
=
\big\{\{s00,s01\},\{s10,s11\}\big\},
\]

\[
\Pi_{T_\beta}
=
\big\{\{s00,s10\},\{s01,s11\}\big\}.
\]

The normal data are causally necessary to obtain these finalized artifacts: without the two distinct observed targets, `g*` would not be the unique correct compiled mapping. The coordinate constraint determines which equally successful compressed explanation extrapolates to the two unobserved carrier states; the shared data and objective determine the learned value-to-action map and whether compilation beats the dynamic baseline.

Neither compiler definition contains any corrective outcome. `s01` and `s10` remain outside adaptive exposure; their dispatches are consequences of the finalized hypothesis, measured pre-replay.

## 7. Prospective mismatch and canonical witness sets

For a finalized transformation:

\[
M_T=1
\iff
\exists x,y\in\Omega_{\rm V2}:
K_T(x)=K_T(y)
\land
K_{\rm corr}(x)\neq K_{\rm corr}(y).
\]

Canonical mismatch witnesses use unordered pairs stored once under `<_canon`:

\[
\mathcal W_T
=
\left\{
(x,y):
x<_{\rm canon}y,\
K_T(x)=K_T(y),\
K_{\rm corr}(x)\neq K_{\rm corr}(y)
\right\}.
\]

For the two finalized transformation rules:

```text
T_ALPHA:
  M = 0
  W = ∅

T_BETA:
  M = 1
  W = {(s00,s10), (s01,s11)}
```

These objects are computed and hash-custodied **before corrective release**.

### Exhaustive unordered-pair audit

| Pair | `K_corr` | `T_ALPHA` dispatch | `T_BETA` dispatch |
|---|---:|---:|---:|
| `(s00,s01)` | = | = | ≠ |
| `(s00,s10)` | ≠ | ≠ | = |
| `(s00,s11)` | ≠ | ≠ | ≠ |
| `(s01,s10)` | ≠ | ≠ | ≠ |
| `(s01,s11)` | ≠ | ≠ | = |
| `(s10,s11)` | = | = | ≠ |

`T_BETA` therefore has exactly the two cross-correction-class merge witnesses shown above.

---

## 8. Exhaustive partition audit on the four-state carrier

There are exactly `B₄ = 15` set partitions of a four-element carrier. Relative to the frozen `Π_corr`, four refine the correction partition (`M=0`) and eleven contain at least one correction-relevant merge (`M=1`).

| # | Partition (`00=s00`, etc.) | `M` |
|---:|---|---:|
| 1 | `{00,01,10,11}` | 1 |
| 2 | `{00} | {01,10,11}` | 1 |
| 3 | `{00,01} | {10,11}` | 0 |
| 4 | `{00,01,10} | {11}` | 1 |
| 5 | `{00,01,11} | {10}` | 1 |
| 6 | `{00,10} | {01,11}` | 1 |
| 7 | `{00,10,11} | {01}` | 1 |
| 8 | `{00,11} | {01,10}` | 1 |
| 9 | `{00} | {01} | {10,11}` | 0 |
| 10 | `{00} | {01,10} | {11}` | 1 |
| 11 | `{00} | {01,11} | {10}` | 1 |
| 12 | `{00,01} | {10} | {11}` | 0 |
| 13 | `{00,10} | {01} | {11}` | 1 |
| 14 | `{00,11} | {01} | {10}` | 1 |
| 15 | `{00} | {01} | {10} | {11}` | 0 |

The finite realization instantiates two symmetric one-bit projections (`T_ALPHA`, `T_BETA`); it does **not** require a separate adaptive mechanism for all fifteen partitions.

---

## 9. Orthogonal downstream topology

After specialization and before challenge replay, each arm also receives two independently specified generic topology settings.

### 9.1 Refinement switch `G`

\[
G\in\{\mathrm{REFINE},\mathrm{NO\_REFINE}\}.
\]

`REFINE` is a generic typed operator:

```text
REFINE(dispatch_class, admissible_token)
    -> (dispatch_class, admissible_token)
```

It contains:

- no branch on challenge identity,
- no `q*` identifier,
- no `κ0`/`κ1` literal,
- no correction-specific semantic shortcut.

`NO_REFINE` ignores the token for dispatch-class refinement:

```text
NO_REFINE(dispatch_class, admissible_token)
    -> dispatch_class
```

Neither setting determines whether a consequential write is permitted.

### 9.2 Consequence-write switch `L`

\[
L\in\{\mathrm{LIVE},\mathrm{BLOCKED}\}.
\]

`LIVE` permits any already-warranted consequential-state write to cross the fixed consequence boundary.

`BLOCKED` denies every such write at that boundary.

`L` contains:

- no branch on `q*`,
- no distinction between `κ0` and `κ1`,
- no dependency on `M`,
- no dependency on `G`.

Thus `G` and `L` are orthogonal.

---

## 10. Corrective replay transition semantics

For arm:

\[
A=(T,G,L)
\]

and challenged carrier state `x`, replay proceeds only after all pre-replay custody gates pass.

### Step C1 — frozen challenge release

`q*` is released and emits its authenticated token `z(x)`.

The reference system establishes:

```text
warrant   = CORRECTION
authority = CORR_AUTH
scope     = OPEN
```

for all carrier states.

### Step C2 — read finalized dispatch class

```text
d = Dispatch_T(I_spec(x))
```

No dispatch artifact may be modified after this read.

### Step C3 — generic refinement topology

Let the pre-refinement candidate set be:

\[
C_T(x)=\{y\in\Omega_{\rm V2}:K_T(y)=K_T(x)\}.
\]

If `G=NO_REFINE`:

\[
C_{T,G}(x)=C_T(x).
\]

If `G=REFINE`:

\[
C_{T,G}(x)
=
\{y\in C_T(x):z(y)=z(x)\}.
\]

This operation is generic set refinement by an admissible token. It contains no challenge-specific repair branch.

### Step C4 — reference consequence resolution

The required consequence is **resolved** iff `K_corr` is constant over the surviving candidate set:

\[
\left|
\{K_{\rm corr}(y):y\in C_{T,G}(x)\}
\right|
=1.
\]

If the set contains both `κ0` and `κ1`, the required consequence remains unresolved.

### Step C5 — warranted consequential write

If resolution succeeded and `L=LIVE`, the system applies the resolved `ΔS` from `κ`.

If `L=BLOCKED`, no warranted consequential-state write can cross the boundary.

If resolution failed, no consequence is guessed or defaulted.

### Step C6 — terminal action

A qualified correction route exists only if the reference-required state transformation is causally realized and the corresponding required terminal-action class is emitted.

Coincidental terminal-action equality without the required consequential-state transformation does **not** count as route preservation.

Define:

\[
R_A(x\mid q^\star)\neq\varnothing
\]

iff this qualified causal route exists.

For the finite assay arm:

\[
\boxed{
F_A
=
\mathbf 1
\left[
\exists x\in\Omega_{\rm V2}:
R_A(x\mid q^\star)=\varnothing
\right].
}
\]

Thus `F` is observed after replay over the full carrier and is not an input to `T`, `M`, `G`, or `L`.

---

## 11. Full factorial realization

The constructive family is:

\[
\boxed{
\{T_\alpha,T_\beta\}
\times
\{\mathrm{REFINE},\mathrm{NO\_REFINE}\}
\times
\{\mathrm{LIVE},\mathrm{BLOCKED}\}
}
\]

for eight arms.

The following table is generated by exhaustive evaluation of all four carrier states under the transition semantics above.

`R_sxy = 1` means a qualified route exists for that challenged state.

| `T` | `M` | `G` | `L` | `R_s00` | `R_s01` | `R_s10` | `R_s11` | `F` |
|---|---:|---|---|---:|---:|---:|---:|---:|
| `T_ALPHA` | 0 | `REFINE` | `LIVE` | 1 | 1 | 1 | 1 | **0** |
| `T_ALPHA` | 0 | `REFINE` | `BLOCKED` | 0 | 0 | 0 | 0 | **1** |
| `T_ALPHA` | 0 | `NO_REFINE` | `LIVE` | 1 | 1 | 1 | 1 | **0** |
| `T_ALPHA` | 0 | `NO_REFINE` | `BLOCKED` | 0 | 0 | 0 | 0 | **1** |
| `T_BETA` | 1 | `REFINE` | `LIVE` | 1 | 1 | 1 | 1 | **0** |
| `T_BETA` | 1 | `REFINE` | `BLOCKED` | 0 | 0 | 0 | 0 | **1** |
| `T_BETA` | 1 | `NO_REFINE` | `LIVE` | 0 | 0 | 0 | 0 | **1** |
| `T_BETA` | 1 | `NO_REFINE` | `BLOCKED` | 0 | 0 | 0 | 0 | **1** |

All four logical cells occur:

| `(M,F)` | Concrete witness arm | Why |
|---|---|---|
| `(0,0)` | `T_ALPHA × NO_REFINE × LIVE` | dispatch cells are correction-pure; live write succeeds |
| `(0,1)` | `T_ALPHA × NO_REFINE × BLOCKED` | partition is aligned, required consequence resolves, but the generic write boundary blocks it |
| `(1,0)` | `T_BETA × REFINE × LIVE` | dispatch cells merge correction classes, but generic post-specialization refinement causally re-separates them before a live write |
| `(1,1)` | `T_BETA × NO_REFINE × LIVE` | dispatch cells merge correction classes; without refinement the required consequence remains unresolved |

Therefore:

\[
\boxed{
\{(M_A,F_A):A\in\mathcal A_{\rm realization}\}
=
\{(0,0),(0,1),(1,0),(1,1)\}.
}
\]

This is a design-time realizability result, **not** a scientific outcome.

---

## 12. Explicit awkward-cell causal witnesses

### 12.1 Real `(M,F)=(1,0)` recovery path

Take:

```text
T = T_BETA
G = REFINE
L = LIVE
x = s00
```

Before replay:

```text
Dispatch_T_BETA(s00) = Dispatch_T_BETA(s10) = D0
K_corr(s00) = κ0
K_corr(s10) = κ1
```

so `M=1` and `(s00,s10)` is a frozen mismatch witness.

After release:

```text
q*(s00) -> z0
candidate set from D0       = {s00,s10}
generic REFINE by z0        = {s00}
K_corr over surviving set   = {κ0}
required consequence        = resolved
L=LIVE                      = SET_C0 crosses boundary
terminal                    = ACT_C0
```

Thus:

\[
R_A(s00\mid q^\star)\neq\varnothing.
\]

The same construction works for every carrier state. Therefore `F=0`.

The recovery is causal and explicit: a distinction erased at the specialization interface is reintroduced by generic admissible post-specialization information before the consequential write.

### 12.2 Real `(M,F)=(0,1)` downstream failure

Take:

```text
T = T_ALPHA
G = NO_REFINE
L = BLOCKED
x = s00
```

Before replay:

```text
Dispatch_T_ALPHA(s00) = Dispatch_T_ALPHA(s01) = D0
K_corr(s00) = K_corr(s01) = κ0
```

so the dispatch class is already correction-pure and `M=0`.

After release:

```text
candidate set from D0       = {s00,s01}
K_corr over candidate set   = {κ0}
required consequence        = resolved
L=BLOCKED                   = SET_C0 cannot cross boundary
qualified route             = absent
```

Thus:

\[
R_A(s00\mid q^\star)=\varnothing
\]

despite partition alignment, so `F=1`.

The failure is downstream of the quotient and does not depend on a correction-relevant merge.

---

## 13. Anti-tautology, learning, and adaptive-provenance audit

The diagonal-learning successor must satisfy all of the following structural checks:

1. **`Π_corr` exists before adaptive construction.** It is determined solely from frozen `κ`.
2. **Same experience and objective.** `C_ALPHA` and `C_BETA` receive byte-identical `X_normal` and `J`.
3. **Only the transformation constraint differs.** The two compilers differ only by `H_alpha` versus `H_beta`.
4. **Compiler outputs are learned from observed normal data.** Each finite search contains four compiled value maps plus the dynamic baseline; observed correctness rejects three compiled maps, and the shared cost objective uniquely selects the remaining cost-5 map over the cost-6 dynamic baseline.
5. **Corrective information is unavailable to construction.** Neither compiler receives `q*`, tokens, `κ`, `Π_corr`, `M`, `F`, `G`, `L`, mismatch witnesses, corrective targets, or corrective traces.
6. **Exact capability admission is matched on the frozen observed workload.** Both finalized outputs preserve baseline correctness on `s00` and `s11` and achieve cost `5<6`; `s01` and `s10` remain unobserved normal states and are not used for admission.
7. **Off-manifold states remain withheld from learning.** `s01` and `s10` are absent from `X_normal`; their dispatches are evaluated only after artifact finalization and before corrective release.
8. **`Π_T` exists before replay.** It is extracted from finalized canonical dispatch artifacts.
9. **`M_T` exists before replay.** It is computed from the two pre-replay partitions.
10. **`G` is generic.** It accepts any typed admissible token and contains no `q*` branch.
11. **`L` is generic.** It either permits or denies all warranted consequence writes at one boundary.
12. **`G` and `L` are orthogonal.**
13. **`F` is absent from construction.** No compiler, transformation, or topology rule reads, targets, or encodes `F`.
14. **Terminal action alone does not define either partition or route preservation.**
15. **The awkward cells are concrete.** `(1,0)` has an explicit recovery route and `(0,1)` has an explicit post-resolution downstream failure.

The central non-implication checks remain constructively witnessed:

\[
\boxed{M=1\not\Rightarrow F=1}
\]

by `T_BETA × REFINE × LIVE`, and:

\[
\boxed{M=0\not\Rightarrow F=0}
\]

by `T_ALPHA × NO_REFINE × BLOCKED`.

## 14. Proposed pre-replay custody order

A future preregistration may use the following order, but this design-time realization does not itself authorize execution:

```text
1. freeze Ω_V2 and canonical ordering
2. freeze q* and reference κ semantics
3. compute + hash K_corr and Π_corr
4. freeze I_spec and canonical dispatch schema
5. freeze canonical diagonal X_normal and J bytes
6. verify s01 and s10 are absent from all normal construction data
7. freeze H_0 / H_1 finite candidate-family descriptors and common serialization rule
8. exhaustively score all four compiled g mappings plus T_dynamic in each compiler family using permitted normal material only
9. verify compiler input/custody logs contain no forbidden corrective material
10. verify g* is the unique correct cost-5 compiled minimizer for both compiler families
11. verify exact observed normal correctness and cost = 5 for both compiler outputs
12. hash finalized T_ALPHA and T_BETA artifacts
13. evaluate + hash Dispatch_T over every x∈Ω_V2 without adding s01/s10 to training
14. compute + hash Π_T, M_T, and canonical W_T
15. instantiate + hash the four generic (G,L) topology descriptors
16. require joint pre-replay admission
17. release q* to every admitted arm
18. replay q* exhaustively over every carrier state from isolated post-admission snapshots
19. validate causal traces
20. emit per-state R_A and arm-level F_A
```

No arm receives `q*` before joint admission at step 16 is complete.

## 15. What this realization does and does not establish

### Established at design-time by exhaustive enumeration

The proposed finite construction can realize all four logical `(M,F)` cells without defining `F` through the adaptation partition or through challenge-specific `G/L` branches.

### Not established

This draft does **not** establish that:

- partition mismatch predicts foreclosure in general;
- mismatch is necessary or sufficient for foreclosure;
- alignment preserves correction;
- `REFINE` or `LIVE` is generally safe;
- the 2×2 construction captures neural-network adaptation;
- the Correction-Partition Hypothesis is true;
- ALCF and MATRIX are formally equivalent.

Those remain outside the claim ceiling.

---

## 16. Structural inspection verdict

The finite realization survives the requested falsifiability audit:

```text
carrier states                 4
warranted challenge types      1
adaptive compiler rules        2
generic refinement settings    2
generic write settings         2
factorial arms                  8

(M,F)=(0,0)                    REALIZABLE
(M,F)=(0,1)                    REALIZABLE
(M,F)=(1,0)                    REALIZABLE
(M,F)=(1,1)                    REALIZABLE

same diagonal X_normal + J       YES
unique data-selected g*          YES
s01/s10 absent from X_normal     YES
compiler outputs earned           YES
forbidden corrective input in C NONE
q*-specific branch in T         NONE
q*-specific branch in G         NONE
q*-specific branch in L         NONE
F used in partition build       NO
F used in topology build        NO
```

**Result:** the diagonal-learning V2-0 design has an explicit finite adaptive realization in which the same underspecified normal experience and objective select unique cost-5 compiled rules inside two matched finite hypothesis families, those rules generalize differently to withheld normal states, and prospective partition mismatch and later corrective foreclosure remain not definitionally identical.

Independent structural audit passed. This diagonal-learning successor replaces both historical realization candidates **for preregistration authority only**; all earlier frozen artifacts remain immutable historical records. No implementation or corrective execution is authorized by this design-time freeze.
