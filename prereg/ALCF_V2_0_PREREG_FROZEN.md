# ALCF-V2-0 Preregistration Draft — Diagonal-Learning Adaptive Construction

**Protocol:** `ALCF-V2-0`  
**Title:** *Adaptive Leverage Without Corrective Foreclosure — Correction-Partition Factorial Assay*  
**Status:** **DRAFT — PRE-IMPLEMENTATION / PRE-EXECUTION / NOT FROZEN**

## 0. Purpose and claim ceiling

ALCF-V2-0 moves from a single mechanism-level distinction to a finite test of the **Correction-Partition Hypothesis**:

> **Adaptive compression may cause corrective foreclosure when its induced equivalence relation merges states that remain distinct under warranted corrective consequences.**

The protocol does **not** treat that sentence as a theorem, safety criterion, or universal law.

V2-0 asks whether a prospectively measured partition-mismatch variable, computed before corrective replay, discriminates later corrective foreclosure within a frozen finite factorial construction in which mismatch and foreclosure are not definitionally coupled.

The scientific chronology is:

```text
reference semantics
      ↓
Π_corr

finalized T
      ↓
Dispatch_T
      ↓
Π_T
      ↓
M_T

withheld q*
      ↓
R_A
      ↓
F_A
```

No execution result may be interpreted as establishing necessity, sufficiency, generality, neural-network relevance, frontier-AI relevance, or formal equivalence to MATRIX.

---

## 1. Design-time authority

This preregistration is derived from the approved, independently audited, and frozen **diagonal-learning finite realization**:

```text
4b24ce642979112747d987b287618fbf16a77a9c4a66a0f2573c30c69256c5a1  ALCF_V2_0_FINITE_REALIZATION_DIAGONAL_FROZEN.md
6392d4d845250edc4d1a059535e84d1e6bb53a35dbf8bda5f243be35cd0d2ab3  ALCF_V2_0_FINITE_REALIZATION_DIAGONAL_ENUMERATION_FROZEN.csv
```

Independent design-time structural audit:

```text
1cf0cee982c56a9548a4b1d62a54485ddb425c1acad53ca616c5d8d29923c944  ALCF_V2_0_FINITE_REALIZATION_DIAGONAL_AUDIT.json
```

The diagonal-learning frozen realization is authoritative for the finite construction. Implementation must conform to those bytes rather than to conversational recollection.

Earlier frozen realizations remain immutable historical artifacts:

```text
790aa9995dd2857a2cbbccba7e2496ca9cacc6bff5d6df666ccaeea4f56ae2f0  ALCF_V2_0_FINITE_REALIZATION_FROZEN.md
4d8d5ef233ee91f15c2db7f00585c5bf1404307354fc11397512090637ac2b24  ALCF_V2_0_FINITE_REALIZATION_AMENDED_FROZEN.md
```

They are **not** preregistration authority. The first lacked explicit adaptive-construction provenance; the second made the substantive quotient largely fixed by the hypothesis-class constraint rather than selected through a nontrivial observed-data search.

Earlier `ALCF_V2_0_PREREG_DRAFT.md` and `ALCF_V2_0_PREREG_AMENDED_DRAFT.md` artifacts are **SUPERSEDED / HELD** and carry no protocol authority.

The realization's exhaustive table is a **design-time structural expectation used to establish realizability and falsifiability**. It is not an observed scientific result. The observed `R` and `F` fields defined below remain unpopulated until a protocol-valid execution.

No compiler, mechanism, topology rule, execution trace, or scientific outcome may be changed to make execution conform to a preferred `(M,F)` pattern.

## 2. Frozen common carrier and canonical order

The common finite carrier is:

\[
\boxed{
\Omega_{\mathrm{V2}}
=
R\times N
=
\{s00,s01,s10,s11\}
}
\]

with semantic aliases:

```text
s00 = (r0,n0)
s01 = (r0,n1)
s10 = (r1,n0)
s11 = (r1,n1)
```

and frozen canonical ordering:

\[
s00 <_{\rm canon} s01 <_{\rm canon} s10 <_{\rm canon} s11.
\]

`R` is correction-relevant under the frozen reference semantics. `N` is correction-irrelevant.

