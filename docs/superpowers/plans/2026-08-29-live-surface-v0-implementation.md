# LIVE-SURFACE v0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first executable LIVE-SURFACE / CURRENT-ORGAN specimen in LOADOUT: deterministic manifest validation, exact-SHA constitution resolution, bounded loading receipts, an owned portable LOADOUT skill, and hostile tests proving live-across-occurrences / pinned-within-an-occurrence behavior.

**Architecture:** Production code remains standard-library-only and network-agnostic. A pure resolver consumes host-supplied repository evidence rather than performing network access itself; LOADOUT validates owner manifests, freezes one exact commit SHA, verifies requested paths stay inside declared roots, and emits an attributable resolution receipt. The first specimen is LOADOUT-only; 3rdi and ALEX conform in separate follow-on changes after this contract is executable.

**Tech Stack:** Python 3.11+, standard library only in production, pytest for tests, JSON Schema documents as published contracts, Markdown portable skill.

**Spec:** `docs/superpowers/specs/2026-08-29-live-surface-current-organ-design.md`

## Global Constraints

- Standard library only in production code.
- No production network access; hosts supply repository evidence explicitly.
- The resolver freezes one exact 40-hex commit SHA per occurrence.
- Branch names and mutable URLs are routing hints, never replay identities.
- Successful retrieval never grants effect, merge, publication, or write authority.
- Repository paths must be normalized relative paths with no `..`, absolute paths, or escape outside declared roots.
- Missing or malformed live evidence yields an explicit unresolved/refused result; never silently guess another canonical entrypoint.
- Embedded fallback is labeled `UNRESOLVED` and never described as current.
- LOADOUT owns the protocol contract, not neighboring organ semantics.

---

## File map

- Create `src/loadout/live_surface.py` — manifest validation, path normalization, constitution resolution, minimum-load selection, receipt generation.
- Create `schemas/current-organ-v0.schema.json` — published owner-manifest contract.
- Create `schemas/live-surface-receipt-v0.schema.json` — published resolution-receipt contract.
- Create `.live/current-organ.json` — LOADOUT-owned first manifest specimen.
- Create `skills/loadout/SKILL.md` — portable thin router/bootstrap for LOADOUT.
- Create `tests/test_live_surface.py` — LIVE-SURFACE-001 through 008 plus validation/unit cases.
- Modify `src/loadout/cli.py` — add a pure local `resolve-live` command that reads manifest/evidence JSON files and emits the receipt/constitution JSON.
- Modify `tests/test_cli.py` — CLI smoke coverage for `resolve-live`.
- Modify `README.md` — document the LIVE-SURFACE executable floor and ownership boundary.

---

### Task 1: Manifest and receipt contracts

**Files:**
- Create: `schemas/current-organ-v0.schema.json`
- Create: `schemas/live-surface-receipt-v0.schema.json`
- Create: `src/loadout/live_surface.py`
- Test: `tests/test_live_surface.py`

**Interfaces:**
- Produces: `validate_current_organ_manifest(manifest: dict) -> list[str]`
- Produces: `normalize_repo_path(path: str) -> str`
- Produces constants `MANIFEST_SCHEMA = "static-collective/current-organ/v0"` and `RECEIPT_SCHEMA = "static-collective/live-surface-receipt/v0"`.

- [ ] **Step 1: Write failing manifest validation tests**

```python
from loadout.live_surface import normalize_repo_path, validate_current_organ_manifest


def valid_manifest():
    return {
        "schema": "static-collective/current-organ/v0",
        "organ": "loadout",
        "owner": "the-static-collective/LOADOUT",
        "entrypoint": "skills/loadout/SKILL.md",
        "state": None,
        "allowed_roots": ["skills/loadout", "docs", "schemas"],
        "resolution": "default-branch-head-then-pin",
        "fallback": "embedded-bootstrap",
    }


def test_valid_manifest_has_no_errors():
    assert validate_current_organ_manifest(valid_manifest()) == []


def test_manifest_rejects_wrong_schema_and_unsafe_entrypoint():
    manifest = valid_manifest()
    manifest["schema"] = "wrong"
    manifest["entrypoint"] = "../ALEX/SKILL.md"
    errors = validate_current_organ_manifest(manifest)
    assert "unsupported schema" in errors
    assert "entrypoint is not a safe repository-relative path" in errors


def test_normalize_repo_path_refuses_escape():
    import pytest
    with pytest.raises(ValueError, match="unsafe repository path"):
        normalize_repo_path("skills/loadout/../../secret")
```

- [ ] **Step 2: Run the focused test and verify RED**

