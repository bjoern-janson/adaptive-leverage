# ALCF-V0 Faithful Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the frozen ALCF-V0 finite assay machinery and test suite without modifying preregistration bytes or executing the scientific assay.

**Architecture:** Use six small Python modules: immutable protocol symbols/state in `model.py`; canonical hash-chained events in `trace.py`; normal-workload-only intervention construction and custody in `interventions.py`; deterministic assay primitives and reachability/localization in `assay.py`; a pure decision-rule classifier in `classify.py`; package exports in `__init__.py`. The implementation is deterministic, has no network/random/time dependency, and treats software faults separately from frozen scientific classifications.

**Tech Stack:** Python >=3.11, standard library only for runtime code, `pytest>=8` for tests, `dataclasses`, `enum`, `hashlib`, `json`.

**Spec:** `docs/superpowers/specs/2026-09-13-alcf-v0-implementation-design.md`

## Global Constraints

- `prereg/ALCF_V0_PREREG_FROZEN.md` SHA-256 must remain `05e8edd5c9aa7d5e15cf46575eb1efe2c91d1674054e53e6ed3a23a94e7f8192`.
- `prereg/ALCF_V0_PROTOCOL_FROZEN.json` SHA-256 must remain `7b476c5020f0b81e6a1bceb712b877f5d52d0cbf6d99b0e164e7f705f06c1188`.
- Do not modify any file under `prereg/`.
- Do not execute the scientific assay or commit result/custody/trace artifacts.
- No randomness, wall-clock dependence, network access, or free-form protocol symbols.
- Arm `A` compiler accepts normal-workload inputs only; corrective artifacts are structurally absent from its public compile API.
- `E5A` remains a distinct observed edge and is never normalized to frozen `E5`/`E6`.
- Reachability and localization are trace-derived; endpoint action is insufficient.
- Programming faults raise implementation exceptions; they are never converted into scientific classifications.
- Positive/null fixtures in tests are software fixtures only, not scientific results.

## Execution Tasks

1. Add package metadata plus immutable finite state and exact baseline `E1`–`E6` paths, with tests written and observed failing first.
2. Add canonical JSON trace events, hash chaining, and mutation/deletion validation, test-first.
3. Add normal-workload-only `COMPILE_DISPATCH`, finalized-artifact hashing, custody manifests, leakage detection, and C/A/E state interventions, test-first.
4. Add deterministic precheck/fork/capability/correction primitives plus trace-derived reachability and first-missing-edge localization, test-first.
5. Add a pure frozen-rule classifier covering every stop/invalid/null/positive rule, test-first.
6. Add frozen-byte hash tests and run full clean validation; do not generate or commit assay result artifacts.

## Required Terminal State

```text
ALCF-V0 protocol        FROZEN
implementation spec     APPROVED
implementation          COMPLETE
software validation     PASS
assay execution         NOT STARTED
scientific result       NONE
```

Implementation completion is not a scientific result.