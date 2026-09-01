# OpenManus Nervous-System v0 Design

**Date:** 2026-09-01  
**Status:** DIRECTION APPROVED · DESIGN FOR REVIEW · IMPLEMENTATION NOT YET ADMITTED  
**Repository:** `the-static-collective/LOADOUT`  
**External provider:** `FoundationAgents/OpenManus`  
**Initial upstream pin:** `3309bf4e416fb1c74b008f3e86494439a31bad53`

## 0. Decision

LOADOUT will gain a provider adapter that can constitute and invoke a **bounded, mortal OpenManus worker** without granting OpenManus authority to decide its own world.

Core relation:

```text
LOADOUT = nervous system / constitution
OpenManus = execution limb
ALEX = provenance and claim discipline
3rdi = observer-local projection discipline
human / owner gate = authority
```

The adapter is not a second planner, policy engine, or semantic authority system.

```text
provider intelligence != provider authority
available tool != bound capability
worker memory != evidence store
worker observation != truth
successful execution != admission
receipt != authority
```

## 1. Why this seam exists

`LOADOUT.dev/v0` already owns task cuts, provider-independent capability names, effect classes, adapter/body binding, owner gates, effect intents, effect receipts, and refusal when requested effects exceed the constituted world.

The missing surface is live provider orchestration: carrying one already-compiled effect intent across an external execution boundary and returning an attributable result.

OpenManus supplies useful machinery LOADOUT should not duplicate:

- stepwise agent execution;
- local and MCP tool invocation;
- browser automation;
- Python and file operations;
- sandbox variants;
- replaceable LLM providers;
- explicit lifecycle cleanup.

The v0 design therefore treats OpenManus as an **untrusted effectful provider** behind the existing LOADOUT membrane.

## 2. Chosen integration shape

### 2.1 JSON-stdio subprocess boundary

V0 uses a subprocess/JSON-stdio adapter rather than importing OpenManus into the LOADOUT process.

```text
CompileReceipt + EffectIntent
            ↓
LOADOUT membrane checks
            ↓
OpenManusAdapter
            ↓
canonical worker envelope (JSON)
            ↓
provider command over stdin/stdout
            ↓
canonical provider result (JSON)
            ↓
EffectReceipt
```

Reasons:

1. LOADOUT remains Python-standard-library-only.
2. OpenManus dependency churn stays outside LOADOUT.
3. The provider executable can be pinned and replaced independently.
4. Process environment and inherited capabilities can be explicitly narrowed.
5. Replay can bind to exact provider body time.
6. Tests can use a deterministic fake provider command without installing OpenManus.

### 2.2 Rejected alternatives

**In-process import:** rejected for v0 because it collapses dependency and lifecycle boundaries and makes provider internals part of LOADOUT's runtime constitution.

**MCP-only integration:** deferred. OpenManus can consume MCP and expose MCP tooling, but v0 needs one narrow worker-envelope contract rather than ambient exposure of generic `bash`/`editor`-class tools.

**Multi-agent OpenManus flow:** deferred. The first proof requires one mortal worker, not a provider-local society whose internal delegation becomes difficult to attribute.

## 3. V0 capability surface

The first OpenManus adapter may advertise only these provider-independent effect classes:

```text
OBSERVE
LOCAL_COMPUTE
LOCAL_MUTATE
```

`LOCAL_MUTATE` is restricted to a declared sandbox/workspace root.

The adapter MUST NOT advertise or perform in v0:

```text
REMOTE_PROPOSE
REMOTE_MUTATE
PUBLISH
LAND
credential discovery
ambient host-shell authority
Git write operations
repository merge operations
external publication
```

A provider may internally possess broader machinery. Unadvertised provider machinery is outside the constituted world and must not become reachable through the adapter.

## 4. Provider body identity

The adapter body remains governed by the existing `AdapterBody` law:

```text
body_time_id = adapter_id@source_sha
authority = none
```

V0 adapter id:

```text
openmanus.worker.json-stdio/v0
```

Initial body time:

```text
openmanus.worker.json-stdio/v0@3309bf4e416fb1c74b008f3e86494439a31bad53
```

The upstream SHA identifies the OpenManus source body the adapter contract was inspected against. It does not claim that arbitrary local provider installations actually match that source. Runtime launch configuration must separately identify the provider command used for the occurrence.

Replay with an unpinned body remains refused by the existing compiler.

## 5. Worker envelope

The adapter lowers one already-admitted `EffectIntent` into a canonical JSON object.

Schema name:

```text
loadout.openmanus-worker-envelope/v0
```

