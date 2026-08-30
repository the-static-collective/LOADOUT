# REBIND-WITHOUT-RETROJECTION-001 — LOADOUT operational witness

**Status:** operational design witness / no authority expansion
**Owner:** LOADOUT live-reference resolution semantics
**Cross-project boundary:** National Treasure owns the structural bridge; ALEX owns hostile research attribution tests; 3rdi owns observer-local visualization.

> **LIVE ACROSS OCCURRENCES. PINNED WITHIN AN OCCURRENCE.**

## Purpose

Document the exact operational behavior that makes `REBIND-WITHOUT-RETROJECTION-001` testable rather than metaphorical.

A live ChatGPT-facing organ surface may remain stable across occurrences while selecting different exact organ bodies over time. Within one occurrence, however, the selected body must be pinned and receipted.

The live address therefore has one job:

```text
continuity / re-entry
```

The exact body receipt has another:

```text
historical attribution / replay / derivation
```

Neither replaces the other.

## Identity layers

```text
LOGICAL REF
    ALEX
    LOADOUT
    other live organ name

RESOLUTION EVENT
    occurrence-local attempt to select current body

RESOLVED BODY
    exact repository + commit SHA + manifest evidence

HISTORICAL CONSEQUENCE
    receipt emitted under that pinned body
```

Required non-collapse:

```text
LOGICAL REF != RESOLVED BODY
CURRENT RESOLUTION != HISTORICAL PRODUCER
RESOLVED != UNRESOLVED != REFUSE
FALLBACK != CURRENT
```

## Resolution receipt

Candidate minimal shape, expressed descriptively rather than as a schema promotion:

```json
{
  "logical_ref": "ALEX",
  "occurrence": "O17",
  "resolution_status": "RESOLVED",
  "resolved_repo": "the-static-collective/ALEX.2",
  "resolved_body": "sha:abc123",
  "manifest": "sha:def456"
}
```

Every downstream body-sensitive consequence should be able to retain or reference this exact resolution receipt.

## Rebinding across occurrences

```text
O17:
  ALEX -> sha:A

O18:
  ALEX -> sha:B
```

Lawful statements:

```text
logical_ref(O17) == logical_ref(O18) == ALEX
resolved_body(O17) != resolved_body(O18)
```

If `R17` was produced under O17:

```text
producer(R17) = sha:A
```

After O18 resolves to `sha:B`, the historical relation remains:

```text
producer(R17) = sha:A
```

not:

```text
producer(R17) = current(ALEX) = sha:B
```

## The key refusal

Historical replay or attribution must refuse any operation that silently substitutes a new live resolution for the recorded producer body.

```text
CURRENT RESOLUTION != HISTORICAL PRODUCER
```

If the exact historical body is unavailable, the honest result is an explicit inability to replay/materialize that body. The live surface may still be resolvable for present work, but that present body cannot impersonate historical execution.

## Unresolved control

```text
O19:
  logical_ref = ALEX
  connector/current-organ resolution unavailable
```

Required result:

```text
resolution_status = UNRESOLVED
```

Forbidden behavior:

```text
use embedded fallback
or last-known body
and report it as CURRENT
```

A fallback may be separately labeled and bounded if LOADOUT already permits that mode, but its identity must not collapse into current live resolution.

## Target-relative coarse projection

A downstream target that asks only for continuing ownership may lawfully emit:

```json
{"owner":"ALEX"}
```

without carrying the exact body in its user-facing projection.

This is safe only when:

```text
1. the target explicitly declares body identity irrelevant;
2. the underlying provenance remains available somewhere appropriate;
3. the coarse record is not later reused as if it were sufficient for replay or historical derivation.
```

LOADOUT does not decide every downstream target. It supplies enough exact resolution evidence so those targets can make an honest choice.

## Relationship to CURRENT-ORGAN / LIVE-SURFACE

The live surface is a stable re-entry membrane rather than the organ body itself.

The intended operational law is therefore:

```text
ACROSS OCCURRENCES:
    the logical organ address may resolve to a newer body

WITHIN ONE OCCURRENCE:
    the exact selected body remains pinned
    and consequences are attributed to that body
```

This is the concrete witness for the broader structural claim:

```text
continuing addressability
can coexist with
changing exact embodiment
without historical impersonation
```

## Hostile acceptance vector

### Case A — rebinding is allowed

```text
O1: L -> A
O2: L -> B
```

PASS if both occurrences succeed and retain the same logical reference with distinct exact body receipts.

### Case B — within-occurrence drift is forbidden

```text
O1 starts with L -> A
upstream current organ changes to B before O1 ends
```

PASS only if O1 remains pinned to A.

### Case C — historical replay does not chase current

```text
R1 produced under A
current L -> B
replay R1
```

PASS only if replay selects A or honestly refuses because A cannot be materialized.

### Case D — unresolved stays unresolved

```text
current resolution unavailable
```

PASS only if LOADOUT does not label fallback/embedded/last-known body as current.

### Case E — coarse owner view

```text
target = owner-only
```

PASS if output may collapse A/B to logical owner L while the exact source receipt remains intact for body-sensitive uses.

## Authority boundary

This witness does not give LOADOUT authority to decide:

- whether a research claim is supported;
- whether an ALEX body is canonical or PRESENT;
- what an observer knows;
- how a Name should be interpreted historically or theologically;
- whether a downstream macrostate is semantically valid beyond its declared target.

LOADOUT resolves and receipts. Other owners interpret within their own constitutions.

## Resolution time HOLD

No new universal clock is required here.

The sufficient operational primitive is an occurrence-qualified resolution receipt. A separate resolution-time coordinate should be introduced only if an executable counterexample proves the existing temporal coordinates plus resolution event cannot preserve a material distinction.

## Seal

> **THE ADDRESS MAY MOVE FORWARD THROUGH NEW BODIES. THE RECEIPT MUST KEEP POINTING BACK TO THE BODY THAT ACTUALLY ACTED.**

> **REBIND FOR THE PRESENT. PIN FOR THE OCCURRENCE. ATTRIBUTE TO THE BODY. NEVER RETROJECT.**
