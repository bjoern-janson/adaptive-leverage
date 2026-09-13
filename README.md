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

## Current state

```text
ALCF-V0 DESIGN        CLOSED
ALCF-V0 PROTOCOL      FROZEN
PROTOCOL MUTATION     FORBIDDEN
IMPLEMENTATION        NOT YET LANDED
EXECUTION             NOT STARTED
SCIENTIFIC RESULT     NONE
```

The frozen protocol is authoritative. Editorial summaries in this README do not override it.

- `prereg/ALCF_V0_PREREG_FROZEN.md` — human-readable frozen preregistration
- `prereg/ALCF_V0_PROTOCOL_FROZEN.json` — machine-readable frozen protocol
- `prereg/ALCF_V0_SHA256SUMS_FROZEN.txt` — frozen artifact hashes

The capability intervention is subject to a custody restriction: it must be derived exclusively from the preregistered normal workload, with the corrective condition withheld until the intervention is finalized and hashed.

## Claim ceiling

A positive ALCF-V0 result may support only the bounded claim frozen in the preregistration. It does **not** establish a general capability/corrigibility tradeoff, a property of neural networks, or a property of frontier AI systems.

A clean null is a valid result:

\[
\Delta\operatorname{Cap}>0\not\Rightarrow\text{corrective foreclosure}.
\]

## Execution boundary

Implementation must instantiate the frozen protocol rather than revise it. Execution and scientific interpretation are separate later steps. Any ambiguity that cannot be resolved without changing protocol semantics is a protocol defect, not permission for a silent implementation choice.
