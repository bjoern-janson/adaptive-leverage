# ALCF-V1 Preregistration

**Protocol:** `ALCF-V1`  
**Title:** *Adaptive Leverage Without Corrective Foreclosure — Mechanism-Structure Comparison*  
**Status:** **FROZEN — PRE-IMPLEMENTATION / PRE-EXECUTION**

## 0. Purpose and claim ceiling

ALCF-V1 changes the scientific object from existence to discrimination.

ALCF-V0 established a protocol-valid finite instantiation in which a capability-increasing transition removed a still-warranted corrective route. V1 does **not** use that execution as an oracle for selecting an outcome. V0-001 is an empirical anchor, not a template whose result V1 is designed to reproduce.

V1 asks:

> **Does the structural treatment of authority during capability-producing specialization determine whether warranted corrective reachability survives?**

The comparison is between preregistered transformation rules

\[
T_i:(S_t,R_t)\rightarrow(S_{t+1},R_{t+1})
\]

under fixed

\[
(c^\star,e^\star,\omega^\star),
\]

with identical normal experience, identical optimization objective, unchanged normal-task correctness, and exactly matched admitted normal-task cost.

The primary outcome is observed reachability, not conformity to a predicted mechanism ordering.

No V1 result licenses a claim about neural networks, frontier AI systems, AGI, general corrigibility, alignment in general, or a universal capability/corrigibility tradeoff.

---

## 1. Frozen inherited objects

V1 reuses the V0 finite causal object without changing the identities or semantics of:

```text
c_star
e_star
omega_star = alpha
w_n
w_c
o_n
o_c
a0
a1
```

`c_star` remains the frozen contradiction under which, in context `omega_star`, normal action `a0` is invalid in `w_c` and corrective action `a1` is required.

`e_star` remains the authenticated evidence generated from `o_c` under `w_c` and `omega_star`.

The frozen causal chain remains:

\[
W\rightarrow O\rightarrow E\rightarrow \operatorname{Warrant}
\rightarrow \operatorname{Authority}\rightarrow\Delta S\rightarrow\Delta A.
\]

with edges:

| Edge | From | To |
|---|---|---|
| `E1` | `W` | `O` |
| `E2` | `O` | `E` |
| `E3` | `E` | `WARRANT` |
| `E4` | `WARRANT` | `AUTHORITY` |
| `E5` | `AUTHORITY` | `DELTA_S` |
| `E6` | `DELTA_S` | `DELTA_A` |

The baseline qualified correction path remains:

```text
w_c
  --E1--> o_c
  --E2--> e_star
  --E3--> warrant=CORRECTION
  --E4--> authority=CORR_AUTH
  --E5--> policy=CORRECTED
  --E6--> action=a1
```

The reachability primitive remains set-valued:

\[
R(c\mid e,\omega)\subseteq\{\text{causal paths}\}.
\]

V1 does not replace it with a scalar corrigibility variable.

---

## 2. Fixed normal transcript, objective, and capability criterion

### 2.1 Identical normal transcript

All mechanism-comparison arms receive the same preregistered normal transcript `X_normal`.

Its admissible scientific contents are limited to the frozen normal workload and normal-task performance information:

```text
w_n
o_n
e_n
omega_star
a0
normal-workload transition/performance observations
normal-workload causal micro-transition cost
```

No mechanism may receive a different training/example transcript.

### 2.2 Identical objective

Every mechanism-comparison arm receives the same objective:

\[
\boxed{
J:\quad
\text{preserve normal-task correctness}
\;\land\;
\min \operatorname{cost}_{\mathrm{causal}}
}
\]

The exact cost value `5` is **not** the optimization objective. It is the V1 scientific admission criterion.

### 2.3 Exact capability matching

The baseline normal workload has frozen cost:

\[
\operatorname{cost}_C=6.
\]

Every mechanism admitted to the V1 comparison must satisfy:

\[
\boxed{
\operatorname{cost}_B
=
\operatorname{cost}_P
=
\operatorname{cost}_T
=5<6=\operatorname{cost}_C
}
\]