Run: `pytest -q tests/test_live_surface.py`

Expected: collection/import failure because `loadout.live_surface` does not exist.

- [ ] **Step 3: Implement minimal validation and normalization**

`normalize_repo_path()` must convert `\\` to `/`, reject empty paths, absolute paths, `.`/`..` segments, and return `/`-joined normalized segments. `validate_current_organ_manifest()` must return deterministic error strings in field-order for missing/invalid `schema`, `organ`, `owner`, `entrypoint`, `allowed_roots`, `resolution`, and `fallback`.

- [ ] **Step 4: Publish exact JSON Schema contracts**

`current-organ-v0.schema.json` must require `schema`, `organ`, `owner`, `entrypoint`, `allowed_roots`, `resolution`, and `fallback`; `state` may be string or null. `live-surface-receipt-v0.schema.json` must require `schema`, `organ`, `owner`, `resolved_ref`, `resolved_sha`, `manifest_path`, `entrypoint`, `loaded`, `freshness`, and `fallback_used`; `resolved_sha` pattern is `^[0-9a-f]{40}$` when freshness is `RESOLVED`.

- [ ] **Step 5: Run focused tests and compile check**

Run: `python -m compileall -q src && pytest -q tests/test_live_surface.py`

Expected: PASS.

- [ ] **Step 6: Commit**

Commit message: `feat: define live-surface contracts`

---

### Task 2: Exact-SHA resolver and bounded loading

**Files:**
- Modify: `src/loadout/live_surface.py`
- Modify: `tests/test_live_surface.py`

**Interfaces:**
- Consumes: validated current-organ manifest.
- Produces: `resolve_current_organ(manifest: dict, evidence: dict, *, requested_paths: list[str] | None = None) -> dict`
- Produces receipt under result key `receipt` and loaded content under result key `documents`.

Host evidence shape:

```python
{
    "resolved_ref": "main",
    "resolved_sha": "0123456789abcdef0123456789abcdef01234567",
    "files": {
        ".live/current-organ.json": "{...}",
        "skills/loadout/SKILL.md": "...",
        "docs/example.md": "...",
    },
}
```

- [ ] **Step 1: Write RED tests for pinning and minimum loading**

```python
def test_resolver_pins_exact_sha_and_loads_entrypoint_only_by_default():
    manifest = valid_manifest()
    evidence = {
        "resolved_ref": "main",
        "resolved_sha": "0123456789abcdef0123456789abcdef01234567",
        "files": {
            "skills/loadout/SKILL.md": "skill",
            "docs/extra.md": "extra",
        },
    }
    result = resolve_current_organ(manifest, evidence)
    assert result["receipt"]["resolved_sha"] == evidence["resolved_sha"]
    assert result["receipt"]["loaded"] == ["skills/loadout/SKILL.md"]
    assert result["documents"] == {"skills/loadout/SKILL.md": "skill"}


def test_requested_path_outside_allowed_roots_is_refused():
    manifest = valid_manifest()
    evidence = {"resolved_ref": "main", "resolved_sha": "0" * 40, "files": {"skills/loadout/SKILL.md": "skill", "src/loadout/cli.py": "code"}}
    result = resolve_current_organ(manifest, evidence, requested_paths=["src/loadout/cli.py"])
    assert result["status"] == "REFUSE"
    assert "outside allowed roots" in result["reasons"]
```

- [ ] **Step 2: Run focused tests and verify RED**

Run: `pytest -q tests/test_live_surface.py`

Expected: FAIL because `resolve_current_organ` is absent.

- [ ] **Step 3: Implement deterministic resolver**

Rules:
1. validate manifest first;
2. require `resolved_ref` non-empty string;
3. require `resolved_sha` exactly 40 lowercase hex chars;
4. never derive or mutate SHA from branch data;
5. start load-set with entrypoint;
6. append explicitly requested normalized paths in request order without duplicates;
7. every loaded path must equal an allowed root or start with `<root>/`;
8. every loaded path must exist in `evidence["files"]`;
9. return `status="RESOLVED"`, `freshness="RESOLVED"`, `fallback_used=False` only after all requested content is present;
10. receipt ordering is deterministic.

- [ ] **Step 4: Add hostile LIVE-SURFACE-002, 007, and 008 tests**

- 002: call resolver once with SHA A and keep returned receipt; construct later evidence at SHA B and prove the first result is unchanged.
- 007: prove unrequested in-root files are not loaded.
- 008: resolve `main` twice at two SHAs and prove receipts differ despite equal branch names.

- [ ] **Step 5: Run focused tests**