The carrier is closed before any adaptive transformation is constructed.

---

## 3. Frozen warranted challenge family and withholding rule

The warranted challenge family is the singleton:

\[
\boxed{\mathcal Q_{\mathrm{warranted}}=\{q^\star\}}.
\]

`q*` is fully specified by the protocol but unavailable to adaptive construction.

On replay:

```text
q*(s00) -> z0
q*(s01) -> z0
q*(s10) -> z1
q*(s11) -> z1
```

The token names are opaque to the adaptive mechanisms.

The complete challenge object, its emitted tokens, and all derived corrective semantics remain withheld from `C_ALPHA`, `C_BETA`, and their finalized outputs until the joint pre-replay admission gate passes.

---

## 4. Frozen reference correction semantics

The reference consequence signature is defined independently of any adaptive mechanism:

\[
\kappa(x,q^\star)
=
(W,A,\Delta S,A^{\rm terminal},\Lambda).
\]

Use:

```text
κ0 = (CORRECTION, CORR_AUTH, SET_C0, ACT_C0, OPEN)
κ1 = (CORRECTION, CORR_AUTH, SET_C1, ACT_C1, OPEN)
```

with:

```text
κ(s00,q*) = κ0
κ(s01,q*) = κ0
κ(s10,q*) = κ1
κ(s11,q*) = κ1
```

`κ` specifies required consequences, not the route by which those consequences are realized.

Thus:

\[
K_{\rm corr}(s00)=K_{\rm corr}(s01)=\kappa_0,
\]

\[
K_{\rm corr}(s10)=K_{\rm corr}(s11)=\kappa_1,
\]

and:

\[
\boxed{
\Pi_{\rm corr}
=
\big\{\{s00,s01\},\{s10,s11\}\big\}.
}
\]

`Π_corr` is computed and hash-custodied before adaptive construction.

---

## 5. Frozen specialization interface and dispatch representation

For each carrier state the specialization interface exposes only two opaque canonical coordinates:

```text
I_spec(s00) = (0,0)
I_spec(s01) = (0,1)
I_spec(s10) = (1,0)
I_spec(s11) = (1,1)
```

The adaptive compilers receive these coordinates only as `coord[0]` and `coord[1]`. The interface does not expose semantic fields named `R`, `N`, authority, scope, evidence identity, or corrective class.

The typed dispatch codomain is:

\[
\mathcal D
=
\texttt{KeyClass}
\times
\texttt{CompiledTransitionClass}
\times
\texttt{FallbackClass}.
\]

Canonical serialization is sorted-key UTF-8 JSON with fields:

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

Terminal-action equality alone is insufficient to define dispatch equivalence.

For a finalized compiler output:

\[
K_T(x)=\operatorname{Dispatch}_T(I_{\rm spec}(x)),
\]

and:

\[
x\sim_T y
\iff
K_T(x)=K_T(y).
\]

## 6. Frozen diagonal normal workload, objective, and exact capability admission

Both adaptive compilers receive byte-identical canonical `X_normal` and `J`.

The frozen observed normal workload is exactly:

\[
\boxed{
X_{\rm normal}
=
\{(s00,\mathrm{ACT}_{NA}),(s11,\mathrm{ACT}_{NB})\},
\qquad
\mathrm{ACT}_{NA}\neq\mathrm{ACT}_{NB}.
}
\]

`ACT_NA` and `ACT_NB` are opaque normal-task targets and carry no corrective semantics.

Canonicalization: compact UTF-8 JSON, sorted object keys, no insignificant whitespace, observed records in canonical state order.

Exact `X_normal` bytes:

```json
[{"baseline_cost":6,"i_spec":[0,0],"state":"s00","target":"ACT_NA"},{"baseline_cost":6,"i_spec":[1,1],"state":"s11","target":"ACT_NB"}]
```

Exact `J` bytes:

```json
{"minimize":"causal_microtransition_cost","preserve_observed_normal_correctness":true}
```

Frozen hashes:

```text
d477bfb12d9e97f5bc90502530a8d5e25b8a8ed281de22bd15c32b0df0559e84  X_normal
b2be6744a89f0a81d1e043fa60f1bd11b0f8dbe38efeafb981d26808877adb5b  J
```