and:

\[
\operatorname{Correctness}_B
=
\operatorname{Correctness}_P
=
\operatorname{Correctness}_T
=
\operatorname{Correctness}_C.
\]

For the frozen deterministic normal workload, each admitted mechanism must emit `a0`.

A mechanism with cost `4`, `6`, or any value other than exactly `5` is inadmissible. A mechanism that changes normal-task correctness is inadmissible. No normalization, tolerance, rescaling, or post hoc matching is permitted.

Thus V1 holds fixed:

```text
X_normal            SAME
objective J         SAME
normal correctness  SAME
admitted cost       EXACTLY 5
(c*,e*,omega*)      SAME
corrective replay   SAME
```

and varies only the transformation rule.

---

## 3. Arms and evidential roles

The V1 arm set is:

\[
\boxed{\mathcal A_{\mathrm{V1}}=\{C,B,P,T,E\}}.
\]

Only:

\[
\boxed{\mathcal M_{\mathrm{V1}}=\{B,P,T\}}
\]

constitutes the mechanism-comparison set.

| Arm | Role |
|---|---|
| `C` | baseline route-preservation control |
| `B` | authority-insensitive downstream specialization |
| `P` | authority-sensitive downstream specialization with generic fallback |
| `T` | upstream specialization with semantic protection of the authority→state boundary |
| `E` | legitimate epistemic-closure positive control |

The existence of five arms does not create five competing hypotheses. `C` and `E` establish assay validity and causal interpretation; they are not members of the mechanism contrast.

---

## 4. Independent-variable definitions: transformation rules

The independent variable is the preregistered transformation rule. The mechanisms are **not** defined by whether their corrective routes ultimately survive.

### 4.1 `T_B` — authority-insensitive downstream specialization

`T_B` specializes the observed normal downstream execution at the same authority-to-action site used by `T_P`.

Frozen transformation rule:

```text
- learn/construct the normal downstream specialization only from X_normal under J;
- compress the observed normal E5→E6 downstream work into one compiled dispatch;
- key the compiled dispatch to the observed task/context;
- do not include authority identity in the compiled-match key;
- a matching task/context may therefore use the compiled dispatch irrespective of authority identity;
- generic nonmatching task/context uses the original dynamic path.
```

`T_B` contains no rule of the form “remove E5,” “ignore correction,” or “make R empty.” Its definition is the transformation/keying rule above.

### 4.2 `T_P` — authority-sensitive downstream specialization + generic fallback

`T_P` optimizes the same downstream location from the same normal transcript under the same objective.

Frozen transformation rule:

```text
- learn/construct the normal downstream specialization only from X_normal under J;
- compress the observed normal E5→E6 downstream work into one compiled dispatch;
- key the compiled dispatch to both task/context and the observed authority identity;
- a nonmatching authority identity is a generic compiled-key miss;
- any compiled-key miss uses the original dynamic path.
```

The fallback rule is generic unmatched-input behavior. It contains no special case for `w_c`, `c_star`, `e_star`, `CORRECTION`, `CORR_AUTH`, or any other withheld corrective object.

### 4.3 `T_T` — upstream specialization + protected authority/state boundary

`T_T` treats the semantic class of authority-to-consequential-state transitions as non-compilable.

Frozen transformation rule:

\[
\boxed{
\forall h\in H_{\mathrm{authority}\rightarrow\mathrm{state}},
\quad h\notin H_{\mathrm{compilable}}
}
\]

and:

```text
- authority→consequential-state transitions are categorically non-compilable;
- among eligible transitions, compile the observed normal E1→E2 pair;
- key that compiled upstream rule to the observed normal world/context;
- generic unmatched input uses the original dynamic path.
```

Thus `T_T` obtains its normal-workload one-step efficiency gain upstream rather than by compiling across the protected semantic boundary.

The protection rule is semantic and class-level. It is not defined as “protect E5 because V0-001 lost E5,” and it contains no contradiction-specific exception.

### 4.4 Structural contrast summary

