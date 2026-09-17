# OPENMANUS-LIVE-001 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a credential-free, TDD-proven harness that can run the exact pinned OpenManus body through the existing LOADOUT membrane inside a STATIC-NODE child, independently verify the filesystem and receipt evidence, and stop at HOLD.

**Architecture:** LOADOUT remains the authority that constitutes the worker effect surface. OpenManus remains a bounded JSON-stdio subprocess. A new stdlib-only specimen module freezes one banal `LOCAL_MUTATE` task, verifies the exact provider Git body before launch, snapshots the declared workspace, writes a credential-safe receipt projection, and independently verifies the result. Two thin scripts expose build and verify commands that STATIC-NODE can invoke without a production dependency between LOADOUT and TranchNode.

**Tech Stack:** Python >=3.11 standard library, existing `loadout.dev` compiler/membrane/OpenManus adapter, pytest >=8, Git CLI, JSON bundles, existing `contrib/openmanus/worker.py` for the genuine provider occurrence.

**Spec:** `docs/superpowers/specs/2026-09-16-openmanus-live-001-design.md`

## Global Constraints

- Exact provider pin: `FoundationAgents/OpenManus@3309bf4e416fb1c74b008f3e86494439a31bad53`.
- Exact first effect: `LOCAL_MUTATE` only.
- Do not add or widen `EffectClass`, `OwnerGate`, membrane semantics, or the OpenManus adapter allowlist.
- Provider tools remain `loadout_read_text`, `loadout_calculate`, `loadout_write_text`, and `Terminate` only.
- No browser, shell, native Python tool, native editor, generic MCP, Git write, remote mutation, publication, merge, landing, credential discovery, scheduler, autonomous repair/retry, or promotion path.
- LOADOUT production dependencies remain empty.
- Child environment is explicit allowlist only; never inherit the whole parent environment.
- The provider checkout may contain an untracked `config/config.toml`, but tracked provider source must be clean at the exact pinned HEAD.
- LOADOUT checks that `config/config.toml` exists but never reads or serializes it.
- Durable receipt output stores a safe structural projection of free-form provider testimony; raw stderr and file contents are not persisted.
- Receipt output must be outside the provider workspace.
- `OpenManusProviderReceipt != EffectReceipt != STATIC-NODE receipt/Workmark`.
- `GREEN CHILD != PROMOTED CHILD`.
- Ordinary CI remains credential-free and does not require OpenManus installed.

---

## File Structure

Create:

- `src/loadout/dev/openmanus_live.py` — specimen constants, provider identity checks, explicit child environment, workspace snapshots, live invocation, safe receipt projection, bundle serialization, and independent verification.
- `scripts/openmanus-live-001.py` — operator-facing build command.
- `scripts/verify-openmanus-live-001.py` — independent verify command for STATIC-NODE.
- `tests/fixtures/fake_openmanus_live_provider.py` — deterministic JSON-stdio provider with argv-selected hostile modes.
- `tests/test_dev_openmanus_live.py` — unit and contract tests.
- `tests/test_openmanus_live_scripts.py` — subprocess CLI tests.
- `evals/OPENMANUS-LIVE-001.md` — durable gate document, initially `HARNESS PASS · LIVE PROVIDER NOT RUN`.

Modify:

- `README.md` — operator and STATIC-NODE composition instructions.

Do not modify unless a failing test proves a missing invariant:

- `src/loadout/dev/model.py`
- `src/loadout/dev/compiler.py`
- `src/loadout/dev/membrane.py`
- `src/loadout/dev/openmanus.py`
- `contrib/openmanus/worker.py`

No new published JSON schema is required for this first specimen. The strict parser in `openmanus_live.py` freezes the bundle shape.

---

### Task 1: Freeze the specimen and independent verifier

**Files:**
- Create: `src/loadout/dev/openmanus_live.py`
- Create: `tests/test_dev_openmanus_live.py`

