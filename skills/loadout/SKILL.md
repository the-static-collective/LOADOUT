---
name: loadout
description: Bring the smallest bounded world that can do the job. Resolve current LOADOUT canon from its owning repository when host capability allows, pin one exact commit per occurrence, load only what is needed, preserve authority boundaries, and leave a receipt.
---

# LOADOUT

> Bring the smallest world that can do the job.

LOADOUT is the bounded session/world compiler for the Static Collective. It decides what context and capability may enter a task-world without silently expanding authority.

## Constitutional floor

**Knowledge may load. Capability may bind. Authority does not silently expand.**

Preserve these non-collapses:

```text
TASK != tool list
availability != relevance
relevance != binding
binding != authority
retrieval != adoption
pointer != truth
loaded != supported
orientation != retrieval
receipt != authority
common protocol != common owner
```

The operating flow is:

```text
TASK
  -> CUT
  -> CLASSIFY
  -> DISCOVER
  -> SELECT
  -> REACH
  -> FENCE
  -> BIND
  -> WORK
  -> RECEIPT
```

## LIVE-SURFACE constitution

**Live across occurrences; pinned within an occurrence.**

When the host can read the owning repository:

1. Read `.live/current-organ.json` from `the-static-collective/LOADOUT`.
2. Resolve the repository's current default-branch head.
3. Freeze that exact commit SHA for this occurrence.
4. Read `skills/loadout/SKILL.md` at the pinned SHA.
5. Load only references required by the task and only from manifest-declared roots.
6. Do not re-resolve "latest" during the same occurrence. A newer head requires a new occurrence or an explicit reconstitution.
7. Perform bounded work through the normal LOADOUT gates.
8. Leave a receipt naming the owner, ref, exact SHA, entrypoint, and loaded paths.

A branch name, mutable URL, cached summary, GitBook page, or Free Graph pointer is not an exact replay identity. The commit SHA is.

## Fallback

If live resolution is unavailable or incomplete, the embedded surface may provide this constitutional floor only when it is sufficient for the task.

In that case:

```text
freshness = UNRESOLVED
fallback != current
```

State what could not be resolved. Never describe an embedded snapshot as current merely because no newer owner evidence was reachable.

Do not claim network, GitHub, GitBook, filesystem, or other host capability unless the host actually provides it.

## Ownership boundary

LOADOUT owns bounded world and capability compilation. It does not absorb neighboring organs:

- **ALEX** owns provenance-first research formation, evidence-to-claim derivation, pressure, and refusal.
- **3rdi** owns observer-local projection and attributed cuts.
- **Free Graph** carries historical roads, encounters, ancestry, and resolvable pointers; it does not become current project truth.
- **GitBook Front Room** may orient and expose doors; orientation does not outrank current project-owned evidence.
- **Owning projects and humans** retain admission, mutation, publication, merge, and consequence.

Successful resolution does not grant write, merge, publication, execution, or effect authority.

## Minimum-load discipline

Prefer the smallest sufficient context:

```text
entrypoint
  + directly required references
  + current state only when the task depends on it
  + eval/specimen material only when pressure requires it
```

Reachability is not a reason to ingest a whole repository.

## Receipts

A LIVE-SURFACE receipt records the world actually used. At minimum preserve:

```text
organ
owner
resolved_ref
resolved_sha
entrypoint
loaded paths
freshness
fallback_used
```

A receipt proves what constitution was loaded. It does not prove the resulting answer is correct and does not mint authority.

## Deeper floor

For executable details, schemas, pressure operators, and current architectural specs, follow only the task-relevant doors in this repository at the pinned SHA. The primary README and `docs/` are references, not material to preload automatically.
