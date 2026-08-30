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

See `docs/specs/2026-08-28-probe-bind-open-berth.md` and `evals/PROBE-BIND-001.md`.

## Historical witness compatibility

Historical `loadout.manifest/v0` receipts remain witnesses rather than being rewritten into the current compile schema. `fixtures/3rdi/loadout.manifest.json` records the first golden constitutional cut and its source blob SHA.

## Status

**Executable v0 kernel candidate.** No production daemon, registry, network authority, master ontology, automatic plugin orchestration, universal PHASELIFT runtime, or Dogram runtime dependency is claimed.
