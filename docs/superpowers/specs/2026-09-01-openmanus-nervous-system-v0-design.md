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
provider receipt != effect receipt
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
OpenManusJsonStdioAdapter
            ↓
canonical worker envelope (JSON)
            ↓
provider command over stdin/stdout
            ↓
canonical provider result (JSON)
            ↓
OpenManusProviderReceipt ledger
            ↓
(provider disposition, observed post-state)
            ↓
existing EffectReceipt
```

Reasons:

1. LOADOUT remains Python-standard-library-only.
2. OpenManus dependency churn stays outside LOADOUT.
3. The provider executable can be pinned and replaced independently.
4. Process environment and inherited capabilities can be explicitly narrowed.
5. Replay can bind to exact provider body time.
6. Tests can use a deterministic fake provider command without installing OpenManus.
7. Rich provider testimony stays distinct from the narrow cross-provider `EffectReceipt`.

### 2.2 Rejected alternatives

**In-process import:** rejected for v0 because it collapses dependency and lifecycle boundaries and makes provider internals part of LOADOUT's runtime constitution.

**MCP-only integration:** deferred. OpenManus can consume MCP and expose MCP tooling, but v0 needs one narrow worker-envelope contract rather than ambient exposure of generic `bash`/`editor`-class tools.

**Multi-agent OpenManus flow:** deferred. The first proof requires one mortal worker, not a provider-local society whose internal delegation becomes difficult to attribute.

## 3. V0 capability surface

The first adapter body may advertise provider-independent capabilities whose effect classes are restricted to:

```text
OBSERVE
LOCAL_COMPUTE
LOCAL_MUTATE
```

`LOCAL_MUTATE` is restricted at the LOADOUT envelope level to a declared workspace target. This is a constitutional fence, not an OS sandbox claim.

The adapter MUST NOT advertise in v0:

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

A provider may internally possess broader machinery. Possession does not constitute permission. Deterministic v0 tests prove LOADOUT refuses requests outside the bound surface before provider launch. Actual provider-side containment is a separate live-conformance claim.

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

The upstream SHA identifies the OpenManus source body the adapter contract was inspected against. It does not claim that an arbitrary local provider installation matches that source. Runtime launch configuration separately identifies the provider command used for the occurrence.

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
  "target": "workspace:<relative-posix-path>",
  "precondition_state": "caller supplied state id",
  "parameters_digest": "caller supplied digest",
  "parameters": {"bounded": "string map"},
  "workspace_root": "/declared/workspace/root",
  "max_steps": 20
}
```

### 5.1 V0 target grammar

For this adapter, targets use:

```text
workspace:.
workspace:path/to/object
```

Rules:

- the suffix is a relative POSIX path;
- absolute paths refuse;
- `..` traversal refuses;
- the resolved path must remain under the configured `workspace_root`;
- the exact target string still must already be present in the LOADOUT compile cut.

This gives the adapter a deterministic target boundary without redefining global LOADOUT target semantics.

The envelope carries no owner authority and no semantic authority.

The adapter does not generate task policy from prose. It translates an admitted effect intent.

## 6. Provider result and provider receipt

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

The adapter validates this object and converts it into an immutable `OpenManusProviderReceipt` containing:

```text
body_time_id
capability
effect
target
precondition_state
parameters_digest
provider_disposition
observed_post_state
artifacts
observations
steps_executed
termination
stderr
```

`OpenManusJsonStdioAdapter` preserves these receipts in occurrence-local insertion order through a read-only tuple view, e.g. `provider_receipts`.

The existing `Adapter.invoke()` protocol remains unchanged:

```python
invoke(intent: EffectIntent) -> tuple[str, str | None]
```

After recording the rich provider receipt, it returns only:

```text
(provider_disposition, observed_post_state)
```

The existing membrane then constructs the cross-provider `EffectReceipt` with `semantic_authority=False`.

Therefore:

```text
OpenManusProviderReceipt != EffectReceipt
provider testimony != semantic conclusion
```

`observations` and `artifacts` are attributable provider testimony. ALEX or 3rdi may consume them only through an explicit later handoff; they do not silently enter those systems.

## 7. Adapter responsibilities

Create `OpenManusJsonStdioAdapter` implementing the existing `Adapter` protocol.

Construction inputs:

```text
body_time_id
command_argv
workspace_root
timeout_seconds
max_steps
environment
```

