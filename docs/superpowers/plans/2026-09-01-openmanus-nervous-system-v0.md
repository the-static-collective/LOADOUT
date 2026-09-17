# OpenManus Nervous-System v0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `OPENMANUS-BIND-001`: a standard-library-only LOADOUT adapter that invokes one bounded OpenManus worker occurrence over canonical JSON-stdio, preserves a separate provider-receipt ledger, and proves that provider capability cannot silently enlarge the constituted LOADOUT world.

**Architecture:** `LOADOUT.dev` remains the authority/fence layer. `OpenManusJsonStdioAdapter` accepts only an already-admitted `EffectIntent`, lowers it into `loadout.openmanus-worker-envelope/v0`, invokes an explicit subprocess without a shell, validates one result object, records an `OpenManusProviderReceipt`, and returns only `(provider_disposition, observed_post_state)` through the existing `Adapter` protocol. The optional live shim uses the pinned OpenManus reasoning loop with small LOADOUT-scoped tools rather than exposing OpenManus native Python/editor/browser surfaces directly.

**Tech Stack:** Python 3.11+ standard library in `src/loadout`; pytest 8+ for tests; optional OpenManus provider runtime pinned for live conformance only; no new production dependencies.

**Spec:** `docs/superpowers/specs/2026-09-01-openmanus-nervous-system-v0-design.md`

## Global Constraints

- Production package dependencies remain empty; `src/loadout` must use the Python standard library only.
- Initial inspected upstream pin is exactly `3309bf4e416fb1c74b008f3e86494439a31bad53`.
- Adapter id is exactly `openmanus.worker.json-stdio/v0`.
- V0 supports only `OBSERVE`, `LOCAL_COMPUTE`, and sandbox-scoped `LOCAL_MUTATE`.
- V0 must not advertise or perform `REMOTE_PROPOSE`, `REMOTE_MUTATE`, `PUBLISH`, or `LAND`.
- No `shell=True`; provider command is an explicit argv tuple.
- Child environment is explicit and minimal; parent secrets are not inherited automatically.
- `EffectClass`, `EffectIntent`, `CompileReceipt`, `OwnerGate`, and the existing membrane contract remain unchanged unless a failing test proves a missing invariant.
- Provider receipt is distinct from effect receipt; `EffectReceipt.semantic_authority` remains `False`.
- Deterministic fake-provider tests must pass without OpenManus installed.
- Passing fake-provider tests does not claim live OpenManus conformance.
- The live shim must not expose OpenManus native broad `PythonExecute`, `StrReplaceEditor`, browser, Bash, or generic MCP tools in v0.
- Declared workspace fencing is not represented as OS-level sandbox proof.

---

## File Structure

**Create**

- `src/loadout/dev/openmanus.py` — provider-independent JSON-stdio adapter, result validation, and provider-receipt ledger.
- `schemas/openmanus-worker-envelope-v0.schema.json` — published canonical envelope contract.
- `schemas/openmanus-worker-result-v0.schema.json` — published canonical result contract.
- `tests/fixtures/fake_openmanus_provider.py` — deterministic subprocess fixture for transport and hostile cases.
- `tests/test_dev_openmanus.py` — adapter contract, transport, environment, receipt-ledger, and membrane tests.
- `contrib/openmanus/bounded_ops.py` — stdlib-only workspace/path and bounded arithmetic operations used by the optional live shim.
- `contrib/openmanus/worker.py` — optional OpenManus-aware JSON-stdio shim; dynamic provider imports only after envelope validation.
- `tests/test_contrib_openmanus_ops.py` — deterministic tests for bounded live-shim operations without OpenManus installed.
- `evals/OPENMANUS-BIND-001.md` — executable specimen receipt and promotion boundary.

**Modify**

- `src/loadout/dev/__init__.py` — export the new adapter and provider-receipt type.
- `tests/test_dev_public_api.py` — assert the public export surface.
- `README.md` — document the bounded provider seam and non-claims.

---

### Task 1: Define the adapter identity, provider receipt, and canonical envelope

**Files:**
- Create: `src/loadout/dev/openmanus.py`
- Create: `tests/test_dev_openmanus.py`

**Interfaces:**
- Consumes: `EffectClass`, `EffectIntent`, and `parameter_map()` from `loadout.dev.model`.
- Produces:
  - `OPENMANUS_ADAPTER_ID: str`
  - `OPENMANUS_ENVELOPE_SCHEMA: str`
  - `OPENMANUS_RESULT_SCHEMA: str`
  - `OpenManusProviderReceipt` frozen dataclass
  - `OpenManusJsonStdioAdapter`
  - `OpenManusJsonStdioAdapter.provider_receipts -> tuple[OpenManusProviderReceipt, ...]`
  - private `_build_envelope(intent) -> dict[str, object]`

- [ ] **Step 1: Write failing construction and envelope tests**

Add this initial body to `tests/test_dev_openmanus.py`:

```python
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from loadout.dev.model import EffectClass, EffectIntent
from loadout.dev.openmanus import (
    OPENMANUS_ADAPTER_ID,
    OPENMANUS_ENVELOPE_SCHEMA,
    OpenManusJsonStdioAdapter,
)

UPSTREAM_SHA = "3309bf4e416fb1c74b008f3e86494439a31bad53"
BODY_ID = f"{OPENMANUS_ADAPTER_ID}@{UPSTREAM_SHA}"


def _intent(effect: EffectClass = EffectClass.OBSERVE, **parameters: str) -> EffectIntent:
    return EffectIntent(
        capability="worker.perform",
        effect=effect,
        target="workspace:fixture",
        body_time_id=BODY_ID,
        precondition_state="state:0",
        parameters_digest="sha256:" + "1" * 64,
        parameters=tuple(parameters.items()),
    )


def test_openmanus_adapter_requires_exact_body_time_identity(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="body_time_id"):
        OpenManusJsonStdioAdapter(
            provider_command=(sys.executable, "-c", "pass"),
            workspace_root=tmp_path,
            body_time_id="openmanus.worker.json-stdio/v0@not-a-sha",
        )


def test_openmanus_envelope_preserves_admitted_intent_without_semantic_expansion(tmp_path: Path) -> None:
    adapter = OpenManusJsonStdioAdapter(
        provider_command=(sys.executable, "-c", "pass"),
        workspace_root=tmp_path,
        body_time_id=BODY_ID,
        max_steps=7,
    )
    envelope = adapter._build_envelope(_intent(request="inspect the fixture"))
    assert envelope == {
        "schema": OPENMANUS_ENVELOPE_SCHEMA,
        "body_time_id": BODY_ID,
        "capability": "worker.perform",
        "effect": "OBSERVE",
        "target": "workspace:fixture",
        "precondition_state": "state:0",
        "parameters_digest": "sha256:" + "1" * 64,
        "parameters": {"request": "inspect the fixture"},
        "workspace_root": str(tmp_path.resolve()),
        "max_steps": 7,
    }
```

- [ ] **Step 2: Run the targeted tests and verify RED**

Run:

```bash
pytest -q tests/test_dev_openmanus.py -k "requires_exact_body_time_identity or envelope_preserves"
```

Expected: collection/import failure because `loadout.dev.openmanus` does not exist.

- [ ] **Step 3: Implement the minimum identity, dataclass, constructor, and envelope builder**

Create `src/loadout/dev/openmanus.py` with these exact public definitions and the minimum supporting validation:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Mapping, Sequence

from loadout.dev.model import EffectClass, EffectIntent, parameter_map

OPENMANUS_ADAPTER_ID = "openmanus.worker.json-stdio/v0"
OPENMANUS_ENVELOPE_SCHEMA = "loadout.openmanus-worker-envelope/v0"
OPENMANUS_RESULT_SCHEMA = "loadout.openmanus-worker-result/v0"

_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_ALLOWED_EFFECTS = frozenset({
    EffectClass.OBSERVE,
    EffectClass.LOCAL_COMPUTE,
    EffectClass.LOCAL_MUTATE,
})


@dataclass(frozen=True)
class OpenManusProviderReceipt:
    body_time_id: str
    capability: str
    effect: EffectClass
    target: str
    precondition_state: str
    disposition: str
    observed_post_state: str | None
    artifacts: tuple[object, ...]
    observations: tuple[object, ...]
    steps_executed: int
    termination: str
    stderr: str


class OpenManusJsonStdioAdapter:
    def __init__(
        self,
        *,
        provider_command: Sequence[str],
        workspace_root: str | Path,
        body_time_id: str,
        child_env: Mapping[str, str] | None = None,
        timeout_seconds: float = 30.0,
        max_steps: int = 20,
    ) -> None:
        prefix = f"{OPENMANUS_ADAPTER_ID}@"
        if not body_time_id.startswith(prefix) or _SHA40.fullmatch(body_time_id[len(prefix):]) is None:
            raise ValueError("body_time_id must be openmanus adapter id plus exact sha40")
        if not provider_command or any(not isinstance(part, str) or not part for part in provider_command):
            raise ValueError("provider_command must be a non-empty argv sequence")
        root = Path(workspace_root).resolve()
        if not root.is_dir():
            raise ValueError("workspace_root must exist and be a directory")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if max_steps <= 0:
            raise ValueError("max_steps must be positive")
        self.provider_command = tuple(provider_command)
        self.workspace_root = root
        self.body_time_id = body_time_id
        self.child_env = dict(child_env or {})
        self.timeout_seconds = float(timeout_seconds)
        self.max_steps = int(max_steps)
        self._provider_receipts: list[OpenManusProviderReceipt] = []

    @property
    def provider_receipts(self) -> tuple[OpenManusProviderReceipt, ...]:
        return tuple(self._provider_receipts)

    def _build_envelope(self, intent: EffectIntent) -> dict[str, object]:
        if intent.effect not in _ALLOWED_EFFECTS:
            raise ValueError("unsupported OpenManus effect")
        params = parameter_map(intent)
        return {
            "schema": OPENMANUS_ENVELOPE_SCHEMA,
            "body_time_id": self.body_time_id,
            "capability": intent.capability,
            "effect": intent.effect.value,
            "target": intent.target,
            "precondition_state": intent.precondition_state,
            "parameters_digest": intent.parameters_digest,
            "parameters": params,
            "workspace_root": str(self.workspace_root),
            "max_steps": self.max_steps,
        }
