# LIVE-SURFACE / CURRENT-ORGAN Design

**Date:** 2026-08-29  
**Owner:** LOADOUT  
**Status:** approved architecture; implementation not yet admitted

## 1. Purpose

The ChatGPT-uploaded surface for a Static Collective organ should not carry a stale copy of the organ's changing doctrine, runtime map, frontier, or methods.

It should be a small, stable **re-entry membrane** that resolves the organ's current project-owned constitution from attributable sources, pins that constitution for the present occurrence, loads only the bounded material needed for the task, and leaves a receipt.

The governing compression is:

> **The uploaded plugin is not the organ. It is a stable re-entry membrane that constitutes the current organ from attributable sources.**

This design makes LOADOUT the owner of the common resolution protocol without making LOADOUT the owner of ALEX, 3rdi, Free Graph, Novelist, Riqor, or any other organ's semantics.

## 2. Problem

The current custom-plugin surfaces were useful bootstrap artifacts, but they become stale because their instructions are copied into ChatGPT while the owning repositories keep moving.

Two failure modes follow:

1. **stale-surface drift** — the uploaded instructions describe an older organ than the repository now contains;
2. **manual resynchronization burden** — important improvements require repeated editing and re-uploading of otherwise stable surfaces.

A naive fix would make one central Collective plugin that owns current state for all organs. This is rejected. It would collapse local project authority into a central brain and make one routing surface an accidental source of truth.

The desired property is instead:

```text
COMMON LIVE-PULL PROTOCOL
        !=
COMMON OWNER
```

## 3. Existing floor

This design composes with existing LOADOUT law:

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

and preserves:

```text
availability != relevance
relevance != binding
binding != authority
router choice != evidence
receipt != authority
```

It also composes with the current neighboring ownership split:

- **LOADOUT** owns bounded world/capability compilation;
- **3rdi** owns observer-local projection and attributed cut constitution;
- **ALEX** owns provenance-first research formation, derivation pressure, source-to-claim support, and refusal;
- **Free Graph** remembers roads, encounters, and resolvable pointers without becoming current-state authority;
- **GitBook Front Room** provides orientation and doors, not project-owned current truth;
- **owning projects / humans** retain admission, publication, merge, mutation, and consequence.

## 4. Core invariants

The protocol must preserve these non-collapses:

```text
uploaded surface != organ
bootstrap != current doctrine
resolver result != authority
latest != admitted
current head != mutable-during-run
pointer != truth
loaded != supported
retrieval != adoption
orientation != retrieval
live != unpinned
fallback != current
common protocol != common owner
```

A live pull may discover current material. It does not silently constitute that material outside the organ that owns it.

## 5. Selected architecture

### 5.1 Stable bootstrap

Each uploaded ChatGPT-facing surface contains only material expected to change rarely:

- organ identity;
- owning repository or canonical owner location;
- a small constitutional kernel;
- source-precedence rules;
- the live-resolution procedure;
- authority and side-effect boundaries;
- failure/fallback behavior;
- receipt requirements.

It should not contain volatile frontier state, a large method catalog, current repo summaries, current tests, or copied versions of deep reference files.

### 5.2 Current-organ manifest

Each participating organ owns a small machine-readable manifest at a stable path.

Initial proposed path:

```text
.live/current-organ.json
```

Minimal shape:

```json
{
  "schema": "static-collective/current-organ/v0",
  "organ": "alex",
  "owner": "the-static-collective/ALEX.2",
  "entrypoint": "skills/alex/SKILL.md",
  "state": null,
  "orientation": {
    "kind": "gitbook-front-room",
    "required": false
  },
  "resolution": "default-branch-head-then-pin",
  "fallback": "embedded-bootstrap"
}
```

The manifest is a route declaration, not a truth declaration. Its owning repository controls its own manifest.

### 5.3 Resolve once, then pin

At invocation:

```text
USER INVOKES ORGAN
       |
       v
STABLE BOOTSTRAP
       |
       v
RESOLVE OWNER
       |
       v
FETCH CURRENT MANIFEST
       |
       v
RESOLVE DEFAULT-BRANCH HEAD
       |
       v
PIN EXACT COMMIT SHA
       |
       v
LOAD MINIMUM NEEDED MATERIAL @ SHA
       |
       v
WORK
       |
       v
RECEIPT
```

The exact SHA is frozen for the bounded occurrence.

A run must not repeatedly ask for "latest" and silently mix material from multiple heads. If the owner advances during the run, the new head is available only to a new occurrence or an explicit reconstitution step.