**Interfaces:**
- Consumes: `OPENMANUS_ADAPTER_ID` from `loadout.dev.openmanus`.
- Produces:
  - `PINNED_OPENMANUS_SHA: str`
  - `PINNED_BODY_ID: str`
  - `LIVE_BUNDLE_SCHEMA: str`
  - `SPECIMEN_INPUT_PATH: str`
  - `SPECIMEN_OUTPUT_PATH: str`
  - `SPECIMEN_INPUT_BYTES: bytes`
  - `SPECIMEN_OUTPUT_BYTES: bytes`
  - `snapshot_workspace(root: Path) -> dict[str, str]`
  - `workspace_state_id(snapshot: Mapping[str, str]) -> str`
  - `verify_live_bundle(bundle_path: Path, workspace_root: Path) -> tuple[bool, tuple[str, ...]]`

- [ ] **Step 1: Write the first failing tests**

Start `tests/test_dev_openmanus_live.py` with concrete contract tests:

```python
from pathlib import Path

from loadout.dev.openmanus_live import (
    SPECIMEN_INPUT_BYTES,
    SPECIMEN_INPUT_PATH,
    SPECIMEN_OUTPUT_BYTES,
    SPECIMEN_OUTPUT_PATH,
    snapshot_workspace,
    workspace_state_id,
)


def test_frozen_specimen_contract() -> None:
    assert SPECIMEN_INPUT_PATH == "specimen/input.txt"
    assert SPECIMEN_OUTPUT_PATH == "specimen/output.txt"
    assert SPECIMEN_INPUT_BYTES == b"OPENMANUS-LIVE-001 INPUT" + bytes([10])
    assert SPECIMEN_OUTPUT_BYTES == b"OPENMANUS-LIVE-001 OUTPUT" + bytes([10])


def test_snapshot_is_stable_and_content_addressed(tmp_path: Path) -> None:
    (tmp_path / "z.txt").write_bytes(b"z")
    (tmp_path / "a.txt").write_bytes(b"a")
    first = snapshot_workspace(tmp_path)
    second = snapshot_workspace(tmp_path)
    assert list(first) == ["a.txt", "z.txt"]
    assert first == second
    assert workspace_state_id(first).startswith("workspace-state:sha256:")
```

- [ ] **Step 2: Run the focused tests and observe RED**

```bash
pytest -q tests/test_dev_openmanus_live.py
```

Expected: import/collection failure because `loadout.dev.openmanus_live` does not exist.

- [ ] **Step 3: Implement constants and snapshot functions**

Create `src/loadout/dev/openmanus_live.py`:

```python
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from loadout.dev.openmanus import OPENMANUS_ADAPTER_ID

PINNED_OPENMANUS_SHA = "3309bf4e416fb1c74b008f3e86494439a31bad53"
PINNED_BODY_ID = f"{OPENMANUS_ADAPTER_ID}@{PINNED_OPENMANUS_SHA}"
LIVE_BUNDLE_SCHEMA = "loadout.openmanus-live-001/v0"
SPECIMEN_INPUT_PATH = "specimen/input.txt"
SPECIMEN_OUTPUT_PATH = "specimen/output.txt"
SPECIMEN_INPUT_BYTES = b"OPENMANUS-LIVE-001 INPUT" + bytes([10])
SPECIMEN_OUTPUT_BYTES = b"OPENMANUS-LIVE-001 OUTPUT" + bytes([10])


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def snapshot_workspace(root: Path) -> dict[str, str]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError("workspace root must exist")
    result: dict[str, str] = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        result[path.relative_to(root).as_posix()] = _sha256(path.read_bytes())
    return result


def workspace_state_id(snapshot: Mapping[str, str]) -> str:
    payload = json.dumps(
        dict(sorted(snapshot.items())), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "workspace-state:" + _sha256(payload)
```

- [ ] **Step 4: Add concrete verifier fixtures and failing cases**

Add a `_write_valid_bundle()` helper that writes the exact eight top-level keys:

```python
EXPECTED_BUNDLE_KEYS = {
    "schema",
    "provider",
    "specimen",
    "before",
    "after",
    "provider_receipt",
    "effect_receipt",
    "runtime",
}
```

Create tests named:

- `test_verifier_accepts_exact_expected_mutation`
- `test_verifier_rejects_wrong_output`
- `test_verifier_rejects_modified_input`
- `test_verifier_rejects_unexpected_workspace_delta`
- `test_verifier_rejects_wrong_provider_pin`
- `test_verifier_rejects_provider_not_completed`
- `test_verifier_rejects_semantic_authority`
- `test_verifier_rejects_bundle_snapshot_disagreement`

Each test must mutate one concrete field or file from the valid fixture and assert the exact reason string returned by `verify_live_bundle()`.

- [ ] **Step 5: Run verifier tests and observe RED**

```bash
pytest -q tests/test_dev_openmanus_live.py -k verifier
```

Expected: failures because `verify_live_bundle()` is absent.

- [ ] **Step 6: Implement strict independent verification**

`verify_live_bundle()` must re-read the workspace and enforce all of these conditions:

```text
schema == loadout.openmanus-live-001/v0
provider.checkout_sha == 3309bf4e416fb1c74b008f3e86494439a31bad53
provider.body_time_id == PINNED_BODY_ID
specimen.effect == LOCAL_MUTATE
specimen.target == workspace:specimen
specimen.input_path == specimen/input.txt
specimen.output_path == specimen/output.txt
input bytes == SPECIMEN_INPUT_BYTES
output bytes == SPECIMEN_OUTPUT_BYTES
only before->after changed/new path == specimen/output.txt
provider_receipt.disposition == COMPLETED
provider_receipt.body_time_id == PINNED_BODY_ID
0 <= provider_receipt.steps_executed <= runtime.max_steps
effect_receipt.provider_disposition == COMPLETED
effect_receipt.semantic_authority is false
bundle.after == freshly observed snapshot
```

Return only stable reason codes:

```text
WRONG_SCHEMA
PIN_MISMATCH
WRONG_EFFECT
WRONG_TARGET
WRONG_INPUT
WRONG_OUTPUT
UNEXPECTED_DELTA
PROVIDER_NOT_COMPLETED
PROVIDER_RECEIPT_IDENTITY_MISMATCH
INVALID_STEP_COUNT
EFFECT_RECEIPT_NOT_COMPLETED
SEMANTIC_AUTHORITY_WIDENED
SNAPSHOT_MISMATCH
```

- [ ] **Step 7: Run Task 1 tests and observe GREEN**

```bash
pytest -q tests/test_dev_openmanus_live.py
```

Expected: PASS.

- [ ] **Step 8: Commit Task 1**

```bash
git add src/loadout/dev/openmanus_live.py tests/test_dev_openmanus_live.py
git commit -m "test: freeze OPENMANUS-LIVE-001 verification contract"
```

---

### Task 2: Prove provider identity, environment discipline, and durable receipt hygiene

**Files:**
- Modify: `src/loadout/dev/openmanus_live.py`
- Modify: `tests/test_dev_openmanus_live.py`

**Interfaces:**
- Produces:
  - `resolve_git_head(repo: Path) -> str`
  - `provider_tracked_tree_clean(repo: Path) -> bool`
  - `build_child_env(provider_checkout: Path, forwarded_names: tuple[str, ...], source_env: Mapping[str, str]) -> dict[str, str]`
  - `safe_provider_receipt(receipt: OpenManusProviderReceipt) -> dict[str, object]`

- [ ] **Step 1: Write RED provider-identity tests**

Use a helper that initializes a temporary Git repository, commits one tracked file, and returns its HEAD. Prove three concrete cases: `resolve_git_head()` returns a lowercase SHA40; modifying the tracked file makes `provider_tracked_tree_clean()` false; adding only untracked `config/config.toml` leaves it true.

- [ ] **Step 2: Run the identity tests and observe RED**

```bash
pytest -q tests/test_dev_openmanus_live.py -k "git_head or tracked_tree"
```

- [ ] **Step 3: Implement exact Git-body checks**