```

- [ ] **Step 4: Run targeted tests and verify GREEN**

Run:

```bash
pytest -q tests/test_dev_openmanus.py -k "requires_exact_body_time_identity or envelope_preserves"
```

Expected: 2 passed.

- [ ] **Step 5: Commit Task 1**

```bash
git add src/loadout/dev/openmanus.py tests/test_dev_openmanus.py
git commit -m "feat: define bounded OpenManus worker envelope"
```

---

### Task 2: Prove JSON-stdio transport, environment narrowing, result validation, and provider receipts

**Files:**
- Modify: `src/loadout/dev/openmanus.py`
- Modify: `tests/test_dev_openmanus.py`
- Create: `tests/fixtures/fake_openmanus_provider.py`

**Interfaces:**
- Consumes: Task 1 `OpenManusJsonStdioAdapter._build_envelope()`.
- Produces:
  - `OpenManusJsonStdioAdapter.invoke(intent) -> tuple[str, str | None]`
  - one `OpenManusProviderReceipt` appended for every provider launch, including transport/schema failure
  - no receipt when refusal happens before launch

- [ ] **Step 1: Add a deterministic fake provider fixture**

Create `tests/fixtures/fake_openmanus_provider.py` with exactly one JSON object emitted on stdout for normal modes:

```python
from __future__ import annotations

import json
import os
import sys
import time


envelope = json.loads(sys.stdin.read())
mode = envelope.get("parameters", {}).get("fixture_mode", "ok")

if mode == "timeout":
    time.sleep(5)
elif mode == "malformed":
    sys.stdout.write("not-json")
elif mode == "multi":
    sys.stdout.write("{}\n{}\n")
elif mode == "wrong-schema":
    print(json.dumps({"schema": "wrong/v0", "disposition": "COMPLETED"}))
else:
    observations = [{
        "allowed_env": os.environ.get("LOADOUT_ALLOWED"),
        "secret_env": os.environ.get("LOADOUT_SECRET"),
        "effect": envelope["effect"],
    }]
    print(json.dumps({
        "schema": "loadout.openmanus-worker-result/v0",
        "disposition": "REFUSED" if mode == "refused" else "COMPLETED",
        "observed_post_state": None if mode == "refused" else "state:1",
        "artifacts": [{"path": "artifact.txt"}],
        "observations": observations,
        "provider_receipt": {
            "steps_executed": 3,
            "termination": mode,
        },
    }))
    print("provider diagnostic", file=sys.stderr)
```

- [ ] **Step 2: Add failing transport tests**

Append tests covering all of these behaviors:

```python
import os

FAKE_PROVIDER = Path(__file__).parent / "fixtures" / "fake_openmanus_provider.py"


def _adapter(tmp_path: Path, **kwargs) -> OpenManusJsonStdioAdapter:
    return OpenManusJsonStdioAdapter(
        provider_command=(sys.executable, str(FAKE_PROVIDER)),
        workspace_root=tmp_path,
        body_time_id=BODY_ID,
        **kwargs,
    )


def test_invoke_returns_narrow_effect_result_and_preserves_rich_provider_receipt(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path)
    assert adapter.invoke(_intent(fixture_mode="ok")) == ("COMPLETED", "state:1")
    receipt = adapter.provider_receipts[-1]
    assert receipt.body_time_id == BODY_ID
    assert receipt.disposition == "COMPLETED"
    assert receipt.observed_post_state == "state:1"
    assert receipt.artifacts == ({"path": "artifact.txt"},)
    assert receipt.steps_executed == 3
    assert "provider diagnostic" in receipt.stderr