Core rule:

> **Live across occurrences; pinned within an occurrence.**

### 5.4 Minimum-load discipline

After pinning, the bootstrap reads the smallest sufficient set:

1. organ entrypoint;
2. only references directly required by the selected mode/task;
3. current project state only when the task depends on it;
4. owner-specific evals/specimens only when pressure or verification requires them.

It must not ingest the full repository merely because the repository is reachable.

This copies the useful Creator Workspace pattern without importing its domain semantics: small router, focused recall, narrow handoff, explicit host evidence.

### 5.5 Source precedence

When sources conflict, use this precedence unless the owning organ declares a stricter local rule:

```text
1. current-turn user material
2. exact-SHA project-owned current state / canon
3. project-owned references needed by the selected mode
4. current GitBook orientation / shared vocabulary
5. Free Graph historical roads and resolvable pointers
6. embedded bootstrap snapshot
```

The lower layer may help locate a higher layer. It may not overrule it merely by being easier to retrieve.

### 5.6 Honest degradation

If live resolution fails:

```text
LIVE PULL SUCCEEDS
  -> use owner material pinned at exact SHA
  -> freshness = RESOLVED

LIVE PULL FAILS
  -> use embedded bootstrap only when sufficient
  -> freshness = UNRESOLVED
  -> state exactly what could not be verified
  -> never call the snapshot current
```

A missing connector, unavailable repository, inaccessible manifest, malformed manifest, unresolved ref, or failed read is not evidence that the organ has no newer state.

`UNRESOLVED` is a valid terminal result when freshness is material to the task.

## 6. Ownership and authority

LOADOUT owns only the **LIVE-SURFACE protocol contract** and its compiler/reference implementation.

Each organ owns:

- its manifest;
- its entrypoint;
- its deeper references;
- its project state;
- its local semantic rules;
- its adoption/promotions;
- any side effects or consequences in its world.

Therefore:

```text
LOADOUT resolves ALEX
    !=
LOADOUT defines ALEX

LOADOUT pins 3rdi
    !=
LOADOUT constitutes 3rdi semantics

Free Graph points to current owner evidence
    !=
Free Graph stores current truth
```

No manifest field may silently grant write authority, publication authority, merge authority, network authority, or tool permission.

## 7. First conforming organs

### 7.1 LOADOUT

LOADOUT is the first specimen because the problem is itself world compilation.

LOADOUT will add:

```text
skills/loadout/SKILL.md
.live/current-organ.json
```

The portable skill should be a thin task/world router over the existing executable kernel and references.

The uploaded `@loadout` ChatGPT surface then becomes a bootstrap into that current pinned skill rather than a second independent copy of LOADOUT doctrine.

### 7.2 3rdi

3rdi already has the closest target shape:

- thin enough primary `SKILL.md`;
- deeper references behind named doors;
- executable scripts and labs in-repo;
- clear constitutional non-collapses.

Initial change should therefore be minimal:

- add `.live/current-organ.json`;
- pressure the current `SKILL.md` for any remaining volatile material;
- replace the uploaded ChatGPT surface with the common bootstrap plus 3rdi identity/kernel.

### 7.3 ALEX

ALEX currently concentrates many modes and protocols in one large `SKILL.md`.

The first refactor should split volatile/deep behavior into bounded references while preserving the entrypoint as router and constitutional floor.

Candidate doors include:

```text
references/modes/
  find-read-compare.md
  trace-dossier-audit.md
  pressure.md
  formation-trace.md
  ungate.md

references/contracts/
  source-routing.md
  evidence-model.md
  research-receipt.md
  constitutional-hardening.md
```

Exact paths may differ after repo inspection; the invariant is more important than the directory spelling.

The ChatGPT surface should not reproduce these bodies.

## 8. Receipt contract

Every live constitution should be able to emit a compact receipt equivalent to:

```json
{
  "schema": "static-collective/live-surface-receipt/v0",
  "organ": "alex",
  "owner": "the-static-collective/ALEX.2",
  "resolved_ref": "main",
  "resolved_sha": "<40-hex>",
  "manifest_path": ".live/current-organ.json",
  "entrypoint": "skills/alex/SKILL.md",
  "loaded": [
    "skills/alex/SKILL.md",
    "skills/alex/references/pressure.md"
  ],
  "freshness": "RESOLVED",
  "fallback_used": false
}
```

This receipt proves which constitution was used. It does not prove the correctness of the organ's answer or grant authority to act.

## 9. Host capability boundary

The protocol is host-portable, but live pull is capability-dependent.