Required fields:

```json
{
  "schema": "loadout.openmanus-worker-envelope/v0",
  "body_time_id": "openmanus.worker.json-stdio/v0@<sha40>",
  "capability": "provider-independent capability name",
  "effect": "OBSERVE | LOCAL_COMPUTE | LOCAL_MUTATE",
  "target": "declared LOADOUT target",
  "precondition_state": "caller supplied state id",
  "parameters_digest": "caller supplied digest",
  "parameters": {"bounded": "string map"},
  "workspace_root": "/declared/sandbox/root",
  "max_steps": 20
}
```

The envelope carries no owner authority and no semantic authority.

The adapter does not generate task policy from prose. It translates an admitted effect intent.

## 6. Provider result

The provider command must return exactly one JSON result object on stdout.

Schema name:

```text
loadout.openmanus-worker-result/v0
```

Required shape:

```json
{
  "schema": "loadout.openmanus-worker-result/v0",
  "disposition": "COMPLETED | REFUSED | ERROR",
  "observed_post_state": "string-or-null",
  "artifacts": [],
  "observations": [],
  "provider_receipt": {
    "steps_executed": 0,
    "termination": "string"
  }
}
```

`observations` and `artifacts` are provider testimony. They do not become ALEX claims, 3rdi projections, canonical repository state, or owner decisions merely by being returned.

`EffectReceipt.semantic_authority` remains `False`.

## 7. Adapter responsibilities

Create `OpenManusJsonStdioAdapter` implementing the existing `Adapter` protocol:

```python
body_time_id: str
invoke(intent: EffectIntent) -> tuple[str, str | None]
```

The adapter owns only transport-boundary checks and execution translation.

It MUST:

- verify its body-time id at construction;
- accept only an explicit provider command argv tuple;
- accept only an explicit workspace root;
- reject unsupported effect classes before launch;
- convert bounded parameters using existing `parameter_map()`;
- reject duplicate or malformed parameters through existing model law;
- encode one canonical JSON envelope;
- launch without a shell;
- provide the envelope on stdin;
- enforce an execution timeout;
- capture stdout and stderr separately;
- reject empty, malformed, multi-object, or wrong-schema stdout;
- map provider `COMPLETED`, `REFUSED`, and `ERROR` to provider dispositions without claiming semantic authority;
- return an attributable post-state only when the provider supplies one;
- avoid mutating the parent process environment.

It MUST NOT:

- call `shell=True`;
- interpolate task text into a shell command;
- infer additional capabilities from the provider executable;
- grant network, Git, publication, or credential reach not represented by the compiled binding;
- reinterpret provider observations as evidence conclusions.

## 8. Environment discipline

The subprocess receives a caller-declared environment allowlist, not `os.environ` wholesale.

V0 default inherited environment is empty except for explicitly configured transport/runtime variables required to locate the provider executable.

Secrets are not automatically forwarded.

This is intentionally stricter than ordinary OpenManus local execution. If a later task needs an API key, browser credential, network token, or remote account, that becomes a separately designed capability and authority crossing.

## 9. Workspace discipline

`workspace_root` is resolved before invocation.

For `LOCAL_MUTATE`:

- the root must exist;
- the root must be explicitly declared in adapter configuration;
- the target must remain inside the LOADOUT cut;
- the adapter contract promises only that LOADOUT passed this boundary deliberately.

V0 does not claim OS-level confinement merely because a path was declared. Real sandbox enforcement belongs to the provider/runtime configuration and must be reported as such.

Therefore:

```text
declared workspace fence != kernel sandbox
provider sandbox claim != LOADOUT proof
```

A later `SandboxManus` integration may strengthen this boundary without changing the provider-independent LOADOUT effect model.

## 10. OpenManus-side shim

V0 adds a small provider-side shim script outside LOADOUT's import graph. The shim's job is intentionally mechanical:

```text
read one envelope
validate schema
construct one Manus/SandboxManus occurrence
expose only envelope-selected provider tools
run bounded request
emit one result object
cleanup
exit
```

The shim is the only OpenManus-aware component. LOADOUT knows only the JSON contract.

The initial shim may live in `contrib/openmanus/` in LOADOUT as integration glue, but it must remain optional and outside the production `loadout` package dependency graph.

## 11. First proving specimen — OPENMANUS-BIND-001

The first hostile specimen proves **power without self-constitution**.

Constituted world:

```text
Target: temporary sandbox fixture
Allowed:
  - bounded read
  - local Python computation
  - local write under sandbox root
Forbidden:
  - Git mutation
  - network publication
  - host credential access
  - writes outside sandbox root
```