def test_child_environment_is_allowlisted_not_parent_inherited(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOADOUT_SECRET", "parent-secret")
    adapter = _adapter(tmp_path, child_env={"LOADOUT_ALLOWED": "yes"})
    adapter.invoke(_intent())
    observation = adapter.provider_receipts[-1].observations[0]
    assert observation["allowed_env"] == "yes"
    assert observation["secret_env"] is None


@pytest.mark.parametrize("mode", ["malformed", "multi", "wrong-schema"])
def test_invalid_provider_stdout_is_typed_provider_error(tmp_path: Path, mode: str) -> None:
    adapter = _adapter(tmp_path)
    disposition, post_state = adapter.invoke(_intent(fixture_mode=mode))
    assert disposition == "ERROR"
    assert post_state is None
    assert adapter.provider_receipts[-1].disposition == "ERROR"


def test_provider_timeout_is_typed_provider_error(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path, timeout_seconds=0.05)
    assert adapter.invoke(_intent(fixture_mode="timeout")) == ("ERROR", None)
    assert adapter.provider_receipts[-1].termination == "TIMEOUT"


def test_unsupported_effect_refuses_before_subprocess_launch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = _adapter(tmp_path)
    launched = False

    def fail_if_called(*args, **kwargs):
        nonlocal launched
        launched = True
        raise AssertionError("provider must not launch")

    monkeypatch.setattr("loadout.dev.openmanus.subprocess.run", fail_if_called)
    assert adapter.invoke(_intent(EffectClass.REMOTE_MUTATE)) == ("REFUSE", None)
    assert launched is False
    assert adapter.provider_receipts == ()
```

- [ ] **Step 3: Run the transport tests and verify RED**

Run:

```bash
pytest -q tests/test_dev_openmanus.py -k "invoke_returns or environment_is_allowlisted or invalid_provider_stdout or provider_timeout or unsupported_effect"
```

Expected: failures because `invoke()` and result parsing do not exist.

- [ ] **Step 4: Implement canonical subprocess execution and strict result parsing**

Add imports:

```python
import json
import subprocess
```

Implement these private helpers in `OpenManusJsonStdioAdapter`:

```python
    def _record_error(self, intent: EffectIntent, *, termination: str, stderr: str = "") -> tuple[str, None]:
        self._provider_receipts.append(OpenManusProviderReceipt(
            body_time_id=self.body_time_id,
            capability=intent.capability,
            effect=intent.effect,
            target=intent.target,
            precondition_state=intent.precondition_state,
            disposition="ERROR",
            observed_post_state=None,
            artifacts=(),
            observations=(),
            steps_executed=0,
            termination=termination,
            stderr=stderr,
        ))
        return "ERROR", None

    def _parse_result(self, intent: EffectIntent, stdout: str, stderr: str) -> tuple[str, str | None]:
        stripped = stdout.strip()
        try:
            value = json.loads(stripped)
        except (json.JSONDecodeError, TypeError):
            return self._record_error(intent, termination="MALFORMED_RESULT", stderr=stderr)
        if not isinstance(value, dict) or value.get("schema") != OPENMANUS_RESULT_SCHEMA:
            return self._record_error(intent, termination="WRONG_RESULT_SCHEMA", stderr=stderr)
        disposition = value.get("disposition")
        if disposition not in {"COMPLETED", "REFUSED", "ERROR"}:
            return self._record_error(intent, termination="INVALID_DISPOSITION", stderr=stderr)
        post_state = value.get("observed_post_state")
        if post_state is not None and not isinstance(post_state, str):
            return self._record_error(intent, termination="INVALID_POST_STATE", stderr=stderr)
        artifacts = value.get("artifacts")
        observations = value.get("observations")
        provider_receipt = value.get("provider_receipt")
        if not isinstance(artifacts, list) or not isinstance(observations, list) or not isinstance(provider_receipt, dict):
            return self._record_error(intent, termination="INVALID_RESULT_SHAPE", stderr=stderr)
        steps = provider_receipt.get("steps_executed")
        termination = provider_receipt.get("termination")
        if not isinstance(steps, int) or steps < 0 or not isinstance(termination, str):
            return self._record_error(intent, termination="INVALID_PROVIDER_RECEIPT", stderr=stderr)
        self._provider_receipts.append(OpenManusProviderReceipt(
            body_time_id=self.body_time_id,
            capability=intent.capability,
            effect=intent.effect,
            target=intent.target,
            precondition_state=intent.precondition_state,
            disposition=disposition,
            observed_post_state=post_state,
            artifacts=tuple(artifacts),
            observations=tuple(observations),
            steps_executed=steps,
            termination=termination,
            stderr=stderr,
        ))
        return disposition, post_state
```

Implement `invoke()`:

```python
    def invoke(self, intent: EffectIntent) -> tuple[str, str | None]:
        if intent.effect not in _ALLOWED_EFFECTS:
            return "REFUSE", None
        if intent.body_time_id != self.body_time_id:
            return "REFUSE", None
        try:
            envelope = self._build_envelope(intent)
        except ValueError:
            return "REFUSE", None
        payload = json.dumps(envelope, sort_keys=True, separators=(",", ":"))
        try:
            completed = subprocess.run(
                list(self.provider_command),
                input=payload,
                text=True,
                check=False,
                capture_output=True,
                env=dict(self.child_env),
                shell=False,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as error:
            stderr = error.stderr if isinstance(error.stderr, str) else ""
            return self._record_error(intent, termination="TIMEOUT", stderr=stderr)
        except (FileNotFoundError, OSError) as error:
            return self._record_error(intent, termination="PROVIDER_UNAVAILABLE", stderr=str(error))
        if completed.returncode != 0:
            return self._record_error(intent, termination=f"EXIT_{completed.returncode}", stderr=completed.stderr)
        return self._parse_result(intent, completed.stdout, completed.stderr)
```

Do not add environment inheritance or shell fallback.

- [ ] **Step 5: Run Task 2 tests and full current suite**

```bash
pytest -q tests/test_dev_openmanus.py
pytest -q
```

Expected: all tests pass.

- [ ] **Step 6: Commit Task 2**

```bash
git add src/loadout/dev/openmanus.py tests/test_dev_openmanus.py tests/fixtures/fake_openmanus_provider.py
git commit -m "feat: execute bounded OpenManus provider over json stdio"
```

---

### Task 3: Prove the existing LOADOUT membrane prevents provider self-constitution

**Files:**
- Modify: `tests/test_dev_openmanus.py`

**Interfaces:**
- Consumes: `compile_world()`, `invoke_effect()`, `AdapterBody`, `CapabilityRequest`, `CapabilitySpec`, `CompileRequest`.
- Produces: hostile proof that the provider process is never launched when the compiled world rejects the intent.

- [ ] **Step 1: Add hostile membrane tests using a launch-marker provider**

Add imports:

```python
from loadout.dev.compiler import compile_world
from loadout.dev.membrane import invoke_effect
from loadout.dev.model import (
    AdapterBody,
    CapabilityRequest,
    CapabilitySpec,
    CompileRequest,
    RefusalReason,
)
```

Add helper:

```python
BODY = AdapterBody(
    adapter_id=OPENMANUS_ADAPTER_ID,
    body_time_id=BODY_ID,
    source_sha=UPSTREAM_SHA,
    capabilities=(
        CapabilitySpec("worker.perform", EffectClass.OBSERVE),
        CapabilitySpec("worker.compute", EffectClass.LOCAL_COMPUTE),
        CapabilitySpec("worker.mutate", EffectClass.LOCAL_MUTATE),
    ),
)


def _compiled(capability: str, effect: EffectClass) -> object:
    return compile_world(CompileRequest(
        task_id="OPENMANUS-BIND-001",
        task_text="bounded worker specimen",
        cut_targets=frozenset({"workspace:fixture"}),
        requested_capabilities=(CapabilityRequest(
            capability,
            effect,
            "workspace:fixture",
            body_time_id=BODY_ID,
        ),),
        available_bodies=(BODY,),
    ))
```

Add three tests asserting `adapter.provider_receipts == ()` after membrane refusal:

```python
def test_remote_mutation_binding_is_refused_before_openmanus_launch(tmp_path: Path) -> None:
    compiled = _compiled("worker.perform", EffectClass.OBSERVE)
    adapter = _adapter(tmp_path)
    intent = _intent(EffectClass.REMOTE_MUTATE)
    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="state:0")
    assert receipt.reason == RefusalReason.EFFECT_OUTSIDE_FENCE
    assert adapter.provider_receipts == ()


def test_target_outside_cut_is_refused_before_openmanus_launch(tmp_path: Path) -> None:
    compiled = _compiled("worker.perform", EffectClass.OBSERVE)
    adapter = _adapter(tmp_path)
    intent = EffectIntent(
        "worker.perform", EffectClass.OBSERVE, "workspace:other", BODY_ID,
        "state:0", "sha256:" + "2" * 64,
    )
    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="state:0")
    assert receipt.reason == RefusalReason.TARGET_OUTSIDE_CUT
    assert adapter.provider_receipts == ()


