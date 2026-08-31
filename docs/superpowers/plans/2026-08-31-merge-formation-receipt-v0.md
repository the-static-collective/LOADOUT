# MERGE-FORMATION-RECEIPT-001 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deterministically classify whether a declared merge candidate preserves disjoint main/feature content, loses content, requires overlap review, or lacks enough evidence, while reporting verification and history topology as independent facts.

**Architecture:** A pure `loadout.dev.merge_formation` analyzer consumes only frozen `loadout.merge-formation-evidence/v0` JSON. It never invokes Git/GitHub and never mutates workflow state. A module CLI reads one evidence file and emits one canonical receipt to stdout.

**Tech Stack:** Python >=3.11; standard library only; dataclasses/enum/re/hashlib/json as needed; existing `loadout.canonical.canonical_json`; pytest.

**Spec:** `docs/superpowers/specs/2026-08-31-merge-formation-receipt-v0-design.md`

## Global Constraints

- `STALE != UNSAFE` and `behind_main` is descriptive only.
- Content preservation, combined verification, and formation topology remain separate receipt surfaces.
- Overlap never auto-promotes to safe in v0.
- Green checks never override detected content loss.
- HUMANENTROPY remains a research nickname; runtime emits neutral mechanical facts only.
- The analyzer performs no Git/GitHub calls, merges, Ready mutations, or semantic conflict judgments.
- Reordered lawful evidence must produce byte-identical canonical output after path sorting.

---

### Task 1: Freeze the evidence model and refusal codes

**Files:**
- Create: `src/loadout/dev/merge_formation.py`
- Create: `tests/test_dev_merge_formation.py`
- Create: `tests/fixtures/merge_formation/`

**Interfaces:**
- Exception:

```python
class MergeFormationInputError(ValueError):
    reason_code: str
    residual: str
```

- Function:

```python
def analyze_merge_formation(evidence: dict[str, object]) -> dict[str, object]: ...
```

- Freeze these evidence fields:

```text
schema = loadout.merge-formation-evidence/v0
base_sha
main_sha
feature_sha
candidate_sha: str | null
behind_main: bool
surface_complete: bool
candidate_complete: bool
combined_verification: pass | fail | not-run | unknown
candidate_parent_shas: list[str] (optional; order preserved)
surface: list[path record]
```

- Path record fields:

```text
path
base_digest: sha256:* | null
main_digest: sha256:* | null
feature_digest: sha256:* | null
candidate_digest: sha256:* | null
main_changed: bool
feature_changed: bool
resolution: main | feature | combined | manual | null
sentinel: bool (optional, default false)
```

`null` digest means the path is absent in that tree. Unknown candidate state is represented by `candidate_complete=false`, not by abusing `null`.

- [ ] **Step 1: Write RED malformed-evidence tests**

Add one valid packet helper and tests for:

```text
WRONG_SCHEMA
MISSING_IDENTITY
DUPLICATE_PATH
INVALID_DIGEST_STATE
DECLARED_CHANGE_MISMATCH
CANDIDATE_IDENTITY_REQUIRED
INVALID_CHECK_STATE
```

Example declared-change mismatch:

```python
record = {
    "path": "a.txt",
    "base_digest": digest("base"),
    "main_digest": digest("base"),
    "feature_digest": digest("feature"),
    "candidate_digest": digest("feature"),
    "main_changed": True,
    "feature_changed": True,
    "resolution": None,
}
with pytest.raises(MergeFormationInputError) as exc:
    analyze_merge_formation(packet(surface=[record]))
assert exc.value.reason_code == "DECLARED_CHANGE_MISMATCH"
```

- [ ] **Step 2: Run focused RED**

```bash
pytest -q tests/test_dev_merge_formation.py
```

Expected: import failure.

- [ ] **Step 3: Implement validation helpers**

Validate 40-lowercase-hex SHAs for commit identities and `sha256:` + 64 lowercase hex characters for non-null file digests. Derive:

```python
main_changed = main_digest != base_digest
feature_changed = feature_digest != base_digest
```

and refuse when declared booleans disagree. Sort surface records by `path`; preserve `candidate_parent_shas` order.

- [ ] **Step 4: Run focused GREEN**

