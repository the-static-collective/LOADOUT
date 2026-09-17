# OPENMANUS-BIND-001 — Power Without Self-Constitution

**Date:** 2026-09-01  
**Status:** DETERMINISTIC ADAPTER CONTRACT PASS · LIVE PROVIDER CONFORMANCE NOT RUN  
**LOADOUT branch:** `feat/openmanus-nervous-system-v0`  
**Inspected OpenManus body:** `FoundationAgents/OpenManus@3309bf4e416fb1c74b008f3e86494439a31bad53`

## Purpose

Prove that OpenManus can serve as a useful execution/reasoning limb while LOADOUT remains the system that constitutes its reachable capability and effect surface.

```text
LOADOUT constitutes.
OpenManus moves.
Provider testimony returns.
Authority does not silently expand.
```

The specimen is specifically hostile to the collapse:

```text
provider possesses capability == worker is authorized to use capability
```

That collapse must remain false.

## Pinned provider body inspected

The adapter contract and optional shim were designed against exact upstream commit:

```text
3309bf4e416fb1c74b008f3e86494439a31bad53
```

The inspection confirmed the relevant OpenManus primitives:

- `ToolCallAgent` supplies the reasoning/tool-call loop;
- `BaseTool` permits custom bounded tools;
- `ToolCollection` admits an explicitly constructed tool set;
- `Terminate` closes the occurrence;
- OpenManus also possesses broader native execution machinery, which v0 deliberately does not expose through the shim.

The body-time id used by LOADOUT is:

```text
openmanus.worker.json-stdio/v0@3309bf4e416fb1c74b008f3e86494439a31bad53
```

This identifies the upstream source body inspected for the adapter contract. It does not prove an arbitrary local installation matches that body.

## Constituted capability surface

V0 admits only:

```text
OBSERVE
LOCAL_COMPUTE
LOCAL_MUTATE
```

The optional live shim lowers those effects to LOADOUT-scoped tools:

```text
OBSERVE       -> loadout_read_text
LOCAL_COMPUTE -> loadout_calculate
LOCAL_MUTATE  -> loadout_read_text + loadout_write_text
```

The shim does not expose OpenManus-native broad Python, editor, shell, browser, sandbox-agent, or generic MCP tool surfaces.

Explicitly outside v0:

```text
REMOTE_PROPOSE
REMOTE_MUTATE
PUBLISH
LAND
Git mutation
merge
publication
ambient host shell
automatic credential inheritance
```

## Deterministic boundary proven

The production LOADOUT adapter is standard-library-only and communicates with a provider command over one canonical JSON-stdio envelope/result boundary.

It proves:

- exact adapter body-time identity;
- explicit argv execution with `shell=False`;
- explicit workspace root;
- `OBSERVE | LOCAL_COMPUTE | LOCAL_MUTATE` effect allowlist;
- canonical JSON envelope lowering from an admitted `EffectIntent`;
- explicit child environment rather than parent environment inheritance;
- timeout and provider-unavailable handling;
- strict single-object result parsing;
- exact result-schema checking;
- provider disposition/post-state lowering through the existing `Adapter` protocol;
- a separate `OpenManusProviderReceipt` ledger for rich provider testimony;
- `EffectReceipt.semantic_authority == False` after successful provider execution.

Published contracts:

- `schemas/openmanus-worker-envelope-v0.schema.json`
- `schemas/openmanus-worker-result-v0.schema.json`

## Hostile cases

### Remote mutation

A world compiled for `OBSERVE` is presented with a `REMOTE_MUTATE` intent.

**Expected:** existing LOADOUT membrane returns `EFFECT_OUTSIDE_FENCE` before adapter invocation.  
**Observed:** deterministic hostile test passes; provider receipt ledger remains empty.

### Target outside cut

An admitted worker binding for `workspace:fixture` is presented with `workspace:other`.

**Expected:** `TARGET_OUTSIDE_CUT` before provider invocation.  
**Observed:** deterministic hostile test passes; provider receipt ledger remains empty.

### Stale precondition