def test_stale_precondition_is_refused_before_openmanus_launch(tmp_path: Path) -> None:
    compiled = _compiled("worker.perform", EffectClass.OBSERVE)
    adapter = _adapter(tmp_path)
    receipt = invoke_effect(
        compiled,
        _intent(),
        {BODY_ID: adapter},
        current_state="state:newer",
    )
    assert receipt.reason == RefusalReason.STATE_STALE
    assert adapter.provider_receipts == ()
```

- [ ] **Step 2: Run hostile tests**

```bash
pytest -q tests/test_dev_openmanus.py -k "before_openmanus_launch"
```

Expected: pass using the unchanged core membrane. If any test requires changing membrane/model code, stop and identify the exact failed invariant before editing those files.

- [ ] **Step 3: Add the success non-laundering integration test**

```python
def test_successful_openmanus_execution_never_mints_semantic_authority(tmp_path: Path) -> None:
    compiled = _compiled("worker.perform", EffectClass.OBSERVE)
    adapter = _adapter(tmp_path)
    receipt = invoke_effect(compiled, _intent(), {BODY_ID: adapter}, current_state="state:0")
    assert receipt.provider_disposition == "COMPLETED"
    assert receipt.observed_post_state == "state:1"
    assert receipt.semantic_authority is False
    assert receipt.reason is None
    assert len(adapter.provider_receipts) == 1
```

- [ ] **Step 4: Run the complete adapter and membrane tests**

```bash
pytest -q tests/test_dev_openmanus.py tests/test_dev_membrane.py
```

Expected: all pass.

- [ ] **Step 5: Commit Task 3**

```bash
git add tests/test_dev_openmanus.py
git commit -m "test: prove OpenManus cannot self-expand LOADOUT authority"
```

---

### Task 4: Publish the JSON contracts and public LOADOUT.dev surface

**Files:**
- Create: `schemas/openmanus-worker-envelope-v0.schema.json`
- Create: `schemas/openmanus-worker-result-v0.schema.json`
- Modify: `tests/test_dev_openmanus.py`
- Modify: `src/loadout/dev/__init__.py`
- Modify: `tests/test_dev_public_api.py`

**Interfaces:**
- Consumes: Task 1 constants/types.
- Produces: parseable published schemas and stable public exports.

- [ ] **Step 1: Write failing schema/public-export tests**

Append to `tests/test_dev_openmanus.py`:

```python
import json


def test_published_openmanus_schemas_match_runtime_contract_names() -> None:
    repo_root = Path(__file__).parents[1]
    envelope_schema = json.loads((repo_root / "schemas" / "openmanus-worker-envelope-v0.schema.json").read_text())
    result_schema = json.loads((repo_root / "schemas" / "openmanus-worker-result-v0.schema.json").read_text())
    assert envelope_schema["properties"]["schema"]["const"] == OPENMANUS_ENVELOPE_SCHEMA
    assert result_schema["properties"]["schema"]["const"] == "loadout.openmanus-worker-result/v0"
    assert set(envelope_schema["properties"]["effect"]["enum"]) == {"OBSERVE", "LOCAL_COMPUTE", "LOCAL_MUTATE"}
```

Append to `tests/test_dev_public_api.py`:

```python
def test_public_api_exports_openmanus_provider_surface() -> None:
    expected = {"OpenManusJsonStdioAdapter", "OpenManusProviderReceipt"}
    assert expected <= set(dev.__all__)
    for name in expected:
        assert hasattr(dev, name)