```bash
pytest -q tests/test_dev_merge_formation.py
```

- [ ] **Step 5: Commit the evidence floor**

```bash
git add src/loadout/dev/merge_formation.py tests/test_dev_merge_formation.py tests/fixtures/merge_formation
git commit -m "feat: validate merge formation evidence"
```

---

### Task 2: Implement content-preservation classification

**Files:**
- Modify: `src/loadout/dev/merge_formation.py`
- Modify: `tests/test_dev_merge_formation.py`
- Create fixture files under: `tests/fixtures/merge_formation/`

**Interfaces:**
- Classification strings:

```text
SAFE_CONTENT_COMPOSITION
OVERLAP_REVIEW_REQUIRED
INCOMPLETE_EVIDENCE
LOSS_DETECTED
```

- Precedence:

```text
LOSS_DETECTED > INCOMPLETE_EVIDENCE > OVERLAP_REVIEW_REQUIRED > SAFE_CONTENT_COMPOSITION
```

- [ ] **Step 1: Add RED disjoint-safe fixture**

Freeze `safe-disjoint.json`:

```text
base: neither a.txt nor b.txt
main: adds a.txt
feature: adds b.txt
candidate: contains both exact digests
behind_main: true
combined_verification: pass
```

Require `SAFE_CONTENT_COMPOSITION`, `content_loss=false`, `main_preserved=["a.txt"]`, `feature_preserved=["b.txt"]`.

- [ ] **Step 2: Add RED loss fixtures**

Freeze separate fixtures where candidate drops the feature-only path, drops the main-only path, and restores base bytes over a main-only edit. Require `LOSS_DETECTED` and exact `lost` entries naming both path and side.

- [ ] **Step 3: Add RED overlap fixtures**

Both main and feature change `same.txt`; one candidate equals feature bytes and one uses a third combined digest. Both must classify `OVERLAP_REVIEW_REQUIRED`, regardless of `resolution` label.

- [ ] **Step 4: Add RED incomplete-evidence fixture**

Set `candidate_sha=null`, `candidate_complete=false`, and keep valid main/feature digests. Require `INCOMPLETE_EVIDENCE`, not loss.

- [ ] **Step 5: Run focused RED**

```bash
pytest -q tests/test_dev_merge_formation.py
```

- [ ] **Step 6: Implement path classification**

For each path:

```text
main-only change    -> candidate must equal main digest when candidate_complete
feature-only change -> candidate must equal feature digest when candidate_complete
both changed        -> overlap
sentinel unchanged  -> candidate drift is unintended overwrite / loss-class finding
```

Unchanged non-sentinel paths make no preservation claim.

- [ ] **Step 7: Derive final classification with fixed precedence**

Populate:

```python
"paths": {
    "feature_preserved": [...],
    "main_preserved": [...],
    "overlap": [...],
    "lost": [...],
    "incomplete": [...],
}
```

Sort every path list lexicographically.

- [ ] **Step 8: Run focused GREEN**

```bash
pytest -q tests/test_dev_merge_formation.py
```

- [ ] **Step 9: Commit content classification**

```bash
git add src/loadout/dev/merge_formation.py tests/test_dev_merge_formation.py tests/fixtures/merge_formation
git commit -m "feat: classify merge content preservation"
```

---

### Task 3: Keep checks and formation topology orthogonal

**Files:**
- Modify: `src/loadout/dev/merge_formation.py`
- Modify: `tests/test_dev_merge_formation.py`
- Add fixtures under: `tests/fixtures/merge_formation/`

**Interfaces:**
- Receipt adds:

```json
{
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

- [ ] **Step 1: Add RED check-orthogonality controls**

Case A: lost feature + `combined_verification=pass` must remain `LOSS_DETECTED`.

Case B: safe disjoint content + `combined_verification=fail` must remain `SAFE_CONTENT_COMPOSITION` while checks report `fail`.

- [ ] **Step 2: Add RED topology controls**

For the same content surface, compare:

```python
candidate_parent_shas=[main_sha]
```

versus:

```python
candidate_parent_shas=[main_sha, feature_sha]
```

Require identical content classification but different `candidate_has_multiple_parents`. Compute:

```python
histories_diverged = main_sha != feature_sha
formation_data_available = histories_diverged or candidate_has_multiple_parents
```

- [ ] **Step 3: Run focused RED**

```bash
pytest -q tests/test_dev_merge_formation.py
```

- [ ] **Step 4: Implement orthogonal receipt surfaces**

Never derive `combined_verification` from content. Never derive content safety from parent count. Freeze `authority: "none"`.

- [ ] **Step 5: Add deterministic receipt identity**

Use existing `loadout.canonical.canonical_json`. Add:

```python
def render_merge_formation_receipt(receipt: dict[str, object]) -> str:
    return canonical_json(receipt) + "\n"
```

- [ ] **Step 6: Prove reordered surface determinism**

Shuffle the input `surface` list and require byte-identical `render_merge_formation_receipt(...)` output. Parent order remains unchanged in the receipt.

- [ ] **Step 7: Commit topology/check separation**

```bash
git add src/loadout/dev/merge_formation.py tests/test_dev_merge_formation.py tests/fixtures/merge_formation
git commit -m "feat: receipt merge formation topology"
```

---

### Task 4: Add the no-side-effect CLI

**Files:**
- Modify: `src/loadout/dev/merge_formation.py`
- Create: `tests/test_dev_merge_formation_cli.py`

**Interfaces:**
- Command:

```bash
python -m loadout.dev.merge_formation evidence.json
```

- stdout: exactly one canonical `loadout.merge-formation-receipt/v0` JSON object + newline.
- malformed input exits `2` and prints stable reason code + residual to stderr.

- [ ] **Step 1: Add RED CLI success test**

Invoke the module against `safe-disjoint.json`. Assert exit `0`, empty stderr, schema `loadout.merge-formation-receipt/v0`, and classification `SAFE_CONTENT_COMPOSITION`.

- [ ] **Step 2: Add RED malformed CLI test**

Use wrong schema; assert exit `2` and stderr includes `WRONG_SCHEMA`.

- [ ] **Step 3: Run focused RED**

```bash
pytest -q tests/test_dev_merge_formation_cli.py
```

- [ ] **Step 4: Implement argparse/file boundary**

Read UTF-8 JSON from one required positional path. Catch only `OSError`, `json.JSONDecodeError`, and `MergeFormationInputError`; do not catch programming errors as evidence refusals.

- [ ] **Step 5: Add static no-host-access guard**

Test module source contains no imports of `subprocess`, `urllib`, `requests`, `socket`, or GitHub client packages. The analyzer is intentionally source-system agnostic.

- [ ] **Step 6: Run focused GREEN**

```bash
pytest -q tests/test_dev_merge_formation.py tests/test_dev_merge_formation_cli.py
```

- [ ] **Step 7: Commit the CLI**

```bash
git add src/loadout/dev/merge_formation.py tests/test_dev_merge_formation_cli.py
git commit -m "feat: add merge formation receipt cli"
```

---

### Task 5: Seal HUMANENTROPY as interpretation, not runtime ontology

**Files:**
- Create: `docs/MERGE-FORMATION-RECEIPT-001.md`
- Modify: `src/loadout/dev/__init__.py`
- Modify: `tests/test_dev_public_api.py`

**Interfaces:**
- Public development API may export `analyze_merge_formation`, `MergeFormationInputError`, and `render_merge_formation_receipt`.

- [ ] **Step 1: Add public API test**

Require the three explicitly exported names to import from `loadout.dev`; do not export a `HumanEntropy` type or `humanentropy()` function.

- [ ] **Step 2: Write the boundary document**

State exactly:

```text
behind main != unsafe
formation data != truth
formation data != authority
HUMANENTROPY = research interpretation layer
runtime = content preservation + check state + topology facts
```

Include the four classification definitions and the fixed precedence.

- [ ] **Step 3: Run the full LOADOUT floor**

```bash
python -m compileall -q src
pytest -q
```

Expected: all current + new tests pass.

- [ ] **Step 4: Commit the seal**

```bash
git add docs/MERGE-FORMATION-RECEIPT-001.md src/loadout/dev/__init__.py tests/test_dev_public_api.py
git commit -m "docs: seal merge formation receipt boundary"
```