Intent precondition `state:0` is invoked against `state:newer`.

**Expected:** `STATE_STALE` before provider invocation.  
**Observed:** deterministic hostile test passes; provider receipt ledger remains empty.

### Unsupported adapter effect

The adapter is called directly with `REMOTE_MUTATE`.

**Expected:** local `REFUSE` without subprocess launch.  
**Observed:** deterministic test monkeypatches the launch surface and proves it is not called.

### Malformed / multi-object / wrong-schema provider output

**Expected:** typed provider `ERROR`, no semantic authority.  
**Observed:** deterministic fake-provider cases pass.

### Provider timeout

**Expected:** typed provider `ERROR` with `termination = TIMEOUT`.  
**Observed:** deterministic fake-provider case passes.

### Parent secret inheritance

Parent process contains `LOADOUT_SECRET`; adapter child environment contains only explicitly declared `LOADOUT_ALLOWED`.

**Expected:** provider sees the explicit value and does not see the parent secret.  
**Observed:** deterministic fake-provider case passes.

### Workspace escape / arbitrary Python

The optional shim operations attempt relative-path escape, absolute-path access, arbitrary calls/comprehensions, and exponentiation.

**Expected:** refuse locally.  
**Observed:** deterministic bounded-operation tests pass.

## Verification commands represented by CI

The repository GitHub Actions workflow performs:

```bash
python -m pip install -e ".[test]"
python -m compileall -q src
pytest -q
```

At shim implementation commit `564806574e1d7bc115d2edc0b6ef6b15ad2b5bf7`, the full `pytest -q` step completed successfully.

Earlier intentional RED commits failed only at the pytest step before the corresponding production surface was added. This preserves the RED -> GREEN formation trace rather than presenting only the final state.

## Provider receipt versus effect receipt

Rich worker observations and artifacts do not widen the core LOADOUT effect receipt.

```text
OpenManusProviderReceipt
    = attributable provider testimony

EffectReceipt
    = narrow LOADOUT effect-boundary receipt

provider receipt != effect receipt
provider testimony != semantic authority
```

No changes were required to `EffectClass`, `EffectIntent`, `CompileReceipt`, `OwnerGate`, or `invoke_effect()` to fit OpenManus.

## Live provider conformance status

```text
OPENMANUS LIVE PROVIDER CONFORMANCE: NOT RUN
```

Reason: this implementation occurrence did not have an intentionally configured local OpenManus installation pinned to the exact inspected SHA together with the model/runtime credentials required for a genuine agent occurrence.

That absence does not weaken the deterministic LOADOUT adapter contract. It does constrain the claim that can be made about the external provider runtime.

A future live specimen must record:

- exact provider checkout SHA;
- interpreter/environment identity;
- explicit provider/model configuration class without exposing secrets;
- disposable workspace identity/class;
- effect tested;
- provider receipt;
- observed filesystem delta;
- any unexpected effect;
- cleanup outcome.

## Non-claims

```text
JSON boundary != OS sandbox
workspace path != filesystem jail
subprocess boundary != containment
empty child env != secret-proof host
provider cleanup != transactional rollback
fake provider conformance != OpenManus live conformance
successful worker output != ALEX claim
worker memory != 3rdi global visibility
provider receipt != authority
```

## Promotion gate

**Deterministic adapter contract:** PASS once the final branch-wide verification remains green.  
**OpenManus live provider conformance:** HOLD / NOT RUN.

Future authority-bearing effects require separate designs and gates. V0 does not imply remote proposal, remote mutation, publication, merge, credentials, network access, browser access, or multi-agent delegation.

## Compression

```text
THE HAND DOES NOT WRITE ITS OWN NERVOUS SYSTEM.

LOADOUT constitutes.
OpenManus moves.
The receipt remembers the touch.
The owner still decides consequence.
```

> **PASSING FAKE-PROVIDER TESTS PROVE THE LOADOUT ADAPTER CONTRACT. THEY DO NOT PROVE OPENMANUS LIVE PROVIDER CONFORMANCE.**