Run: `pytest -q tests/test_live_surface.py`

Expected: PASS.

- [ ] **Step 6: Commit**

Commit message: `feat: add exact-sha live resolver`

---

### Task 3: Honest unresolved/fallback behavior

**Files:**
- Modify: `src/loadout/live_surface.py`
- Modify: `tests/test_live_surface.py`

**Interfaces:**
- Produces: `unresolved_current_organ(manifest: dict, *, reason: str, embedded_entrypoint: str | None = None) -> dict`

- [ ] **Step 1: Write RED tests for LIVE-SURFACE-001, 003, and 004**

Required assertions:
- stale embedded text never overrides successful live evidence (001);
- missing live entrypoint returns unresolved/refused and does not guess a sibling path (003);
- connector/evidence unavailable may return embedded entrypoint only with `freshness="UNRESOLVED"`, `fallback_used=True`, and `resolved_sha=None` (004).

- [ ] **Step 2: Run focused tests and verify RED**

Run: `pytest -q tests/test_live_surface.py`

Expected: FAIL on missing unresolved helper/behavior.

- [ ] **Step 3: Implement unresolved result**

Return shape:

```python
{
    "status": "UNRESOLVED",
    "reasons": [reason],
    "documents": {} if embedded_entrypoint is None else {manifest["entrypoint"]: embedded_entrypoint},
    "receipt": {
        "schema": "static-collective/live-surface-receipt/v0",
        "organ": manifest.get("organ"),
        "owner": manifest.get("owner"),
        "resolved_ref": None,
        "resolved_sha": None,
        "manifest_path": ".live/current-organ.json",
        "entrypoint": manifest.get("entrypoint"),
        "loaded": [] if embedded_entrypoint is None else [manifest["entrypoint"]],
        "freshness": "UNRESOLVED",
        "fallback_used": embedded_entrypoint is not None,
    },
}
```

The live resolver must delegate to this shape for malformed/missing evidence rather than manufacturing a current result.

- [ ] **Step 4: Run focused tests**

Run: `pytest -q tests/test_live_surface.py`

Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `feat: preserve unresolved live-surface state`

---

### Task 4: LOADOUT-owned manifest and portable skill

**Files:**
- Create: `.live/current-organ.json`
- Create: `skills/loadout/SKILL.md`
- Modify: `tests/test_live_surface.py`

**Interfaces:**
- Manifest entrypoint: `skills/loadout/SKILL.md`.
- Skill declares LOADOUT identity, core non-collapses, resolution procedure, owner boundary, fallback rule, and receipt rule only.

- [ ] **Step 1: Write RED repository-specimen test**

```python
import json
from pathlib import Path


def test_repository_manifest_points_to_existing_portable_skill():
    manifest = json.loads(Path(".live/current-organ.json").read_text())
    assert validate_current_organ_manifest(manifest) == []
    assert Path(manifest["entrypoint"]).is_file()
    text = Path(manifest["entrypoint"]).read_text()
    assert "Live across occurrences; pinned within an occurrence." in text
    assert "Knowledge may load. Capability may bind. Authority does not silently expand." in text
```

- [ ] **Step 2: Run focused test and verify RED**

Run: `pytest -q tests/test_live_surface.py`

Expected: FAIL because manifest/skill files do not exist.

- [ ] **Step 3: Create `.live/current-organ.json`**

Exact manifest:

```json
{
  "schema": "static-collective/current-organ/v0",
  "organ": "loadout",
  "owner": "the-static-collective/LOADOUT",
  "entrypoint": "skills/loadout/SKILL.md",
  "state": null,
  "allowed_roots": ["skills/loadout", "docs", "schemas", "evals"],
  "resolution": "default-branch-head-then-pin",
  "fallback": "embedded-bootstrap"
}
```

- [ ] **Step 4: Create thin `skills/loadout/SKILL.md`**

The skill must include:
- purpose: smallest world that can do the job;
- flow: TASK → CUT → CLASSIFY → DISCOVER → SELECT → REACH → FENCE → BIND → WORK → RECEIPT;
- constitutional law: `Knowledge may load. Capability may bind. Authority does not silently expand.`;
- live-surface law: `Live across occurrences; pinned within an occurrence.`;
- retrieval/adoption, pointer/truth, loaded/supported, receipt/authority non-collapses;
- exact resolution steps: fetch manifest, resolve owner head, pin SHA, load only needed declared roots, work, receipt;
- fallback: embedded floor is `UNRESOLVED`, never current;
- neighboring ownership: ALEX evidence/derivation, 3rdi projection, Free Graph historical roads, owners retain consequence;
- no network/tool claim when host cannot provide it.

