# OPENMANUS-LIVE-001 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a credential-free, TDD-proven harness that can run the exact pinned OpenManus body through the existing LOADOUT membrane inside a STATIC-NODE child, independently verify the resulting filesystem and receipt evidence, and stop at HOLD.

**Architecture:** LOADOUT remains the provider-constituting authority and OpenManus remains a bounded JSON-stdio subprocess worker. A new stdlib-only specimen module freezes one banal `LOCAL_MUTATE` task, verifies the exact provider Git body before launch, snapshots the declared workspace, emits a credential-safe receipt projection, and independently verifies the resulting delta. Two thin scripts expose build and verify commands that STATIC-NODE can invoke without introducing a production dependency between LOADOUT and TranchNode.

**Tech Stack:** Python >=3.11 standard library, existing `loadout.dev` compiler/membrane/OpenManus adapter, pytest >=8, Git CLI, JSON bundles, existing `contrib/openmanus/worker.py` for the genuine provider occurrence.

**Spec:** `docs/superpowers/specs/2026-09-16-openmanus-live-001-design.md`

## Global Constraints

- Exact provider pin: `FoundationAgents/OpenManus@3309bf4e416fb1c74b008f3e86494439a31bad53`.
- Exact live effect: `LOCAL_MUTATE` only.
- Do not add or widen `EffectClass`, `OwnerGate`, membrane semantics, or the OpenManus adapter allowlist.
- Provider tools remain `loadout_read_text`, `loadout_calculate`, `loadout_write_text`, and `Terminate` only.
- No browser, shell, native Python tool, native editor, generic MCP, Git write, remote mutation, publication, merge, landing, credential discovery, scheduler, autonomous retry/repair, or promotion path.
- LOADOUT production dependencies remain empty.
- Child environment is explicit allowlist only; never inherit the whole parent environment.
- The provider checkout may contain an untracked `config/config.toml`, but tracked provider source must be clean at the exact pinned HEAD.
- LOADOUT must not read or serialize credential values from OpenManus configuration. Durable receipt output therefore stores a safe structural projection of free-form provider testimony rather than raw stderr or file contents.
- Receipt output must be outside the provider workspace.
- `OpenManusProviderReceipt != EffectReceipt != STATIC-NODE receipt/Workmark`.
- `GREEN CHILD != PROMOTED CHILD`.
- Ordinary CI remains credential-free and does not require OpenManus installed.

---

## File Structure

Create:

- `src/loadout/dev/openmanus_live.py` — fixed specimen constants, provider identity checks, explicit child environment, workspace snapshots, live invocation, safe receipt projection, bundle serialization, and independent verification.
- `scripts/openmanus-live-001.py` — operator-facing build command.
- `scripts/verify-openmanus-live-001.py` — independent verify command for STATIC-NODE.
- `tests/fixtures/fake_openmanus_live_provider.py` — deterministic JSON-stdio provider with argv-selected hostile modes.
- `tests/test_dev_openmanus_live.py` — contract tests.
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

- [ ] **Step 1: Write the initial failing tests**

Create `tests/test_dev_openmanus_live.py` with:

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
    assert SPECIMEN_INPUT_BYTES == b"OPENMANUS-LIVE-001 INPUT\n"
    assert SPECIMEN_OUTPUT_BYTES == b"OPENMANUS-LIVE-001 OUTPUT\n"


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

Expected: import/collection failure because the module does not exist.

- [ ] **Step 3: Implement the frozen constants and snapshot functions**

Create `src/loadout/dev/openmanus_live.py` with:

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
SPECIMEN_INPUT_BYTES = b"OPENMANUS-LIVE-001 INPUT\n"
SPECIMEN_OUTPUT_BYTES = b"OPENMANUS-LIVE-001 OUTPUT\n"


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

- [ ] **Step 4: Write failing verifier tests**

Add helper fixtures that write a strict bundle with top-level keys exactly:

```python
{
    "schema": "loadout.openmanus-live-001/v0",
    "provider": {},
    "specimen": {},
    "before": {},
    "after": {},
    "provider_receipt": {},
    "effect_receipt": {},
    "runtime": {},
}
```

Add these exact test names:

```python
def test_verifier_accepts_exact_expected_mutation(tmp_path: Path) -> None: ...
def test_verifier_rejects_wrong_output(tmp_path: Path) -> None: ...
def test_verifier_rejects_modified_input(tmp_path: Path) -> None: ...
def test_verifier_rejects_unexpected_workspace_delta(tmp_path: Path) -> None: ...
def test_verifier_rejects_wrong_provider_pin(tmp_path: Path) -> None: ...
def test_verifier_rejects_provider_not_completed(tmp_path: Path) -> None: ...
def test_verifier_rejects_semantic_authority(tmp_path: Path) -> None: ...
def test_verifier_rejects_bundle_snapshot_disagreement(tmp_path: Path) -> None: ...
```

Each test must build concrete fixture JSON; do not mock `verify_live_bundle()`.

- [ ] **Step 5: Run verifier tests and observe RED**

```bash
pytest -q tests/test_dev_openmanus_live.py -k verifier
```

Expected: failures because `verify_live_bundle` is not implemented.

- [ ] **Step 6: Implement strict independent verification**

`verify_live_bundle()` must re-read the workspace and enforce:

```text
schema == loadout.openmanus-live-001/v0
provider.checkout_sha == 3309bf4e416fb1c74b008f3e86494439a31bad53
provider.body_time_id == openmanus.worker.json-stdio/v0@3309bf4e416fb1c74b008f3e86494439a31bad53
specimen.effect == LOCAL_MUTATE
specimen.target == workspace:specimen
specimen.input_path == specimen/input.txt
specimen.output_path == specimen/output.txt
input bytes == OPENMANUS-LIVE-001 INPUT\n
output bytes == OPENMANUS-LIVE-001 OUTPUT\n
only before->after changed/new path == specimen/output.txt
provider_receipt.disposition == COMPLETED
provider_receipt.body_time_id == PINNED_BODY_ID
0 <= provider_receipt.steps_executed <= runtime.max_steps
effect_receipt.provider_disposition == COMPLETED
effect_receipt.semantic_authority is false
bundle.after == freshly observed snapshot
```

Return stable reason strings rather than provider prose:

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

### Task 2: Prove provider identity, environment discipline, and safe receipt serialization

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

Add tests that initialize temporary Git repositories and assert:

```python
def test_resolve_git_head_returns_lowercase_sha40(tmp_path: Path) -> None: ...
def test_provider_tracked_tree_clean_rejects_modified_tracked_file(tmp_path: Path) -> None: ...
def test_provider_tracked_tree_clean_allows_untracked_config_file(tmp_path: Path) -> None: ...
```

The third test must create an untracked `config/config.toml` and still expect `True` because the body pin concerns tracked provider source while runtime configuration is intentionally local.

- [ ] **Step 2: Run identity tests and observe RED**

```bash
pytest -q tests/test_dev_openmanus_live.py -k "git_head or tracked_tree"
```

- [ ] **Step 3: Implement exact Git-body checks**

Use only shell-free Git calls:

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
            "git", "-C", str(repo.resolve()), "status", "--porcelain=v1",
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

- [ ] **Step 4: Write RED explicit-environment tests**

Add:

```python
def test_child_env_contains_only_pythonpath_and_forwarded_names(tmp_path: Path) -> None: ...
def test_child_env_refuses_missing_forwarded_name(tmp_path: Path) -> None: ...
```

Expected mapping for `forwarded_names=("HTTPS_PROXY",)` is exactly:

```python
{
    "PYTHONPATH": str(provider_checkout.resolve()),
    "HTTPS_PROXY": source_env["HTTPS_PROXY"],
}
```

No `PATH`, `HOME`, API key, or unrelated parent environment variable appears unless explicitly named.

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

- [ ] **Step 6: Write RED durable-receipt hygiene tests**

Construct an `OpenManusProviderReceipt` whose `observations` contain file content and whose `stderr` contains a fake credential marker. Assert the durable projection:

```python
def test_safe_provider_receipt_drops_free_form_content_and_stderr() -> None: ...
```

Required durable shape:

```python
{
    "body_time_id": PINNED_BODY_ID,
    "capability": "worker.mutate",
    "effect": "LOCAL_MUTATE",
    "target": "workspace:specimen",
    "precondition_state": "workspace-state:sha256:<digest>",
    "disposition": "COMPLETED",
    "observed_post_state": "<string-or-null>",
    "artifact_paths": ["specimen/output.txt"],
    "observation_tools": ["loadout_read_text", "loadout_write_text"],
    "steps_executed": 2,
    "termination": "TERMINATE",
    "stderr_present": True,
}
```