```

- [ ] **Step 2: Run and verify RED**

```bash
pytest -q tests/test_dev_openmanus.py -k published_openmanus_schemas
pytest -q tests/test_dev_public_api.py -k openmanus_provider_surface
```

Expected: missing schema files and missing exports.

- [ ] **Step 3: Create exact envelope schema**

Create `schemas/openmanus-worker-envelope-v0.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "loadout.openmanus-worker-envelope/v0",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema", "body_time_id", "capability", "effect", "target", "precondition_state", "parameters_digest", "parameters", "workspace_root", "max_steps"],
  "properties": {
    "schema": {"const": "loadout.openmanus-worker-envelope/v0"},
    "body_time_id": {"type": "string"},
    "capability": {"type": "string", "minLength": 1},
    "effect": {"enum": ["OBSERVE", "LOCAL_COMPUTE", "LOCAL_MUTATE"]},
    "target": {"type": "string", "minLength": 1},
    "precondition_state": {"type": "string", "minLength": 1},
    "parameters_digest": {"type": "string", "minLength": 1},
    "parameters": {"type": "object", "additionalProperties": {"type": "string"}},
    "workspace_root": {"type": "string", "minLength": 1},
    "max_steps": {"type": "integer", "minimum": 1}
  }
}
```

- [ ] **Step 4: Create exact result schema**

Create `schemas/openmanus-worker-result-v0.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "loadout.openmanus-worker-result/v0",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema", "disposition", "observed_post_state", "artifacts", "observations", "provider_receipt"],
  "properties": {
    "schema": {"const": "loadout.openmanus-worker-result/v0"},
    "disposition": {"enum": ["COMPLETED", "REFUSED", "ERROR"]},
    "observed_post_state": {"type": ["string", "null"]},
    "artifacts": {"type": "array"},
    "observations": {"type": "array"},
    "provider_receipt": {
      "type": "object",
      "additionalProperties": false,
      "required": ["steps_executed", "termination"],
      "properties": {
        "steps_executed": {"type": "integer", "minimum": 0},
        "termination": {"type": "string"}
      }
    }
  }
}
```

- [ ] **Step 5: Export only the intended public classes**

In `src/loadout/dev/__init__.py`, import:

```python
from loadout.dev.openmanus import OpenManusJsonStdioAdapter, OpenManusProviderReceipt
```

Add only those two names to `__all__`. Do not export private parser/transport helpers.

- [ ] **Step 6: Run schema/public API tests and full suite**

```bash
pytest -q tests/test_dev_openmanus.py tests/test_dev_public_api.py
pytest -q
```

Expected: all pass.

- [ ] **Step 7: Commit Task 4**

```bash
git add schemas/openmanus-worker-envelope-v0.schema.json schemas/openmanus-worker-result-v0.schema.json src/loadout/dev/__init__.py tests/test_dev_openmanus.py tests/test_dev_public_api.py
git commit -m "docs: publish OpenManus worker json contracts"
```

---

### Task 5: Build LOADOUT-scoped operations for the optional live OpenManus shim

**Files:**
- Create: `contrib/openmanus/bounded_ops.py`
- Create: `tests/test_contrib_openmanus_ops.py`

**Interfaces:**
- Produces:
  - `resolve_workspace_path(workspace_root: Path, relative_path: str) -> Path`
  - `read_text(workspace_root: Path, relative_path: str) -> str`
  - `write_text(workspace_root: Path, relative_path: str, content: str) -> str`
  - `evaluate_arithmetic(expression: str) -> int | float`
- These functions use only stdlib and are the only filesystem/compute primitives the v0 live shim wraps as OpenManus tools.

- [ ] **Step 1: Write failing path-boundary and arithmetic tests**

Create `tests/test_contrib_openmanus_ops.py`:

```python
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).parents[1] / "contrib" / "openmanus" / "bounded_ops.py"
spec = importlib.util.spec_from_file_location("bounded_ops", MODULE_PATH)
assert spec is not None and spec.loader is not None
bounded_ops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bounded_ops)


def test_read_and_write_are_confined_to_declared_workspace(tmp_path: Path) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    assert bounded_ops.write_text(root, "notes/a.txt", "hello") == "notes/a.txt"
    assert bounded_ops.read_text(root, "notes/a.txt") == "hello"
    with pytest.raises(ValueError, match="outside workspace"):
        bounded_ops.write_text(root, "../escape.txt", "no")
    with pytest.raises(ValueError, match="outside workspace"):
        bounded_ops.read_text(root, "/etc/passwd")


def test_bounded_arithmetic_accepts_numbers_and_basic_operators() -> None:
    assert bounded_ops.evaluate_arithmetic("(2 + 3) * 4") == 20
    assert bounded_ops.evaluate_arithmetic("7 / 2") == 3.5


@pytest.mark.parametrize("expression", ["__import__('os').system('echo nope')", "open('x')", "[x for x in range(3)]", "2 ** 1000"])
def test_bounded_arithmetic_rejects_code_and_unbounded_shapes(expression: str) -> None:
    with pytest.raises(ValueError):
        bounded_ops.evaluate_arithmetic(expression)
```

- [ ] **Step 2: Run and verify RED**

```bash
pytest -q tests/test_contrib_openmanus_ops.py
```

Expected: missing `bounded_ops.py`.

- [ ] **Step 3: Implement workspace confinement and small arithmetic AST**

Create `contrib/openmanus/bounded_ops.py` using `Path.resolve()` plus a relative-to-root check. The arithmetic evaluator must parse `ast.Expression` and recursively accept only:

```text
ast.Constant containing int/float
ast.UnaryOp with UAdd/USub
ast.BinOp with Add/Sub/Mult/Div/FloorDiv/Mod
```

Reject `Pow` in v0 to avoid unbounded magnitude. Reject booleans. Cap source expression length at 256 characters. After each operation, reject numeric results whose absolute value exceeds `1_000_000_000_000`.

Use this exact path rule:

```python
resolved = (workspace_root.resolve() / relative_path).resolve()
try:
    resolved.relative_to(workspace_root.resolve())
except ValueError as error:
    raise ValueError("path outside workspace") from error
