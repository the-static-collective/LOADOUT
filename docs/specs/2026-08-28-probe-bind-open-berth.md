# PROBE-BIND + OPEN-BERTH design

**Date:** 2026-08-28  
**Status:** CANDIDATE DESIGN — no runtime conformance claimed

## 1. Why this belongs in LOADOUT

Recent ALEX work distinguishes two operations that ordinary language may both call a decoder:

```text
LENS / REPRESENTATION
world -> coordinate system -> projection

PROBE / INTERVENTION
world + input -> changed world -> projection
```

If the operation can change the target's future, LOADOUT must not bind it as if it were merely a read-only lens.

Core law:

> **REPRESENTATION CAPABILITY != INTERVENTION CAPABILITY.**

This is an execution boundary, not a semantic claim. ALEX may later evaluate what a probe result bears on; 3rdi may describe what was visible before and after; LOADOUT owns whether the effectful capability was lawfully bound in the first place.

## 2. Candidate compile distinction

A future `loadout.compile/v0`-compatible surface should be able to distinguish at least:

```text
capability:
  operation: inspect | transform-representation | intervene
  target: <bounded target ref>
  requested_effects: [...]
  effect_fence: [...]
  authority: none | <owner-local receipt>
```

This document does **not** adopt that object as a universal schema. It records the semantic distinction the compiler must preserve however the eventual contract represents it.

### Required behavior

```text
read-only decode
  + no target mutation
  -> may bind under inspection fence

active probe
  + possible target mutation / state transition / external effect
  -> requires explicit effect fence

active probe
  + no attributable effect authorization
  -> REFUSE / CAPABILITY_GAP / OWNER_GATE
```

A tool's brand or availability does not decide the category. The intended operation and reachable effects do.

## 3. `PROBE-BIND-001`

Use one nominal capability in two modes against the same bounded fixture.

### World A — lens

```text
input: target occurrence T0
operation: transform representation only
allowed effects: none
expected:
  capability may bind
  target digest unchanged
  authority unchanged
```

### World B — probe

```text
input: target occurrence T0
operation: deliver declared input u capable of changing target state
allowed effects: none
expected:
  REFUSE before intervention
  target digest unchanged
  no result may masquerade as observational decoding
```

### World C — fenced probe

```text
input: target occurrence T0
operation: deliver declared input u
allowed effects: exact bounded probe effect
expected:
  capability may bind
  probe receipt required
  target transition remains attributable
  semantic inference remains outside LOADOUT
```

### Hostile siblings

1. **Brand laundering** — same tool name, hidden mutation path. Must refuse if the reachable effect exceeds the declared fence.
2. **Mode laundering** — caller labels an intervention `decode`. Classification follows effect semantics, not label.
3. **Fence widening** — child compile inherits context but not parent's effect permission.
4. **Probe drift** — parameters change after compile. Requires recompile or refusal.
5. **Result laundering** — successful execution does not mint evidence, support, truth, admission, publication, or canon.

## 4. Interest selects pressure; it does not authorize it

A useful emerging role for interest is experiment allocation:

```text
interest(q)
   ↓
select unresolved neighborhood
   ↓
propose discriminating probe
```

But:

```text
interest != evidence
interest != support
interest != effect authority
```

LOADOUT may use an interest receipt as attributable selection context. It must still compile the actual capability/effect boundary independently.

## 5. 13th Cup refinement — OPEN BERTH

The recent completion-move work suggests a stronger interpretation of the 13th Cup.

The missing thing may not be another object. It may be an **admissible incidence**: a relation deliberately left open so novelty can enter without being forced into an existing role.

```text
ADD NODE
!=
OPEN RELATION -> INSERT
```

Candidate server topology:

```text
CUP
├── bounded constitution
├── current capabilities
├── current relations
└── OPEN BERTH
      ↓
   candidate arrival
      ↓
   local verification
      ↓
   local admission or refusal
```

The berth is not authority. It is a declared possibility of lawful contact.

### Non-collapses

```text
open != admitted
invited != trusted
received != executable
compatible != identical
descended-from != subordinate-to
```

## 6. RECEIVE / HOLD / POUR

The server-facing compression remains:

```text
RECEIVE
  arrival without silent trust

HOLD
  preserve identity/provenance/boundaries/unresolved state

POUR
  expose portable artifacts/contracts/receipts without exporting authority
```

A Cup succeeds when another Cup can independently verify enough of what was poured to constitute its own bounded world.

## 7. Future proving sequence

1. `PROBE-BIND-001` — lens vs intervention effect boundary.
2. `OPEN-BERTH-001` — isolated node vs leaf attachment vs edge-interior insertion using a deterministic graph fixture.
3. `13TH-CUP-DEATH-001` — constitute Cup B from Cup A, disconnect A, require B to verify itself and invite Cup C.
4. `13TH-CUP-FORK-001` — instantiate one snapshot twice and refuse silent singular-continuity claims.

No network federation protocol is earned by this document.

## Seal

> **LOADOUT COMPILES THE QUESTION'S MEANS. IF THE QUESTION CAN TOUCH THE WORLD, THE TOUCH BELONGS IN THE FENCE.**

> **THE 13TH CUP MAY BE LESS AN EXTRA CUP THAN THE OPENING THROUGH WHICH ANOTHER CUP CAN LAWFULLY ARRIVE.**
