# LOADOUT

> **Bring the smallest world that can do the job.**

LOADOUT is the Static Collective's bounded session/world compiler. It decides what context may enter, what capabilities may bind, what effects remain fenced, and what stays asleep.

Core law:

> **Knowledge may load. Capability may bind. Authority does not silently expand.**

## What LOADOUT owns

```text
TASK
  ↓
CUT
  ↓
CLASSIFY
  ↓
DISCOVER
  ↓
SELECT
  ↓
REACH
  ↓
FENCE
  ↓
BIND
  ↓
WORK
  ↓
RECEIPT
```

LOADOUT may compile a bounded world containing ALEX, 3rdi, Free Graph, local tools, repository adapters, research tools, or nothing beyond the native task surface. Availability does not imply relevance; relevance does not imply binding; binding does not imply permission to produce effects.

## Non-collapses

```text
task != tool list
mention != mandatory binding
availability != relevance
capability availability != authority
discovery != invocation
read authority != write authority
missing capability != missing task
router choice != evidence
representation capability != intervention capability
receipt != authority
reflection != mutation
```

## Executable floor

The first runtime is intentionally small and deterministic. Production code uses the Python standard library only.

```text
REACH   calculate declared reachable effects / required capability reachability
DELTA   compare bounded records deterministically
FENCE   identify reachable effects outside the exact fence
BIND    BIND | REFUSE | UNRESOLVED
TRACE   preserve why a decision was made
ABLATE  remove one binding counterfactually without mutating the parent
```

Install for development and run:

```bash
python -m pip install -e ".[test]"
pytest -q
loadout --help
```

Machine-facing commands:

```text
loadout bind
loadout compile
loadout envelope-alex
loadout delta
loadout reach
loadout ablate
loadout trace
loadout decay
loadout reconstitute
loadout resolve-live
```

`loadout.compile/v0` is owned here. The ALEX adapter lowers an immutable compile into `alex.run-envelope/v0`; sharing a protocol does not merge the two systems.

For effectful capabilities, **a fence alone is not authorization**. The compiler requires an attributable authorization source and owner-gate reference for each allowed reachable effect and carries those references forward unchanged.

### PHASELIFT reconstitution boundary

Project 0 crossing testimony may be received and inspected through the bounded Project 0 adapter. LOADOUT alone evaluates the receiver-local reconstitution threshold.

```text
source testimony
  -> Project 0 crossing
  -> LOADOUT local threshold
  -> LIFT | DEGRADED | HOLD | REFUSE
```

Source authority never becomes local authorization by transport. `LIFT` and `DEGRADED` may emit a new `loadout.world-birth/v0` receipt after local compilation and authorization. `HOLD` and `REFUSE` do not constitute a world. Source proposals, when adopted, receive new LOADOUT-local proposal identities rather than becoming executable destination edges unchanged.

This surface proves bounded crossing/reconstitution only. It does not claim a network protocol, daemon, universal PHASELIFT runtime, automatic merge plane, or portable `PROTECTED` ontology.

## LIVE-SURFACE / CURRENT-ORGAN v0

The uploaded ChatGPT-facing surface is not the organ. It is a stable re-entry membrane that can resolve the current owner material when the host provides attributable repository evidence.

```text
uploaded surface != organ

resolve owner head
  -> pin exact SHA
  -> load minimally
  -> work
  -> receipt
```

Core law:

> **Live across occurrences; pinned within an occurrence.**

LOADOUT owns the common resolution protocol, not neighboring organ semantics:

```text
common protocol != common owner
fallback != current
retrieval != adoption
pointer != truth
loaded != supported
receipt != authority
```

The first owner manifest lives at `.live/current-organ.json`. It points to the portable LOADOUT entrypoint at `skills/loadout/SKILL.md` and declares the repository roots eligible for bounded loading.

The production resolver in `loadout.live_surface` performs **no network access**. A host supplies already-attributed evidence containing the repository owner, a resolved ref, an exact 40-hex commit SHA, the pinned `.live/current-organ.json`, and the file bodies available at that SHA. LOADOUT verifies that the evidence owner matches the manifest owner and that the manifest body is the one present at the pinned SHA before it loads the entrypoint or any requested references. It then selects only allowed, explicitly needed paths and emits a receipt.