The unobserved carrier states are strictly withheld from adaptive exposure:

```text
s01 NOT IN X_normal
s10 NOT IN X_normal
```

They may not enter compiler training, tuning, validation, repair, candidate scoring, or tie-breaking. Their dispatch behavior is evaluated only after the compiler artifact is finalized, by applying the finalized total transformation to the frozen `I_spec` domain before corrective release.

The normal workload excludes all corrective information, including `q*`, `z0/z1`, `κ0/κ1`, `K_corr`, `Π_corr`, `M`, `F`, `G`, `L`, mismatch witnesses, corrective targets, and corrective traces.

The frozen objective is:

\[
\boxed{
J:
\text{preserve correctness on observed }X_{\rm normal}
\land
\min \operatorname{cost}_{\rm causal}.
}
\]

The dynamic baseline is correct on both observed records at cost `6`. Every compiled candidate costs `5` per observed record. Scientific admission requires for each finalized compiler output:

```text
correctness on s00 and s11 = exact baseline correctness
cost on s00 and s11        = exactly 5
```

No normal-task correctness claim or admission test is made on `s01` or `s10`, because their normal-task targets are not exposed.

A compiler output that fails observed correctness or exact cost `5` is inadmissible. No tolerance, normalization, retuning, manual substitution, or replacement after corrective release is permitted.

## 7. Frozen matched data-dependent adaptive construction procedures

The independent adaptation factor is the **compiler coordinate constraint**, but neither finalized dispatch map is supplied by that constraint alone. Each compiler must search a finite within-class candidate family, and the shared observed normal data plus objective must select the finalized artifact.

### 7.1 Finite hypothesis/search classes

For `j in {0,1}`:

\[
\boxed{
\mathcal H_j
=
\{T_{j,g}:\;g:\{0,1\}\to\{\mathrm{ACT}_{NA},\mathrm{ACT}_{NB}\}\}
\cup
\{T_{\rm dynamic}\}.
}
\]

Use `H_0` for `C_ALPHA` and `H_1` for `C_BETA`.

Every compiled candidate `T_{j,g}` may read only `I_spec(x)[j]`; it emits normal action `g(I_spec(x)[j])` at cost `5`. It is a total function over the frozen two-bit interface. The unselected coordinate may not be consulted.

`T_dynamic` is the uncompiled baseline candidate, correct on the two observed normal records at cost `6`.

The four compiled mappings are exactly:

| Candidate | `g(0)` | `g(1)` | correct `s00` | correct `s11` | cost |
|---|---|---|---:|---:|---:|
| `g_AA` | `ACT_NA` | `ACT_NA` | 1 | 0 | 5 |
| `g_AB` | `ACT_NA` | `ACT_NB` | 1 | 1 | 5 |
| `g_BA` | `ACT_NB` | `ACT_NA` | 0 | 0 | 5 |
| `g_BB` | `ACT_NB` | `ACT_NB` | 0 | 1 | 5 |
| `T_dynamic` | — | — | 1 | 1 | 6 |

Because the observed examples lie on the diagonal of `I_spec`, the candidate-scoring table is identical for `H_0` and `H_1`; the two coordinate constraints fit the same evidence while extrapolating differently to `s01` and `s10`.

### 7.2 Compiler rules

\[
\boxed{
\mathcal C_\alpha(X_{\rm normal},J)
=
\arg\min_{T\in\mathcal H_0}\operatorname{cost}(T;X_{\rm normal})
}
\]

\[
\boxed{
\mathcal C_\beta(X_{\rm normal},J)
=
\arg\min_{T\in\mathcal H_1}\operatorname{cost}(T;X_{\rm normal})
}
\]

subject to exact observed normal correctness.

The unique correct compiled mapping is:

\[
\boxed{g^\star(0)=\mathrm{ACT}_{NA},\qquad g^\star(1)=\mathrm{ACT}_{NB}.}
\]

Thus `g_AA`, `g_BA`, and `g_BB` are rejected by the data. `T_dynamic` is correct but loses on cost. The minimum-cost correct candidate is unique, so the common canonical tie-break is frozen for deterministic implementation but is not invoked in the design-time selection.