```

Require `relative_path` to be non-empty, non-absolute, and NUL-free. `write_text()` may create parent directories under the root and must use UTF-8.

- [ ] **Step 4: Run deterministic bounded-op tests**

```bash
pytest -q tests/test_contrib_openmanus_ops.py
```

Expected: all pass.

- [ ] **Step 5: Commit Task 5**

```bash
git add contrib/openmanus/bounded_ops.py tests/test_contrib_openmanus_ops.py
git commit -m "feat: add bounded operations for OpenManus live shim"
```

---

### Task 6: Add the optional pinned OpenManus worker shim without making OpenManus a LOADOUT dependency

**Files:**
- Create: `contrib/openmanus/worker.py`
- Modify: `tests/test_contrib_openmanus_ops.py`

**Interfaces:**
- Consumes: envelope schema from Task 4 and bounded operations from Task 5.
- Produces: executable JSON-stdio provider command compatible with `OpenManusJsonStdioAdapter` when OpenManus is explicitly installed.

- [ ] **Step 1: Add a failing pre-import validation test**

Append a subprocess test proving malformed envelopes are rejected without requiring OpenManus:

```python
import json
import subprocess
import sys

WORKER = Path(__file__).parents[1] / "contrib" / "openmanus" / "worker.py"


def test_worker_rejects_wrong_schema_before_openmanus_import() -> None:
    completed = subprocess.run(
        [sys.executable, str(WORKER)],
        input=json.dumps({"schema": "wrong/v0"}),
        text=True,
        capture_output=True,
        check=False,
        env={},
    )
    assert completed.returncode == 0
    result = json.loads(completed.stdout)
    assert result["schema"] == "loadout.openmanus-worker-result/v0"
    assert result["disposition"] == "REFUSED"
    assert result["provider_receipt"]["termination"] == "INVALID_ENVELOPE"
```

- [ ] **Step 2: Run and verify RED**

```bash
pytest -q tests/test_contrib_openmanus_ops.py -k worker_rejects
```

Expected: missing worker script.

- [ ] **Step 3: Implement worker envelope validation before any OpenManus import**

Create `contrib/openmanus/worker.py` with this high-level order:

```text
1. read stdin once
2. parse one JSON object
3. require schema == loadout.openmanus-worker-envelope/v0
4. require effect in OBSERVE | LOCAL_COMPUTE | LOCAL_MUTATE
5. require existing workspace_root directory
6. require parameters.request non-empty
7. only then dynamically import OpenManus modules
8. construct effect-specific LOADOUT-scoped BaseTool wrappers
9. construct one ToolCallAgent occurrence with only those tools + Terminate
10. run request with max_steps from envelope
11. emit exactly one loadout.openmanus-worker-result/v0 object
12. cleanup through agent.run()/cleanup lifecycle
```

For pre-import refusal, emit:

```json
{
  "schema": "loadout.openmanus-worker-result/v0",
  "disposition": "REFUSED",
  "observed_post_state": null,
  "artifacts": [],
  "observations": [],
  "provider_receipt": {"steps_executed": 0, "termination": "INVALID_ENVELOPE"}
}
```

- [ ] **Step 4: Wrap only LOADOUT-scoped tools**

Inside a function called only after dynamic imports, define OpenManus `BaseTool` wrappers around Task 5 operations:

```text
OBSERVE       -> loadout_read_text
LOCAL_COMPUTE -> loadout_calculate
LOCAL_MUTATE  -> loadout_read_text + loadout_write_text
```

Do not instantiate OpenManus `Manus`, `SandboxManus`, `PythonExecute`, `StrReplaceEditor`, `Bash`, browser tools, or MCP clients. Use the pinned OpenManus `ToolCallAgent` only as the reasoning/tool-call loop and `ToolCollection` as the tool container.

Each wrapper must hard-bind `workspace_root`; the model receives only relative paths or arithmetic expressions.

The system prompt must include these invariants verbatim:

```text
You are a bounded worker inside a LOADOUT-constituted occurrence.
Use only the supplied tools.
Do not claim authority, publication, external mutation, or access beyond the declared workspace.
Finish with Terminate when the bounded request is complete or cannot be completed.
```

- [ ] **Step 5: Keep stdout contract clean**

Provider/library diagnostic text must go to stderr. Before invoking the OpenManus runtime, use `contextlib.redirect_stdout(sys.stderr)` around provider construction/run if necessary, then print only the final JSON result to real stdout.

The result must set:

```text
artifacts       = paths written by loadout_write_text during this occurrence
observations    = outputs returned by bounded tools during this occurrence
steps_executed  = agent.current_step
termination     = COMPLETED | AGENT_ERROR | PROVIDER_UNAVAILABLE
```

`observed_post_state` may be a deterministic SHA-256 digest over sorted artifact paths plus UTF-8 file contents under those written paths. It must not claim whole-workspace state.

- [ ] **Step 6: Add source-level hostile assertions**

Append:

```python
def test_live_worker_does_not_expose_broad_openmanus_tools() -> None:
    source = WORKER.read_text(encoding="utf-8")
    for banned in (
        "PythonExecute(", "StrReplaceEditor(", "Bash(", "SandboxManus(",
        "BrowserUse", "MCPClients(", "shell=True",
    ):
        assert banned not in source
