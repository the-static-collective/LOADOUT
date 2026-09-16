# OPENMANUS-LIVE-001 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a credential-free, TDD-proven live-specimen harness that can run the exact pinned OpenManus body through the existing LOADOUT membrane inside a STATIC-NODE child, independently verify the resulting filesystem/receipt evidence, and stop at HOLD.

**Architecture:** LOADOUT remains provider-constituting authority and OpenManus remains a bounded subprocess worker behind the existing JSON-stdio adapter. A new stdlib-only specimen module owns fixed fixture content, pinned-provider identity checks, workspace snapshots, receipt-bundle serialization, and independent verification; two thin operator scripts expose build and verify commands that STATIC-NODE can call without creating a production dependency between repositories.

**Tech Stack:** Python >=3.11 standard library, existing `loadout.dev` compiler/membrane/OpenManus adapter, pytest >=8 for tests, Git CLI for exact checkout identity, JSON receipt bundles, existing `contrib/openmanus/worker.py` for the genuine provider occurrence.

**Spec:** `docs/superpowers/specs/2026-09-16-openmanus-live-001-design.md`

## Global Constraints

- Exact OpenManus source pin: `FoundationAgents/OpenManus@3309bf4e416fb1c74b008f3e86494439a31bad53`.
- First live effect is exactly `LOCAL_MUTATE`; do not add any new `EffectClass` or widen the OpenManus adapter allowlist.
- Provider-side tools remain `loadout_read_text`, `loadout_calculate`, `loadout_write_text`, and `Terminate`; do not expose browser, shell, native Python execution, native editor, generic MCP, Git write, remote mutation, publication, merge, landing, credential discovery, or multi-agent delegation.
- LOADOUT production dependencies remain empty; all new production code is Python standard-library-only.
- Child environment is explicit allowlist only; never inherit `os.environ` wholesale.
- Credential values never enter committed files, stdout fixtures, bundle JSON, provider receipts, effect receipts, or test snapshots.
- Receipt/output directory must be outside the provider workspace so receipt writes cannot masquerade as provider workspace delta.
- `OpenManusProviderReceipt != EffectReceipt != STATIC-NODE receipt/Workmark`.
- `GREEN CHILD != PROMOTED CHILD`; this plan adds no promotion, merge, publication, scheduler, retry/repair loop, or daemon path.
- Live OpenManus execution remains an explicit operator action. Ordinary CI remains credential-free and uses a fake live provider.

---

## File Structure

Create:

- `src/loadout/dev/openmanus_live.py` — fixed specimen contract, provider/check-out identity checks, explicit environment construction, workspace snapshots, live invocation, bundle serialization, and independent bundle/workspace verification.
- `scripts/openmanus-live-001.py` — thin operator-facing build command for the live/fake provider occurrence.
- `scripts/verify-openmanus-live-001.py` — thin independent verify command intended to be passed directly to STATIC-NODE.
- `tests/fixtures/fake_openmanus_live_provider.py` — deterministic JSON-stdio provider that performs the exact fixture mutation and can deliberately create hostile deltas/results.
- `tests/test_dev_openmanus_live.py` — unit/contract tests for pinning, env discipline, secret redaction, workspace deltas, receipt identity, and verifier behavior.
- `tests/test_openmanus_live_scripts.py` — subprocess-level proof that build/verify scripts compose using the fake provider without credentials.
- `evals/OPENMANUS-LIVE-001.md` — durable gate/field-receipt document; starts at `HARNESS PASS · LIVE PROVIDER NOT RUN` and records the exact human-run command/receipt only after a real occurrence.

Modify:

- `README.md` — document the opt-in live specimen command, its non-claims, and STATIC-NODE composition example.

Do not modify unless a failing test proves an invariant is missing:

- `src/loadout/dev/model.py`
- `src/loadout/dev/compiler.py`
- `src/loadout/dev/membrane.py`
- `src/loadout/dev/openmanus.py`
- `contrib/openmanus/worker.py`

No new JSON schema file is planned for the specimen bundle in v0. The strict parser in `openmanus_live.py` freezes the bundle key set; adding a published schema is a later compatibility decision, not required to prove this occurrence.

---

### Task 1: Freeze the specimen contract and independent workspace verifier