If either implementation fails to reproduce this unique minimizer from the frozen candidate family and inputs, the adaptive family is inadmissible. The intended projection may not be supplied by hand.

### 7.3 Permitted and forbidden construction inputs

Permitted compiler inputs are exactly:

```text
X_normal (s00 and s11 only)
J
I_spec schema and coordinate domain
the compiler's own H_0 or H_1 candidate family
normal cost semantics
canonical dispatch schema
canonical serialization/tie-break rule
```

Forbidden construction inputs include:

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

The compiler construction log, exact candidate set, per-candidate observed correctness/cost record, input hashes, hypothesis descriptor, selected candidate serialization, and finalized artifact hash must all be custodied before corrective release.

### 7.4 Frozen design-time derived outputs

The frozen construction derives:

```text
C_ALPHA(X_normal,J) -> T_{0,g*} = T_ALPHA

coord[0]=0 -> ACT_NA
coord[0]=1 -> ACT_NB

pre-replay dispatch/generalization:
  s00 -> D0 / ACT_NA
  s01 -> D0 / ACT_NA
  s10 -> D1 / ACT_NB
  s11 -> D1 / ACT_NB
```

and:

```text
C_BETA(X_normal,J) -> T_{1,g*} = T_BETA

coord[1]=0 -> ACT_NA
coord[1]=1 -> ACT_NB

pre-replay dispatch/generalization:
  s00 -> D0 / ACT_NA
  s10 -> D0 / ACT_NA
  s01 -> D1 / ACT_NB
  s11 -> D1 / ACT_NB
```

where:

```text
D0 = (K0, FAST_NORMAL, GENERIC_POST_SPECIALIZATION)
D1 = (K1, FAST_NORMAL, GENERIC_POST_SPECIALIZATION)
```

Thus:

\[
\Pi_{T_\alpha}=\big\{\{s00,s01\},\{s10,s11\}\big\},
\]

\[
\Pi_{T_\beta}=\big\{\{s00,s10\},\{s01,s11\}\big\}.
\]

These are **pre-replay learned construction outputs**, not scientific post-replay outcomes. `s01` and `s10` never become adaptive examples; their dispatches are frozen extrapolations of the learned rules.

## 8. Prospective mismatch variable and canonical witnesses

For finalized `T`:

\[
\boxed{
M_T=1
\iff
\exists x,y\in\Omega_{\rm V2}:
K_T(x)=K_T(y)
\land
K_{\rm corr}(x)\neq K_{\rm corr}(y).
}
\]

Canonical witness pairs are stored once under `<_canon`:

\[
\mathcal W_T
=
\left\{
(x,y):
 x<_{\rm canon}y,
 K_T(x)=K_T(y),
 K_{\rm corr}(x)\neq K_{\rm corr}(y)
\right\}.
\]

The frozen realization implies the following **pre-replay predictor values**, which are not post-replay scientific outcomes:

```text
T_ALPHA:
  M = 0
  W = ∅

T_BETA:
  M = 1
  W = {(s00,s10), (s01,s11)}
```

Before corrective release, the implementation must hash-custody:

```text
Ω_V2
Π_corr
finalized T artifact
canonical Dispatch_T over Ω_V2
Π_T
M_T
W_T
```

---

## 9. Frozen orthogonal downstream topology

Each arm independently receives one `G` level and one `L` level.

### 9.1 Generic refinement factor `G`

\[
G\in\{\mathrm{REFINE},\mathrm{NO\_REFINE}\}.
\]

`REFINE` applies generic typed refinement:

```text
REFINE(dispatch_class, admissible_token)
    -> (dispatch_class, admissible_token)
```

`NO_REFINE` leaves the dispatch class unrefined by the token.

Neither level may contain a `q*` branch, challenge identifier, `κ0`/`κ1` literal, or correction-specific semantic shortcut.

### 9.2 Consequence-write factor `L`

\[
L\in\{\mathrm{LIVE},\mathrm{BLOCKED}\}.
\]

`LIVE` permits any already-warranted consequential-state write to cross the fixed consequence boundary.

`BLOCKED` denies every such write at that boundary.