A local host adapter can exercise the same contract with JSON files:

```bash
loadout resolve-live manifest.json evidence.json --path docs/needed.md
```

A successful result exits `0` with `freshness = RESOLVED`. An unresolved or refused result exits `2`. If live owner evidence cannot be obtained, an embedded bootstrap may be used only as an explicitly `UNRESOLVED` fallback; it must never be represented as current.

Published contracts:

- `schemas/current-organ-v0.schema.json`
- `schemas/live-surface-receipt-v0.schema.json`

Design and implementation plan:

- `docs/superpowers/specs/2026-08-29-live-surface-current-organ-design.md`
- `docs/superpowers/plans/2026-08-29-live-surface-v0-implementation.md`

## READ-ONLY-HOST-ADAPTER-001

`LocalGitReadAdapter` is the first real read-only host proof for LOADOUT.dev. It uses the existing effect-intent and adapter protocol rather than creating a second authority system.

```text
LocalGitReadAdapter = real read-only host proof
CURRENT ref != immutable object
host access != write authority
adapter result != semantic truth
```

Its complete v0 host capability surface is:

```text
git.resolve_ref
git.read_blob
```

`git.resolve_ref` resolves a named local ref to one exact commit SHA. `git.read_blob` reads exact bytes from `<commit-sha>:<path>` inside declared repository roots. Results are content-addressed and retained only in memory. CURRENT-ORGAN can therefore resolve a mutable ref once, pin the returned SHA, and keep reading the same immutable constitution even after the branch advances.

The adapter exposes no generic shell capability and no Git write or network operation. Checkout, switch, merge, reset, commit, push, fetch, pull, clone, remote mutation, credentials, arbitrary shell execution, and network clients are outside the v0 surface. Shell metacharacters remain literal argv data, path traversal refuses before Git invocation, and successful host reads do not grant merge, publication, mutation, or semantic authority.

## OPENMANUS-BIND-001 — bounded execution limb

> **LOADOUT constitutes; OpenManus moves.**

`OpenManusJsonStdioAdapter` is the first provider-orchestration proof for an agentic worker behind the existing LOADOUT.dev membrane. The adapter does not let OpenManus choose what world it inhabits. An already-compiled `EffectIntent` crosses a canonical JSON-stdio boundary, the provider returns attributable testimony, and the existing membrane emits the narrow `EffectReceipt`.

```text
CompileReceipt + EffectIntent
        ↓
LOADOUT membrane
        ↓
OpenManusJsonStdioAdapter
        ↓
JSON-stdio worker occurrence
        ↓
OpenManusProviderReceipt
        ↓
existing EffectReceipt
```

The first body is pinned to the inspected upstream source identity:

```text
openmanus.worker.json-stdio/v0@3309bf4e416fb1c74b008f3e86494439a31bad53
```

V0 admits only:

```text
OBSERVE
LOCAL_COMPUTE
LOCAL_MUTATE
```

`LOCAL_MUTATE` is workspace-local. Remote proposal, remote mutation, publication, landing, Git writes, merge authority, ambient shell, browser reach, generic MCP reach, and automatic credential inheritance are not part of the v0 body.

The optional shim in `contrib/openmanus/` uses OpenManus's `ToolCallAgent` reasoning loop with LOADOUT-scoped tools only:

```text
OBSERVE       -> loadout_read_text
LOCAL_COMPUTE -> loadout_calculate
LOCAL_MUTATE  -> loadout_read_text + loadout_write_text
```

It does not expose OpenManus's broader native execution surfaces. Rich worker observations and artifacts are preserved in a separate `OpenManusProviderReceipt`; they do not widen `EffectReceipt` and do not become semantic authority.

Published contracts:

- `schemas/openmanus-worker-envelope-v0.schema.json`
- `schemas/openmanus-worker-result-v0.schema.json`

Proof receipt:

- `evals/OPENMANUS-BIND-001.md`