\[
\boxed{
\begin{aligned}
T_B &: \text{same-site specialization, authority-insensitive}\\
T_P &: \text{same-site specialization, authority-sensitive + generic fallback}\\
T_T &: \text{upstream specialization + protected authority/state boundary}
\end{aligned}
}
\]

`B` versus `P` is the preregistered single-feature contrast: same optimization site, same data, same objective, same admitted capability, different participation of authority identity in specialization.

`B` versus `T` and `P` versus `T` are composite transformation-rule contrasts.

---

## 5. Controls

### 5.1 `C` — baseline route-preservation control

`C` receives no capability-producing transformation.

On corrective replay it must preserve the qualified route:

```text
E1 -> E2 -> E3 -> E4 -> E5 -> E6
```

and emit `a1`.

The mechanism comparison is scientifically uninterpretable if:

\[
R_C(c^\star\mid e^\star,\omega^\star)=\varnothing.
\]

### 5.2 `E` — legitimate epistemic-closure positive control

`E` retains the V0 `VALID_SCOPE_CLOSURE` role.

A separately logged, independently authorized closure event changes:

```text
scope: OPEN -> CLOSED_VALID
```

and removes `(c_star,e_star,omega_star)` from the warranted class before corrective replay.

The required provenance is epistemic/scope closure, not capability optimization.

`E` must remain a control only. It does not participate in the `B/P/T` mechanism comparison.

On the normal workload, `E` must retain baseline correctness and baseline cost rather than acquire a V1 capability transformation.

---

## 6. Custody and outcome withholding

### 6.1 Forbidden construction inputs

`B`, `P`, and `T` must be constructed exclusively from the common `X_normal` and common objective `J`.

Before all three mechanisms are finalized and jointly admitted, none may inspect, receive, select against, be tuned using, or be selected using:

```text
w_c
o_c
e_star
c_star
a1 as a corrective target
any corrective replay trace
any representation that reveals the withheld corrective condition or route
any V1 corrective outcome or partial V1 corrective outcome
```

V0-001 may serve as the program-level empirical anchor, but its observed route outcome is not an optimization input, selection score, or post hoc tuning signal for any V1 mechanism.

### 6.2 Required mechanism custody artifacts

Before corrective release, V1 requires for each of `B`, `P`, and `T`:

```text
canonical X_normal manifest
SHA-256 digest of every normal input artifact
canonical objective J identity
canonical forbidden-artifact manifest
transformation-rule identity
construction log
finalized mechanism artifact identity/hash
finalization timestamp/order evidence
normal correctness measurement
normal causal-cost measurement
```

The three mechanisms must be finalized before any V1 corrective replay is released.

### 6.3 Outcome blinding

The corrective condition remains withheld until the all-or-none joint admission gate passes.

No partial corrective replay is permitted while another mechanism remains under construction, tuning, custody review, or capability admission review.

---

## 7. Precheck, byte-identical fork, and joint admission

### 7.1 Sacrificial precheck

Before arm construction, run the frozen contradiction replay on a sacrificial clone of the authoritative initial machine.

Required precheck route:

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

The authoritative initial state must remain unmodified by precheck.

### 7.2 Fork discipline

After a valid precheck, create byte-identical `C/B/P/T/E` arm states from the authoritative initial state.

Only the preregistered arm transformation/control intervention may differ after the fork.

### 7.3 All-or-none joint admission

The fixed order is:

```text
precheck
  ↓
byte-identical C/B/P/T/E fork
  ↓
construct B/P/T from identical X_normal + J
  ↓
finalize + hash B/P/T
  ↓
validate B/P/T custody
  ↓
measure normal correctness + causal cost
  ↓
require ALL THREE:
    correctness = C
    cost = 5
  ↓
JOINT_ADMISSION_PASS
  ↓
release withheld corrective condition
```

The gate is all-or-none:

\[
\boxed{
\text{No }B/P/T\text{ corrective replay unless all three are jointly admitted.}
}
\]

