# READ-ONLY-HOST-ADAPTER-001 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconcile CURRENT-ORGAN onto current LOADOUT, then prove one real local-Git read boundary that resolves refs and reads immutable blobs without exposing write/network authority.

**Architecture:** First replay the still-valid LIVE-SURFACE / CURRENT-ORGAN v0 payload from PR #5 onto current `main` and rerun its floor. Then extend `EffectIntent` with a backward-compatible deterministic parameter carrier, implement `LocalGitReadAdapter` under the existing adapter protocol, and let CURRENT-ORGAN use that adapter to build host evidence pinned to one exact commit.

**Tech Stack:** Python >=3.11; standard library production code; `subprocess`, `pathlib`, `hashlib`; pytest; local Git executable for integration tests only.

**Spec:** `docs/superpowers/specs/2026-08-31-read-only-host-adapter-v0-design.md`

## Global Constraints

- `READ != WRITE`; no checkout/switch/merge/reset/commit/push/fetch/pull.
- No network or credential surface.
- Repository root is fixed at adapter construction.
- `git.read_blob` reads exact `<commit>:<path>` bytes, never working-tree fallback.
- Path traversal refuses before Git invocation.
- `body_time_id` remains explicit and stable for one workflow occurrence.
- Adapter result never becomes semantic truth/evidence/authority.
- FakeAdapter and all existing LOADOUT.dev behavior remain compatible.

---

### Task 1: Reconcile LIVE-SURFACE / CURRENT-ORGAN v0 onto current main

**Files:**
- Reconcile from PR #5 head `6cb369a1ee391de545c8de6d5682486470ffbdc9`:
  - `.live/current-organ.json`
  - `src/loadout/live_surface.py`
  - `schemas/current-organ-v0.schema.json`
  - `schemas/live-surface-receipt-v0.schema.json`
  - `skills/loadout/SKILL.md`
  - `src/loadout/cli.py` LIVE-SURFACE portions only
  - `tests/test_live_surface.py`
  - `tests/test_cli.py` LIVE-SURFACE cases only
  - `docs/superpowers/specs/2026-08-29-live-surface-current-organ-design.md`
  - `docs/superpowers/plans/2026-08-29-live-surface-v0-implementation.md`
  - `README.md` LIVE-SURFACE section only if it composes cleanly with current README

**Interfaces:**
- Preserve `resolve_current_organ(...)` and `loadout resolve-live` behavior from the verified #5 implementation.

- [ ] **Step 1: Create a fresh implementation branch from current `main`**

Use a new branch such as `impl/read-only-host-adapter-v0`; do not move or rewrite `feat/live-surface-v0`.

- [ ] **Step 2: Compare #5 payload against current main before copying**

Run:

```bash
git diff --name-status main...6cb369a1ee391de545c8de6d5682486470ffbdc9
git diff main...6cb369a1ee391de545c8de6d5682486470ffbdc9 -- src/loadout/cli.py tests/test_cli.py README.md
```

For files now independently present on `main`, retain current bytes unless #5 contains behavior absent from current main. For overlapping files, compose only the LIVE-SURFACE hunks; never restore older unrelated code.

- [ ] **Step 3: Replay the minimum current-compatible payload**

Copy the new files exactly where still absent. Integrate the LIVE-SURFACE CLI/tests/README hunks onto current equivalents.

- [ ] **Step 4: Run the old feature floor on current ancestry**

```bash
python -m compileall -q src
pytest -q tests/test_live_surface.py tests/test_cli.py
pytest -q
```

Expected: all pass on current main ancestry. If a behavioral assertion fails, fix toward the approved 2026-08-29 LIVE-SURFACE contract rather than forcing old bytes.

- [ ] **Step 5: Commit the reconciliation**

```bash
git add .live/current-organ.json src/loadout/live_surface.py schemas/current-organ-v0.schema.json schemas/live-surface-receipt-v0.schema.json skills/loadout/SKILL.md src/loadout/cli.py tests/test_live_surface.py tests/test_cli.py docs/superpowers/specs/2026-08-29-live-surface-current-organ-design.md docs/superpowers/plans/2026-08-29-live-surface-v0-implementation.md README.md
git commit -m "feat: reconcile current-organ resolution onto main"
```

Only stage paths that actually changed.

---

### Task 2: Add a deterministic capability-parameter carrier to EffectIntent