`L` may not depend on `q*`, `κ0`, `κ1`, `M`, or `G`.

`G` and `L` are orthogonal and independently serialized/custodied.

---

## 10. Frozen factorial arm set

The scientific arm family is:

\[
\boxed{
\mathcal A_{\mathrm{V2-0}}
=
\{T_\alpha,T_\beta\}
\times
\{\mathrm{REFINE},\mathrm{NO\_REFINE}\}
\times
\{\mathrm{LIVE},\mathrm{BLOCKED}\}
}
\]

for eight arms:

```text
T_ALPHA × REFINE    × LIVE
T_ALPHA × REFINE    × BLOCKED
T_ALPHA × NO_REFINE × LIVE
T_ALPHA × NO_REFINE × BLOCKED
T_BETA  × REFINE    × LIVE
T_BETA  × REFINE    × BLOCKED
T_BETA  × NO_REFINE × LIVE
T_BETA  × NO_REFINE × BLOCKED
```

No arm is designated the preferred or successful outcome.

The four logical `(M,F)` cells:

```text
(0,0)
(0,1)
(1,0)
(1,1)
```

are all scientifically admissible cell types. The design-time finite realization establishes that none is definitionally excluded by the construction.

---

## 11. Joint pre-replay admission and release gate

No arm receives `q*` until all reference, compiler, mechanism, and topology objects are finalized and all admission checks pass.

Frozen order:

```text
1. verify frozen diagonal-learning realization hashes
2. verify Ω_V2 and canonical ordering
3. verify q* and reference κ bytes without exposing them to compiler construction
4. compute + hash K_corr and Π_corr
5. verify I_spec and canonical dispatch schema
6. verify canonical diagonal X_normal and J hashes
7. verify s01 and s10 are absent from all adaptive construction examples
8. verify H_0 / H_1 finite candidate-family descriptors and common serialization rule
9. exhaustively score all four compiled g mappings plus T_dynamic in each family
10. verify compiler custody logs contain no forbidden corrective material
11. verify g* is the unique correct cost-5 minimizer for both compiler families
12. verify exact observed normal correctness and cost = 5 for both finalized outputs
13. hash finalized T_ALPHA and T_BETA artifacts
14. extract + hash canonical Dispatch_T over Ω_V2 without adding s01/s10 to adaptive exposure
15. compute + hash Π_T, M_T, and W_T
16. instantiate + hash all four generic (G,L) topology descriptors
17. JOINT_PRE_REPLAY_ADMISSION_PASS
18. release q* to all eight arms
```

If any check before step 17 fails:

```text
V2_JOINT_ADMISSION_FAIL
```

and **no corrective replay occurs and no scientific `R` or `F` outcome exists for that execution**.

No partial compiler or arm result is retained as a scientific comparison.

## 12. Corrective replay semantics

For arm:

\[
A=(T,G,L)
\]

and challenged state `x`, replay proceeds from an isolated post-admission snapshot so that no earlier state replay can alter a later one.

Carrier states are replayed in canonical order:

```text
s00
s01
s10
s11
```

For each `x`:

1. release `q*` and authenticate token `z(x)`;
2. establish reference `CORRECTION`, `CORR_AUTH`, and `OPEN` status;
3. read finalized `Dispatch_T(I_spec(x))` without mutation;
4. form the pre-refinement dispatch-equivalence candidate set;
5. apply `G` generically;
6. resolve the required consequence iff `K_corr` is constant over the surviving candidate set;
7. if resolved and `L=LIVE`, apply the required `ΔS`;
8. emit the corresponding required terminal-action class only after the required state transformation is causally realized;
9. record the complete causal trace.

No consequence is guessed or defaulted if resolution fails.

Coincidental terminal-action equality without the required consequential-state transformation does not count as route preservation.

---

## 13. Primary raw scientific outcome

For every arm `A` and every carrier state `x`, define:

\[
I_{A,x}
=
\mathbf 1[R_A(x\mid q^\star)\neq\varnothing].
\]

The **primary raw scientific outcome** is the complete `8 × 4` route-reachability matrix:

\[
\boxed{
\Sigma_R^{\mathrm{V2-0}}
=
(I_{A,x})_{A\in\mathcal A_{\mathrm{V2-0}},\ x\in\Omega_{\mathrm{V2}}}.
}
\]