- [ ] **Step 5: Run focused test**

Run: `pytest -q tests/test_live_surface.py`

Expected: PASS.

- [ ] **Step 6: Commit**

Commit message: `feat: add loadout current-organ specimen`

---

### Task 5: Authority and source-precedence hostile tests

**Files:**
- Modify: `tests/test_live_surface.py`
- Modify: `src/loadout/live_surface.py` only if a failing test exposes a missing contract rule.

**Interfaces:** No new public API required unless the test demonstrates a missing pure helper.

- [ ] **Step 1: Add LIVE-SURFACE-005 test**

Model owner content and an orientation/history document as separate requested material. Assert the receipt preserves both paths but the resolver never emits a field such as `adopted_from`, `authority_owner`, or `current_truth` derived from orientation/history. Owner content remains the constitution entrypoint.

- [ ] **Step 2: Add LIVE-SURFACE-006 test**

Use a manifest containing an extra unknown field such as `"write_authority": true`. Assert validation rejects unknown authority-bearing fields (or, if schema policy allows extensions, assert the resolver ignores it and receipt contains no authority grants). Selected v0 policy: **reject unknown top-level fields** to keep the contract tight.

- [ ] **Step 3: Run focused tests**

Run: `pytest -q tests/test_live_surface.py`

Expected: PASS after any minimal validator hardening.

- [ ] **Step 4: Commit**

Commit message: `test: pressure live-surface authority boundaries`

---

### Task 6: Local CLI adapter

**Files:**
- Modify: `src/loadout/cli.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Produces command: `loadout resolve-live MANIFEST EVIDENCE [--path PATH ...]`.
- Reads JSON from local files only; no network access.
- Emits one JSON object to stdout; exit code 0 for `RESOLVED`, exit code 2 for `UNRESOLVED`/`REFUSE`.

- [ ] **Step 1: Write RED CLI smoke test**

Create temporary manifest/evidence files, invoke `python -m loadout.cli resolve-live ...`, assert JSON receipt SHA and bounded loaded list.

- [ ] **Step 2: Run CLI test and verify RED**

Run: `pytest -q tests/test_cli.py`

Expected: FAIL because `resolve-live` is not registered.

- [ ] **Step 3: Add parser and handler**

Import `resolve_current_organ`; read UTF-8 JSON files; pass repeated `--path` values in user order; print sorted-key JSON using the CLI's existing output convention; do not catch programming exceptions beyond converting declared unresolved/refused results into exit code 2.

- [ ] **Step 4: Run CLI test**

Run: `pytest -q tests/test_cli.py`

Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `feat: expose local live resolver cli`

---

### Task 7: Documentation and full verification

**Files:**
- Modify: `README.md`

**Interfaces:** Documents existing behavior only.

- [ ] **Step 1: Add README LIVE-SURFACE section**

Document:

```text
uploaded surface != organ
resolve owner head -> pin SHA -> load minimally -> work -> receipt
live across occurrences; pinned within an occurrence
fallback != current
common protocol != common owner
```

Include the manifest path `.live/current-organ.json`, portable entrypoint `skills/loadout/SKILL.md`, and local CLI example using fixture JSON files. State explicitly that production resolver code performs no network access.

- [ ] **Step 2: Run full verification**

Run:

```bash
python -m compileall -q src
pytest -q
```

Expected: exit 0 and zero failing tests.

- [ ] **Step 3: Verify hostile-case coverage by name**

Run:

```bash
pytest -q tests/test_live_surface.py -vv
```

Confirm the suite includes coverage corresponding to LIVE-SURFACE-001 through LIVE-SURFACE-008.

- [ ] **Step 4: Inspect branch diff**

Confirm only the planned LOADOUT protocol/specimen files changed; no ALEX or 3rdi semantics are copied into LOADOUT.

- [ ] **Step 5: Commit**

Commit message: `docs: document live-surface executable floor`

---

## Follow-on plans after LOADOUT v0

These are intentionally separate because each neighboring repository owns its own semantics:

1. **3rdi conforming specimen:** add its owner manifest, pressure its current thin `SKILL.md`, prove current-head-then-pin against the LOADOUT resolver contract.
2. **ALEX current-organ refactor:** split the large entrypoint into thin router + bounded references without semantic drift, then add its manifest and conformance specimen.
3. **ChatGPT upload surfaces:** generate tiny stable bootstraps for LOADOUT/3rdi/ALEX only after all three owner-side specimens are verified.

No follow-on plan may centralize organ authority in LOADOUT.
