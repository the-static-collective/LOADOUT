# MERGE-FORMATION-RECEIPT-001 Design

## Status

Approved architectural slice against `LOADOUT/main@41e5e5055d0a87518c67af4d63442662a508eed4`.

Research nickname: **HUMANENTROPY — THE GRAPH REMEMBERS THE HAND**.

`humanentropy` is not a runtime ontology or safety verdict. The executable emits neutral content-preservation and formation-topology facts that later humans/ALEX may interpret.

## Goal

Replace the crude heuristic

```text
behind main -> suspicious
```

with a bounded executable question:

```text
If these histories are composed, does the candidate preserve the intended feature contribution and the already-landed main contribution on the declared surface?
```

The tool receipts composition structure. It never merges anything.

## Core laws

```text
STALE != UNSAFE
MERGEABLE != SEMANTICALLY CORRECT
GREEN CHECKS != CONTENT-PRESERVATION PROOF
DIFFERENT HISTORY != DAMAGED TREE
SAME FINAL TREE != SAME FORMATION HISTORY
FORMATION DATA != TRUTH
FORMATION DATA != AUTHORITY
```

A braided history may be useful provenance when content integrity survives.

## Ownership

LOADOUT owns this because it is developer-workflow constitution and bounded effect fencing: inspect a proposed state transition, report what would be preserved/lost, and stop before owner admission.

ALEX may later interpret a formation receipt as research provenance. Dogram may calculate graph properties over supplied history. GitHub remains an external source system. None of those systems are imported into the pure analyzer.

## Architecture

Split v0 into two layers:

```text
host/source evidence
    -> merge-formation.evidence/v0
    -> pure MergeFormation analyzer
    -> merge-formation.receipt/v0
```

The analyzer does not call GitHub or Git itself. That keeps the semantic core deterministic and allows evidence to come from:

- connected GitHub tooling;
- a future local Git adapter;
- frozen fixtures;
- another owner-approved source.

A later host adapter may generate evidence packets, but it must not be required for the core executable.

## Evidence packet

Schema:

```text
loadout.merge-formation-evidence/v0
```

Required identity:

```json
{
  "schema": "loadout.merge-formation-evidence/v0",
  "base_sha": "...",
  "main_sha": "...",
  "feature_sha": "...",
  "candidate_sha": "... or null",
  "behind_main": true,
  "surface": []
}
```

`base_sha` is the declared common comparison base used to define each side's contribution. It is not inferred by the analyzer.

`candidate_sha` is present only when a concrete candidate/merge result has been materialized or observed. The analyzer must distinguish a hypothetical overlap inspection from verification of an actual candidate tree.

## Surface records

Each path in the union of relevant main/feature changes is represented once:

```json
{
  "path": "docs/example.md",
  "base_digest": "sha256:... or null",
  "main_digest": "sha256:... or null",
  "feature_digest": "sha256:... or null",
  "candidate_digest": "sha256:... or null",
  "main_changed": false,
  "feature_changed": true,
  "resolution": null
}
```

`null` digest means path absent in that tree, not unknown. Unknown evidence uses an explicit evidence-completeness field rather than overloading null.

For overlapping paths, optional `resolution` may be:

```text
main
feature
combined
manual
```

This label is testimony about the chosen resolution strategy, not proof that the resolution is semantically good.

The analyzer derives `main_changed` and `feature_changed` from digests and rejects packets whose declared booleans disagree.

## Content-preservation rules

For a feature-only changed path:

```text
feature_digest != base_digest
main_digest == base_digest
```

A concrete candidate preserves the feature contribution only when:

```text
candidate_digest == feature_digest
```

For a main-only changed path, candidate must equal `main_digest`.

For an unchanged path, the analyzer makes no preservation claim unless the path was explicitly included as a hostile sentinel.

### Disjoint contributions

If all changed paths are disjoint and a concrete candidate preserves both sides exactly, classify:

```text
SAFE_CONTENT_COMPOSITION
```

This means only that the declared content surface was preserved.

### Overlap

If both sides changed the same path, exact side-preservation is impossible unless the resulting bytes happen to match one side.

The analyzer classifies overlapping paths separately:

```text
OVERLAP_REVIEW_REQUIRED
```

unless evidence explicitly proves a known resolution and a higher-level reviewer has separately accepted its semantics. v0 does not auto-promote `combined` or `manual` to safe.

### Loss

If a feature-only or main-only contribution is absent/reverted in the candidate:

```text
LOSS_DETECTED
```

The receipt identifies exact paths and which side's contribution was lost.

### Incomplete evidence

If candidate bytes are unavailable, declared paths are missing from the packet, or evidence completeness is false:

```text
INCOMPLETE_EVIDENCE
```

Do not guess safe from mergeability or green checks.

## Receipt

Schema:

```text
loadout.merge-formation-receipt/v0
```

Example:

```json
{
  "schema": "loadout.merge-formation-receipt/v0",
  "base_sha": "base",
  "main_sha": "main",
  "feature_sha": "feature",
  "candidate_sha": "candidate",
  "behind_main": true,
  "classification": "SAFE_CONTENT_COMPOSITION",
  "content_loss": false,
  "unintended_overwrite_detected": false,
  "paths": {
    "feature_preserved": ["research/new.md"],
    "main_preserved": ["runtime/new.py"],
    "overlap": [],
    "lost": [],
    "incomplete": []
  },
  "formation": {
    "histories_diverged": true,
    "candidate_has_multiple_parents": true,
    "formation_data_available": true
  },
  "checks": {
    "combined_verification": "pass"
  },
  "authority": "none"
}
```

`combined_verification` is supplied evidence with allowed values:

```text
pass
fail
not-run
unknown
```

The analyzer must not manufacture a pass because content preservation succeeded.

## Formation topology

Optional evidence may describe candidate parent SHAs:

```json
{
  "candidate_parent_shas": ["main", "feature"]
}
```

The analyzer may state mechanically:

```text
candidate_has_multiple_parents = true
histories_diverged = main_sha != feature_sha
formation_data_available = histories_diverged || candidate_has_multiple_parents
```

It must not state that the topology is meaningful, desirable, human-authored, or evidentiary.

The Daily Slice term HUMANENTROPY remains the interpretation layer:

```text
attributable irregularity introduced by human traversal through a system
```

Runtime output stays neutral.

## Status matrix

Final classification precedence:

```text
LOSS_DETECTED
  > INCOMPLETE_EVIDENCE
  > OVERLAP_REVIEW_REQUIRED
  > SAFE_CONTENT_COMPOSITION
```

A failing combined verification does not rewrite the content classification. It is reported orthogonally:

```text
content composition safe
+ combined verification fail
=
DO NOT CLAIM READY
```

The receipt may expose a convenience `ready_candidate` boolean only if it is strictly derived as:

```text
classification == SAFE_CONTENT_COMPOSITION
AND combined_verification == pass
```

Even then `ready_candidate != merge authority`.

Preferred v0 is to omit this boolean and leave the two facts separate.

## Hostile controls

Freeze at least these synthetic cases:

1. feature adds file A, main adds file B, candidate contains both -> safe content composition;
2. branch is many commits behind but contributions remain disjoint -> same result as case 1;
3. candidate drops feature file -> loss detected;
4. candidate drops main file -> loss detected;
5. candidate silently restores base bytes over main-only edit -> loss detected;
6. both sides edit same path -> overlap review required;
7. overlap candidate equals feature side -> still overlap review required, not automatically safe;
8. no candidate digests -> incomplete evidence;
9. green combined check + lost file -> loss remains primary;
10. safe content composition + failed combined check -> both facts preserved;
11. two candidate parents reported -> formation data available;
12. identical final file surface with one-parent vs two-parent candidate -> content classification may match while formation topology differs;
13. input record booleans disagree with digests -> refuse malformed evidence;
14. reordered input surface -> byte-identical canonical receipt after sorting paths.

## CLI

Expose a developer-local command that consumes one evidence JSON file and prints one canonical receipt to stdout.

Suggested command:

```text
loadout-dev merge-formation evidence.json
```

If current packaging does not yet provide a `loadout-dev` executable, a module entry point is acceptable:

```text
python -m loadout.dev.merge_formation evidence.json
```

The CLI performs no Git or GitHub writes and no merge operation.

## Canonicalization

Paths are sorted lexicographically. Parent SHA order is preserved because parent order can carry formation information; the analyzer may additionally expose a sorted set only for membership checks.

Digest strings are opaque identities after syntax validation. The analyzer does not hash unavailable source bytes itself.

Repeated identical evidence produces byte-identical receipt JSON.

## Error handling

Malformed packets refuse with stable reason codes, including:

```text
WRONG_SCHEMA
MISSING_IDENTITY
DUPLICATE_PATH
INVALID_DIGEST_STATE
DECLARED_CHANGE_MISMATCH
CANDIDATE_IDENTITY_REQUIRED
INVALID_CHECK_STATE
```

Malformed evidence is distinct from incomplete but lawful evidence.

## Boundaries

This slice does not:

- merge branches;
- mark PRs ready;
- call GitHub;
- infer semantic conflict from textual overlap;
- treat no-overlap as universal safety;
- treat tests as content proof;
- treat content proof as semantic proof;
- declare humanentropy true;
- mint evidence/support/authority;
- rewrite Git history.

## Acceptance

Complete when the pure analyzer classifies all hostile fixtures deterministically, reports content preservation independently from combined checks and topology, refuses malformed evidence, and makes `behind_main` purely descriptive rather than a safety verdict.

> **THE GRAPH MAY REMEMBER THE HAND. THE TOOL ONLY PROVES WHAT THE HAND DID NOT DROP.**
