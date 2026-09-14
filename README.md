# Adaptive Leverage

**Adaptive leverage without corrective foreclosure** asks whether an adaptive system can increase its causal leverage over future states while preserving the warranted causal routes by which future world differences can revise consequential system state.

The primitive for ALCF-V0 is set-valued:

\[
R_t:\mathcal C_{\mathrm{warranted}}\rightarrow 2^{\mathrm{causal\ paths}}
\]

with the preregistered target event:

\[
\Delta\operatorname{Cap}>0
\land
R_t(c^\star\mid e^\star,\omega^\star)\neq\varnothing
\land
R_{t+1}(c^\star\mid e^\star,\omega^\star)=\varnothing,
\]

plus provenance showing that route loss is attributable to the capability transition rather than to a warrant-validating epistemic transition.

## Current repository state

```text
ALCF-V0 DESIGN                 CLOSED
ALCF-V0 PROTOCOL               FROZEN
ALCF-V0 IMPLEMENTATION         PRESENT
ALCF-V1 PREREGISTRATION        FROZEN
ALCF-V1 IMPLEMENTATION         PRESENT
ALCF-V2-0 DESIGN AUTHORITY     FROZEN
ALCF-V2-0 PREREGISTRATION      FROZEN
ALCF-V2-0 IMPLEMENTATION       PRESENT (DORMANT RUNNER)
ALCF-V2-0 CORRECTIVE RELEASE   NOT RUN
ALCF-V2-0 R / F / D / C_MF_obs UNOBSERVED
ALCF-V2-0 SCIENTIFIC RESULT    NONE
```

Repository implementation presence does not authorize scientific execution. Frozen protocol artifacts are authoritative; editorial summaries in this README do not override them.

- `prereg/ALCF_V0_PREREG_FROZEN.md` — frozen V0 preregistration
- `prereg/ALCF_V0_PROTOCOL_FROZEN.json` — machine-readable frozen V0 protocol
- `prereg/ALCF_V1_PREREG_FROZEN.md` — frozen V1 preregistration
- `prereg/ALCF_V2_0_FINITE_REALIZATION_DIAGONAL_FROZEN.md` — frozen V2-0 finite-realization authority
- `prereg/ALCF_V2_0_PREREG_FROZEN.md` — frozen V2-0 preregistration bytes
- `prereg/ALCF_V2_0_PREREG_FREEZE_RECORD.txt` — V2-0 freeze custody record

The capability intervention is subject to a custody restriction: it must be derived exclusively from the preregistered normal workload, with the corrective condition withheld until the intervention is finalized and hashed.

## Claim ceiling

A positive ALCF-V0 result may support only the bounded claim frozen in the preregistration. It does **not** establish a general capability/corrigibility tradeoff, a property of neural networks, or a property of frontier AI systems.

A clean null is a valid result:

\[
\Delta\operatorname{Cap}>0\not\Rightarrow\text{corrective foreclosure}.
\]

## Execution boundary

Implementation must instantiate the frozen protocol rather than revise it. Execution and scientific interpretation are separate later steps. Any ambiguity that cannot be resolved without changing protocol semantics is a protocol defect, not permission for a silent implementation choice.