```python
def resolve_git_head(repo: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo.resolve()), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
        shell=False,
    )
    value = completed.stdout.strip()
    if completed.returncode != 0 or re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise ValueError("provider checkout identity unavailable")
    return value


def provider_tracked_tree_clean(repo: Path) -> bool:
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(repo.resolve()),
            "status",
            "--porcelain=v1",
            "--untracked-files=no",
        ],
        check=False,
        capture_output=True,
        text=True,
        shell=False,
    )
    if completed.returncode != 0:
        raise ValueError("provider checkout status unavailable")
    return completed.stdout == ""
```

- [ ] **Step 4: Write RED environment tests**

Prove that `build_child_env()` returns exactly `PYTHONPATH=<provider checkout>` plus explicitly named variables, and raises `ValueError` when a requested variable name is absent from the source mapping. Assert that unrelated `PATH`, `HOME`, and fake API-key variables do not appear unless explicitly named.

- [ ] **Step 5: Implement explicit child environment**

```python
def build_child_env(
    provider_checkout: Path,
    forwarded_names: tuple[str, ...],
    source_env: Mapping[str, str],
) -> dict[str, str]:
    env = {"PYTHONPATH": str(provider_checkout.resolve())}
    for name in sorted(set(forwarded_names)):
        if not name or "=" in name or name not in source_env:
            raise ValueError(f"missing explicit environment variable: {name}")
        env[name] = source_env[name]
    return env
```

- [ ] **Step 6: Write RED durable-receipt test**

Construct a real `OpenManusProviderReceipt` containing a fake secret in `stderr`, file content in `observations`, and one artifact path. Assert that `safe_provider_receipt()` keeps only structural fields, artifact paths, observation tool names, step count, termination, and `stderr_present`, while the fake secret and observed file content are absent from `json.dumps(result)`.

- [ ] **Step 7: Implement `safe_provider_receipt()`**

The durable projection must have exactly these keys:

```text
body_time_id
capability
effect
target
precondition_state
disposition
observed_post_state
artifact_paths
observation_tools
steps_executed
termination
stderr_present
```

For artifacts retain only string `path` values. For observations retain only string `tool` values. Never persist raw `observations`, raw artifact payloads, or raw `stderr`.

- [ ] **Step 8: Run Task 2 tests and observe GREEN**

```bash
pytest -q tests/test_dev_openmanus_live.py
```

Expected: PASS.

- [ ] **Step 9: Commit Task 2**

```bash
git add src/loadout/dev/openmanus_live.py tests/test_dev_openmanus_live.py
git commit -m "feat: harden OpenManus live provider identity"
```

---

### Task 3: Build the credential-free live harness with a fake provider

**Files:**
- Modify: `src/loadout/dev/openmanus_live.py`
- Modify: `tests/test_dev_openmanus_live.py`
- Create: `tests/fixtures/fake_openmanus_live_provider.py`

**Interfaces:**
- Consumes: Task 1 verifier; Task 2 identity/environment/receipt helpers; existing `compile_world()`, `invoke_effect()`, model types, and `OpenManusJsonStdioAdapter`.
- Produces:
  - `run_live_specimen(*, provider_checkout: Path, provider_command: tuple[str, ...], workspace_root: Path, output_dir: Path, model_config_class: str, forwarded_env_names: tuple[str, ...], source_env: Mapping[str, str], timeout_seconds: float = 30.0, max_steps: int = 20) -> Path`

- [ ] **Step 1: Create the deterministic fake live provider**

`tests/fixtures/fake_openmanus_live_provider.py` selects its test-only behavior from argv:

```python
mode = sys.argv[1] if len(sys.argv) > 1 else "ok"
```

In `ok` mode it reads the envelope from stdin, writes `b"OPENMANUS-LIVE-001 OUTPUT" + bytes([10])` to `<workspace_root>/specimen/output.txt`, then emits this result:

```python
result = {
    "schema": "loadout.openmanus-worker-result/v0",
    "disposition": "COMPLETED",
    "observed_post_state": "fake-live:state:1",
    "artifacts": [{"path": "specimen/output.txt"}],
    "observations": [
        {
            "tool": "loadout_read_text",
            "relative_path": "specimen/input.txt",
            "content": "OPENMANUS-LIVE-001 INPUT",
        },
        {
            "tool": "loadout_write_text",
            "relative_path": "specimen/output.txt",
        },
    ],
    "provider_receipt": {
        "steps_executed": 2,
        "termination": "FAKE_LIVE_COMPLETE",
    },
}
print(json.dumps(result, sort_keys=True))
```