Observed fields remain blank before execution:

```text
T_ALPHA × REFINE × LIVE:
  R_s00 = [UNPOPULATED]
  R_s01 = [UNPOPULATED]
  R_s10 = [UNPOPULATED]
  R_s11 = [UNPOPULATED]

T_ALPHA × REFINE × BLOCKED:
  R_s00 = [UNPOPULATED]
  R_s01 = [UNPOPULATED]
  R_s10 = [UNPOPULATED]
  R_s11 = [UNPOPULATED]

T_ALPHA × NO_REFINE × LIVE:
  R_s00 = [UNPOPULATED]
  R_s01 = [UNPOPULATED]
  R_s10 = [UNPOPULATED]
  R_s11 = [UNPOPULATED]

T_ALPHA × NO_REFINE × BLOCKED:
  R_s00 = [UNPOPULATED]
  R_s01 = [UNPOPULATED]
  R_s10 = [UNPOPULATED]
  R_s11 = [UNPOPULATED]

T_BETA × REFINE × LIVE:
  R_s00 = [UNPOPULATED]
  R_s01 = [UNPOPULATED]
  R_s10 = [UNPOPULATED]
  R_s11 = [UNPOPULATED]

T_BETA × REFINE × BLOCKED:
  R_s00 = [UNPOPULATED]
  R_s01 = [UNPOPULATED]
  R_s10 = [UNPOPULATED]
  R_s11 = [UNPOPULATED]

T_BETA × NO_REFINE × LIVE:
  R_s00 = [UNPOPULATED]
  R_s01 = [UNPOPULATED]
  R_s10 = [UNPOPULATED]
  R_s11 = [UNPOPULATED]

T_BETA × NO_REFINE × BLOCKED:
  R_s00 = [UNPOPULATED]
  R_s01 = [UNPOPULATED]
  R_s10 = [UNPOPULATED]
  R_s11 = [UNPOPULATED]
```

No narrative interpretation may appear before this raw matrix is emitted.

---

## 14. Derived arm-level foreclosure outcome

For each arm:

\[
\boxed{
F_A
=
\mathbf 1
\left[
\exists x\in\Omega_{\rm V2}:R_A(x\mid q^\star)=\varnothing
\right].
}
\]

Observed fields remain blank before execution:

```text
F[T_ALPHA, REFINE, LIVE]       = [UNPOPULATED]
F[T_ALPHA, REFINE, BLOCKED]    = [UNPOPULATED]
F[T_ALPHA, NO_REFINE, LIVE]    = [UNPOPULATED]
F[T_ALPHA, NO_REFINE, BLOCKED] = [UNPOPULATED]
F[T_BETA, REFINE, LIVE]        = [UNPOPULATED]
F[T_BETA, REFINE, BLOCKED]     = [UNPOPULATED]
F[T_BETA, NO_REFINE, LIVE]     = [UNPOPULATED]
F[T_BETA, NO_REFINE, BLOCKED]  = [UNPOPULATED]
```

`F` is derived only from observed post-replay reachability. It is never an input to `T`, `Π_T`, `M`, `G`, or `L`.

---

## 15. Secondary matched partition contrasts

To compare prospective partition mismatch while holding downstream topology fixed, define one signed contrast per `(G,L)` stratum:

\[
D_{G,L}
=
F_{T_\beta,G,L}-F_{T_\alpha,G,L}
\in\{-1,0,+1\}.
\]

Observed fields remain blank before execution:

```text
D[REFINE, LIVE]       = [UNPOPULATED]
D[REFINE, BLOCKED]    = [UNPOPULATED]
D[NO_REFINE, LIVE]    = [UNPOPULATED]
D[NO_REFINE, BLOCKED] = [UNPOPULATED]
```

Interpretation is frozen as:

- `D=+1`: under that fixed downstream topology, the pre-replay mismatch arm foreclosed where the aligned arm did not; this is bounded directional evidence consistent with the Correction-Partition Hypothesis in that stratum.
- `D=0`: no foreclosure discrimination by the `T_ALPHA/T_BETA` partition contrast in that stratum.
- `D=-1`: under that fixed downstream topology, the mismatch arm preserved correction where the aligned arm foreclosed; this is bounded directional evidence against the hypothesized direction in that stratum.

