# ALCF-V2-0-001 — First Scientific Execution

**Status:** VALID first scientific execution. This is the canonical first V2-0 run and must not be rerun to replace its outcome.

## Execution anchors

- Publication `main` at authorization: `aed36ad4a2bc0980e43fa4b51818889eebb492a8`
- Provenance merge: `3a92ea8dc7555849165a415e29698b2978f76888`
- Audited implementation: `8fcad36b84caa8a496f29b16cf29257565c75a41`
- Audited implementation tree: `ca5f11510ce8348368cbf1254a784e48d72a0b29`
- Implementation bundle SHA-256: `f136d36fbcfe5df9a1c0eadd1b382fb4ee20e34d8b7f28e0e4f76a31a98b00e0`
- Final pre-execution STOP audit SHA-256: `0e934446744101b0f449914bd62917b6559d594366658e0eebd0689ced1d9f74`
- Scientific joint admission SHA-256: `1fc1f4c166ba87457ffdf4d23229e12742764e3197165dea91218aec57d35f57`

The run was authorized by the user message `lets roll` after the validated-but-unexecuted boundary had been made explicit.

## Primary empirical object: raw corrective reachability

The empirical anchor is `results/raw_R_matrix.json`. For each arm, the four bits below are ordered `(s00,s01,s10,s11)`, with `1` meaning the warranted corrective route was nonempty and `0` meaning it was empty.

```text
T_ALPHA  REFINE     LIVE       1111
T_ALPHA  REFINE     BLOCKED    0000
T_ALPHA  NO_REFINE  LIVE       1111
T_ALPHA  NO_REFINE  BLOCKED    0000
T_BETA   REFINE     LIVE       1111
T_BETA   REFINE     BLOCKED    0000
T_BETA   NO_REFINE  LIVE       0000
T_BETA   NO_REFINE  BLOCKED    0000
```

## Mechanically derived observations

From the persisted raw `R` matrix:

```text
T_ALPHA  REFINE     LIVE       F=0
T_ALPHA  REFINE     BLOCKED    F=1
T_ALPHA  NO_REFINE  LIVE       F=0
T_ALPHA  NO_REFINE  BLOCKED    F=1
T_BETA   REFINE     LIVE       F=0
T_BETA   REFINE     BLOCKED    F=1
T_BETA   NO_REFINE  LIVE       F=1
T_BETA   NO_REFINE  BLOCKED    F=1
```

The observed logical cell set is:

```math
\mathcal C_{MF}^{obs}=\{(0,0),(0,1),(1,0),(1,1)\}.
```

The frozen matched contrasts are:

```text
D[REFINE, LIVE]        = 0
D[REFINE, BLOCKED]     = 0
D[NO_REFINE, LIVE]     = +1
D[NO_REFINE, BLOCKED]  = 0
```

## Bounded interpretation

Under the fixed downstream topology `(G,L)=(NO_REFINE,LIVE)`, the prospectively measured mismatch arm foreclosed where the aligned arm did not.

This is a **finite-assay directional result**. It is consistent with the Correction-Partition Hypothesis in that preregistered stratum, but it is not a general causal law.

The result also contains important negative information:

- `(1,0)` was observed, so partition mismatch is **not sufficient** for foreclosure in this assay.
- `(0,1)` was observed, so partition alignment is **not sufficient** for preservation in this assay.
- Under `REFINE × LIVE`, downstream refinement recovered enough distinction that both transformations preserved corrective reachability.
- Under `BLOCKED`, the write boundary foreclosed correction in both transformations, so partition structure did not discriminate outcome there.

A representative mechanism trace is the `T_BETA × NO_REFINE × LIVE` family. Its candidate set can remain heterogeneous across independently frozen corrective-consequence classes, leaving the warranted consequence unresolved and the qualified corrective route absent. Under generic `REFINE`, the candidate set can be reduced to a correction-homogeneous singleton, after which the state write and qualified route become executable.

A useful bounded mechanistic summary is therefore:

```text
prospective partition mismatch
        ↓
unresolved corrective consequence
        ↓
route loss
```

**only when the available downstream topology does not recover the distinction required for correction.**

## Non-claims

ALCF-V2-0-001 does **not** establish:

- `M=1 ⇒ F=1`;
- `M=0 ⇒ F=0`;
- that partition mismatch is necessary or sufficient for corrective foreclosure;
- a general safety/corrigibility theorem;
- a claim about neural networks, transformers, frontier models, or AGI;
- equivalence with MATRIX or any broader representation theory.

The primary scientific object remains the persisted raw `R` matrix and its 32 isolated replay traces. All interpretation is downstream of those observations.

## Custody

- `results/SHA256SUMS.txt` verifies the scientific result artifacts created by the runner.
- `ALCF_V2_0_001_FIRST_SCIENTIFIC_EXECUTION_RECORD.json` records the run-level derived objects and independent recomputation checks.
- `ALCF_V2_0_001_EXECUTION_ANCHOR.json` records execution provenance.
- `ALCF_V2_0_IMPLEMENTATION_COMPLETE_STOP_AUDIT.json` preserves the final validated-but-unexecuted software boundary immediately preceding science.
- `ARCHIVE_IDENTITY.json` records the exact original ZIP archive identity.
- No second scientific execution was performed during fossilization.
