# ALCF-V2-0 Post-Run Repository Audit

**Audit status:** REVIEWED — NON-INVALIDATING FINDINGS

**Scientific object protected:** `ALCF-V2-0-001`

**Audit scope:** public repository state after fossilization of the first V2-0 scientific execution. This document records implementation-level findings identified by repository inspection. It does not modify or reinterpret the frozen scientific result.

## Provenance boundary

The canonical first scientific run is `ALCF-V2-0-001` and is fossilized under `scientific_runs/ALCF-V2-0-001/`. The scientific result record binds the run to the audited implementation `8fcad36b84caa8a496f29b16cf29257565c75a41`, audited tree `ca5f11510ce8348368cbf1254a784e48d72a0b29`, publication `main` at authorization `aed36ad4a2bc0980e43fa4b51818889eebb492a8`, provenance merge `3a92ea8dc7555849165a415e29698b2978f76888`, and implementation bundle SHA-256 `f136d36fbcfe5df9a1c0eadd1b382fb4ee20e34d8b7f28e0e4f76a31a98b00e0`.

This audit intentionally does **not** alter files under the scientific run directory and does not authorize or recommend a rerun.

## Finding A — explicit consequential-state transition is absent from replay

**Location:** `src/adaptive_leverage/v2/replay.py`

The replay engine represents state realization as a boolean predicate:

```text
resolved consequence AND LIVE write boundary
```

and then exposes the stored `state_update` / `terminal_action` fields as consequences. There is no explicit mutable or transition-verified consequential state object implementing:

```text
S0 --Delta S--> S1
```

before terminal action.

**Assessment:** non-invalidating for V2-0-001 under the frozen finite realization, because the protocol specifies a required consequential-state class but the finite implementation uses a typed write predicate as its realization mechanism. The distinction should nevertheless be made explicit in a future protocol so that `Delta S` is an observed transition rather than a labeled field plus permission bit.

**V2-1 recommendation:** represent the consequential state before and after replay and require terminal action to be causally downstream of the verified transition.

## Finding B — challenge token and reference consequence are coupled in the real adapter

**Location:** `src/adaptive_leverage/v2/replay.py`

The real adapter constructs both the opaque challenge token and the reference consequence from the same carrier state inside `_sealed_real_reference_for_state()`. The specification conceptually distinguishes:

```text
q*(x) -> z
```

from:

```text
(x, q*) -> kappa
```

but the runtime implementation materializes both through one helper.

**Assessment:** non-invalidating for V2-0-001. The frozen reference semantics remain independently specified and hash-custodied, and the run was admitted against those frozen objects. The implementation nevertheless does not provide maximal runtime separation between the challenge oracle and the reference-semantic oracle.

**V2-1 recommendation:** separate challenge-token generation from consequence semantics into independently sealed interfaces and verify their agreement at replay time instead of constructing both from one runtime helper.

## Finding C — `C_MF_obs` derives mismatch from transformation identity rather than a supplied predictor artifact

**Location:** `src/adaptive_leverage/v2/classify.py`

The classifier contains the fixed mapping:

```text
T_ALPHA -> M=0
T_BETA  -> M=1
```

and combines it with observed `F` to produce `C_MF_obs`. The pre-replay partition objects are still produced, hashed, admitted, and fossilized, but the classifier itself does not consume an explicit validated mismatch/predictor record.

**Assessment:** non-invalidating for V2-0-001 because joint admission binds the finalized dispatch/partition/predictor objects before corrective release, while the persisted run contains those objects. The standalone classifier is nevertheless less provenance-complete than the scientific architecture suggests.

**V2-1 recommendation:** pass a validated pre-replay predictor object into classification and derive `C_MF_obs` from that object plus `F`, rather than maintaining arm-identity-to-M mappings inside the classifier.

## Finding D — release token is an API-level construction guard, not cryptographic authorization

**Location:** `src/adaptive_leverage/v2/assay.py`

`CorrectiveReleaseToken` requires an internal nonce object during construction, preventing ordinary callers from instantiating a token through the public dataclass constructor. However, this is a Python process-local guard, not a cryptographic unforgeability mechanism.

**Assessment:** non-invalidating and appropriate to the current finite software model. The assay is not specified as an adversarial process-isolation or cryptographic authorization system.

**V2-1 recommendation:** describe the invariant as an API/process construction guard unless a future protocol explicitly requires cryptographic or process-isolated authorization semantics.

## Finding E — execution surface does not itself require an empty result directory

**Location:** `src/adaptive_leverage/v2/runner.py` and artifact writers

The artifact layer refuses to overwrite an existing file with different bytes, which protects custody, but the runner does not itself require the requested output directory to be absent or empty before execution.

**Assessment:** non-invalidating for V2-0-001. The first run was executed from the validated clean boundary and the resulting artifact set was independently hashed and audited.

**V2-1 recommendation:** enforce an explicit fresh-output precondition or record a verified empty-directory state before scientific release.

## What these findings do not show

This audit does **not** establish that:

- the V2-0-001 scientific result is invalid;
- the raw `R` matrix was fabricated or replaced;
- the observed directional result was selected from the design-time expectation;
- the frozen finite realization was altered after execution;
- partition mismatch is necessary or sufficient for corrective foreclosure.

The committed scientific result remains the bounded statement recorded in `scientific_runs/ALCF-V2-0-001/SCIENTIFIC_RESULT.md`.

## Preservation rule

These findings are prospective engineering/protocol guidance. They must not be used to modify the V2-0-001 apparatus or replace its first-run outcome. Any corrective implementation changes belong to a separately identified future protocol/result identity.
