---
name: loadout
description: Use when a task requires deciding which project context, tools, capabilities, or effects should enter a bounded occurrence; when multiple organs are available but only some are relevant; when capability, authority, side effects, freshness, or current-project state must be fenced; or when compiling, ablating, or recompiling a task world with an attributable receipt.
---

# LOADOUT

**Bring the smallest world that can do the job.**

LOADOUT is the bounded session/world compiler. It may discover context and capabilities, but it does not silently turn availability into relevance, relevance into binding, or binding into authority.

> **Knowledge may load. Capability may bind. Authority does not silently expand.**

Hold these non-collapses throughout the run:

```text
mention != mandatory binding
availability != relevance
relevance != binding
binding != authority
discovery != invocation
read authority != write authority
router choice != evidence
representation capability != intervention capability
receipt != authority
reflection != mutation
live != unpinned
latest != admitted
```

## Compile the bounded world

Use the smallest sufficient path:

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

1. **CUT** — state the task, owner question, stopping condition, relevant time/knowledge cut, and effect boundary.
2. **CLASSIFY** — distinguish needed knowledge, representation, computation, intervention, and publication/mutation effects.
3. **DISCOVER** — find available context, organs, tools, and owner-owned state without treating availability as selection.
4. **SELECT** — choose only what materially helps the task. An explicit mention is evidence of interest, not automatic binding.
5. **REACH** — determine what the selected capability can actually reach, including indirect or future-facing effects.
6. **FENCE** — name effects that must remain outside the occurrence. A fence alone is not authorization.
7. **BIND** — return `BIND`, `REFUSE`, or `UNRESOLVED`. Effectful bindings require attributable authorization and owner-gate evidence.
8. **WORK** — operate only inside the admitted world. Missing capability may reduce method without invalidating the task.
9. **RECEIPT** — preserve why each binding existed, what stayed asleep, what authority was present, and what remained unresolved.

## Live constitution

For ChatGPT-facing or other portable surfaces, apply the LIVE-SURFACE contract owned by this repository:

> **Resolve live. Pin locally. Load minimally. Preserve ownership. Receipt the world.**
>
> **Live across occurrences; pinned within an occurrence.**

When current organ state matters:

1. resolve the owning repository's `.live/current-organ.json` from its default branch;
2. resolve that branch to one exact commit SHA;
3. freeze the SHA for the bounded occurrence;
4. load the manifest entrypoint and only task-required references at that SHA;
5. never mix a newer head into the occurrence without an explicit reconstitution;
6. if live resolution fails, mark freshness `UNRESOLVED` and use only an embedded/static floor that is sufficient for the task.

A successful resolver result does not grant semantic ownership or effect authority. GitBook and Free Graph may orient or point; exact-SHA project-owned material owns local project constitution.

The canonical design is `docs/superpowers/specs/2026-08-29-live-surface-current-organ-design.md`.

## Executable floor

The repository kernel currently exposes deterministic operations for reachability, deltas, fences, binding, trace, ablation, decay, ALEX envelope lowering, and reflective recompile proposals. Use executable paths when the task needs machine-checked compilation; otherwise preserve the same constitutional distinctions in reasoning.

Core reflective hatch:

```text
COMPILE
  -> RECEIPT / REIFY
  -> PRESSURE
  -> RECOMPILE PROPOSAL
  -> GATE
  -> COMPILE'
```

A proposal is inert. It cannot expand authority or capability merely because reflection found a better shape.

## Neighbor ownership

- **3rdi** owns observer-local projection and attributed cut/decoder constitution.
- **ALEX** owns provenance-first research formation, derivation pressure, source-to-claim support, and refusal.
- **Free Graph** remembers roads and ancestry without becoming current-state authority.
- **LOADIN.STEAD** resolves declared destinations; `route != admit`.
- **Owning projects and humans** retain admission, publication, merge, mutation, and consequence.

LOADOUT may constitute a world containing another organ. It does not become that organ.

## Completion check

Before finishing, verify:

- the world contains no capability or context merely because it was available;
- every effectful binding has an attributable authorization source and owner gate;
- current-project material, when required, was resolved and pinned rather than repeatedly fetched as mutable `latest`;
- missing live access is visible rather than converted into false freshness;
- router/output choices were not promoted into evidence;
- the receipt distinguishes knowledge loaded, capabilities bound, effects fenced, and authority actually present.