Test sequence:

1. Compile a world that binds one OpenManus body to the three allowed effect classes.
2. Invoke an `OBSERVE` intent and preserve the provider invocation receipt.
3. Invoke `LOCAL_COMPUTE` and verify an attributable returned post-state.
4. Invoke `LOCAL_MUTATE` inside the declared sandbox fixture.
5. Attempt an unsupported remote mutation and prove refusal occurs before provider launch.
6. Attempt a target outside the compile cut and prove refusal occurs before provider launch.
7. Attempt with stale precondition state and prove refusal occurs before provider launch.
8. Attempt with a wrong body-time id and prove refusal occurs before provider launch.
9. Feed malformed provider JSON and map it to provider refusal/error without semantic authority.
10. Compare declared reachable effects with observed provider effects in the eval receipt.

Pass condition:

> The worker can perform useful bounded work, but cannot enlarge its constituted capability surface by possessing additional OpenManus tools.

## 12. Testing strategy

V0 uses TDD and separates contract proof from live-provider proof.

### Deterministic contract tests

A fake JSON-stdio provider executable proves:

- exact envelope shape;
- argv execution without shell;
- environment allowlisting;
- effect allowlisting;
- timeout behavior;
- stdout/stderr separation;
- malformed-result refusal;
- deterministic result mapping;
- no provider launch after membrane refusal.

These tests run in ordinary CI without OpenManus.

### Optional live integration test

A separately marked test may execute the pinned OpenManus shim when the provider environment is explicitly installed and configured.

Failure or absence of the live provider must not falsify the deterministic LOADOUT contract tests.

Passing fake-provider tests does not claim OpenManus runtime conformance.

## 13. Files expected in the first implementation

Likely new files:

```text
src/loadout/dev/openmanus.py
schemas/openmanus-worker-envelope-v0.schema.json
schemas/openmanus-worker-result-v0.schema.json
contrib/openmanus/worker.py
tests/fixtures/fake_openmanus_provider.py
tests/test_dev_openmanus.py
evals/OPENMANUS-BIND-001.md
```

Likely modified files:

```text
src/loadout/dev/__init__.py
README.md
```

No change to `EffectClass`, `EffectIntent`, `CompileReceipt`, `OwnerGate`, or the core membrane is required unless implementation evidence proves a real missing invariant.

That last restriction is deliberate: OpenManus must fit the nervous system before the nervous system changes to fit OpenManus.

## 14. Error and refusal model

Use existing provider refusal vocabulary where possible:

```text
PROVIDER_UNAVAILABLE
PROVIDER_REFUSED
```

Transport/schema errors remain provider failures rather than new authority states.

If implementation reveals a distinction that changes caller behavior materially, add the smallest new refusal reason only after a failing test demonstrates the need.

## 15. Security posture

V0 is a bounded orchestration proof, not a secure sandbox product.

Explicit non-claims:

```text
JSON boundary != sandbox
subprocess boundary != containment
workspace path != filesystem jail
empty env != secret-proof host
provider refusal != effect rollback
OpenManus cleanup != transactional execution
```

Consequently the first live specimen should run only against disposable local material.

## 16. Neighbor ownership after integration

### LOADOUT
Constitutes the worker world, binds capabilities, fences effects, issues intents, and records effect receipts.

### OpenManus
Executes only the provider work admitted through the adapter occurrence and returns observations/artifacts.

### ALEX
May ingest attributable returned source observations and decide how they participate in evidence formation. Worker output is not automatically a claim.

### 3rdi
May project worker observations under declared observer/cut/decoder coordinates. Worker memory is not global visibility.

### Human / owning world
Retains authority for publication, merge, remote mutation, adoption, and consequence.

## 17. Promotion gates

V0 may be called a working adapter only after deterministic contract tests pass.

A stronger claim — `OPENMANUS LIVE PROVIDER CONFORMANCE` — requires an actual pinned-provider specimen and its receipt.

Future gates, separately designed:

1. Browser-only worker capability.
2. Network observation capability.
3. Credential-bearing provider occurrences.
4. Remote proposal effects.
5. Owner-gated remote mutation.
6. MCP-composed worker organs.
7. Multi-agent internal delegation with attributable sub-worker receipts.

None are implied by v0.

## 18. Compression

```text
LOADOUT constitutes.
OpenManus moves.
ALEX remembers where the claim came from.
3rdi remembers who could see it.
The owner decides what becomes consequence.

THE HAND DOES NOT WRITE ITS OWN NERVOUS SYSTEM.
```