**Files:**
- Create: `src/loadout/dev/openmanus_live.py`
- Create: `tests/test_dev_openmanus_live.py`

**Interfaces:**
- Consumes: `EffectClass`, `OpenManusProviderReceipt`, existing SHA/body-id constants from `loadout.dev.openmanus`.
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

- [ ] **Step 1: Write failing tests for the frozen fixture and workspace snapshot**

Add tests equivalent to:

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


def test_snapshot_is_content_addressed_and_path_sorted(tmp_path: Path) -> None:
    (tmp_path / "z.txt").write_bytes(b"z")
    (tmp_path / "a.txt").write_bytes(b"a")
    first = snapshot_workspace(tmp_path)
    second = snapshot_workspace(tmp_path)
    assert list(first) == ["a.txt", "z.txt"]
    assert first == second
    assert workspace_state_id(first).startswith("workspace-state:sha256:")


def test_frozen_specimen_is_banal_and_exact() -> None:
    assert SPECIMEN_INPUT_PATH == "specimen/input.txt"
    assert SPECIMEN_OUTPUT_PATH == "specimen/output.txt"
    assert SPECIMEN_INPUT_BYTES == b"OPENMANUS-LIVE-001 INPUT\n"
    assert SPECIMEN_OUTPUT_BYTES == b"OPENMANUS-LIVE-001 OUTPUT\n"
```

- [ ] **Step 2: Run the focused tests and confirm RED**

Run:

```bash
pytest -q tests/test_dev_openmanus_live.py
```

Expected: collection/import failure because `loadout.dev.openmanus_live` does not exist.

- [ ] **Step 3: Implement the minimal specimen constants and snapshot functions**

Create `src/loadout/dev/openmanus_live.py` with these exact constants and behavior:

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
_ALLOWED_SPECIMEN_PATHS = frozenset({SPECIMEN_INPUT_PATH, SPECIMEN_OUTPUT_PATH})


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def snapshot_workspace(root: Path) -> dict[str, str]:
    resolved = root.resolve()
    if not resolved.is_dir():
        raise ValueError("workspace root must exist")
    result: dict[str, str] = {}
    for path in sorted(p for p in resolved.rglob("*") if p.is_file()):
        relative = path.relative_to(resolved).as_posix()
        result[relative] = _sha256(path.read_bytes())
    return result


def workspace_state_id(snapshot: Mapping[str, str]) -> str:
    payload = json.dumps(dict(sorted(snapshot.items())), sort_keys=True, separators=(",", ":")).encode()
    return "workspace-state:" + _sha256(payload)
```

- [ ] **Step 4: Add failing independent-verifier tests**

Construct a minimal bundle fixture with a strict top-level shape:

```python
{
    "schema": LIVE_BUNDLE_SCHEMA,
    "provider": {
        "checkout_sha": PINNED_OPENMANUS_SHA,
        "body_time_id": PINNED_BODY_ID,
        "model_config_class": "test/fake",
    },
    "specimen": {
        "effect": "LOCAL_MUTATE",
        "target": "workspace:specimen",
        "input_path": SPECIMEN_INPUT_PATH,
        "output_path": SPECIMEN_OUTPUT_PATH,
    },
    "before": {...},
    "after": {...},
    "provider_receipt": {...},
    "effect_receipt": {...},
    "runtime": {...},
}
```

Add tests proving `verify_live_bundle()`:

```python
def test_verifier_accepts_exact_expected_mutation(...): ...
def test_verifier_rejects_wrong_output_bytes(...): ...
def test_verifier_rejects_modified_input(...): ...
def test_verifier_rejects_unexpected_workspace_path(...): ...
def test_verifier_rejects_wrong_provider_pin(...): ...
def test_verifier_rejects_provider_not_completed(...): ...
def test_verifier_rejects_semantic_authority_true(...): ...
def test_verifier_rejects_missing_or_extra_bundle_keys(...): ...
def test_verifier_rejects_bundle_snapshot_that_disagrees_with_filesystem(...): ...
```

The successful fixture must contain exactly one new path, `specimen/output.txt`, while `specimen/input.txt` remains byte-identical.

- [ ] **Step 5: Run the verifier tests and confirm RED**