Test-only modes are exact strings:

```text
unexpected-delta  -> also writes specimen/rogue.txt
wrong-output      -> writes WRONG plus a trailing LF to specimen/output.txt
provider-refused  -> emits REFUSED and does not mutate the workspace
```

- [ ] **Step 2: Write RED runner tests**

Create concrete tests proving all of these cases:

```text
wrong provider HEAD refuses before provider launch
dirty tracked provider tree refuses before provider launch
receipt output inside workspace refuses
blank model_config_class refuses
missing provider config/config.toml refuses
fake ok provider produces a bundle accepted by verify_live_bundle
fake provider-refused preserves a bundle that verifier rejects
fake unexpected-delta preserves evidence and verifier returns UNEXPECTED_DELTA
fake wrong-output preserves evidence and verifier returns WRONG_OUTPUT
```

For fake-provider tests, monkeypatch `resolve_git_head()` to the exact pin and `provider_tracked_tree_clean()` to `True`, and create an empty `config/config.toml` only as an existence witness. The fake provider never reads it.

- [ ] **Step 3: Run runner tests and observe RED**

```bash
pytest -q tests/test_dev_openmanus_live.py -k "run or fake"
```

- [ ] **Step 4: Implement `run_live_specimen()`**

The implementation sequence is fixed:

```text
resolve paths
require output outside workspace
require provider HEAD == exact pin
require tracked provider tree clean
require provider config/config.toml exists without reading it
require non-empty model_config_class
prepare exact input fixture and refuse pre-existing output/extra specimen paths
snapshot workspace and derive precondition state
compile one worker.mutate / LOCAL_MUTATE capability to workspace:specimen
construct one EffectIntent with exact pinned body id
construct explicit child env
construct OpenManusJsonStdioAdapter
invoke_effect exactly once
snapshot workspace after provider return
project provider receipt through safe_provider_receipt
serialize effect receipt structurally
write one atomic bundle to output_dir/openmanus-live-001.json
return bundle path for COMPLETED, REFUSED, or ERROR after launch
```

The provider object in the bundle is exactly:

```python
{
    "checkout_sha": PINNED_OPENMANUS_SHA,
    "body_time_id": PINNED_BODY_ID,
    "tracked_tree_clean": True,
    "config_source": "config/config.toml",
    "model_config_class": model_config_class,
}
```

The runtime object records only Python version, exact LOADOUT Git HEAD, `max_steps`, `timeout_seconds`, sorted forwarded environment variable names, and `cleanup="provider_process_exited"`.

Pre-launch configuration failures raise `ValueError` and do not create a success-looking bundle. Never serialize environment values, config contents, raw provider stderr, or raw provider observation content.

- [ ] **Step 5: Run Task 3 plus neighboring OpenManus tests**

```bash
pytest -q \
  tests/test_dev_openmanus_live.py \
  tests/test_dev_openmanus.py \
  tests/test_dev_openmanus_strict_result.py \
  tests/test_dev_openmanus_target_boundary.py \
  tests/test_contrib_openmanus_ops.py
```

Expected: PASS.

- [ ] **Step 6: Commit Task 3**

```bash
git add src/loadout/dev/openmanus_live.py tests/test_dev_openmanus_live.py tests/fixtures/fake_openmanus_live_provider.py
git commit -m "feat: add OPENMANUS-LIVE-001 harness"
```

---

### Task 4: Add STATIC-NODE-friendly build and verify commands

**Files:**
- Create: `scripts/openmanus-live-001.py`
- Create: `scripts/verify-openmanus-live-001.py`
- Create: `tests/test_openmanus_live_scripts.py`

**Interfaces:**
- Consumes: `run_live_specimen()` and `verify_live_bundle()`.
- Produces stable CLI surfaces for STATIC-NODE `--build` and `--verify`.