The deterministic adapter contract is testable without OpenManus installed. **OpenManus live provider conformance is a separate gate and is not claimed until an exact pinned provider occurrence actually executes.** Declaring a workspace path is also not an OS sandbox claim.

### Dogram-shaped, not Dogram-dependent

Dogram's metaoscillatory architecture informs the reflective hatch:

```text
COMPILE
  ↓
RECEIPT / REIFY
  ↓
PRESSURE
  ↓
RECOMPILE PROPOSAL
  ↓
GATE
  ↓
COMPILE'
```

The proposal is inert. It cannot become a compile without a matching admitted gate receipt, and the meta-gate refuses authority or capability expansion.

## Neighbor ownership

- **ALEX** owns provenance, research formation, derivation pressure, and refusal.
- **3rdi** owns observer-local projection, decoder/cut constitution, and attributed viewpoint.
- **Free Graph** remembers roads and ancestry without becoming execution authority.
- **LOADIN.STEAD** resolves declared destinations; `route != admit`.
- **Owning worlds / humans** retain admission, publication, merge, mutation, and consequence.

## The server is not the Collective

```text
SERVER != COLLECTIVE
```

A host is an occurrence capable of constituting a bounded world. The first always-available server should be replaceable from attributable configuration, contracts, artifacts, and receipts.

The current project compression is **13th Cup**: not a central ruler, but a prepared opening through which another independently bounded world may arrive.

```text
RECEIVE
   ↓
 HOLD
   ↓
 POUR
```

- `receive != accept`
- `hold != possess`
- `pour != impose`
- `invited-by != controlled-by`
- `compatible-with != identical-to`

A successful Cup carries enough information to help another Cup constitute itself without inheriting the inviter's authority.

## Current proving frontier

The first LOADOUT-specific hostile boundary is **`PROBE-BIND-001`**: a capability that only changes representation may remain read-only, while the same nominal tool used to alter a target's future must cross an explicit effect fence.

PHASELIFT `CROSSING-001 / RECONSTITUTE-001` additionally proves that one immutable Project 0 crossing may yield receiver-local `LIFT`, `DEGRADED`, `HOLD`, or `REFUSE`, and that lawful lifts may fork into distinct successor worlds without importing source authority or rewriting historical producers. See `evals/CROSSING-001.md`.

`OPENMANUS-BIND-001` now proves the provider boundary variant: a capable agentic worker may remain useful without gaining the right to constitute its own effect surface. See `evals/OPENMANUS-BIND-001.md`.

See `docs/specs/2026-08-28-probe-bind-open-berth.md` and `evals/PROBE-BIND-001.md`.

## Historical witness compatibility

Historical `loadout.manifest/v0` receipts remain witnesses rather than being rewritten into the current compile schema. `fixtures/3rdi/loadout.manifest.json` records the first golden constitutional cut and its source blob SHA.

## Status

**Executable v0 kernel candidate with a `LOADOUT.dev/v0` conformance floor.** The repository includes provider-independent capability compilation, body-declared reachable effects, exact adapter-body attribution, effect fencing, state-bound developer workflow gates, inert effect intents/receipts, deterministic fake-adapter hostile tests, the bounded PHASELIFT receiver/reconstitution proof, the host-supplied LIVE-SURFACE / CURRENT-ORGAN resolution protocol, the real local-Git read-only host proof, and the deterministic `OPENMANUS-BIND-001` JSON-stdio agent-provider boundary.

It does **not** claim OpenManus live-provider conformance, credential storage, remote OpenManus effects, merge/publication automation, background watching, a universal PHASELIFT runtime, full Dogram lowering, a production daemon, network authority, a master ontology, a secure OS sandbox, or a Dogram runtime dependency.

See `docs/specs/2026-08-28-loadout-dev-native-developer-toolset.md`, `docs/superpowers/plans/2026-08-28-loadout-dev-v0.md`, `docs/superpowers/specs/2026-09-01-openmanus-nervous-system-v0-design.md`, `docs/superpowers/plans/2026-09-01-openmanus-nervous-system-v0.md`, and `evals/OPENMANUS-BIND-001.md`.