Run:

```bash
pytest -q tests/test_dev_openmanus_live.py -k verifier
```

Expected: failures because `verify_live_bundle` is absent.

- [ ] **Step 6: Implement strict independent verification**

Implement `verify_live_bundle(bundle_path, workspace_root)` so it:

1. parses exactly one JSON object;
2. requires the exact top-level key set shown above;
3. requires `schema == LIVE_BUNDLE_SCHEMA`;
4. requires `provider.checkout_sha == PINNED_OPENMANUS_SHA` and `provider.body_time_id == PINNED_BODY_ID`;
5. requires specimen `effect == "LOCAL_MUTATE"`, `target == "workspace:specimen"`, and the frozen input/output paths;
6. re-reads the current filesystem instead of trusting the bundle's `after` map;
7. requires input bytes exactly `SPECIMEN_INPUT_BYTES` and output bytes exactly `SPECIMEN_OUTPUT_BYTES`;
8. requires the only before->after changed/new path to be `SPECIMEN_OUTPUT_PATH`;
9. requires `provider_receipt.disposition == "COMPLETED"` and `provider_receipt.body_time_id == PINNED_BODY_ID`;
10. requires `provider_receipt.steps_executed` to be an integer in `0..max_steps` where `max_steps` is recorded in `runtime`;
11. requires `effect_receipt.provider_disposition == "COMPLETED"` and `effect_receipt.semantic_authority is False`;
12. returns `(False, tuple_of_machine_readable_reasons)` for evidence failure rather than raising, while malformed/unreadable invocation arguments may raise `ValueError`.