- [ ] **Step 1: Write RED CLI tests**

Use subprocess tests to prove the build command requires absolute `--provider-checkout`, `--provider-python`, `--workspace`, and `--output`; requires a non-empty `--model-config-class`; and refuses output inside workspace. Prove the verify command exits 0 only for a passing bundle and exits 1 while printing stable reason codes for failed evidence.

Frozen build arguments:

```text
--provider-checkout ABS_PATH
--provider-python ABS_PATH
--workspace ABS_PATH
--output ABS_PATH
--model-config-class LABEL
--pass-env NAME
--timeout-seconds N
--max-steps N
```

`--pass-env` is repeatable and optional. Timeout defaults to 30 seconds; max steps defaults to 20.

Frozen verify arguments:

```text
--workspace ABS_PATH
--bundle ABS_PATH
```

- [ ] **Step 2: Run CLI tests and observe RED**

```bash
pytest -q tests/test_openmanus_live_scripts.py
```

- [ ] **Step 3: Implement `scripts/openmanus-live-001.py`**

Core call:

```python
repo_root = Path(__file__).resolve().parents[1]
provider_command = (
    str(provider_python),
    str(repo_root / "contrib" / "openmanus" / "worker.py"),
)
bundle = run_live_specimen(
    provider_checkout=provider_checkout,
    provider_command=provider_command,
    workspace_root=workspace,
    output_dir=output,
    model_config_class=args.model_config_class,
    forwarded_env_names=tuple(args.pass_env),
    source_env=os.environ,
    timeout_seconds=args.timeout_seconds,
    max_steps=args.max_steps,
)
print(bundle)
```

Validate arguments before the call. Return 0 when an evidence bundle is produced; provider success remains the verifier's job. Never print environment values.

- [ ] **Step 4: Implement `scripts/verify-openmanus-live-001.py`**

```python
passed, reasons = verify_live_bundle(bundle_path, workspace_root)
if passed:
    print("OPENMANUS-LIVE-001 VERIFIED")
    raise SystemExit(0)
print("OPENMANUS-LIVE-001 HOLD: " + ",".join(reasons), file=sys.stderr)
raise SystemExit(1)
```

The verifier must not launch OpenManus, inspect provider config, or use model credentials.

- [ ] **Step 5: Prove script composition without a production fake-provider flag**

Do not add `--fake-provider`. Generate a passing bundle/workspace through Task 3's Python API, then invoke the verifier script as a subprocess and assert exit 0. Build-script tests remain argument/boundary tests because the production build command is intentionally locked to `contrib/openmanus/worker.py`.

- [ ] **Step 6: Run Task 4 tests and observe GREEN**

```bash
python -m compileall -q src scripts
pytest -q tests/test_openmanus_live_scripts.py tests/test_dev_openmanus_live.py
```

Expected: PASS.

- [ ] **Step 7: Commit Task 4**

```bash
git add scripts/openmanus-live-001.py scripts/verify-openmanus-live-001.py tests/test_openmanus_live_scripts.py
git commit -m "feat: expose OPENMANUS-LIVE-001 build and verify commands"
```

---

### Task 5: Freeze the field gate and branch-wide proof

**Files:**
- Create: `evals/OPENMANUS-LIVE-001.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: Tasks 1-4 plus TranchNode's existing `STATIC-NODE-001` CLI contract.
- Produces: a precise pre-live receipt and copyable field-run commands.

- [ ] **Step 1: Create the eval document without inventing live evidence**

Start with:

```markdown
# OPENMANUS-LIVE-001 — Nested Live Provider Conformance

**Status:** HARNESS PASS · LIVE PROVIDER NOT RUN
**OpenManus pin:** `3309bf4e416fb1c74b008f3e86494439a31bad53`
**LOADOUT carrier:** PR #18 `feat/openmanus-nervous-system-v0`
**Outer harness:** TranchNode `STATIC-NODE-001`