Do not serialize raw `observations`, raw artifact payloads, raw `stderr`, or credential/config contents.

- [ ] **Step 7: Implement `safe_provider_receipt()`**

The function must accept only the existing receipt dataclass and extract structural fields. For artifacts, retain only string `path` values. For observations, retain only string `tool` names. Any other provider testimony is intentionally omitted from the durable specimen bundle.

This is the credential-hygiene interpretation of the design requirement `credentials are absent from preserved receipts`: the adapter still holds rich provider testimony in-memory for the occurrence, while the durable field artifact is a safe projection.

- [ ] **Step 8: Run Task 2 tests and observe GREEN**

```bash
pytest -q tests/test_dev_openmanus_live.py
```

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
- Consumes: Task 1 verifier, Task 2 identity/env/receipt helpers, existing `compile_world()`, `invoke_effect()`, model types, and `OpenManusJsonStdioAdapter`.
- Produces:
  - `run_live_specimen(*, provider_checkout: Path, provider_command: tuple[str, ...], workspace_root: Path, output_dir: Path, model_config_class: str, forwarded_env_names: tuple[str, ...], source_env: Mapping[str, str], timeout_seconds: float = 30.0, max_steps: int = 20) -> Path`

- [ ] **Step 1: Create the fake live provider**

`tests/fixtures/fake_openmanus_live_provider.py` must select behavior only from its first argv argument:

```python
mode = sys.argv[1] if len(sys.argv) > 1 else "ok"
```

It reads one JSON envelope from stdin. In `ok` mode it writes exactly `OPENMANUS-LIVE-001 OUTPUT\n` to `<workspace_root>/specimen/output.txt` and emits:

```json
{
  "schema": "loadout.openmanus-worker-result/v0",
  "disposition": "COMPLETED",
  "observed_post_state": "fake-live:state:1",
  "artifacts": [{"path": "specimen/output.txt"}],
  "observations": [
    {"tool": "loadout_read_text", "relative_path": "specimen/input.txt", "content": "OPENMANUS-LIVE-001 INPUT\n"},
    {"tool": "loadout_write_text", "relative_path": "specimen/output.txt"}
  ],
  "provider_receipt": {"steps_executed": 2, "termination": "FAKE_LIVE_COMPLETE"}
}
```

Additional test-only argv modes:

```text
unexpected-delta  -> also writes specimen/rogue.txt
wrong-output      -> writes WRONG\n to output
provider-refused  -> emits REFUSED without mutation
```

- [ ] **Step 2: Write RED runner tests**

Add concrete tests for:

```python
def test_run_refuses_wrong_provider_head_before_launch(tmp_path: Path, monkeypatch) -> None: ...
def test_run_refuses_dirty_tracked_provider_tree(tmp_path: Path, monkeypatch) -> None: ...
def test_run_refuses_output_inside_workspace(tmp_path: Path, monkeypatch) -> None: ...
def test_run_refuses_missing_model_config_class(tmp_path: Path, monkeypatch) -> None: ...
def test_run_refuses_missing_provider_config_toml(tmp_path: Path, monkeypatch) -> None: ...
def test_run_live_specimen_fake_provider_passes_independent_verifier(tmp_path: Path, monkeypatch) -> None: ...
def test_run_preserves_refused_provider_bundle(tmp_path: Path, monkeypatch) -> None: ...
def test_verifier_rejects_fake_unexpected_delta(tmp_path: Path, monkeypatch) -> None: ...
def test_verifier_rejects_fake_wrong_output(tmp_path: Path, monkeypatch) -> None: ...
```

For fake-provider tests, monkeypatch `resolve_git_head()` to the exact pin and `provider_tracked_tree_clean()` to `True`; create an empty `config/config.toml` only as an existence witness. The fake provider never reads it.

- [ ] **Step 3: Run runner tests and observe RED**

```bash
pytest -q tests/test_dev_openmanus_live.py -k "run_ or fake_"
```

- [ ] **Step 4: Implement `run_live_specimen()`**

The function must execute this exact sequence:

1. resolve `provider_checkout`, `workspace_root`, and `output_dir`;
2. require all three directories to exist, creating only `output_dir` when its parent exists;
3. refuse if `output_dir` is inside `workspace_root`;
4. require `resolve_git_head(provider_checkout) == PINNED_OPENMANUS_SHA`;
5. require `provider_tracked_tree_clean(provider_checkout) is True`;
6. require `<provider_checkout>/config/config.toml` to exist, but never open or read it;
7. require non-empty `model_config_class`;
8. prepare `specimen/input.txt` with exact frozen bytes and refuse any pre-existing `specimen/output.txt` or additional path under `specimen/`;
9. snapshot workspace and derive `precondition_state`;
10. construct one `AdapterBody` advertising only `CapabilitySpec("worker.mutate", EffectClass.LOCAL_MUTATE)`;
11. compile task id `OPENMANUS-LIVE-001` with cut target `workspace:specimen`;
12. construct one `EffectIntent` for capability `worker.mutate`, effect `LOCAL_MUTATE`, target `workspace:specimen`, exact pinned body id, derived precondition state, and one `request` parameter whose text requires the frozen output and forbids other path changes;
13. build the explicit child env from Task 2;
14. construct `OpenManusJsonStdioAdapter` with exact body id, provided argv, workspace, timeout, max steps, and explicit env;
15. call `invoke_effect()` exactly once;
16. snapshot workspace after invocation;
17. project the latest provider receipt with `safe_provider_receipt()` if a provider launch produced one;
18. serialize the effect receipt structurally with `dataclasses.asdict()` plus enum-value conversion;
19. record runtime metadata: Python version, exact LOADOUT Git head, max steps, timeout, sorted forwarded env names, and `cleanup="provider_process_exited"`;
20. write one atomic JSON bundle to `<output_dir>/openmanus-live-001.json` using a temporary sibling and `Path.replace()`;
21. return the bundle path even for provider `REFUSED` or `ERROR` after launch so failed evidence remains inspectable.

Pre-launch configuration failures raise `ValueError` and must not create a success-looking bundle.

The bundle's `provider` object records only:

```json
{
  "checkout_sha": "3309bf4e416fb1c74b008f3e86494439a31bad53",
  "body_time_id": "openmanus.worker.json-stdio/v0@3309bf4e416fb1c74b008f3e86494439a31bad53",
  "tracked_tree_clean": true,
  "config_source": "config/config.toml",
  "model_config_class": "<operator supplied non-secret label>"
}
```

Never serialize config contents, API keys, environment values, or raw provider stderr/observation content.

- [ ] **Step 5: Run Task 3 and neighboring OpenManus tests**

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
- Produces two stable CLI surfaces suitable for STATIC-NODE `--build` and `--verify`.

- [ ] **Step 1: Write RED CLI tests**

Create subprocess tests that prove these exact rules:

```text
build requires absolute --provider-checkout
build requires absolute --provider-python
build requires absolute --workspace
build requires absolute --output
build requires non-empty --model-config-class
build refuses output inside workspace
verify returns 0 only for independently verified bundle
verify returns 1 and stable reason codes for failed evidence
```

Frozen build CLI:

```text
--provider-checkout ABS_PATH
--provider-python ABS_PATH
--workspace ABS_PATH
--output ABS_PATH
--model-config-class LABEL
--pass-env NAME       # repeatable, optional
--timeout-seconds N   # default 30
--max-steps N         # default 20
```

Frozen verify CLI:

```text
--workspace ABS_PATH
--bundle ABS_PATH
```

- [ ] **Step 2: Run CLI tests and observe RED**

```bash
pytest -q tests/test_openmanus_live_scripts.py
```

- [ ] **Step 3: Implement `scripts/openmanus-live-001.py`**

The script must:

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

Validation must occur before this call. The script returns 0 when an evidence bundle is produced, not when the provider self-reports success; independent verification is the next phase.

Never print environment values.

- [ ] **Step 4: Implement `scripts/verify-openmanus-live-001.py`**

Use exactly:

```python
passed, reasons = verify_live_bundle(bundle_path, workspace_root)
if passed:
    print("OPENMANUS-LIVE-001 VERIFIED")
    raise SystemExit(0)
print("OPENMANUS-LIVE-001 HOLD: " + ",".join(reasons), file=sys.stderr)
raise SystemExit(1)
```