Use stable reason strings such as:

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
EFFECT_RECEIPT_NOT_COMPLETED
SEMANTIC_AUTHORITY_WIDENED
SNAPSHOT_MISMATCH
INVALID_STEP_COUNT
```

- [ ] **Step 7: Run focused tests and confirm GREEN**

Run:

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

### Task 2: Add exact provider identity, explicit environment, and live bundle construction

**Files:**
- Modify: `src/loadout/dev/openmanus_live.py`
- Modify: `tests/test_dev_openmanus_live.py`
- Create: `tests/fixtures/fake_openmanus_live_provider.py`

**Interfaces:**
- Consumes: Task 1 constants/snapshot/verifier plus existing `compile_world()`, `invoke_effect()`, `AdapterBody`, `CapabilityRequest`, `CapabilitySpec`, `CompileRequest`, `EffectClass`, `EffectIntent`, and `OpenManusJsonStdioAdapter`.
- Produces:
  - `resolve_git_head(repo: Path) -> str`
  - `build_child_env(provider_checkout: Path, forwarded_names: tuple[str, ...], source_env: Mapping[str, str]) -> dict[str, str]`
  - `run_live_specimen(*, provider_checkout: Path, provider_command: tuple[str, ...], workspace_root: Path, output_dir: Path, model_config_class: str, forwarded_env_names: tuple[str, ...], source_env: Mapping[str, str], timeout_seconds: float = 30.0, max_steps: int = 20) -> Path`

- [ ] **Step 1: Write RED tests for provider pin and output/workspace separation**

Add:

```python
def test_resolve_git_head_requires_exact_pinned_sha(...): ...
def test_run_refuses_wrong_provider_checkout_sha(...): ...
def test_run_refuses_output_directory_inside_workspace(...): ...
def test_run_refuses_missing_model_config_class(...): ...
```

For unit tests, initialize temporary Git repositories and monkeypatch `PINNED_OPENMANUS_SHA` only at the module boundary when testing generic `resolve_git_head`; the actual live-run test must prove a mismatch against the real frozen constant returns/refuses with `PIN_MISMATCH` before provider launch.

- [ ] **Step 2: Run pin/boundary tests and confirm RED**

Run:

```bash
pytest -q tests/test_dev_openmanus_live.py -k "git_head or provider_checkout or output_directory or model_config"
```

Expected: FAIL because identity/environment runner helpers are absent.

- [ ] **Step 3: Implement exact Git identity and path-boundary helpers**

`resolve_git_head(repo)` must use:

```python
subprocess.run(
    ["git", "-C", str(repo), "rev-parse", "HEAD"],
    check=False,
    capture_output=True,
    text=True,
    shell=False,
)
```

Require return code 0 and a lowercase 40-hex SHA; otherwise raise `ValueError("provider checkout identity unavailable")`.

Add a path helper equivalent to:

```python
def _is_within(parent: Path, child: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False
```

`run_live_specimen` must refuse if `output_dir` is within `workspace_root`.

- [ ] **Step 4: Write RED tests for explicit child environment and secret non-serialization**

Add tests proving:

```python
def test_child_env_contains_only_pythonpath_and_explicit_forwarded_names(...): ...
def test_missing_requested_forwarded_env_name_refuses(...): ...
def test_bundle_records_forwarded_variable_names_not_values(...): ...
def test_secret_value_never_appears_in_bundle_json(...): ...
```

`build_child_env()` must always set exactly one harness-owned variable:

```text
PYTHONPATH=<absolute pinned OpenManus checkout>
```

plus explicitly named forwarded values. It must not forward `PATH`, `HOME`, or any other parent variable unless the operator explicitly names it.

- [ ] **Step 5: Run env tests and confirm RED**

Run:

```bash
pytest -q tests/test_dev_openmanus_live.py -k "child_env or secret or forwarded"
```

Expected: FAIL.

- [ ] **Step 6: Implement explicit environment construction**

Implement:

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

Bundle/runtime metadata records only `forwarded_env_names`, never values.

- [ ] **Step 7: Create a fake live provider and RED end-to-end runner test**

Create `tests/fixtures/fake_openmanus_live_provider.py` as a JSON-stdio executable fixture. It must:

1. read one envelope from stdin;
2. validate the expected envelope schema/body/effect;
3. for normal mode, read `specimen/input.txt`, write exactly `OPENMANUS-LIVE-001 OUTPUT\n` to `specimen/output.txt`, and emit a canonical `loadout.openmanus-worker-result/v0` `COMPLETED` object;
4. support hostile request modes through the request string suffix or a dedicated bounded parameter:
   - `unexpected-delta` writes `specimen/rogue.txt` too;
   - `wrong-output` writes incorrect bytes;
   - `provider-refused` emits `REFUSED` without mutation.

The normal result should report:

```json
{
  "schema": "loadout.openmanus-worker-result/v0",
  "disposition": "COMPLETED",
  "observed_post_state": "fake-live:state:1",
  "artifacts": [{"path": "specimen/output.txt"}],
  "observations": [{"fixture": "OPENMANUS-LIVE-001"}],
  "provider_receipt": {"steps_executed": 2, "termination": "FAKE_LIVE_COMPLETE"}
}
```

Write a test invoking `run_live_specimen()` with the fake provider command and a monkeypatched `resolve_git_head()` that returns the exact frozen pin. Expected result: bundle path exists, output file is correct, bundle contains both provider/effect receipts, and `verify_live_bundle()` returns `(True, ())`.

- [ ] **Step 8: Run the end-to-end runner test and confirm RED**

Run:

```bash
pytest -q tests/test_dev_openmanus_live.py -k run_live_specimen
```

Expected: FAIL because `run_live_specimen` is absent.

- [ ] **Step 9: Implement the minimal live specimen runner**

`run_live_specimen()` must:

1. resolve/validate all paths and output-outside-workspace rule;
2. require exact provider checkout SHA `PINNED_OPENMANUS_SHA` before provider launch;
3. require non-empty `model_config_class`;
4. create `specimen/` if needed and write the exact input fixture;
5. refuse if any pre-existing path exists under `specimen/` other than the exact input file with exact expected bytes;
6. snapshot workspace before provider invocation and derive `precondition_state = workspace_state_id(before)`;
7. construct an `AdapterBody` with only `CapabilitySpec("worker.mutate", EffectClass.LOCAL_MUTATE)`;
8. compile one world with task id `OPENMANUS-LIVE-001`, cut target `workspace:specimen`, and the exact pinned body id;
9. construct one `EffectIntent` with capability `worker.mutate`, effect `LOCAL_MUTATE`, target `workspace:specimen`, exact body id, the derived precondition state, and request text exactly instructing the frozen output mutation/no-other-path rule;
10. construct `OpenManusJsonStdioAdapter` using the explicit provider argv, exact workspace root, exact body id, allowlisted child env, timeout, and max steps;
11. call `invoke_effect(compiled, intent, {PINNED_BODY_ID: adapter}, current_state=precondition_state)` exactly once;
12. snapshot workspace after invocation;
13. serialize one bundle JSON with strict keys: `schema`, `provider`, `specimen`, `before`, `after`, `provider_receipt`, `effect_receipt`, `runtime`;
14. serialize dataclass/enum fields into plain JSON without secret values;
15. write atomically to `<output_dir>/openmanus-live-001.json` via temporary sibling + `Path.replace()`;
16. return the bundle path regardless of provider `COMPLETED|REFUSED|ERROR` after launch so evidence survives failure; pre-launch configuration errors raise `ValueError` and do not create a success-looking bundle.

Record runtime metadata:

```json
{
  "python": "<sys.version split first token>",
  "loadout_head": "<git head or explicit unavailable marker if not a checkout>",
  "max_steps": 20,
  "timeout_seconds": 30.0,
  "forwarded_env_names": ["NAME_ONLY"],
  "cleanup": "provider_process_exited"
}
```

Do not include environment values or provider command arguments that contain secret values. Record provider argv only as executable/script basenames if needed; otherwise omit it.

- [ ] **Step 10: Add hostile-run tests**

Use fake provider modes to prove:

```python
def test_runner_preserves_refused_provider_bundle(...): ...
def test_verifier_rejects_fake_unexpected_delta(...): ...
def test_verifier_rejects_fake_wrong_output(...): ...
```

The runner should preserve evidence; the verifier decides whether the occurrence passes.

- [ ] **Step 11: Run Task 2 tests and confirm GREEN**

Run:

```bash
pytest -q tests/test_dev_openmanus_live.py tests/test_dev_openmanus.py tests/test_dev_openmanus_strict_result.py tests/test_dev_openmanus_target_boundary.py
```

Expected: PASS.

- [ ] **Step 12: Commit Task 2**

```bash
git add src/loadout/dev/openmanus_live.py tests/test_dev_openmanus_live.py tests/fixtures/fake_openmanus_live_provider.py
git commit -m "feat: add bounded OpenManus live specimen harness"
```

---

### Task 3: Add STATIC-NODE-friendly build and verify scripts

**Files:**
- Create: `scripts/openmanus-live-001.py`
- Create: `scripts/verify-openmanus-live-001.py`
- Create: `tests/test_openmanus_live_scripts.py`

**Interfaces:**
- Consumes: `run_live_specimen()` and `verify_live_bundle()` from Task 2.
- Produces stable operator commands suitable for STATIC-NODE `--build` and `--verify`.

- [ ] **Step 1: Write RED subprocess tests for CLI argument discipline**

Add tests that invoke each script with `sys.executable` and prove:

```python
def test_build_cli_requires_absolute_provider_checkout(...): ...
def test_build_cli_requires_absolute_workspace_and_output(...): ...
def test_build_cli_requires_model_config_class(...): ...
def test_build_cli_rejects_output_inside_workspace(...): ...
def test_verify_cli_returns_zero_only_for_verified_bundle(...): ...
def test_verify_cli_returns_one_and_prints_reason_codes_for_bad_bundle(...): ...
```

The build CLI arguments are frozen as:

```text
--provider-checkout ABS_PATH
--provider-python ABS_PATH
--workspace ABS_PATH
--output ABS_PATH
--model-config-class LABEL
--pass-env NAME       # repeatable; optional
--timeout-seconds N   # optional; default 30
--max-steps N         # optional; default 20
```

The provider command built by the script is exactly:

```text
<provider-python> <LOADOUT_REPO>/contrib/openmanus/worker.py
```

The verify CLI arguments are:

```text
--workspace ABS_PATH
--bundle ABS_PATH
```

- [ ] **Step 2: Run CLI tests and confirm RED**

Run:

```bash
pytest -q tests/test_openmanus_live_scripts.py
```

Expected: FAIL because scripts do not exist.

- [ ] **Step 3: Implement the build script as a thin adapter**

`scripts/openmanus-live-001.py` must:

1. parse only the frozen arguments above;
2. require all path arguments absolute before resolving;
3. require `provider-python` to exist and be a file;
4. locate LOADOUT repo root from `Path(__file__).resolve().parents[1]`;
5. construct provider command `(str(provider_python), str(repo_root / "contrib/openmanus/worker.py"))`;
6. pass `os.environ` only as the source mapping to `run_live_specimen`; the function forwards only names explicitly listed by `--pass-env`;
7. print only the resulting bundle path on stdout;
8. print configuration/refusal diagnostics to stderr;
9. return exit code 0 only when a bundle is produced; provider completion is intentionally not the build script's final truth because independent verification is a separate STATIC-NODE phase;
10. never print forwarded environment values.

- [ ] **Step 4: Implement the verify script independently**

`scripts/verify-openmanus-live-001.py` must call only `verify_live_bundle()` and:

```python
passed, reasons = verify_live_bundle(bundle_path, workspace_root)
if passed:
    print("OPENMANUS-LIVE-001 VERIFIED")
    raise SystemExit(0)
print("OPENMANUS-LIVE-001 HOLD: " + ",".join(reasons), file=sys.stderr)
raise SystemExit(1)
```

The verify script must not launch OpenManus, consult model configuration, or trust provider self-report beyond the preserved receipt fields checked by the verifier.

- [ ] **Step 5: Add a fake-provider script composition test**

Because the build CLI freezes the genuine `contrib/openmanus/worker.py` command, do not add a hidden `--fake-provider` production flag. Instead test CLI parsing/path behavior directly and keep end-to-end fake provider composition at the Python API layer from Task 2. Add one subprocess test of the verifier against a bundle/workspace generated by the Task 2 API.

This preserves the law:

```text
production CLI surface != test-only provider injection surface
```

- [ ] **Step 6: Run CLI and full OpenManus tests and confirm GREEN**

Run:

```bash
pytest -q tests/test_openmanus_live_scripts.py tests/test_dev_openmanus_live.py tests/test_dev_openmanus.py tests/test_contrib_openmanus_ops.py
```

Expected: PASS.

- [ ] **Step 7: Commit Task 3**

```bash
git add scripts/openmanus-live-001.py scripts/verify-openmanus-live-001.py tests/test_openmanus_live_scripts.py
git commit -m "feat: expose OPENMANUS-LIVE-001 build and verify commands"
```

---

### Task 4: Freeze the field gate, documentation, and branch-wide proof

**Files:**
- Create: `evals/OPENMANUS-LIVE-001.md`
- Modify: `README.md`
- Modify: `tests/test_dev_openmanus_live.py` only if a final documentation/receipt invariant needs executable proof.

**Interfaces:**
- Consumes: completed harness/scripts from Tasks 1-3 and the already-existing STATIC-NODE CLI contract from TranchNode PR #73.
- Produces: durable instructions for a human-run nested specimen and a precise claim boundary.

- [ ] **Step 1: Create the eval document at the pre-live state**

`evals/OPENMANUS-LIVE-001.md` starts with:

```markdown
# OPENMANUS-LIVE-001 — Nested Live Provider Conformance

**Status:** HARNESS PASS · LIVE PROVIDER NOT RUN
**OpenManus pin:** `3309bf4e416fb1c74b008f3e86494439a31bad53`
**LOADOUT carrier:** PR #18 `feat/openmanus-nervous-system-v0`
**Outer harness:** TranchNode `STATIC-NODE-001`

OPENMANUS LIVE PROVIDER CONFORMANCE: NOT RUN
```

Document the three witness layers and repeat these non-claims verbatim:

```text
JSON boundary != OS sandbox
observed clean delta != proof of impossible escape
provider COMPLETED != independent verification
STATIC-NODE VERIFIED != promotion
Workmark != authority
```

Include an empty field-occurrence section whose state is explicitly `NOT RUN`; do not invent dates, model/provider identities, receipt hashes, or pass results before the actual operator occurrence.

- [ ] **Step 2: Document exact nested operator commands in README**

Document two stages.

First, direct LOADOUT harness command inside a prepared child:

```bash
python scripts/openmanus-live-001.py \
  --provider-checkout /absolute/path/to/OpenManus \
  --provider-python /absolute/path/to/openmanus-venv/bin/python \
  --workspace /absolute/path/to/disposable-workspace \
  --output /absolute/path/to/receipts \
  --model-config-class '<non-secret-label>' \
  --pass-env '<explicit-required-variable-name>'

python scripts/verify-openmanus-live-001.py \
  --workspace /absolute/path/to/disposable-workspace \
  --bundle /absolute/path/to/receipts/openmanus-live-001.json
```

Second, show STATIC-NODE composition conceptually using the existing TranchNode command without claiming a cross-repo dependency:

```bash
npm run static-node:001 -- \
  --repo /absolute/path/to/LOADOUT \
  --task-id openmanus-live-001 \
  --build '<explicit OPENMANUS-LIVE-001 build command>' \
  --verify '<explicit OPENMANUS-LIVE-001 verify command>' \
  --output /absolute/path/to/static-node-receipts
```

State clearly that the current STATIC-NODE implementation lives on its own draft carrier until separately promoted/merged; the nested field run must use a checkout containing that implementation.

- [ ] **Step 3: Run focused proof**

Run:

```bash
python -m compileall -q src scripts
pytest -q tests/test_dev_openmanus_live.py tests/test_openmanus_live_scripts.py tests/test_dev_openmanus.py tests/test_dev_openmanus_strict_result.py tests/test_dev_openmanus_target_boundary.py tests/test_contrib_openmanus_ops.py tests/test_dev_public_api.py
```

Expected: PASS.

- [ ] **Step 4: Run branch-wide repository verification**

Run the same commands represented by existing CI plus script compilation:

```bash
python -m pip install -e ".[test]"
python -m compileall -q src scripts
pytest -q
```

Expected: PASS with no credential requirement and no OpenManus installation requirement for ordinary CI.

- [ ] **Step 5: Inspect the final diff for authority expansion**

Explicitly verify the branch diff contains no changes to:

```text
EffectClass
OwnerGate
core membrane effect semantics
OpenManus adapter allowlist
STATIC-NODE promotion semantics
```

Search for accidental dangerous surfaces:

```bash
grep -R "shell=True\|os\.environ\.copy\|REMOTE_MUTATE\|PUBLISH\|LAND" -n src/loadout/dev/openmanus_live.py scripts tests/test_dev_openmanus_live.py tests/test_openmanus_live_scripts.py
```

Expected:

- no `shell=True`;
- no wholesale environment copy;
- no live harness request for `REMOTE_MUTATE`, `PUBLISH`, or `LAND`.

- [ ] **Step 6: Commit Task 4**

```bash
git add README.md evals/OPENMANUS-LIVE-001.md
git commit -m "docs: freeze OPENMANUS-LIVE-001 field gate"
```

- [ ] **Step 7: Update PR #18 receipt only after fresh CI is green**

Update the PR body with:

```text
OPENMANUS-LIVE-001 HARNESS: PASS
OPENMANUS LIVE PROVIDER CONFORMANCE: NOT RUN
```

Include the exact final head SHA and exact successful workflow run id. Keep the PR draft until the genuine pinned provider occurrence is run and reviewed.

Do not change the claim to live-provider PASS from fake-provider/CI evidence.

---

## Field Occurrence After Harness Implementation

The real provider occurrence is intentionally not an ordinary implementation-plan task because it requires a machine with the exact pinned OpenManus checkout and deliberately supplied model/runtime credentials.

The human/operator field run must:

1. use an exact clean LOADOUT parent containing this harness;
2. use STATIC-NODE-001 to create the isolated child;
3. run the build script with the exact pinned provider checkout and explicitly named credential/config variables;
4. run the independent verify script as STATIC-NODE's verify command;
5. inspect LOADOUT bundle, provider receipt, effect receipt, STATIC-NODE attempt receipt, child delta, and optional Workmark;
6. confirm `HOLD` and `promotionAuthorized=false` remain intact;
7. only then amend `evals/OPENMANUS-LIVE-001.md` with the exact dated occurrence facts and change the specimen-scoped claim to `PASS FOR OPENMANUS-LIVE-001 SPECIMEN` if every success condition from the design is met.

No implementation task may pre-write that PASS.