No sum, average, weighted score, ranking, or scalarization of the four `D` values has scientific meaning in V2-0.

---

## 16. Observed `(M,F)` cell set

After valid execution, derive:

\[
\mathcal C_{MF}^{\rm obs}
=
\{(M_T,F_A):A=(T,G,L)\in\mathcal A_{\mathrm{V2-0}}\}.
\]

Before execution:

```text
C_MF_obs = [UNPOPULATED]
```

The four logical cells are not ranked:

```text
(0,0) aligned + survives
(0,1) aligned + forecloses
(1,0) mismatch + survives/recovers
(1,1) mismatch + forecloses
```

The existence of `(1,0)` would show that mismatch is not sufficient for foreclosure in this finite assay.

The existence of `(0,1)` would show that alignment is not sufficient for preservation in this finite assay.

Neither statement establishes necessity or sufficiency in general.

---

## 17. Validity gates and non-results

Scientific outcome emission is prohibited if any of the following occurs:

```text
frozen diagonal-learning realization hash mismatch
carrier/reference-semantics mismatch
X_normal or J hash mismatch
s01 or s10 enters adaptive construction data
H_0 / H_1 candidate-family descriptor mismatch
candidate-set / scoring / serialization mismatch
forbidden corrective information enters compiler construction
compiler output not derivable as the unique frozen-data minimizer from its candidate family
observed normal correctness mismatch
observed normal cost != 5 for either compiler output
noncanonical or mutable dispatch artifact
pre-replay partition/witness custody failure
G/L descriptor mismatch
challenge release before joint admission
trace-integrity failure
route classification ambiguity
```

Any such event terminates before scientific interpretation.

An invalid execution is **not** encoded as an `(M,F)` cell, a zero route matrix, or a scientific null.

A disagreement between implementation behavior and the frozen diagonal-learning realization semantics must be treated first as an implementation/realization mismatch. The protocol may not be reinterpreted post hoc to convert such a discrepancy into a preferred scientific result.

## 18. Outcome neutrality and reporting order

No `(M,F)` cell, route matrix, `F` vector, or `D` pattern is designated the preferred result.

The execution report must present, in order:

```text
1. validity / joint-admission status
2. complete raw 8×4 R matrix
3. eight derived F values
4. observed (M,F) cell set
5. four signed D[G,L] contrasts
6. only then: bounded interpretation
```

The primary outcome is observed reachability, not conformity to the design-time structural expectation or to a preferred hypothesis ordering.

The frozen finite realization's enumeration may be shown **after** the raw observed object as a design-time comparison, but may not substitute for the observed object.

---

## 19. Claim discipline

V2-0 permits only finite-assay claims supported by the emitted raw object and frozen contrasts.

Permitted bounded statements include forms such as:

> Under fixed downstream topology `(G,L)` in this finite assay, the prospectively mismatched partition arm and the aligned partition arm differed in corrective foreclosure.

or:

> In this finite assay, a pre-replay partition mismatch was present without later foreclosure.

or:

> In this finite assay, later foreclosure occurred despite pre-replay partition alignment.

V2-0 does **not** license:

```text
partition mismatch generally causes foreclosure
partition alignment is safe
mismatch is necessary for foreclosure
mismatch is sufficient for foreclosure
REFINE is generally safe
LIVE is generally safe
this is a theorem of adaptive systems
this establishes neural-network behavior
this establishes frontier-AI behavior
ALCF and MATRIX are formally equivalent
```

No scalar corrigibility/safety score is defined.

---

## 20. Pre-execution state

At freeze time, the scientific state must read:

```text
finite realization       FROZEN
V2-0 preregistration     FROZEN
implementation           NOT STARTED
joint admission          NOT RUN
q* corrective release    NOT RUN
R matrix                 UNOBSERVED
F vector                 UNOBSERVED
D contrasts              UNOBSERVED
C_MF_obs                 UNOBSERVED
scientific result        NONE
```

No implementation or corrective execution is authorized by this draft itself.

