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
loadout resolve-live
```

`loadout.compile/v0` is owned here. The ALEX adapter lowers an immutable compile into `alex.run-envelope/v0`; sharing a protocol does not merge the two systems.

For effectful capabilities, **a fence alone is not authorization**. The compiler requires an attributable authorization source and owner-gate reference for each allowed reachable effect and carries those references forward unchanged.

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

See `docs/specs/2026-08-28-probe-bind-open-berth.md` and `evals/PROBE-BIND-001.md`.

## Historical witness compatibility

Historical `loadout.manifest/v0` receipts remain witnesses rather than being rewritten into the current compile schema. `fixtures/3rdi/loadout.manifest.json` records the first golden constitutional cut and its source blob SHA.

## Status

**Executable v0 kernel candidate.** No production daemon, registry, network authority, master ontology, automatic plugin orchestration, or Dogram runtime dependency is claimed.