It must not launch OpenManus or inspect provider configuration.

- [ ] **Step 5: Prove script composition without a production fake-provider flag**

Do not add `--fake-provider`. Generate a passing bundle/workspace through Task 3's Python API, then invoke only the verifier script in subprocess and assert exit 0. CLI build tests remain argument/boundary tests because the production build command is intentionally locked to `contrib/openmanus/worker.py`.

- [ ] **Step 6: Run Task 4 tests**

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
- Produces a precise pre-live receipt and copyable field-run commands.

- [ ] **Step 1: Create the eval document without inventing live evidence**

Start `evals/OPENMANUS-LIVE-001.md` with:

```markdown
# OPENMANUS-LIVE-001 — Nested Live Provider Conformance

**Status:** HARNESS PASS · LIVE PROVIDER NOT RUN
**OpenManus pin:** `3309bf4e416fb1c74b008f3e86494439a31bad53`
**LOADOUT carrier:** PR #18 `feat/openmanus-nervous-system-v0`
**Outer harness:** TranchNode `STATIC-NODE-001`

OPENMANUS LIVE PROVIDER CONFORMANCE: NOT RUN
```

Repeat these non-claims:

```text
JSON boundary != OS sandbox
observed clean delta != proof of impossible escape
provider COMPLETED != independent verification
STATIC-NODE VERIFIED != promotion
Workmark != authority
```

Leave the field occurrence explicitly `NOT RUN`; do not pre-write a model, date, receipt hash, Workmark, or PASS.

- [ ] **Step 2: Document direct LOADOUT field commands**

README command shape:

```bash
python scripts/openmanus-live-001.py \
  --provider-checkout /absolute/path/to/OpenManus \
  --provider-python /absolute/path/to/openmanus-venv/bin/python \
  --workspace /absolute/path/to/disposable-workspace \
  --output /absolute/path/to/receipts \
  --model-config-class 'local config.toml / chosen model class'

python scripts/verify-openmanus-live-001.py \
  --workspace /absolute/path/to/disposable-workspace \
  --bundle /absolute/path/to/receipts/openmanus-live-001.json
```

Explain that the exact pinned OpenManus checkout must have a local `config/config.toml`; LOADOUT checks its existence but does not read or serialize it. The pinned OpenManus source itself resolves configuration relative to its own project root, so the provider process does not need LOADOUT to ingest credentials.

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

- [ ] **Step 6: Perform an authority-expansion grep**

```bash
grep -R "shell=True\|os\.environ\.copy\|REMOTE_MUTATE\|PUBLISH\|LAND" -n \
  src/loadout/dev/openmanus_live.py scripts tests/test_dev_openmanus_live.py tests/test_openmanus_live_scripts.py
```

Expected: no `shell=True`, no whole-environment copy, and no harness request for remote/publish/land effects.

- [ ] **Step 7: Commit docs and gate**

```bash
git add README.md evals/OPENMANUS-LIVE-001.md
git commit -m "docs: freeze OPENMANUS-LIVE-001 field gate"
```

- [ ] **Step 8: Update PR #18 only after fresh exact-head CI is green**

Add exact final head and exact successful workflow run id, then state:

```text
OPENMANUS-LIVE-001 HARNESS: PASS
OPENMANUS LIVE PROVIDER CONFORMANCE: NOT RUN
```

Keep PR #18 draft. Fake-provider CI must never be used to claim live-provider conformance.

---

## Field Occurrence After Harness Implementation

The genuine occurrence is intentionally separate from credential-free implementation because it requires a machine containing:

- the exact pinned OpenManus checkout;
- a clean tracked provider tree;
- a local untracked/ignored `config/config.toml` with the chosen runtime/model configuration;
- the provider virtual environment;
- a checkout containing STATIC-NODE-001.

The operator then runs the nested specimen, inspects LOADOUT's bundle plus STATIC-NODE's attempt receipt/delta/optional Workmark, and confirms `HOLD` with `promotionAuthorized=false`.

Only after one exact occurrence satisfies every success condition in the design may `evals/OPENMANUS-LIVE-001.md` change to:

```text
OPENMANUS LIVE PROVIDER CONFORMANCE: PASS FOR OPENMANUS-LIVE-001 SPECIMEN
```

No implementation task may pre-write that PASS.