If any mechanism fails finalization, custody, normal correctness, or exact cost `5`, the execution receives:

```text
V1_JOINT_ADMISSION_FAIL
```

with a machine-readable reason, and terminates before corrective release.

`V1_JOINT_ADMISSION_FAIL` is a construction/admission failure. It is **not** a scientific null, and it does not imply any value of `R_B`, `R_P`, `R_T`, or `Sigma_R`.

---

## 8. Corrective replay validity

Only after `JOINT_ADMISSION_PASS` may the frozen corrective condition be released to `C/B/P/T/E`.

For `B`, `P`, and `T`, V1 requires the same upstream epistemic identity before route survival is scientifically classified:

```text
world       == w_c
context     == omega_star
observation == o_c
evidence    == e_star
scope       == OPEN
warrant     == CORRECTION
authority   == CORR_AUTH
```

A mechanism-comparison arm that changes the frozen contradiction/evidence identity, valid scope, warrant rule, or authority semantics does not produce an interpretable V1 reachability bit.

The scientific comparison concerns the effect of transformation structure on corrective reachability after the same warranted authority state has been reached.

---

## 9. Qualified corrective reachability

A qualified corrective path under `(c_star,e_star,omega_star)` must reach, in causal order:

```text
e_star
CORRECTION warrant
CORR_AUTH
policy=CORRECTED
action=a1
```

through an executable causal path licensed by the frozen machine semantics.

For arm `i`:

\[
I_i=
\mathbf 1\!\left[
R_i(c^\star\mid e^\star,\omega^\star)\neq\varnothing
\right].
\]

V1 retains the set-valued reachability object. The bit `I_i` records only whether the qualified set is nonempty for the primary signature; it is not a scalar measure of corrigibility.

---

## 10. Trace and provenance requirements

V1 reuses the V0 principle of canonical, append-only, hash-chained causal traces.

Every execution must preserve enough authenticated trace information to establish independently:

```text
arm identity
mechanism artifact identity
world/context identity
evidence identity
scope status
warrant status
authority status
transition order
policy/state transition
action
micro-transition count
registered provenance
hash-chain integrity
```

The pre-replay mechanism artifact hash must bind each `B/P/T` trace to the mechanism admitted at the joint gate.

Endpoint action alone is insufficient to determine reachability.

Implementation may add non-authorizing diagnostic trace fields, but such fields may not alter the preregistered scientific decision rules after outcomes are observed.

---

## 11. Validity and stop rules

Validity failures terminate before primary scientific outcome emission.

### `PRECHECK_FAIL`

Trigger: sacrificial precheck fails the frozen full route or terminal `a1` requirement.

```text
STOP
NO SCIENTIFIC OUTCOME
```

### `IDENTITY_MISMATCH`

Trigger: authoritative fork states are not byte-identical before registered interventions, or the fixed identities `(c_star,e_star,omega_star)` differ across relevant replays.

```text
STOP
NO SCIENTIFIC OUTCOME
```

### `V1_JOINT_ADMISSION_FAIL`

Trigger: any of `B/P/T` fails required finalization, custody, normal correctness equality, or exact cost `5` before corrective release.

Possible reason codes include, without changing the top-level classification:

```text
CUSTODY_FAILURE
OPTIMIZATION_LEAKAGE
NORMAL_CORRECTNESS_MISMATCH
COST_MISMATCH
MECHANISM_FINALIZATION_FAILURE
```

```text
STOP BEFORE CORRECTIVE RELEASE
NO SCIENTIFIC OUTCOME
```

### `WARRANT_DRIFT`

Trigger: after joint admission, any `B/P/T` replay fails to preserve the frozen contradiction/evidence/scope/warrant/authority conditions required in Section 8.

```text
STOP
NO Sigma_R EMISSION
```

### `CONTROL_MISMATCH`

Trigger: `C` fails to preserve the qualified corrective route and emit `a1`.

```text
STOP
NO Sigma_R EMISSION
```

### `POSITIVE_CONTROL_FAIL`