The adapter owns only transport-boundary checks and execution translation.

It MUST:

- verify the exact `openmanus.worker.json-stdio/v0@<sha40>` body-time form at construction;
- accept only a non-empty explicit provider command argv tuple;
- accept only an explicit existing workspace root;
- reject unsupported effect classes before launch;
- validate the provider-specific workspace target grammar before launch;
- convert bounded parameters using existing `parameter_map()`;
- reject duplicate or malformed parameters through existing model law;
- encode one canonical JSON envelope;
- launch without a shell;
- provide the envelope on stdin;
- enforce a positive execution timeout;
- capture stdout and stderr separately;
- reject empty, malformed, multi-object, or wrong-schema stdout;
- preserve one `OpenManusProviderReceipt` for every launched occurrence, including provider refusal/error;
- map provider `COMPLETED`, `REFUSED`, and `ERROR` to provider dispositions without claiming semantic authority;
- return an attributable post-state only when the provider supplies one;
- avoid mutating the parent process environment.

It MUST NOT:

- call `shell=True`;
- interpolate task text into a shell command;
- infer additional capabilities from the provider executable;
- grant network, Git, publication, or credential reach merely because the provider possesses such machinery;
- reinterpret provider observations as evidence conclusions;
- modify `EffectClass`, `EffectIntent`, `CompileReceipt`, `OwnerGate`, or the core membrane merely to carry OpenManus-specific detail.

## 8. Environment discipline

The subprocess receives a caller-declared environment mapping, not `os.environ` wholesale.

V0 default child environment is empty. The caller must explicitly supply any variables required to locate or operate the provider runtime.

Provider argv should use absolute executable paths when an empty `PATH` would otherwise make resolution ambiguous.

Secrets are not automatically forwarded.

This is intentionally stricter than ordinary OpenManus local execution. If a later task needs an API key, browser credential, network token, or remote account, that becomes a separately designed capability and authority crossing.

## 9. Workspace discipline

`workspace_root` is resolved during adapter construction.

For all v0 targets:

- the root must exist and be a directory;
- the target suffix must be relative;
- path traversal and absolute target suffixes refuse before provider launch;
- envelope paths resolve beneath the declared root.

These checks prove what LOADOUT handed to the provider. They do not prove what arbitrary provider code could do afterward.

```text
declared workspace fence != kernel sandbox
validated envelope path != filesystem jail
provider sandbox claim != LOADOUT proof
```

A later live-conformance gate may use OpenManus `SandboxManus`, a container, or another externally enforced sandbox. That strengthening must not change the provider-independent LOADOUT effect model.

## 10. OpenManus-side shim

V0 adds a small provider-side shim outside LOADOUT's import graph. Its mechanical contract is:

```text
read one envelope
validate schema/body time
disable default browser attachment unless explicitly designed later
construct one bounded OpenManus occurrence
run one request
emit one result object
cleanup
exit
```

The shim is the only OpenManus-aware component. LOADOUT knows only the JSON contract.

The initial shim lives in `contrib/openmanus/worker.py`, remains optional, and is outside the production `loadout` package dependency graph.

### 10.1 Tool discipline

The shim MUST NOT simply instantiate vanilla `Manus` and accept all default tools as proof of bounded capability.

For the first live specimen it must construct an OpenManus `ToolCallAgent` occurrence with an explicitly supplied tool collection appropriate to that specimen, or run the worker in an externally enforced sandbox whose reachable effects are separately attributable.

The deterministic LOADOUT tests do not depend on this shim and do not claim live provider containment.

## 11. First proving specimen — OPENMANUS-BIND-001

The deterministic specimen proves **constitution before provider launch**.

Constituted world:

```text
Target: temporary workspace fixture
Allowed effect classes:
  - OBSERVE
  - LOCAL_COMPUTE
  - LOCAL_MUTATE
Forbidden bindings:
  - REMOTE_PROPOSE
  - REMOTE_MUTATE
  - PUBLISH
  - LAND
```

Test sequence:

1. Compile a world that binds one exact OpenManus adapter body to three fixture capabilities using the allowed effect classes.
2. Invoke an `OBSERVE` intent and preserve both the narrow `EffectReceipt` and rich provider receipt.
3. Invoke `LOCAL_COMPUTE` and verify an attributable returned post-state.
4. Invoke `LOCAL_MUTATE` against an admitted `workspace:<relative-path>` target.
5. Request an unsupported remote mutation and prove refusal occurs before provider launch.
6. Attempt a target outside the compile cut and prove refusal occurs before provider launch.
7. Attempt a traversal/absolute workspace target and prove adapter refusal before provider launch.
8. Attempt with stale precondition state and prove refusal occurs before provider launch.
9. Attempt with a wrong body-time id and prove refusal occurs before provider launch.
10. Feed malformed provider JSON and preserve an attributable provider error receipt without semantic authority.
11. Compare declared reachable effects with launched provider occurrences in the eval receipt.

Pass condition:

> Requests outside the constituted body/effect/target/state boundary do not launch the provider, and launched provider testimony cannot self-promote into authority or semantic truth.

This specimen does **not** prove that arbitrary OpenManus code is OS-contained after launch.

## 12. Testing strategy

V0 uses TDD and separates contract proof from live-provider proof.

### 12.1 Deterministic contract tests

A fake JSON-stdio provider executable proves:

- exact envelope shape;
- argv execution without shell;
- empty-by-default/caller-declared child environment;
- effect allowlisting;
- target grammar and traversal refusal;
- timeout behavior;
- stdout/stderr separation;
- malformed-result handling;
- deterministic provider-receipt preservation;
- deterministic `EffectReceipt` mapping;
- no provider launch after compiler or membrane refusal.

These tests run in ordinary CI without OpenManus.

### 12.2 Optional live integration test

A separately marked test may execute the pinned OpenManus shim when the provider environment is explicitly installed and configured.

Failure or absence of the live provider must not falsify deterministic LOADOUT contract tests.

Passing fake-provider tests does not claim OpenManus runtime conformance.

Passing a live agent task does not claim containment unless the sandbox boundary is separately demonstrated.

## 13. Files expected in the first implementation

New files:

```text
src/loadout/dev/openmanus.py
schemas/openmanus-worker-envelope-v0.schema.json
schemas/openmanus-worker-result-v0.schema.json
contrib/openmanus/worker.py
tests/fixtures/fake_openmanus_provider.py
tests/test_dev_openmanus.py
evals/OPENMANUS-BIND-001.md
```

Modified files:

```text
src/loadout/dev/__init__.py
README.md
```

No change to `EffectClass`, `EffectIntent`, `CompileReceipt`, `OwnerGate`, or the core membrane is expected. If implementation evidence proves a missing invariant, the change requires a failing test and the smallest compatible amendment.

OpenManus must fit the nervous system before the nervous system changes to fit OpenManus.

## 14. Error and refusal model

Use existing provider refusal vocabulary where possible:

```text
PROVIDER_UNAVAILABLE
PROVIDER_REFUSED
```

Adapter transport/schema failures are recorded in the provider receipt and returned to the existing membrane as provider refusal/error dispositions. They do not create authority states.

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

The first live specimen must use disposable material and must not receive production credentials.

## 16. Neighbor ownership after integration

### LOADOUT
Constitutes the worker world, binds capabilities, fences effects, issues intents, preserves cross-provider effect receipts, and preserves attributable provider invocation receipts.

### OpenManus
Executes provider work admitted through one adapter occurrence and returns observations/artifacts. It does not constitute its own LOADOUT authority.

### ALEX
May ingest attributable returned source observations through an explicit handoff and decide how they participate in evidence formation. Worker output is not automatically a claim.

### 3rdi
May project worker observations under declared observer/cut/decoder coordinates through an explicit handoff. Worker memory is not global visibility.

### Human / owning world
Retains authority for publication, merge, remote mutation, adoption, and consequence.

## 17. Promotion gates

V0 may be called a working **transport/constitution adapter** only after deterministic contract tests pass.

A stronger claim — `OPENMANUS LIVE PROVIDER CONFORMANCE` — requires an actual pinned-provider specimen and its receipt.

A still stronger claim — `OPENMANUS CONTAINED PROVIDER CONFORMANCE` — requires evidence for the actual sandbox/container/effect boundary used by that occurrence.

Future gates, separately designed:

1. Contained local compute/mutation worker.
2. Browser-only worker capability.
3. Network observation capability.
4. Credential-bearing provider occurrences.
5. Remote proposal effects.
6. Owner-gated remote mutation.
7. MCP-composed worker organs.
8. Multi-agent internal delegation with attributable sub-worker receipts.

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
