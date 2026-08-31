# MERGE-FORMATION-RECEIPT-001

**Status:** executable development analyzer · source-system agnostic · authority none

`loadout.dev.merge_formation` consumes frozen `loadout.merge-formation-evidence/v0` data and emits deterministic `loadout.merge-formation-receipt/v0` data. It performs no repository access and no workflow mutation.

## Boundary

```text
behind main != unsafe
formation data != truth
formation data != authority
HUMANENTROPY = research interpretation layer
runtime = content preservation + check state + topology facts
```

The runtime uses neutral mechanical vocabulary only. It does not decide semantic conflict, merge a candidate, mark a review Ready, or infer authorization from green checks.

## Content classifications

- `SAFE_CONTENT_COMPOSITION` — every declared main-only and feature-only change is preserved, no sentinel drift is detected, the candidate/surface are complete, and no path is changed by both histories.
- `OVERLAP_REVIEW_REQUIRED` — at least one declared path changed on both main and feature; v0 refuses to promote overlap to mechanical safety regardless of its resolution label.
- `INCOMPLETE_EVIDENCE` — the declared surface or candidate state is incomplete and no stronger loss finding was already established.
- `LOSS_DETECTED` — a main-only or feature-only change is absent/different in the complete candidate, or an unchanged sentinel drifts.

Fixed precedence:

```text
LOSS_DETECTED
  > INCOMPLETE_EVIDENCE
  > OVERLAP_REVIEW_REQUIRED
  > SAFE_CONTENT_COMPOSITION
```

## Orthogonal receipt surfaces

Content preservation, combined verification state, and formation topology are independent. In particular:

- green checks cannot erase detected content loss;
- failed checks do not rewrite a mechanical content-preservation result;
- parent count does not determine content safety;
- `behind_main` is descriptive only;
- parent order is retained as formation data while path evidence is sorted canonically for deterministic replay.

`authority` is always `none`.