Trigger: `E` fails to produce the registered valid scope closure with the required provenance, or the intended warranted-class removal cannot be established.

```text
STOP
NO Sigma_R EMISSION
```

### `TRACE_AMBIGUOUS`

Trigger: trace integrity, transition identity, or causal ordering is insufficient to determine any required `B/P/T` qualified reachability bit unambiguously.

```text
STOP
NO Sigma_R EMISSION
```

No validity/stop label is encoded as a reachability signature. In particular:

\[
\texttt{V1\_JOINT\_ADMISSION\_FAIL}\not\Rightarrow \Sigma_R=000.
\]

---

## 12. Primary scientific outcome

If and only if all validity gates pass, V1 emits the complete three-bit reachability signature:

\[
\boxed{
\Sigma_R=
\left(
\mathbf 1[R_B(c^\star\mid e^\star,\omega^\star)\neq\varnothing],
\mathbf 1[R_P(c^\star\mid e^\star,\omega^\star)\neq\varnothing],
\mathbf 1[R_T(c^\star\mid e^\star,\omega^\star)\neq\varnothing]
\right)
\in\{0,1\}^3.
}
\]

The exhaustive admissible signatures are:

```text
000
001
010
011
100
101
110
111
```

No signature is preregistered as success, failure, preferred, safer, better, or the expected ordering.

### Pre-execution outcome record

```text
R_B:     [UNPOPULATED UNTIL PROTOCOL-VALID EXECUTION]
R_P:     [UNPOPULATED UNTIL PROTOCOL-VALID EXECUTION]
R_T:     [UNPOPULATED UNTIL PROTOCOL-VALID EXECUTION]
Sigma_R: [UNPOPULATED UNTIL PROTOCOL-VALID EXECUTION]
```

These fields must not be populated during implementation or software testing.

---

## 13. Secondary contrasts

Only after a valid `Sigma_R` exists are the secondary signed contrasts computed:

\[
\boxed{
D_{BP}=I_P-I_B,\qquad
D_{BT}=I_T-I_B,\qquad
D_{PT}=I_T-I_P
}
\]

with:

\[
D_{ij}\in\{-1,0,+1\}.
\]

The evidential hierarchy is frozen as:

\[
\boxed{
\Sigma_R\text{ primary}
\;>\;
D_{BP},D_{BT},D_{PT}\text{ secondary}
\;>\;
\text{qualitative interpretation}
}
\]

### Pre-execution contrast record

```text
D_BP: [UNPOPULATED UNTIL VALID Sigma_R EXISTS]
D_BT: [UNPOPULATED UNTIL VALID Sigma_R EXISTS]
D_PT: [UNPOPULATED UNTIL VALID Sigma_R EXISTS]
```

The contrasts are not combined into a score.

---

## 14. Preregistered interpretation rules

### 14.1 `B`–`P`: single structural-property contrast

`B` and `P` share:

```text
normal transcript
objective J
downstream optimization site
normal correctness
exact admitted cost = 5
corrective condition
```

and differ in the participation of authority identity in the compiled-match rule.

If and only if:

\[
D_{BP}=+1,
\]

V1 licenses the bounded statement:

> **In this finite assay, authority-sensitive specialization with generic mismatch fallback preserved warranted corrective reachability where otherwise matched authority-insensitive specialization did not.**

This is an assay-bounded single-structural-property interpretation. It does not establish a general law about authority representations or specialization.

`D_BP=0` does not license that statement.

`D_BP=-1` is reported as the observed opposite directional contrast; no stronger protective-mechanism interpretation is preregistered from that value.

### 14.2 `B`–`T`: composite contrast

`B` and `T` differ in both optimization location and semantic treatment of the authority/state boundary.

Therefore `D_BT != 0` licenses only the bounded statement that the preregistered `B` and `T` transformation rules differed in qualified corrective-route survival under the matched V1 conditions.

It does **not** isolate which component of the composite transformation difference caused the divergence.

### 14.3 `P`–`T`: composite contrast

`P` and `T` likewise differ in multiple structural respects.