OPENMANUS LIVE PROVIDER CONFORMANCE: NOT RUN
```

Repeat these non-claims exactly:

```text
JSON boundary != OS sandbox
observed clean delta != proof of impossible escape
provider COMPLETED != independent verification
STATIC-NODE VERIFIED != promotion
Workmark != authority
```

Do not pre-write a model, date, receipt hash, Workmark, or PASS.

- [ ] **Step 2: Document direct LOADOUT field commands**

```bash
python scripts/openmanus-live-001.py \
  --provider-checkout /absolute/path/to/OpenManus \
  --provider-python /absolute/path/to/openmanus-venv/bin/python \
  --workspace /absolute/path/to/disposable-workspace \
  --output /absolute/path/to/receipts \
  --model-config-class 'local-config-chosen-model'

python scripts/verify-openmanus-live-001.py \
  --workspace /absolute/path/to/disposable-workspace \
  --bundle /absolute/path/to/receipts/openmanus-live-001.json
```

Explain that the exact pinned OpenManus checkout must have a local `config/config.toml`; LOADOUT checks only existence. The pinned OpenManus source resolves configuration relative to its own project root, so LOADOUT does not need to ingest credential contents.

- [ ] **Step 3: Document STATIC-NODE composition without creating a cross-repo dependency**

```bash
npm run static-node:001 -- \
  --repo /absolute/path/to/LOADOUT \
  --task-id openmanus-live-001 \
  --build '<explicit OPENMANUS-LIVE-001 build command>' \
  --verify '<explicit OPENMANUS-LIVE-001 verify command>' \
  --output /absolute/path/to/static-node-receipts
```

State that STATIC-NODE currently lives on its own draft carrier until separately promoted/merged; the field machine must use a checkout containing that implementation.

- [ ] **Step 4: Run focused verification**

```bash
python -m compileall -q src scripts
pytest -q \
  tests/test_dev_openmanus_live.py \
  tests/test_openmanus_live_scripts.py \
  tests/test_dev_openmanus.py \
  tests/test_dev_openmanus_strict_result.py \
  tests/test_dev_openmanus_target_boundary.py \
  tests/test_contrib_openmanus_ops.py \
  tests/test_dev_public_api.py
```

Expected: PASS without credentials or OpenManus installed.

- [ ] **Step 5: Run branch-wide verification**

```bash
python -m pip install -e ".[test]"
python -m compileall -q src scripts
pytest -q
```

Expected: PASS.

- [ ] **Step 6: Perform the authority-expansion grep**

```bash
grep -R "shell=True\|os\.environ\.copy\|REMOTE_MUTATE\|PUBLISH\|LAND" -n \
  src/loadout/dev/openmanus_live.py scripts tests/test_dev_openmanus_live.py tests/test_openmanus_live_scripts.py
```

Expected: no `shell=True`, no whole-environment copy, and no harness request for remote/publish/land effects.

- [ ] **Step 7: Commit docs and field gate**

```bash
git add README.md evals/OPENMANUS-LIVE-001.md
git commit -m "docs: freeze OPENMANUS-LIVE-001 field gate"
```

- [ ] **Step 8: Update PR #18 only after fresh exact-head CI is green**

Record the exact final head and exact successful workflow run id, then state:

```text
OPENMANUS-LIVE-001 HARNESS: PASS
OPENMANUS LIVE PROVIDER CONFORMANCE: NOT RUN
```

Keep PR #18 draft. Fake-provider CI must never be used to claim live-provider conformance.

---

## Field Occurrence After Harness Implementation

The genuine occurrence is intentionally separate from credential-free implementation because it requires a machine containing the exact pinned OpenManus checkout, a clean tracked provider tree, a local `config/config.toml`, the provider virtual environment, and a checkout containing STATIC-NODE-001.

The operator runs the nested specimen, inspects LOADOUT's bundle plus STATIC-NODE's attempt receipt/delta/optional Workmark, and confirms `HOLD` with `promotionAuthorized=false`.

Only after one exact occurrence satisfies every success condition in the design may `evals/OPENMANUS-LIVE-001.md` change to:

```text
OPENMANUS LIVE PROVIDER CONFORMANCE: PASS FOR OPENMANUS-LIVE-001 SPECIMEN
```

No implementation task may pre-write that PASS.
