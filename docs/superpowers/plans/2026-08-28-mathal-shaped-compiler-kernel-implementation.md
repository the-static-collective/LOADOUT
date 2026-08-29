# LOADOUT Mathal-Shaped Compiler Kernel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Build the first deterministic executable LOADOUT compiler kernel with PROBE-BIND enforcement, ALEX envelope compatibility, 3rdi historical-fixture validation, counterfactual pressure operators, and a proposal-gated recompile hatch.

**Architecture:** Pure Python functions implement `REACH`, `DELTA`, `FENCE`, `BIND`, `TRACE`, `ABLATE`, compile canonicalization, decay checks, and proposal gating. External adapters consume immutable compile records; no operator performs network access or mints authority. Dogram shapes operator boundaries but is not imported.

**Tech Stack:** Python 3.11+, standard library only, pytest for tests, JSON files for schemas/fixtures.

**Spec:** `docs/superpowers/specs/2026-08-28-mathal-shaped-compiler-kernel-design.md`

## Global Constraints

- Standard library only in production code.
- `loadout.compile/v0` must remain byte-for-byte field compatible with the existing ALEX handshake key set.
- Canonical digests use SHA-256 over sorted compact JSON excluding the digest field itself.
- No dynamic code execution, network access, ambient plugin invocation, or authority inference.
- Reflection creates inert proposals only; gated admission is mandatory before recompile application.

---

### Task 1: PROBE-BIND kernel

**Files:**
- Create: `src/loadout/__init__.py`
- Create: `src/loadout/canonical.py`
- Create: `src/loadout/reach.py`
- Create: `src/loadout/fence.py`
- Create: `src/loadout/bind.py`
- Test: `tests/test_probe_bind.py`

**Interfaces:**
- Produces: `evaluate_binding(capability: dict, effect_fence: list[str]) -> dict`
- Produces: `reachable_effects(capability: dict) -> tuple[str, ...] | None`

- [x] Write tests for lens BIND, unfenced probe REFUSE, fenced probe BIND, unresolved reachability, label laundering, and parameter drift.
- [x] Run `pytest -q tests/test_probe_bind.py`; verify RED because `loadout.bind` does not exist.
- [x] Implement minimal deterministic reach/fence/bind functions and binding receipts.
- [x] Run `pytest -q tests/test_probe_bind.py`; verify GREEN.

### Task 2: Canonical compile and ALEX adapter

**Files:**
- Create: `src/loadout/compile.py`
- Create: `src/loadout/adapters/__init__.py`
- Create: `src/loadout/adapters/alex.py`
- Test: `tests/test_compile_and_alex.py`

**Interfaces:**
- Produces: `compile_loadout(spec: dict) -> dict`
- Produces: `to_alex_envelope(compile_record: dict, request: dict) -> dict`

- [x] Write tests asserting exact compile keys, stable digest, non-inherited effect authority, and exact ALEX envelope keys.
- [x] Run the task test and verify RED.
- [x] Implement minimal compiler and adapter.
- [x] Run the task test and verify GREEN.

### Task 3: Historical 3rdi witness

**Files:**
- Create: `src/loadout/history.py`
- Create: `fixtures/3rdi/loadout.manifest.json`
- Test: `tests/test_history.py`

**Interfaces:**
- Produces: `validate_historical_manifest(manifest: dict) -> list[str]`

- [x] Write a test proving the fixture is accepted as `loadout.manifest/v0` while remaining distinct from `loadout.compile/v0`.
- [x] Run and verify RED.
- [x] Implement minimal historical validator.
- [x] Run and verify GREEN.

### Task 4: DELTA, ABLATE, and task reachability

**Files:**
- Create: `src/loadout/delta.py`
- Create: `src/loadout/pressure/__init__.py`
- Create: `src/loadout/pressure/ablate.py`
- Test: `tests/test_pressure.py`

**Interfaces:**
- Produces: `record_delta(left: dict, right: dict) -> list[dict]`
- Produces: `ablate_binding(compile_record: dict, capability: str, new_compile_id: str) -> dict`
- Produces: `task_reachable(compile_record: dict) -> dict`

- [x] Write tests proving deterministic delta paths and that ablating a required capability changes reachability without mutating the parent compile.
- [x] Run and verify RED.
- [x] Implement minimal operators.
- [x] Run and verify GREEN.

### Task 5: Proposal-only recompile gate and decay

**Files:**
- Create: `src/loadout/decay.py`
- Create: `src/loadout/pressure/recompile.py`
- Test: `tests/test_recompile_gate.py`

**Interfaces:**
- Produces: `decay_reasons(compile_record: dict, observed_at: str, signals: dict | None = None) -> list[str]`
- Produces: `propose_recompile(base_compile: dict, patch: dict, *, reason: str, proposal_id: str, proposed_compile_id: str) -> dict`
- Produces: `gate_recompile_proposal(base_compile: dict, proposal: dict) -> dict`
- Produces: `apply_recompile_proposal(base_compile: dict, proposal: dict, gate_receipt: dict) -> dict`

- [x] Write tests proving expired compile decay, gate bypass refusal, proposal-digest tamper refusal, authority/capability non-expansion, and authorization-provenance preservation.
- [x] Run and verify RED.
- [x] Implement minimal decay/proposal/gate/application behavior.
- [x] Run and verify GREEN.

### Task 6: CLI, schemas, CI, and docs

**Files:**
- Create: `pyproject.toml`
- Create: `src/loadout/cli.py`
- Create: `src/loadout/__main__.py`
- Create: `schemas/compile-v0.schema.json`
- Create: `schemas/context-pack-v0.schema.json`
- Create: `schemas/recompile-proposal-v0.schema.json`
- Create: `.github/workflows/test.yml`
- Modify: `README.md`
- Test: `tests/test_cli.py`

**Interfaces:**
- Produces console command `loadout` with `bind`, `compile`, `envelope-alex`, `delta`, `reach`, `ablate`, `trace`, and `decay` subcommands that read JSON files and emit JSON to stdout.

- [x] Write CLI smoke tests before creating CLI production code.
- [x] Run and verify RED.
- [x] Implement CLI and packaging, then run all tests.
- [x] Add JSON schemas, CI workflow, and README executable-floor documentation.
- [x] Run `python -m compileall -q src` and `pytest -q` with zero failures.

## Verification receipt

- Local TDD suite: `24 passed`.
- `python -m compileall -q src`: exit 0.
- Editable package build/install: `python -m pip install -e . --no-deps --no-build-isolation`: exit 0 using installed setuptools 82.0.1.
- Console entry point: `loadout --help` exposes `bind`, `compile`, `envelope-alex`, `delta`, `reach`, `ablate`, `trace`, and `decay`.
- Network-isolated sandbox note: default pip build isolation could not contact PyPI; this is environmental, not a package test failure.