A host may satisfy resolution through:

- a native GitHub connector;
- a Git checkout already present in a trusted workspace;
- another owner-approved repository adapter;
- a content-addressed local mirror whose source ref and SHA are attributable.

The protocol must not assume a network call exists merely because the bootstrap requests current state.

The host adapter returns evidence of what it actually resolved.

## 10. Failure and hostile cases

The implementation is not conforming until it pressures at least these cases.

### LIVE-SURFACE-001 — stale embedded snapshot

Embedded text describes old doctrine while repository head contains newer doctrine.

Required: live resolution selects the pinned repository version; snapshot is not allowed to override it.

### LIVE-SURFACE-002 — head moves mid-run

Resolve SHA A. Owner advances to SHA B before work finishes.

Required: the occurrence remains on A. B can only enter through a new constitution/re-entry receipt.

### LIVE-SURFACE-003 — manifest drift

Manifest points to a missing or renamed entrypoint.

Required: `UNRESOLVED` or declared fallback. Never silently guess another file and call it canonical.

### LIVE-SURFACE-004 — connector unavailable

No live owner adapter is reachable.

Required: bootstrap may perform only work that its embedded floor can honestly support; freshness remains unresolved.

### LIVE-SURFACE-005 — orientation outranks owner

GitBook or Free Graph contains a newer-looking summary that conflicts with exact-SHA owner material.

Required: owner material wins for local project constitution; the conflicting projection remains attributable rather than erased.

### LIVE-SURFACE-006 — cross-organ authority leak

LOADOUT successfully resolves ALEX and 3rdi.

Required: resolution does not grant LOADOUT semantic ownership, write permission, promotion authority, or consequence authority in either project.

### LIVE-SURFACE-007 — overfetch

A task needs one mode and one reference but the adapter can access the whole repo.

Required: receipt demonstrates bounded loading rather than opportunistic whole-repo ingestion.

### LIVE-SURFACE-008 — mutable URL replay

A later run resolves the same branch name to a different SHA.

Required: receipts distinguish the occurrences and never call branch-name equality exact replay.

## 11. Implementation sequence

After this design is reviewed and approved:

1. define JSON Schemas for current-organ manifest and live-surface receipt in LOADOUT;
2. add a deterministic resolver library that accepts host-supplied repository evidence and emits a pinned constitution;
3. add `skills/loadout/` as the first owner/router skill;
4. add LOADOUT's `.live/current-organ.json`;
5. build hostile tests LIVE-SURFACE-001 through 008;
6. add 3rdi manifest and prove a no-refactor conforming specimen;
7. refactor ALEX entrypoint into router + bounded references without changing its constitutional claims;
8. add ALEX manifest and prove a conforming specimen;
9. generate the three thin ChatGPT upload surfaces from the same protocol template plus organ-owned static kernels;
10. only after those specimens pass, migrate Novelist, Riqor, or other custom plugins.

## 12. Deliberate deferrals

Do not build yet:

- a central Static Collective plugin;
- a network daemon that continuously pushes doctrine into ChatGPT;
- a global plugin registry with authority over owners;
- automatic cross-repo writes;
- silent auto-promotion from a manifest change;
- a universal ontology for every organ;
- a background process that mutates an in-flight occurrence when repositories change;
- full-repo ingestion as a convenience shortcut;
- remote code execution merely because a pinned repo contains scripts.

Live constitution is a retrieval and bounded-world problem first.

## 13. Acceptance criteria

The architecture is successful when:

1. the uploaded surface can stay unchanged while an owning repo evolves;
2. a new invocation can use the newer project-owned constitution without manual re-upload;
3. an in-flight occurrence remains reproducibly pinned to one exact SHA;
4. missing live access degrades visibly rather than manufacturing freshness;
5. the receipt names exactly what was resolved and loaded;
6. ALEX, 3rdi, and LOADOUT retain separate semantic ownership;
7. GitBook and Free Graph remain orientation/history surfaces rather than current project authority;
8. no effect authority is inferred from successful retrieval;
9. the protocol can be implemented without a central daemon or master ontology;
10. changing one organ does not require editing every other organ's uploaded surface.

## 14. Design compression

```text
SURFACE
  does not contain the organ

SURFACE
  knows how to find the owner

OWNER
  declares the current doorway

RESOLVER
  pins one exact constitution

LOADOUT
  bounds what enters

ORGAN
  owns what its material means

RECEIPT
  remembers what world was actually used
```

Final law:

> **Resolve live. Pin locally. Load minimally. Preserve ownership. Receipt the world.**