**Files:**
- Modify: `src/loadout/dev/model.py`
- Modify: `tests/test_dev_model.py`
- Modify: `tests/test_dev_public_api.py` only if exports change

**Interfaces:**
- Extend `EffectIntent` with a final defaulted field:

```python
parameters: tuple[tuple[str, str], ...] = ()
```

- Add helper:

```python
def parameter_map(intent: EffectIntent) -> dict[str, str]: ...
```

- Duplicate keys refuse with `ValueError`; parameters remain strings in v0.

- [ ] **Step 1: Add RED compatibility + validation tests**

Assert existing six-argument `EffectIntent(...)` construction still works and yields `parameters == ()`. Add:

```python
intent = EffectIntent(..., parameters=(("ref", "main"), ("path", "README.md")))
self.assertEqual(parameter_map(intent), {"ref": "main", "path": "README.md"})
```

and duplicate-key refusal.

- [ ] **Step 2: Run focused RED**

```bash
pytest -q tests/test_dev_model.py
```

- [ ] **Step 3: Implement the backward-compatible field + helper**

Keep the field last with a default. Do not change `parameters_digest` semantics in this slice; the adapter consumes only the explicit bounded parameter tuples.

- [ ] **Step 4: Run current LOADOUT.dev tests**

```bash
pytest -q tests/test_dev_model.py tests/test_dev_compiler.py tests/test_dev_membrane.py tests/test_dev_workflow_policies.py tests/test_dev_workflow_state.py
```

- [ ] **Step 5: Commit the parameter carrier**

```bash
git add src/loadout/dev/model.py tests/test_dev_model.py tests/test_dev_public_api.py
git commit -m "feat: carry bounded adapter parameters"
```

Only stage `test_dev_public_api.py` if changed.

---

### Task 3: Implement LocalGitReadAdapter

**Files:**
- Create: `src/loadout/dev/local_git.py`
- Modify: `src/loadout/dev/__init__.py`
- Create: `tests/test_dev_local_git.py`

**Interfaces:**
- Class:

```python
class LocalGitReadAdapter:
    body_time_id: str
    def __init__(self, repository_root: Path, *, body_time_id: str, allowed_roots: tuple[str, ...] = ()) -> None: ...
    def invoke(self, intent: EffectIntent) -> tuple[str, str | None]: ...
    def read_result(self, result_ref: str) -> bytes: ...
```

- Allowed capabilities: `git.resolve_ref`, `git.read_blob`.
- Successful result bytes are held only in an in-memory content-addressed result map. `invoke()` keeps the existing adapter tuple protocol.

- [ ] **Step 1: Add a temporary-repository test helper**

Create a temp repository with explicit local identity:

```bash
git init
git config user.email test@example.invalid
git config user.name LOADOUT-Test
```

Commit `docs/a.txt` as `one\n`, retain the first SHA, then commit a second version `two\n`.

- [ ] **Step 2: Write RED tests for ref resolution and historical blob reads**

Require:

```python
status, ref = adapter.invoke(resolve_ref_intent("HEAD"))
assert status == "RESOLVED"
assert adapter.read_result(ref).decode().strip() == second_sha

status, ref = adapter.invoke(read_blob_intent(first_sha, "docs/a.txt"))
assert status == "RESOLVED"
assert adapter.read_result(ref) == b"one\n"
```

Then mutate the working tree without committing and require the pinned historical read to remain `b"one\n"`.

- [ ] **Step 3: Add RED hostile cases**

Cover:

```text
write-shaped capability -> REFUSE/CAPABILITY_NOT_ALLOWED
absolute path -> REFUSE/PATH_OUTSIDE_FENCE
../ traversal -> REFUSE/PATH_OUTSIDE_FENCE
outside allowed_roots -> REFUSE/PATH_OUTSIDE_FENCE
missing ref -> REFUSE/INVALID_REF
missing object/path -> UNRESOLVED/OBJECT_NOT_FOUND
non-UTF8 blob when text requested -> UNRESOLVED/NON_UTF8_BLOB
```

Patch/mock `subprocess.run` in the traversal test and assert it is never called.

- [ ] **Step 4: Run focused RED**

```bash
pytest -q tests/test_dev_local_git.py
```

Expected: import failure.

- [ ] **Step 5: Implement fixed argv subprocess calls**

For `git.resolve_ref` call only:

```python
["git", "-C", str(root), "rev-parse", "--verify", f"{ref}^{{commit}}"]
```

For `git.read_blob` call only:

```python
["git", "-C", str(root), "show", f"{commit_sha}:{path}"]
```

Use `shell=False`, captured stdout/stderr, no stdin, a minimal environment with `GIT_PAGER=cat`, `PAGER=cat`, and no caller-supplied command environment.

- [ ] **Step 6: Content-address results in memory**

Use `sha256(bytes).hexdigest()` and result refs shaped `sha256:<digest>`. For ref resolution, store the ASCII SHA bytes just like any other result. `read_result()` refuses unknown refs.

- [ ] **Step 7: Run focused GREEN + adapter regression**

```bash
pytest -q tests/test_dev_local_git.py tests/test_dev_membrane.py tests/test_dev_workflow_state.py
```

- [ ] **Step 8: Commit the real adapter**

```bash
git add src/loadout/dev/local_git.py src/loadout/dev/__init__.py tests/test_dev_local_git.py
git commit -m "feat: add local git read adapter"
```

---

### Task 4: Prove CURRENT-ORGAN can consume the real adapter

**Files:**
- Create: `src/loadout/live_git.py`
- Create: `tests/test_live_git.py`
- Modify: `src/loadout/__init__.py` only if public export is required

**Interfaces:**
- Function:

```python
def resolve_live_from_local_git(
    repository_root: Path,
    manifest_path: str = ".live/current-organ.json",
    *,
    ref: str = "HEAD",
    requested_paths: tuple[str, ...] = (),
    body_time_id: str,
) -> dict[str, object]: ...
```

- It uses `LocalGitReadAdapter` to build host evidence, then calls existing `loadout.live_surface.resolve_current_organ()`.

- [ ] **Step 1: Write the branch-drift RED integration test**

Create a temporary Git repo containing `.live/current-organ.json`, `skills/loadout/SKILL.md`, and `docs/needed.md`. Resolve occurrence A. Commit changed skill/docs bytes. Then assert occurrence A remains pinned to the first SHA/bytes and a fresh occurrence B resolves the second SHA/bytes.

- [ ] **Step 2: Run focused RED**

```bash
pytest -q tests/test_live_git.py
```

- [ ] **Step 3: Implement adapter-driven host evidence construction**

Sequence must be:

```text
resolve ref -> exact SHA
read manifest at exact SHA
validate manifest
read only entrypoint + explicitly requested allowed paths at same SHA
call pure resolve_current_organ
```

Never open the working-tree files to satisfy immutable reads.

- [ ] **Step 4: Add cross-root and manifest-owner hostile cases**

Require CURRENT-ORGAN allowed roots to fence requested paths even though Git can technically read them. Require manifest owner mismatch to remain a LIVE-SURFACE refusal rather than being converted to adapter success.

- [ ] **Step 5: Run focused + live-surface tests**

```bash
pytest -q tests/test_live_git.py tests/test_live_surface.py tests/test_dev_local_git.py
```

- [ ] **Step 6: Commit the integration proof**

```bash
git add src/loadout/live_git.py tests/test_live_git.py src/loadout/__init__.py
git commit -m "feat: resolve current organ through local git"
```

Only stage `__init__.py` if changed.

---

### Task 5: Verify unreachable write/network authority

**Files:**
- Modify: `tests/test_dev_local_git.py`
- Modify: `README.md`

**Interfaces:**
- Static hostile guard over `src/loadout/dev/local_git.py`.

- [ ] **Step 1: Add command-surface guard**

Read the adapter source in the test and assert banned command tokens are absent from executable command construction:

```text
checkout switch merge reset commit push fetch pull clone remote
```

Also assert no `shell=True`, `urllib`, `requests`, `http.client`, or socket import is present.

- [ ] **Step 2: Add argv-injection tests**

Pass ref/path strings containing spaces, semicolons, `$()`, and shell metacharacters. Require they remain one argv element and either resolve as literal Git names/paths or refuse; no shell behavior occurs.

- [ ] **Step 3: Run the full repository floor**

```bash
python -m compileall -q src
pytest -q
```

Expected: all tests pass.

- [ ] **Step 4: Document the real-host boundary**

README must state:

```text
LocalGitReadAdapter = real read-only host proof
CURRENT ref != immutable object
host access != write authority
```

and list only `git.resolve_ref` + `git.read_blob` as v0 host capabilities.

- [ ] **Step 5: Commit verification/docs**

```bash
git add tests/test_dev_local_git.py README.md
git commit -m "test: seal read-only git host boundary"
```