```

- [ ] **Step 7: Run deterministic shim tests without OpenManus installed**

```bash
pytest -q tests/test_contrib_openmanus_ops.py
```

Expected: all pass. Do not add a CI requirement for the live provider.

- [ ] **Step 8: Commit Task 6**

```bash
git add contrib/openmanus/worker.py tests/test_contrib_openmanus_ops.py
git commit -m "feat: add optional bounded OpenManus worker shim"
```

---

### Task 7: Land `OPENMANUS-BIND-001` receipt, README boundary, and optional live conformance command

**Files:**
- Create: `evals/OPENMANUS-BIND-001.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: completed deterministic test surface and optional live shim.
- Produces: explicit claim boundary between deterministic adapter conformance and live provider conformance.

- [ ] **Step 1: Write the eval receipt with deterministic pass criteria**

Create `evals/OPENMANUS-BIND-001.md` containing these sections:

```text
Purpose
Pinned provider body inspected
Constituted capability surface
Hostile cases
Deterministic commands run
Observed results
Non-claims
Live provider conformance status
Promotion gate
```

Record the exact upstream SHA `3309bf4e416fb1c74b008f3e86494439a31bad53` and state explicitly:

```text
PASSING FAKE-PROVIDER TESTS PROVE THE LOADOUT ADAPTER CONTRACT.
THEY DO NOT PROVE OPENMANUS LIVE PROVIDER CONFORMANCE.
```

The hostile cases must name remote mutation, target outside cut, stale precondition state, unsupported effect, malformed provider result, wrong schema, timeout, and parent-secret non-inheritance.

- [ ] **Step 2: Add README section**

Add a concise `OPENMANUS-BIND-001` section after the existing LOADOUT.dev host-adapter material:

```text
LOADOUT constitutes; OpenManus moves.
```

Document:

- JSON-stdio boundary;
- exact body-time pin;
- provider receipt vs effect receipt;
- `OBSERVE | LOCAL_COMPUTE | LOCAL_MUTATE` only;
- live shim is optional and uses LOADOUT-scoped tools;
- no remote mutation/publication/merge authority;
- no secure-sandbox claim.

- [ ] **Step 3: Run deterministic verification**

```bash
python -m pip install -e ".[test]"
pytest -q
```

Expected: complete suite passes.

- [ ] **Step 4: Run optional live-provider specimen only when explicitly configured**

When a local checkout of `FoundationAgents/OpenManus` is at exact commit `3309bf4e416fb1c74b008f3e86494439a31bad53` and its runtime/model credentials are intentionally configured, run a disposable workspace specimen using:

```bash
python contrib/openmanus/worker.py < /tmp/openmanus-envelope.json
```

Then exercise the same command through `OpenManusJsonStdioAdapter` with the provider command pointing at that interpreter/script. Record the provider version evidence, command argv, workspace path class (`disposable`), effect tested, returned provider receipt, and whether any unexpected effect occurred.

If the provider is unavailable, record `LIVE PROVIDER CONFORMANCE: NOT RUN` rather than weakening the gate.

- [ ] **Step 5: Update eval receipt with actual verification output**

Record the exact pytest summary and, if run, the live result. Do not use `PASS` for live provider conformance unless the pinned-provider occurrence actually executed.

- [ ] **Step 6: Commit Task 7**

```bash
git add README.md evals/OPENMANUS-BIND-001.md
git commit -m "docs: record OPENMANUS-BIND-001 boundary proof"
```

---

## Final Verification Before Review

- [ ] Run focused tests:

```bash
pytest -q tests/test_dev_openmanus.py tests/test_contrib_openmanus_ops.py tests/test_dev_membrane.py tests/test_dev_public_api.py
```

- [ ] Run full suite:

```bash
pytest -q
```

- [ ] Confirm no production dependency was added:

```bash
python - <<'PY'
from pathlib import Path
text = Path("pyproject.toml").read_text()
assert "dependencies = []" in text
print("production dependencies remain empty")
PY
```

- [ ] Confirm banned broad provider surfaces are not used by the live shim:

```bash
python - <<'PY'
from pathlib import Path
source = Path("contrib/openmanus/worker.py").read_text()
for banned in ("PythonExecute(", "StrReplaceEditor(", "Bash(", "SandboxManus(", "MCPClients(", "shell=True"):
    assert banned not in source, banned
print("bounded live-shim surface confirmed")
PY
```

- [ ] Confirm the existing membrane/model files were not modified unless a failing test forced a separately documented invariant change:

```bash
git diff main...HEAD -- src/loadout/dev/model.py src/loadout/dev/membrane.py
```

Expected: no diff.

- [ ] Inspect the PR diff for accidental authority language or live-conformance overclaim.

## Self-Review Results

**Spec coverage:** All v0 design requirements are assigned: body-time identity and envelope (Task 1); transport, timeout, env narrowing, result validation, provider ledger (Task 2); membrane/refusal proof (Task 3); schemas/public API (Task 4); bounded provider tools (Task 5); optional OpenManus reasoning-loop shim (Task 6); eval/README/live promotion gate (Task 7).

**Placeholder scan:** No implementation step depends on `TBD`, `TODO`, unspecified error handling, or unnamed interfaces.

**Type consistency:** `OpenManusJsonStdioAdapter.invoke()` remains exactly `EffectIntent -> tuple[str, str | None]`; rich output remains in `OpenManusProviderReceipt`; existing `EffectReceipt` and `Adapter` protocol stay unchanged.

**Critical architecture check:** The live worker uses OpenManus for reasoning and tool selection but does not expose its native broad execution tools. This keeps `available provider machinery != bound LOADOUT capability` executable rather than rhetorical.