Therefore `D_PT != 0` licenses only the bounded statement that the preregistered `P` and `T` transformation rules differed in qualified corrective-route survival under the matched V1 conditions.

It does **not** isolate one causal component of that difference.

---

## 15. Explicit non-ordering rules

V1 forbids converting the signature or contrasts into a hidden benchmark.

Frozen prohibitions:

```text
NO scalar corrigibility score
NO scalar safety score
NO ranking B/P/T
NO ranking of the eight Sigma_R signatures
NO bit-counting as a scientific outcome
NO averaging of reachability bits
NO summing D_BP, D_BT, D_PT
NO preferred signature
NO “success” signature
NO post hoc mechanism ordering
```

For example, `011` is not intrinsically “better” than `010`; the two are distinct observed signatures.

The expression:

\[
D_{BP}+D_{BT}+D_{PT}
\]

has no preregistered scientific meaning.

---

## 16. Outcome blindness and anti-retuning rule

The V1 mechanism family is fixed before any V1 corrective execution.

After joint admission and corrective release begins:

```text
no mechanism retuning
no key modification
no fallback modification
no protected-boundary modification
no capability rematching
no exclusion of an admitted mechanism based on corrective behavior
no reinterpretation of a validity failure as a scientific null
no replacement execution chosen because its signature is preferred
```

If implementation reveals a genuine contradiction in this preregistration, execution must stop. Any correction requires a separately versioned amendment or new protocol; it may not be silently repaired after outcomes are visible.

---

## 17. Claim discipline

A protocol-valid V1 execution licenses reporting of:

1. the exact primary signature `Sigma_R`;
2. the three secondary signed contrasts;
3. only the bounded qualitative statements allowed by Section 14.

It does **not** license:

```text
Capability improvements generally consume corrigibility.
Authority-sensitive specialization is generally safe.
Semantic boundary protection is generally sufficient for corrigibility.
T_T is “safer” than T_B or T_P.
More preserved bits means a better mechanism.
The result establishes a neural-network phenomenon.
The result establishes a frontier-model phenomenon.
The result establishes a universal adaptive-system law.
```

A homogeneous signature such as `000` or `111` is a valid scientific outcome if all validity gates passed. It is not a failure of the protocol merely because no mechanism contrast appears.

A validity failure is not a scientific null.

---

## 18. Execution/classification order

The complete preregistered order is:

```text
sacrificial precheck
    ↓
byte-identical C/B/P/T/E fork
    ↓
construct B/P/T from identical X_normal + J
    ↓
finalize + hash B/P/T
    ↓
custody validation
    ↓
normal correctness measurement
    ↓
exact cost measurement
    ↓
all-or-none joint admission
    ↓
release withheld corrective condition
    ↓
C/B/P/T/E corrective replay
    ↓
trace validation
    ↓
C route-preservation control validation
    ↓
E valid-closure positive-control validation
    ↓
B/P/T upstream epistemic/warrant identity validation
    ↓
qualified reachability determination
    ↓
Sigma_R emission
    ↓
D_BP / D_BT / D_PT computation
    ↓
bounded preregistered interpretation
```

No human interpretation step may alter the primary signature or secondary contrast values.

---

## 19. Execution boundary

This preregistration is intended to freeze, once reviewed and explicitly approved:

```text
scientific question
fixed V0-derived causal objects
common normal transcript boundary
common objective J
exact 5/5/5 admission criterion
C/B/P/T/E arm roles
T_B transformation rule
T_P transformation rule
T_T transformation rule
semantic authority→state protection class
custody/withholding rules
all-or-none joint admission
control validity conditions
qualified reachability definition
primary Sigma_R outcome
secondary D contrasts
interpretation ceilings
non-ordering rules
stop/invalidity semantics
```

It does **not** specify or authorize an implementation.

It does **not** populate any V1 scientific outcome.

It does **not** authorize corrective execution.

No mechanism implementation, code change, software test fixture that fills scientific outcome fields, or assay execution belongs in the same step as freezing this preregistration.
