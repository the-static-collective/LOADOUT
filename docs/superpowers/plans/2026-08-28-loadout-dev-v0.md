# LOADOUT.dev/v0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first deterministic executable floor for `LOADOUT.dev/v0`: provider-independent capability compilation, effect fencing, state-bound workflow gates, inert effect intents/receipts, fake adapters, and the complete hostile conformance corpus without live provider credentials.

**Architecture:** Implement LOADOUT.dev as a small Python 3.12 package in LOADOUT. Pure compiler/workflow logic remains separate from effectful adapter invocation; adapters are invoked only through a membrane that checks compiled bindings, exact targets, effect classes, immutable adapter-body identity, current-state preconditions, and owner-local gates. The first runtime uses deterministic fake adapters and keeps Dogram lowering deferred.

**Tech Stack:** Python >=3.12, standard library (`dataclasses`, `enum`, `typing`, `hashlib`, `json`), setuptools, pytest for the test suite. No runtime dependencies.

**Spec:** `docs/specs/2026-08-28-loadout-dev-native-developer-toolset.md`

## Global Constraints

- Preserve the LOADOUT law: **Knowledge may load. Capability may bind. Authority does not silently expand.**
- `LOADOUT.dev/v0` is not a plugin manager, GitHub bot, universal agent runtime, Dogram VM, or semantic authority.
- Provider/product names stay adapter-local; native workflow and compiler semantics use provider-independent capabilities.
- `DISCOVER != invoke`, `SELECT != bind`, `BIND != authorize every operation`, `READY != ADMIT`, `ADMIT != LAND`, and `RECEIPT != authority`.
- Classification follows reachable effects, not provider brand or caller label.
- Read/query computation and arbitrary evaluator execution remain distinct capability/effect classes.
- Dogram receives no ambient GitHub, GitBook, filesystem, shell, network, evaluator, publication, or merge authority in v0.
- Adapter bodies carry `authority: none`; credentials/session grants are not body identity and are not stored by this package.
- Replay/historical adapter selection must be exact-body pinned; no implicit “latest wins.”
- Verification, readiness, and owner admission are state-bound; relevant state drift invalidates stale state-sensitive receipts and gates.
- Review pressure may surface out-of-scope work but must not silently expand the current cut.
- GitBook-shaped publication must cross a proposal/change-request membrane before publication consequence.
- A successful provider call does not mint evidence, truth, publication authority, merge authority, or semantic admission.
- No live provider credentials, network calls, background watchers, provider merge automation, GitBook publication automation, arbitrary Wolfram evaluator execution, dynamic plugin installation, remote adapter download, Cup federation, or full Dogram lowering in v0.
- TDD is mandatory: every production behavior is preceded by a failing test that is run and observed failing for the intended reason.
- Every task ends with a focused green test run and a commit; the final task performs a fresh full-suite verification.

---

## File Structure

Create this runtime surface:

```text
LOADOUT/
├── pyproject.toml
├── loadout/
│   ├── __init__.py
│   └── dev/
│       ├── __init__.py
│       ├── model.py
│       ├── compiler.py
│       ├── adapters.py
│       ├── membrane.py
│       └── workflow.py
├── tests/
│   ├── __init__.py
│   ├── fixtures/
│   │   ├── github_adapter_body.json
│   │   ├── gitbook_adapter_body.json
│   │   ├── wolfram_read_adapter_body.json
│   │   └── wolfram_eval_adapter_body.json
│   ├── test_dev_model.py
│   ├── test_dev_compiler.py
│   ├── test_dev_membrane.py
│   ├── test_dev_workflow_state.py
│   ├── test_dev_workflow_policies.py
│   └── test_dev_public_api.py
└── evals/
    └── LOADOUT-DEV-v0.md
```

Responsibilities:

- `model.py`: immutable vocabulary and transport types only. No provider I/O and no workflow policy logic.
- `compiler.py`: deterministic body selection and capability binding for a bounded developer world.
- `adapters.py`: adapter protocol plus deterministic in-memory fake adapter used by conformance tests.
- `membrane.py`: the only v0 path from an inert `EffectIntent` to adapter invocation.
- `workflow.py`: pure workflow state transitions, freshness invalidation, and named policy constraints.
- `tests/fixtures/*.json`: provider-shaped adapter bodies; data only, no credentials.
- `evals/LOADOUT-DEV-v0.md`: durable mapping from hostile IDs to executable test witnesses.

Do not add a CLI in this plan. The design explicitly permits a CLI only if needed to prove cross-process determinism; the v0 conformance floor can be proved through the Python API and pytest.

---

### Task 1: Bootstrap Package and Immutable Native Model

**Files:**
- Create: `pyproject.toml`
- Create: `loadout/__init__.py`
- Create: `loadout/dev/__init__.py`
- Create: `loadout/dev/model.py`
- Create: `tests/__init__.py`
- Create: `tests/test_dev_model.py`

**Interfaces:**
- Consumes: nothing; this is the executable floor.
- Produces:
  - `Disposition`
  - `EffectClass`
  - `Verb`
  - `EvidenceKind`
  - `RefusalReason`
  - `AdapterBody`
  - `CapabilityRequest`
  - `Binding`
  - `CompileRequest`
  - `CompileReceipt`
  - `EffectIntent`
  - `OwnerGate`
  - `EffectReceipt`
  - `WorkflowEvent`

- [ ] **Step 1: Write the failing model tests**

Create `tests/test_dev_model.py`:

```python
from dataclasses import FrozenInstanceError

import pytest

from loadout.dev.model import (
    AdapterBody,
    EffectClass,
    RefusalReason,
)


def test_adapter_body_requires_exact_sha_bound_body_time_id():
    sha = "a" * 40
    body = AdapterBody(
        adapter_id="github-adapter",
        body_time_id=f"github-adapter@{sha}",
        source_sha=sha,
        capabilities=frozenset({"repo.inspect"}),
    )

    assert body.authority == "none"
    assert body.source_sha == sha


def test_adapter_body_rejects_non_exact_sha():
    with pytest.raises(ValueError, match="40 lowercase hexadecimal"):
        AdapterBody(
            adapter_id="github-adapter",
            body_time_id="github-adapter@abc",
            source_sha="abc",
            capabilities=frozenset({"repo.inspect"}),
        )


def test_adapter_body_rejects_body_time_mismatch():
    sha = "b" * 40
    with pytest.raises(ValueError, match="body_time_id"):
        AdapterBody(
            adapter_id="github-adapter",
            body_time_id=f"other@{sha}",
            source_sha=sha,
            capabilities=frozenset({"repo.inspect"}),
        )


def test_adapter_body_is_immutable():
    sha = "c" * 40
    body = AdapterBody(
        adapter_id="gitbook-adapter",
        body_time_id=f"gitbook-adapter@{sha}",
        source_sha=sha,
        capabilities=frozenset({"docs.inspect"}),
    )

    with pytest.raises(FrozenInstanceError):
        body.authority = "merge"  # type: ignore[misc]


def test_effect_classes_keep_inspection_and_evaluation_distinct():
    assert EffectClass.OBSERVE != EffectClass.REMOTE_MUTATE
    assert EffectClass.LOCAL_COMPUTE != EffectClass.LOCAL_MUTATE


def test_refusal_reason_names_are_stable():
    assert RefusalReason.BODY_PIN_REQUIRED.value == "BODY_PIN_REQUIRED"
    assert RefusalReason.EFFECT_OUTSIDE_FENCE.value == "EFFECT_OUTSIDE_FENCE"
    assert RefusalReason.OWNER_GATE_STALE.value == "OWNER_GATE_STALE"
```

- [ ] **Step 2: Run the model tests and verify RED**

Run:

```bash
python -m pytest tests/test_dev_model.py -q
```

Expected: collection/import failure because `loadout.dev.model` does not exist yet. This is the correct RED witness for the package floor.

- [ ] **Step 3: Add packaging metadata**

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "loadout"
version = "0.0.0"
description = "Bounded capability and effect compiler for Static Collective worlds"
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8"]
```

Create `loadout/__init__.py` and `loadout/dev/__init__.py` as empty package markers for now. Create `tests/__init__.py` as an empty file.

- [ ] **Step 4: Implement the minimal immutable model**

Create `loadout/dev/model.py` with the following exact public names and field shapes:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
import re


_SHA40 = re.compile(r"^[0-9a-f]{40}$")


class Disposition(StrEnum):
    COMPILED = "COMPILED"
    REFUSED = "REFUSED"
    CAPABILITY_GAP = "CAPABILITY_GAP"
    OWNER_GATE = "OWNER_GATE"


class EffectClass(StrEnum):
    OBSERVE = "OBSERVE"
    REPRESENT = "REPRESENT"
    LOCAL_COMPUTE = "LOCAL_COMPUTE"
    LOCAL_MUTATE = "LOCAL_MUTATE"
    REMOTE_PROPOSE = "REMOTE_PROPOSE"
    REMOTE_MUTATE = "REMOTE_MUTATE"
    PUBLISH = "PUBLISH"
    LAND = "LAND"


class Verb(StrEnum):
    CUT = "CUT"
    CONTRACT = "CONTRACT"
    BIND = "BIND"
    FENCE = "FENCE"
    PROBE = "PROBE"
    WITNESS = "WITNESS"
    MUTATE = "MUTATE"
    VERIFY = "VERIFY"
    PROPOSE = "PROPOSE"
    PRESS = "PRESS"
    REPAIR = "REPAIR"
    READY = "READY"
    ADMIT = "ADMIT"
    LAND = "LAND"
    RECEIPT = "RECEIPT"
    REFUSE = "REFUSE"


class EvidenceKind(StrEnum):
    DESIGN_APPROVAL = "DESIGN_APPROVAL"
    TEST_RED = "TEST_RED"
    TEST_GREEN = "TEST_GREEN"
    ROOT_CAUSE_HYPOTHESIS = "ROOT_CAUSE_HYPOTHESIS"
    ROOT_CAUSE_PROBE = "ROOT_CAUSE_PROBE"
    REVIEW_FINDING = "REVIEW_FINDING"
    CHECK = "CHECK"


class RefusalReason(StrEnum):
    CAPABILITY_UNAVAILABLE = "CAPABILITY_UNAVAILABLE"
    CAPABILITY_NOT_BOUND = "CAPABILITY_NOT_BOUND"
    BODY_AMBIGUOUS = "BODY_AMBIGUOUS"
    BODY_PIN_REQUIRED = "BODY_PIN_REQUIRED"
    BODY_NOT_ELIGIBLE = "BODY_NOT_ELIGIBLE"
    EFFECT_OUTSIDE_FENCE = "EFFECT_OUTSIDE_FENCE"
    TARGET_OUTSIDE_CUT = "TARGET_OUTSIDE_CUT"
    STATE_STALE = "STATE_STALE"
    VERIFICATION_STALE = "VERIFICATION_STALE"
    WITNESS_REQUIRED = "WITNESS_REQUIRED"
    DESIGN_GATE_REQUIRED = "DESIGN_GATE_REQUIRED"
    ROOT_CAUSE_REQUIRED = "ROOT_CAUSE_REQUIRED"
    REVIEW_SCOPE_EXCEEDED = "REVIEW_SCOPE_EXCEEDED"
    PROPOSAL_REQUIRED = "PROPOSAL_REQUIRED"
    OWNER_GATE_REQUIRED = "OWNER_GATE_REQUIRED"
    OWNER_GATE_STALE = "OWNER_GATE_STALE"
    PROVIDER_REFUSED = "PROVIDER_REFUSED"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"


@dataclass(frozen=True)
class AdapterBody:
    adapter_id: str
    body_time_id: str
    source_sha: str
    capabilities: frozenset[str]
    authority: str = "none"

    def __post_init__(self) -> None:
        if not _SHA40.fullmatch(self.source_sha):
            raise ValueError("source_sha must be 40 lowercase hexadecimal characters")
        expected = f"{self.adapter_id}@{self.source_sha}"
        if self.body_time_id != expected:
            raise ValueError(f"body_time_id must equal {expected}")
        if self.authority != "none":
            raise ValueError("adapter bodies must carry authority: none")


@dataclass(frozen=True)
class CapabilityRequest:
    capability: str
    effect: EffectClass
    target: str
    body_time_id: str | None = None
    replay: bool = False


@dataclass(frozen=True)
class Binding:
    capability: str
    effect: EffectClass
    target: str
    body_time_id: str


@dataclass(frozen=True)
class CompileRequest:
    task_id: str
    task_text: str
    cut_targets: frozenset[str]
    requested_capabilities: tuple[CapabilityRequest, ...]
    available_bodies: tuple[AdapterBody, ...]


@dataclass(frozen=True)
class CompileReceipt:
    disposition: Disposition
    task_id: str
    bindings: tuple[Binding, ...] = ()
    reasons: tuple[RefusalReason, ...] = ()


@dataclass(frozen=True)
class EffectIntent:
    capability: str
    effect: EffectClass
    target: str
    body_time_id: str
    precondition_state: str
    parameters_digest: str


@dataclass(frozen=True)
class OwnerGate:
    target: str
    effect: EffectClass
    state_id: str
    approval_ref: str


@dataclass(frozen=True)
class EffectReceipt:
    body_time_id: str
    capability: str
    effect: EffectClass
    target: str
    precondition_state: str
    provider_disposition: str
    observed_post_state: str | None
    semantic_authority: bool = False
    reason: RefusalReason | None = None


@dataclass(frozen=True)
class WorkflowEvent:
    verb: Verb
    state_id: str
    evidence: EvidenceKind | None = None
    scope: str | None = None
    effect: EffectClass | None = None
    note: str = ""
```

Remove the unused `field` import if it is not needed after implementation.

- [ ] **Step 5: Run the model tests and verify GREEN**

Run:

```bash
python -m pytest tests/test_dev_model.py -q
```

Expected: all tests pass with no warnings.

- [ ] **Step 6: Run a focused package import check**

Run:

```bash
python -c "from loadout.dev.model import AdapterBody, EffectClass; print(EffectClass.OBSERVE)"
```

Expected stdout:

```text
OBSERVE
```

- [ ] **Step 7: Commit Task 1**

```bash
git add pyproject.toml loadout tests/test_dev_model.py tests/__init__.py
git commit -m "feat: add LOADOUT.dev native model"
```

---

### Task 2: Deterministic Developer-World Compiler and Exact Body Selection

**Files:**
- Create: `loadout/dev/compiler.py`
- Create: `tests/test_dev_compiler.py`
- Create: `tests/fixtures/github_adapter_body.json`
- Create: `tests/fixtures/gitbook_adapter_body.json`
- Create: `tests/fixtures/wolfram_read_adapter_body.json`
- Create: `tests/fixtures/wolfram_eval_adapter_body.json`

**Interfaces:**
- Consumes: `AdapterBody`, `Binding`, `CapabilityRequest`, `CompileRequest`, `CompileReceipt`, `Disposition`, `RefusalReason` from `loadout.dev.model`.
- Produces: `compile_world(request: CompileRequest) -> CompileReceipt`.
- Determinism rule: body candidates are compared by exact `body_time_id`; ambiguity refuses rather than selecting “latest.”

- [ ] **Step 1: Add provider-shaped body fixtures**

Create these four JSON files exactly; hashes are synthetic immutable conformance identities, not claims about live provider code.

`tests/fixtures/github_adapter_body.json`:

```json
{
  "adapter_id": "github-adapter",
  "body_time_id": "github-adapter@1111111111111111111111111111111111111111",
  "source_sha": "1111111111111111111111111111111111111111",
  "capabilities": ["repo.inspect", "repo.file.write", "proposal.create", "landing.request"]
}
```

`tests/fixtures/gitbook_adapter_body.json`:

```json
{
  "adapter_id": "gitbook-adapter",
  "body_time_id": "gitbook-adapter@2222222222222222222222222222222222222222",
  "source_sha": "2222222222222222222222222222222222222222",
  "capabilities": ["docs.inspect", "docs.propose", "docs.publish"]
}
```

`tests/fixtures/wolfram_read_adapter_body.json`:

```json
{
  "adapter_id": "wolfram-read-adapter",
  "body_time_id": "wolfram-read-adapter@3333333333333333333333333333333333333333",
  "source_sha": "3333333333333333333333333333333333333333",
  "capabilities": ["math.inspect", "math.compute"]
}
```

`tests/fixtures/wolfram_eval_adapter_body.json`:

```json
{
  "adapter_id": "wolfram-eval-adapter",
  "body_time_id": "wolfram-eval-adapter@4444444444444444444444444444444444444444",
  "source_sha": "4444444444444444444444444444444444444444",
  "capabilities": ["math.evaluate"]
}
```

- [ ] **Step 2: Write failing compiler tests for `MENTION-BIND-001`, capability gaps, ambiguity, and `BODY-PIN-001`**

Create `tests/test_dev_compiler.py`:

```python
import json
from pathlib import Path

from loadout.dev.compiler import compile_world
from loadout.dev.model import (
    AdapterBody,
    CapabilityRequest,
    CompileRequest,
    Disposition,
    EffectClass,
    RefusalReason,
)


FIXTURES = Path(__file__).parent / "fixtures"


def load_body(name: str) -> AdapterBody:
    data = json.loads((FIXTURES / name).read_text())
    return AdapterBody(
        adapter_id=data["adapter_id"],
        body_time_id=data["body_time_id"],
        source_sha=data["source_sha"],
        capabilities=frozenset(data["capabilities"]),
    )


def test_mention_bind_001_provider_mention_does_not_bind_capability():
    github = load_body("github_adapter_body.json")
    receipt = compile_world(
        CompileRequest(
            task_id="MENTION-BIND-001",
            task_text="Review this and mention GitHub in the explanation.",
            cut_targets=frozenset({"repo:LOADOUT"}),
            requested_capabilities=(),
            available_bodies=(github,),
        )
    )

    assert receipt.disposition == Disposition.COMPILED
    assert receipt.bindings == ()


def test_missing_capability_returns_capability_gap():
    github = load_body("github_adapter_body.json")
    receipt = compile_world(
        CompileRequest(
            task_id="missing-cap",
            task_text="Compute symbolically.",
            cut_targets=frozenset({"calc:1"}),
            requested_capabilities=(
                CapabilityRequest("math.compute", EffectClass.LOCAL_COMPUTE, "calc:1"),
            ),
            available_bodies=(github,),
        )
    )

    assert receipt.disposition == Disposition.CAPABILITY_GAP
    assert receipt.reasons == (RefusalReason.CAPABILITY_UNAVAILABLE,)


def test_unpinned_ambiguous_body_refuses_instead_of_latest_wins():
    body_a = AdapterBody(
        "github-adapter",
        "github-adapter@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        frozenset({"repo.inspect"}),
    )
    body_b = AdapterBody(
        "github-adapter",
        "github-adapter@bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        frozenset({"repo.inspect"}),
    )
    receipt = compile_world(
        CompileRequest(
            task_id="ambiguous",
            task_text="Inspect the repo.",
            cut_targets=frozenset({"repo:LOADOUT"}),
            requested_capabilities=(
                CapabilityRequest("repo.inspect", EffectClass.OBSERVE, "repo:LOADOUT"),
            ),
            available_bodies=(body_b, body_a),
        )
    )

    assert receipt.disposition == Disposition.REFUSED
    assert receipt.reasons == (RefusalReason.BODY_AMBIGUOUS,)


def test_body_pin_001_replay_requires_exact_body_pin():
    github = load_body("github_adapter_body.json")
    receipt = compile_world(
        CompileRequest(
            task_id="BODY-PIN-001",
            task_text="Replay prior repo inspection.",
            cut_targets=frozenset({"repo:LOADOUT"}),
            requested_capabilities=(
                CapabilityRequest(
                    "repo.inspect",
                    EffectClass.OBSERVE,
                    "repo:LOADOUT",
                    replay=True,
                ),
            ),
            available_bodies=(github,),
        )
    )

    assert receipt.disposition == Disposition.REFUSED
    assert receipt.reasons == (RefusalReason.BODY_PIN_REQUIRED,)


def test_exact_body_pin_compiles_deterministically():
    github = load_body("github_adapter_body.json")
    receipt = compile_world(
        CompileRequest(
            task_id="exact-pin",
            task_text="Inspect the repo with the pinned body.",
            cut_targets=frozenset({"repo:LOADOUT"}),
            requested_capabilities=(
                CapabilityRequest(
                    "repo.inspect",
                    EffectClass.OBSERVE,
                    "repo:LOADOUT",
                    body_time_id=github.body_time_id,
                    replay=True,
                ),
            ),
            available_bodies=(github,),
        )
    )

    assert receipt.disposition == Disposition.COMPILED
    assert receipt.bindings[0].body_time_id == github.body_time_id
```

- [ ] **Step 3: Run compiler tests and verify RED**

Run:

```bash
python -m pytest tests/test_dev_compiler.py -q
```

Expected: import failure for missing `loadout.dev.compiler`.

- [ ] **Step 4: Implement minimal deterministic compilation**

Create `loadout/dev/compiler.py`:

```python
from __future__ import annotations

from loadout.dev.model import (
    Binding,
    CompileReceipt,
    CompileRequest,
    Disposition,
    RefusalReason,
)


def compile_world(request: CompileRequest) -> CompileReceipt:
    bindings: list[Binding] = []

    for requested in request.requested_capabilities:
        if requested.target not in request.cut_targets:
            return CompileReceipt(
                disposition=Disposition.REFUSED,
                task_id=request.task_id,
                reasons=(RefusalReason.TARGET_OUTSIDE_CUT,),
            )

        if requested.replay and requested.body_time_id is None:
            return CompileReceipt(
                disposition=Disposition.REFUSED,
                task_id=request.task_id,
                reasons=(RefusalReason.BODY_PIN_REQUIRED,),
            )

        candidates = [
            body
            for body in request.available_bodies
            if requested.capability in body.capabilities
            and (
                requested.body_time_id is None
                or body.body_time_id == requested.body_time_id
            )
        ]

        if not candidates:
            return CompileReceipt(
                disposition=Disposition.CAPABILITY_GAP,
                task_id=request.task_id,
                reasons=(RefusalReason.CAPABILITY_UNAVAILABLE,),
            )

        if len(candidates) != 1:
            return CompileReceipt(
                disposition=Disposition.REFUSED,
                task_id=request.task_id,
                reasons=(RefusalReason.BODY_AMBIGUOUS,),
            )

        body = candidates[0]
        bindings.append(
            Binding(
                capability=requested.capability,
                effect=requested.effect,
                target=requested.target,
                body_time_id=body.body_time_id,
            )
        )

    return CompileReceipt(
        disposition=Disposition.COMPILED,
        task_id=request.task_id,
        bindings=tuple(bindings),
    )
```

Do not inspect `task_text` for provider names. The requested capability set is authoritative for binding; this is the executable content of `MENTION-BIND-001`.

- [ ] **Step 5: Run compiler tests and verify GREEN**

```bash
python -m pytest tests/test_dev_compiler.py -q
```

Expected: all compiler tests pass.

- [ ] **Step 6: Run model + compiler tests together**

```bash
python -m pytest tests/test_dev_model.py tests/test_dev_compiler.py -q
```

Expected: all pass.

- [ ] **Step 7: Commit Task 2**

```bash
git add loadout/dev/compiler.py tests/test_dev_compiler.py tests/fixtures
git commit -m "feat: compile bounded developer capabilities"
```

---

### Task 3: Effect Membrane, Fake Adapter, and Capability/Effect Non-Laundering

**Files:**
- Create: `loadout/dev/adapters.py`
- Create: `loadout/dev/membrane.py`
- Create: `tests/test_dev_membrane.py`

**Interfaces:**
- Consumes: `CompileReceipt`, `Binding`, `EffectIntent`, `EffectReceipt`, `OwnerGate`, `EffectClass`, `RefusalReason`.
- Produces:
  - `Adapter` protocol with `body_time_id: str` and `invoke(intent: EffectIntent) -> tuple[str, str | None]`.
  - `FakeAdapter(body_time_id: str, outcomes: dict[str, tuple[str, str | None]])`.
  - `invoke_effect(compiled, intent, adapters, current_state, owner_gate=None) -> EffectReceipt`.
- `PUBLISH` and `LAND` require a state-bound `OwnerGate` in v0.
- The membrane matches effect classes exactly. No rank/escalation lattice is introduced in v0.

- [ ] **Step 1: Write failing membrane tests for `EFFECT-FENCE-001`, `WOLFRAM-FENCE-001`, target cuts, owner gates, and `RESULT-LAUNDER-001`**

Create `tests/test_dev_membrane.py`:

```python
from loadout.dev.adapters import FakeAdapter
from loadout.dev.compiler import compile_world
from loadout.dev.membrane import invoke_effect
from loadout.dev.model import (
    AdapterBody,
    CapabilityRequest,
    CompileRequest,
    Disposition,
    EffectClass,
    EffectIntent,
    OwnerGate,
    RefusalReason,
)


SHA = "5" * 40
BODY_ID = f"fixture-adapter@{SHA}"
BODY = AdapterBody(
    adapter_id="fixture-adapter",
    body_time_id=BODY_ID,
    source_sha=SHA,
    capabilities=frozenset({"repo.inspect", "repo.file.write", "math.inspect", "landing.request"}),
)


def compiled_for(capability: str, effect: EffectClass, target: str):
    return compile_world(
        CompileRequest(
            task_id="membrane",
            task_text="bounded effect",
            cut_targets=frozenset({target}),
            requested_capabilities=(
                CapabilityRequest(capability, effect, target, body_time_id=BODY_ID),
            ),
            available_bodies=(BODY,),
        )
    )


def test_effect_fence_001_observe_binding_cannot_launder_write():
    compiled = compiled_for("repo.inspect", EffectClass.OBSERVE, "repo:LOADOUT")
    intent = EffectIntent(
        capability="repo.inspect",
        effect=EffectClass.REMOTE_MUTATE,
        target="repo:LOADOUT",
        body_time_id=BODY_ID,
        precondition_state="H0",
        parameters_digest="p0",
    )
    adapter = FakeAdapter(BODY_ID, {"repo.inspect": ("OK", "H0")})

    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="H0")

    assert receipt.reason == RefusalReason.EFFECT_OUTSIDE_FENCE
    assert adapter.invocations == []


def test_target_outside_compiled_binding_refuses_before_adapter():
    compiled = compiled_for("repo.inspect", EffectClass.OBSERVE, "repo:LOADOUT")
    intent = EffectIntent(
        capability="repo.inspect",
        effect=EffectClass.OBSERVE,
        target="repo:OTHER",
        body_time_id=BODY_ID,
        precondition_state="H0",
        parameters_digest="p0",
    )
    adapter = FakeAdapter(BODY_ID, {"repo.inspect": ("OK", "H0")})

    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="H0")

    assert receipt.reason == RefusalReason.TARGET_OUTSIDE_CUT
    assert adapter.invocations == []


def test_wolfram_fence_001_math_inspect_does_not_authorize_evaluate():
    compiled = compiled_for("math.inspect", EffectClass.OBSERVE, "calc:1")
    intent = EffectIntent(
        capability="math.evaluate",
        effect=EffectClass.LOCAL_MUTATE,
        target="calc:1",
        body_time_id=BODY_ID,
        precondition_state="C0",
        parameters_digest="expr",
    )
    adapter = FakeAdapter(BODY_ID, {"math.evaluate": ("OK", "C1")})

    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="C0")

    assert receipt.reason == RefusalReason.CAPABILITY_NOT_BOUND
    assert adapter.invocations == []


def test_land_requires_owner_gate_bound_to_current_state():
    compiled = compiled_for("landing.request", EffectClass.LAND, "pr:2")
    intent = EffectIntent(
        capability="landing.request",
        effect=EffectClass.LAND,
        target="pr:2",
        body_time_id=BODY_ID,
        precondition_state="H7",
        parameters_digest="merge",
    )
    adapter = FakeAdapter(BODY_ID, {"landing.request": ("MERGED", "merged:H7")})

    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="H7")

    assert receipt.reason == RefusalReason.OWNER_GATE_REQUIRED
    assert adapter.invocations == []


def test_stale_owner_gate_refuses_land():
    compiled = compiled_for("landing.request", EffectClass.LAND, "pr:2")
    intent = EffectIntent(
        capability="landing.request",
        effect=EffectClass.LAND,
        target="pr:2",
        body_time_id=BODY_ID,
        precondition_state="H8",
        parameters_digest="merge",
    )
    gate = OwnerGate("pr:2", EffectClass.LAND, "H7", "approval:1")
    adapter = FakeAdapter(BODY_ID, {"landing.request": ("MERGED", "merged:H8")})

    receipt = invoke_effect(
        compiled,
        intent,
        {BODY_ID: adapter},
        current_state="H8",
        owner_gate=gate,
    )

    assert receipt.reason == RefusalReason.OWNER_GATE_STALE
    assert adapter.invocations == []


def test_result_launder_001_success_receipt_never_mints_semantic_authority():
    compiled = compiled_for("repo.inspect", EffectClass.OBSERVE, "repo:LOADOUT")
    intent = EffectIntent(
        capability="repo.inspect",
        effect=EffectClass.OBSERVE,
        target="repo:LOADOUT",
        body_time_id=BODY_ID,
        precondition_state="H0",
        parameters_digest="read",
    )
    adapter = FakeAdapter(BODY_ID, {"repo.inspect": ("OK", "H0")})

    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="H0")

    assert receipt.provider_disposition == "OK"
    assert receipt.semantic_authority is False
    assert receipt.reason is None
```

- [ ] **Step 2: Run membrane tests and verify RED**

```bash
python -m pytest tests/test_dev_membrane.py -q
```

Expected: import failure because `adapters.py` and `membrane.py` do not exist.

- [ ] **Step 3: Implement deterministic fake adapter**

Create `loadout/dev/adapters.py`:

```python
from __future__ import annotations

from typing import Protocol

from loadout.dev.model import EffectIntent


class Adapter(Protocol):
    body_time_id: str

    def invoke(self, intent: EffectIntent) -> tuple[str, str | None]: ...


class FakeAdapter:
    def __init__(
        self,
        body_time_id: str,
        outcomes: dict[str, tuple[str, str | None]],
    ) -> None:
        self.body_time_id = body_time_id
        self.outcomes = dict(outcomes)
        self.invocations: list[EffectIntent] = []

    def invoke(self, intent: EffectIntent) -> tuple[str, str | None]:
        self.invocations.append(intent)
        return self.outcomes[intent.capability]
```

The fake adapter has no network behavior, credentials, implicit authority, or policy decisions.

- [ ] **Step 4: Implement the membrane checks in fail-closed order**

Create `loadout/dev/membrane.py`:

```python
from __future__ import annotations

from collections.abc import Mapping

from loadout.dev.adapters import Adapter
from loadout.dev.model import (
    CompileReceipt,
    Disposition,
    EffectClass,
    EffectIntent,
    EffectReceipt,
    OwnerGate,
    RefusalReason,
)


_OWNER_GATED = frozenset({EffectClass.PUBLISH, EffectClass.LAND})


def _refuse(intent: EffectIntent, reason: RefusalReason) -> EffectReceipt:
    return EffectReceipt(
        body_time_id=intent.body_time_id,
        capability=intent.capability,
        effect=intent.effect,
        target=intent.target,
        precondition_state=intent.precondition_state,
        provider_disposition="REFUSED",
        observed_post_state=None,
        semantic_authority=False,
        reason=reason,
    )


def invoke_effect(
    compiled: CompileReceipt,
    intent: EffectIntent,
    adapters: Mapping[str, Adapter],
    *,
    current_state: str,
    owner_gate: OwnerGate | None = None,
) -> EffectReceipt:
    if compiled.disposition != Disposition.COMPILED:
        return _refuse(intent, RefusalReason.CAPABILITY_NOT_BOUND)

    same_capability = [b for b in compiled.bindings if b.capability == intent.capability]
    if not same_capability:
        return _refuse(intent, RefusalReason.CAPABILITY_NOT_BOUND)

    same_target = [b for b in same_capability if b.target == intent.target]
    if not same_target:
        return _refuse(intent, RefusalReason.TARGET_OUTSIDE_CUT)

    exact = [
        b
        for b in same_target
        if b.effect == intent.effect and b.body_time_id == intent.body_time_id
    ]
    if not exact:
        return _refuse(intent, RefusalReason.EFFECT_OUTSIDE_FENCE)

    if intent.precondition_state != current_state:
        return _refuse(intent, RefusalReason.STATE_STALE)

    if intent.effect in _OWNER_GATED:
        if owner_gate is None:
            return _refuse(intent, RefusalReason.OWNER_GATE_REQUIRED)
        if (
            owner_gate.target != intent.target
            or owner_gate.effect != intent.effect
            or owner_gate.state_id != current_state
        ):
            return _refuse(intent, RefusalReason.OWNER_GATE_STALE)

    adapter = adapters.get(intent.body_time_id)
    if adapter is None or adapter.body_time_id != intent.body_time_id:
        return _refuse(intent, RefusalReason.BODY_NOT_ELIGIBLE)

    disposition, post_state = adapter.invoke(intent)
    return EffectReceipt(
        body_time_id=intent.body_time_id,
        capability=intent.capability,
        effect=intent.effect,
        target=intent.target,
        precondition_state=intent.precondition_state,
        provider_disposition=disposition,
        observed_post_state=post_state,
        semantic_authority=False,
    )
```

Do not catch arbitrary adapter exceptions in this task. A provider error model belongs in a later bounded task only when a real adapter exists; wrapping everything now would erase useful failure information and violate YAGNI.

- [ ] **Step 5: Run membrane tests and verify GREEN**

```bash
python -m pytest tests/test_dev_membrane.py -q
```

Expected: all tests pass.

- [ ] **Step 6: Run compiler + membrane tests together**

```bash
python -m pytest tests/test_dev_compiler.py tests/test_dev_membrane.py -q
```

Expected: all pass.

- [ ] **Step 7: Commit Task 3**

```bash
git add loadout/dev/adapters.py loadout/dev/membrane.py tests/test_dev_membrane.py
git commit -m "feat: fence developer effects behind membrane"
```

---

### Task 4: Pure Workflow State, Fresh Verification, READY/ADMIT/LAND State Binding

**Files:**
- Create: `loadout/dev/workflow.py`
- Create: `tests/test_dev_workflow_state.py`

**Interfaces:**
- Consumes: `WorkflowEvent`, `Verb`, `EffectClass`, `EvidenceKind`, `RefusalReason`.
- Produces:
  - `WorkflowPolicy`
  - `WorkflowState`
  - `TransitionResult`
  - `start_workflow(policy, current_state_id, scope, design_admitted=False) -> WorkflowState`
  - `transition(state, event) -> TransitionResult`
- State drift rule: accepted `MUTATE` or `REPAIR` to a new state clears `verified_state_id`, `ready_state_id`, and `admitted_state_id`.

- [ ] **Step 1: Write failing freshness and consequence-gate tests for `VERIFY-FRESH-001` and `HEAD-DRIFT-001`**

Create `tests/test_dev_workflow_state.py`:

```python
from loadout.dev.model import EffectClass, RefusalReason, Verb, WorkflowEvent
from loadout.dev.workflow import DEV_LAND, start_workflow, transition


def apply(state, event):
    result = transition(state, event)
    assert result.reason is None
    return result.state


def test_verify_fresh_001_old_state_verification_cannot_prove_new_state():
    state = start_workflow(DEV_LAND, current_state_id="H0", scope="pr:2")
    state = apply(state, WorkflowEvent(Verb.PROPOSE, "H0", scope="pr:2"))
    state = apply(state, WorkflowEvent(Verb.VERIFY, "H0", scope="pr:2"))
    state = apply(
        state,
        WorkflowEvent(Verb.MUTATE, "H1", scope="pr:2", effect=EffectClass.REMOTE_PROPOSE),
    )

    assert state.current_state_id == "H1"
    assert state.verified_state_id is None
    assert state.ready_state_id is None
    assert state.admitted_state_id is None


def test_ready_requires_fresh_verification_of_current_state():
    state = start_workflow(DEV_LAND, current_state_id="H0", scope="pr:2")
    state = apply(state, WorkflowEvent(Verb.PROPOSE, "H0", scope="pr:2"))
    result = transition(state, WorkflowEvent(Verb.READY, "H0", scope="pr:2"))

    assert result.reason == RefusalReason.VERIFICATION_STALE


def test_head_drift_001_invalidates_ready_and_admission():
    state = start_workflow(DEV_LAND, current_state_id="H0", scope="pr:2")
    state = apply(state, WorkflowEvent(Verb.PROPOSE, "H0", scope="pr:2"))
    state = apply(state, WorkflowEvent(Verb.VERIFY, "H0", scope="pr:2"))
    state = apply(state, WorkflowEvent(Verb.READY, "H0", scope="pr:2"))
    state = apply(state, WorkflowEvent(Verb.ADMIT, "H0", scope="pr:2"))
    state = apply(
        state,
        WorkflowEvent(Verb.MUTATE, "H1", scope="pr:2", effect=EffectClass.REMOTE_PROPOSE),
    )

    result = transition(state, WorkflowEvent(Verb.LAND, "H1", scope="pr:2", effect=EffectClass.LAND))

    assert result.reason == RefusalReason.OWNER_GATE_STALE


def test_land_accepts_only_exact_current_admitted_state():
    state = start_workflow(DEV_LAND, current_state_id="H7", scope="pr:2")
    state = apply(state, WorkflowEvent(Verb.PROPOSE, "H7", scope="pr:2"))
    state = apply(state, WorkflowEvent(Verb.VERIFY, "H7", scope="pr:2"))
    state = apply(state, WorkflowEvent(Verb.READY, "H7", scope="pr:2"))
    state = apply(state, WorkflowEvent(Verb.ADMIT, "H7", scope="pr:2"))

    result = transition(state, WorkflowEvent(Verb.LAND, "H7", scope="pr:2", effect=EffectClass.LAND))

    assert result.reason is None
    assert result.state.events[-1].verb == Verb.LAND
```

- [ ] **Step 2: Run workflow-state tests and verify RED**

```bash
python -m pytest tests/test_dev_workflow_state.py -q
```

Expected: import failure for missing `loadout.dev.workflow`.

- [ ] **Step 3: Implement the workflow state types and baseline landing policy**

Create `loadout/dev/workflow.py` with these definitions:

```python
from __future__ import annotations

from dataclasses import dataclass, replace

from loadout.dev.model import EvidenceKind, RefusalReason, Verb, WorkflowEvent


@dataclass(frozen=True)
class WorkflowPolicy:
    name: str
    require_design_admission_before_mutate: bool = False
    require_red_before_mutate: bool = False
    require_root_cause_before_repair: bool = False
    lock_repair_scope: bool = False
    require_proposal_before_publish: bool = False


@dataclass(frozen=True)
class WorkflowState:
    policy: WorkflowPolicy
    current_state_id: str
    scope: str
    design_admitted: bool
    verified_state_id: str | None = None
    proposal_state_id: str | None = None
    ready_state_id: str | None = None
    admitted_state_id: str | None = None
    red_witnessed: bool = False
    root_cause_hypothesis: bool = False
    root_cause_probed: bool = False
    events: tuple[WorkflowEvent, ...] = ()


@dataclass(frozen=True)
class TransitionResult:
    state: WorkflowState
    reason: RefusalReason | None = None


DEV_LAND = WorkflowPolicy(name="dev.land@0")


def start_workflow(
    policy: WorkflowPolicy,
    *,
    current_state_id: str,
    scope: str,
    design_admitted: bool = False,
) -> WorkflowState:
    return WorkflowState(
        policy=policy,
        current_state_id=current_state_id,
        scope=scope,
        design_admitted=design_admitted,
    )


def _refuse(state: WorkflowState, reason: RefusalReason) -> TransitionResult:
    return TransitionResult(state=state, reason=reason)
```

- [ ] **Step 4: Implement only the baseline state-sensitive transitions needed by these tests**

Continue `workflow.py`:

```python
def transition(state: WorkflowState, event: WorkflowEvent) -> TransitionResult:
    if event.scope is not None and event.scope != state.scope and event.verb != Verb.PRESS:
        return _refuse(state, RefusalReason.REVIEW_SCOPE_EXCEEDED)

    if event.verb == Verb.PROPOSE:
        next_state = replace(
            state,
            proposal_state_id=state.current_state_id,
            events=state.events + (event,),
        )
        return TransitionResult(next_state)

    if event.verb == Verb.VERIFY:
        if event.state_id != state.current_state_id:
            return _refuse(state, RefusalReason.STATE_STALE)
        next_state = replace(
            state,
            verified_state_id=event.state_id,
            events=state.events + (event,),
        )
        return TransitionResult(next_state)

    if event.verb == Verb.READY:
        if event.state_id != state.current_state_id or state.verified_state_id != event.state_id:
            return _refuse(state, RefusalReason.VERIFICATION_STALE)
        next_state = replace(
            state,
            ready_state_id=event.state_id,
            events=state.events + (event,),
        )
        return TransitionResult(next_state)

    if event.verb == Verb.ADMIT:
        if event.state_id != state.current_state_id or state.ready_state_id != event.state_id:
            return _refuse(state, RefusalReason.OWNER_GATE_STALE)
        next_state = replace(
            state,
            admitted_state_id=event.state_id,
            events=state.events + (event,),
        )
        return TransitionResult(next_state)

    if event.verb in {Verb.MUTATE, Verb.REPAIR}:
        next_state = replace(
            state,
            current_state_id=event.state_id,
            verified_state_id=None,
            ready_state_id=None,
            admitted_state_id=None,
            events=state.events + (event,),
        )
        return TransitionResult(next_state)

    if event.verb == Verb.LAND:
        if event.state_id != state.current_state_id or state.admitted_state_id != event.state_id:
            return _refuse(state, RefusalReason.OWNER_GATE_STALE)
        return TransitionResult(replace(state, events=state.events + (event,)))

    return TransitionResult(replace(state, events=state.events + (event,)))
```

This is intentionally not the final policy logic. Task 5 adds the policy-specific gates only after this state/freshness floor is green.

- [ ] **Step 5: Run workflow-state tests and verify GREEN**

```bash
python -m pytest tests/test_dev_workflow_state.py -q
```

Expected: all pass.

- [ ] **Step 6: Run all tests accumulated so far**

```bash
python -m pytest tests/test_dev_model.py tests/test_dev_compiler.py tests/test_dev_membrane.py tests/test_dev_workflow_state.py -q
```

Expected: all pass.

- [ ] **Step 7: Commit Task 4**

```bash
git add loadout/dev/workflow.py tests/test_dev_workflow_state.py
git commit -m "feat: bind workflow gates to exact state"
```

---

### Task 5: Native Workflow Policy Gates and Scope Preservation

**Files:**
- Modify: `loadout/dev/workflow.py`
- Create: `tests/test_dev_workflow_policies.py`

**Interfaces:**
- Consumes: Task 4 workflow state machine.
- Produces named policies:
  - `DEV_IMPLEMENT = WorkflowPolicy(name="dev.implement@0", require_design_admission_before_mutate=True, require_red_before_mutate=True)`
  - `DEV_DEBUG = WorkflowPolicy(name="dev.debug@0", require_root_cause_before_repair=True)`
  - `DEV_REVIEW = WorkflowPolicy(name="dev.review@0", lock_repair_scope=True)`
  - `DEV_DOCS = WorkflowPolicy(name="dev.docs@0", require_proposal_before_publish=True)`
- Policy checks occur before generic mutation/repair/land acceptance.

- [ ] **Step 1: Write failing hostile policy tests for `DESIGN-GATE-001`, `RED-FIRST-001`, `ROOT-CAUSE-001`, `REVIEW-SCOPE-001`, and `DOC-PUBLISH-001`**

Create `tests/test_dev_workflow_policies.py`:

```python
from loadout.dev.model import (
    EffectClass,
    EvidenceKind,
    RefusalReason,
    Verb,
    WorkflowEvent,
)
from loadout.dev.workflow import (
    DEV_DEBUG,
    DEV_DOCS,
    DEV_IMPLEMENT,
    DEV_REVIEW,
    start_workflow,
    transition,
)


def accept(state, event):
    result = transition(state, event)
    assert result.reason is None
    return result.state


def test_design_gate_001_implementation_mutation_requires_design_admission():
    state = start_workflow(DEV_IMPLEMENT, current_state_id="W0", scope="repo:LOADOUT")
    result = transition(
        state,
        WorkflowEvent(Verb.MUTATE, "W1", scope="repo:LOADOUT", effect=EffectClass.LOCAL_MUTATE),
    )

    assert result.reason == RefusalReason.DESIGN_GATE_REQUIRED


def test_red_first_001_red_witness_must_precede_implementation_mutation():
    state = start_workflow(
        DEV_IMPLEMENT,
        current_state_id="W0",
        scope="repo:LOADOUT",
        design_admitted=True,
    )
    result = transition(
        state,
        WorkflowEvent(Verb.MUTATE, "W1", scope="repo:LOADOUT", effect=EffectClass.LOCAL_MUTATE),
    )

    assert result.reason == RefusalReason.WITNESS_REQUIRED

    state = accept(
        state,
        WorkflowEvent(Verb.WITNESS, "W0", evidence=EvidenceKind.TEST_RED, scope="repo:LOADOUT"),
    )
    result = transition(
        state,
        WorkflowEvent(Verb.MUTATE, "W1", scope="repo:LOADOUT", effect=EffectClass.LOCAL_MUTATE),
    )
    assert result.reason is None


def test_root_cause_001_debug_repair_requires_hypothesis_and_probe():
    state = start_workflow(DEV_DEBUG, current_state_id="B0", scope="repo:LOADOUT")
    state = accept(
        state,
        WorkflowEvent(
            Verb.CONTRACT,
            "B0",
            evidence=EvidenceKind.ROOT_CAUSE_HYPOTHESIS,
            scope="repo:LOADOUT",
        ),
    )

    result = transition(
        state,
        WorkflowEvent(Verb.REPAIR, "B1", scope="repo:LOADOUT", effect=EffectClass.LOCAL_MUTATE),
    )
    assert result.reason == RefusalReason.ROOT_CAUSE_REQUIRED

    state = accept(
        state,
        WorkflowEvent(
            Verb.PROBE,
            "B0",
            evidence=EvidenceKind.ROOT_CAUSE_PROBE,
            scope="repo:LOADOUT",
        ),
    )
    result = transition(
        state,
        WorkflowEvent(Verb.REPAIR, "B1", scope="repo:LOADOUT", effect=EffectClass.LOCAL_MUTATE),
    )
    assert result.reason is None


def test_review_scope_001_out_of_scope_finding_does_not_expand_repair_scope():
    state = start_workflow(DEV_REVIEW, current_state_id="R0", scope="repo:LOADOUT")
    state = accept(
        state,
        WorkflowEvent(
            Verb.PRESS,
            "R0",
            evidence=EvidenceKind.REVIEW_FINDING,
            scope="repo:OTHER",
            note="valid but outside current contract",
        ),
    )

    result = transition(
        state,
        WorkflowEvent(Verb.REPAIR, "R1", scope="repo:OTHER", effect=EffectClass.LOCAL_MUTATE),
    )

    assert result.reason == RefusalReason.REVIEW_SCOPE_EXCEEDED
    assert result.state.scope == "repo:LOADOUT"


def test_doc_publish_001_publish_effect_requires_prior_proposal():
    state = start_workflow(DEV_DOCS, current_state_id="D0", scope="docs:front-room")
    result = transition(
        state,
        WorkflowEvent(Verb.LAND, "D0", scope="docs:front-room", effect=EffectClass.PUBLISH),
    )
    assert result.reason == RefusalReason.PROPOSAL_REQUIRED

    state = accept(state, WorkflowEvent(Verb.PROPOSE, "D0", scope="docs:front-room"))
    state = accept(state, WorkflowEvent(Verb.VERIFY, "D0", scope="docs:front-room"))
    state = accept(state, WorkflowEvent(Verb.READY, "D0", scope="docs:front-room"))
    state = accept(state, WorkflowEvent(Verb.ADMIT, "D0", scope="docs:front-room"))
    result = transition(
        state,
        WorkflowEvent(Verb.LAND, "D0", scope="docs:front-room", effect=EffectClass.PUBLISH),
    )
    assert result.reason is None
```

- [ ] **Step 2: Run policy tests and verify RED**

```bash
python -m pytest tests/test_dev_workflow_policies.py -q
```

Expected: import failure for the new policy constants, or failing assertions because Task 4 does not yet enforce these policy gates.

- [ ] **Step 3: Add the named policy constants**

Add to `loadout/dev/workflow.py` immediately after `DEV_LAND`:

```python
DEV_IMPLEMENT = WorkflowPolicy(
    name="dev.implement@0",
    require_design_admission_before_mutate=True,
    require_red_before_mutate=True,
)
DEV_DEBUG = WorkflowPolicy(
    name="dev.debug@0",
    require_root_cause_before_repair=True,
)
DEV_REVIEW = WorkflowPolicy(
    name="dev.review@0",
    lock_repair_scope=True,
)
DEV_DOCS = WorkflowPolicy(
    name="dev.docs@0",
    require_proposal_before_publish=True,
)
```

- [ ] **Step 4: Teach `transition()` to record witnesses/hypotheses/probes before enforcing mutations**

Insert these cases before the existing generic `MUTATE`/`REPAIR` handling:

```python
    if event.verb == Verb.WITNESS:
        next_state = state
        if event.evidence == EvidenceKind.TEST_RED:
            next_state = replace(next_state, red_witnessed=True)
        return TransitionResult(replace(next_state, events=next_state.events + (event,)))

    if event.verb == Verb.CONTRACT:
        next_state = state
        if event.evidence == EvidenceKind.ROOT_CAUSE_HYPOTHESIS:
            next_state = replace(next_state, root_cause_hypothesis=True)
        return TransitionResult(replace(next_state, events=next_state.events + (event,)))

    if event.verb == Verb.PROBE:
        next_state = state
        if event.evidence == EvidenceKind.ROOT_CAUSE_PROBE:
            next_state = replace(next_state, root_cause_probed=True)
        return TransitionResult(replace(next_state, events=next_state.events + (event,)))
```

- [ ] **Step 5: Enforce design, RED-first, root-cause, review-scope, and docs-proposal gates**

Before accepting generic mutation/repair/land transitions, add:

```python
    if event.verb == Verb.MUTATE:
        if state.policy.require_design_admission_before_mutate and not state.design_admitted:
            return _refuse(state, RefusalReason.DESIGN_GATE_REQUIRED)
        if state.policy.require_red_before_mutate and not state.red_witnessed:
            return _refuse(state, RefusalReason.WITNESS_REQUIRED)

    if event.verb == Verb.REPAIR:
        if state.policy.lock_repair_scope and event.scope != state.scope:
            return _refuse(state, RefusalReason.REVIEW_SCOPE_EXCEEDED)
        if state.policy.require_root_cause_before_repair and not (
            state.root_cause_hypothesis and state.root_cause_probed
        ):
            return _refuse(state, RefusalReason.ROOT_CAUSE_REQUIRED)

    if (
        event.verb == Verb.LAND
        and event.effect == EffectClass.PUBLISH
        and state.policy.require_proposal_before_publish
        and state.proposal_state_id != state.current_state_id
    ):
        return _refuse(state, RefusalReason.PROPOSAL_REQUIRED)
```

Update the module import to include `EffectClass`:

```python
from loadout.dev.model import (
    EffectClass,
    EvidenceKind,
    RefusalReason,
    Verb,
    WorkflowEvent,
)
```

Keep the earlier special rule allowing `PRESS` to carry an out-of-scope finding without changing the state scope. Only `REPAIR` is prohibited from crossing the cut.

- [ ] **Step 6: Run policy tests and verify GREEN**

```bash
python -m pytest tests/test_dev_workflow_policies.py -q
```

Expected: all pass.

- [ ] **Step 7: Re-run state-machine tests to catch policy regressions**

```bash
python -m pytest tests/test_dev_workflow_state.py tests/test_dev_workflow_policies.py -q
```

Expected: all pass.

- [ ] **Step 8: Commit Task 5**

```bash
git add loadout/dev/workflow.py tests/test_dev_workflow_policies.py
git commit -m "feat: encode native developer workflow gates"
```

---

### Task 6: Landing Observation Semantics and Provider-Reported Finality

**Files:**
- Modify: `tests/test_dev_membrane.py`
- Modify: `loadout/dev/membrane.py`

**Interfaces:**
- Consumes: `invoke_effect()` and `EffectReceipt` from Tasks 1 and 3.
- Produces: no new public API. This task tightens the meaning of successful `LAND` receipts.
- Rule: a provider disposition such as `QUEUED` or `AUTO_MERGE_ENABLED` is a successful request but not an observed landed state. `observed_post_state` remains provider evidence, not semantic authority.

- [ ] **Step 1: Add a failing `LAND-OBSERVE-001` test**

Append to `tests/test_dev_membrane.py`:

```python
def test_land_observe_001_queued_request_is_not_reported_as_observed_merge():
    compiled = compiled_for("landing.request", EffectClass.LAND, "pr:2")
    intent = EffectIntent(
        capability="landing.request",
        effect=EffectClass.LAND,
        target="pr:2",
        body_time_id=BODY_ID,
        precondition_state="H9",
        parameters_digest="auto-merge",
    )
    gate = OwnerGate("pr:2", EffectClass.LAND, "H9", "approval:9")
    adapter = FakeAdapter(BODY_ID, {"landing.request": ("QUEUED", None)})

    receipt = invoke_effect(
        compiled,
        intent,
        {BODY_ID: adapter},
        current_state="H9",
        owner_gate=gate,
    )

    assert receipt.provider_disposition == "QUEUED"
    assert receipt.observed_post_state is None
    assert receipt.semantic_authority is False
```

To force a meaningful RED witness, first add an intentionally strict assertion to the current code path if necessary:

```python
assert receipt.observed_post_state == "merged:H9"
```

Run once to observe the mismatch, then replace that assertion with the correct three assertions above before production changes. If the correct final test already passes without a code change, do **not** manufacture production work; record that the existing membrane already satisfies this hostile case and proceed to Step 3 without modifying production code.

- [ ] **Step 2: Run the single test and verify the behavior explicitly**

```bash
python -m pytest tests/test_dev_membrane.py::test_land_observe_001_queued_request_is_not_reported_as_observed_merge -q
```

Expected final behavior: PASS with provider disposition `QUEUED`, `observed_post_state is None`, and `semantic_authority is False`.

- [ ] **Step 3: Add code only if the test exposes an actual collapse**

If Task 3's implementation already preserves provider finality correctly, make no production change. If the implementation had inferred a merge from successful invocation, replace that inference with the provider-returned state only:

```python
    disposition, post_state = adapter.invoke(intent)
    return EffectReceipt(
        body_time_id=intent.body_time_id,
        capability=intent.capability,
        effect=intent.effect,
        target=intent.target,
        precondition_state=intent.precondition_state,
        provider_disposition=disposition,
        observed_post_state=post_state,
        semantic_authority=False,
    )
```

Do not add a derived `merged: bool` in v0; provider-specific finality mapping is deferred until a real landing adapter exists.

- [ ] **Step 4: Run the complete membrane suite**

```bash
python -m pytest tests/test_dev_membrane.py -q
```

Expected: all pass.

- [ ] **Step 5: Commit Task 6**

If only the test changed:

```bash
git add tests/test_dev_membrane.py
git commit -m "test: witness landing request finality"
```

If production code also changed:

```bash
git add loadout/dev/membrane.py tests/test_dev_membrane.py
git commit -m "fix: preserve provider-reported landing finality"
```

---

### Task 7: Public API, Hostile Corpus Map, README Status, and Fresh Full Verification

**Files:**
- Modify: `loadout/dev/__init__.py`
- Create: `tests/test_dev_public_api.py`
- Create: `evals/LOADOUT-DEV-v0.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: all prior tasks.
- Produces the supported v0 import surface from `loadout.dev`:
  - model enums/dataclasses;
  - `compile_world`;
  - `Adapter`, `FakeAdapter`;
  - `invoke_effect`;
  - workflow policy constants and transition functions.

- [ ] **Step 1: Write the failing public API test**

Create `tests/test_dev_public_api.py`:

```python
import loadout.dev as dev


def test_public_api_exports_v0_surface():
    expected = {
        "AdapterBody",
        "CapabilityRequest",
        "CompileRequest",
        "CompileReceipt",
        "EffectClass",
        "EffectIntent",
        "EffectReceipt",
        "OwnerGate",
        "RefusalReason",
        "WorkflowEvent",
        "compile_world",
        "Adapter",
        "FakeAdapter",
        "invoke_effect",
        "DEV_IMPLEMENT",
        "DEV_DEBUG",
        "DEV_REVIEW",
        "DEV_LAND",
        "DEV_DOCS",
        "start_workflow",
        "transition",
    }

    assert expected <= set(dev.__all__)
    for name in expected:
        assert hasattr(dev, name)
```

- [ ] **Step 2: Run the public API test and verify RED**

```bash
python -m pytest tests/test_dev_public_api.py -q
```

Expected: failure because `loadout/dev/__init__.py` does not yet export the v0 surface.

- [ ] **Step 3: Export the exact supported v0 API**

Replace `loadout/dev/__init__.py` with:

```python
from loadout.dev.adapters import Adapter, FakeAdapter
from loadout.dev.compiler import compile_world
from loadout.dev.membrane import invoke_effect
from loadout.dev.model import (
    AdapterBody,
    CapabilityRequest,
    CompileReceipt,
    CompileRequest,
    EffectClass,
    EffectIntent,
    EffectReceipt,
    OwnerGate,
    RefusalReason,
    WorkflowEvent,
)
from loadout.dev.workflow import (
    DEV_DEBUG,
    DEV_DOCS,
    DEV_IMPLEMENT,
    DEV_LAND,
    DEV_REVIEW,
    start_workflow,
    transition,
)


__all__ = [
    "Adapter",
    "AdapterBody",
    "CapabilityRequest",
    "CompileReceipt",
    "CompileRequest",
    "DEV_DEBUG",
    "DEV_DOCS",
    "DEV_IMPLEMENT",
    "DEV_LAND",
    "DEV_REVIEW",
    "EffectClass",
    "EffectIntent",
    "EffectReceipt",
    "FakeAdapter",
    "OwnerGate",
    "RefusalReason",
    "WorkflowEvent",
    "compile_world",
    "invoke_effect",
    "start_workflow",
    "transition",
]
```

- [ ] **Step 4: Run public API test and verify GREEN**

```bash
python -m pytest tests/test_dev_public_api.py -q
```

Expected: PASS.

- [ ] **Step 5: Create the durable hostile-corpus witness map**

Create `evals/LOADOUT-DEV-v0.md`:

```markdown
# LOADOUT.dev/v0 Hostile Conformance Witness

This document maps the architectural hostile corpus to executable pytest witnesses.

| ID | Executable witness | Expected boundary |
| --- | --- | --- |
| `MENTION-BIND-001` | `tests/test_dev_compiler.py::test_mention_bind_001_provider_mention_does_not_bind_capability` | mention does not bind |
| `DESIGN-GATE-001` | `tests/test_dev_workflow_policies.py::test_design_gate_001_implementation_mutation_requires_design_admission` | implementation mutation requires admitted design when policy demands it |
| `RED-FIRST-001` | `tests/test_dev_workflow_policies.py::test_red_first_001_red_witness_must_precede_implementation_mutation` | RED precedes implementation mutation |
| `ROOT-CAUSE-001` | `tests/test_dev_workflow_policies.py::test_root_cause_001_debug_repair_requires_hypothesis_and_probe` | repair requires root-cause pressure |
| `VERIFY-FRESH-001` | `tests/test_dev_workflow_state.py::test_verify_fresh_001_old_state_verification_cannot_prove_new_state` | old-state verification expires |
| `HEAD-DRIFT-001` | `tests/test_dev_workflow_state.py::test_head_drift_001_invalidates_ready_and_admission` | head drift invalidates READY/ADMIT |
| `EFFECT-FENCE-001` | `tests/test_dev_membrane.py::test_effect_fence_001_observe_binding_cannot_launder_write` | read/observe binding cannot mutate |
| `REVIEW-SCOPE-001` | `tests/test_dev_workflow_policies.py::test_review_scope_001_out_of_scope_finding_does_not_expand_repair_scope` | review cannot silently widen cut |
| `DOC-PUBLISH-001` | `tests/test_dev_workflow_policies.py::test_doc_publish_001_publish_effect_requires_prior_proposal` | publication requires proposal membrane |
| `WOLFRAM-FENCE-001` | `tests/test_dev_membrane.py::test_wolfram_fence_001_math_inspect_does_not_authorize_evaluate` | inspection and arbitrary evaluation stay distinct |
| `BODY-PIN-001` | `tests/test_dev_compiler.py::test_body_pin_001_replay_requires_exact_body_pin` | replay requires exact body |
| `RESULT-LAUNDER-001` | `tests/test_dev_membrane.py::test_result_launder_001_success_receipt_never_mints_semantic_authority` | success is not semantic authority |
| `LAND-OBSERVE-001` | `tests/test_dev_membrane.py::test_land_observe_001_queued_request_is_not_reported_as_observed_merge` | request success is not observed landing |

Run the full witness corpus with:

```bash
python -m pytest -q
```

No live provider credentials or network access are part of this witness.
```

- [ ] **Step 6: Update README status without overstating the runtime**

Replace the final `## Status` paragraph in `README.md` with:

```markdown
## Status

`LOADOUT.dev/v0` now has a deterministic executable conformance floor for provider-independent capability compilation, exact adapter-body attribution, effect fencing, state-bound workflow gates, inert effect intents/receipts, and fake-adapter hostile tests.

It does **not** yet claim live autonomous provider orchestration, credential storage, merge/publication automation, background watching, full Dogram lowering, a production daemon, network authority, or a master ontology.

See `docs/specs/2026-08-28-loadout-dev-native-developer-toolset.md`, `docs/superpowers/plans/2026-08-28-loadout-dev-v0.md`, and `evals/LOADOUT-DEV-v0.md`.
```

- [ ] **Step 7: Run the full test suite fresh**

Run:

```bash
python -m pytest -q
```

Expected: all tests pass. Read the complete output; do not infer success from a previous focused run.

- [ ] **Step 8: Run Python bytecode compilation as an independent syntax witness**

```bash
python -m compileall -q loadout
```

Expected: exit code 0 with no output.

- [ ] **Step 9: Verify the hostile IDs are all durably named**

```bash
python - <<'PY'
from pathlib import Path

required = {
    "MENTION-BIND-001",
    "DESIGN-GATE-001",
    "RED-FIRST-001",
    "ROOT-CAUSE-001",
    "VERIFY-FRESH-001",
    "HEAD-DRIFT-001",
    "EFFECT-FENCE-001",
    "REVIEW-SCOPE-001",
    "DOC-PUBLISH-001",
    "WOLFRAM-FENCE-001",
    "BODY-PIN-001",
    "RESULT-LAUNDER-001",
    "LAND-OBSERVE-001",
}
text = Path("evals/LOADOUT-DEV-v0.md").read_text()
missing = sorted(case for case in required if case not in text)
assert not missing, missing
print(f"hostile-corpus:{len(required)}/13")
PY
```

Expected stdout:

```text
hostile-corpus:13/13
```

- [ ] **Step 10: Inspect the final diff for forbidden scope**

Run:

```bash
git diff --check
git status --short
git diff --stat HEAD~6..HEAD
```

Expected:

- `git diff --check` emits no whitespace errors.
- No credential files, network clients, live provider SDKs, background daemons, Dogram runtime changes, or unrelated repository changes appear.
- Only the LOADOUT.dev package, tests/fixtures, README status, eval witness, and packaging metadata are present.

If the task count caused a different commit range, use `git log --oneline --decorate -10` to identify the first implementation commit and inspect from its parent instead of guessing a range.

- [ ] **Step 11: Commit Task 7**

```bash
git add loadout/dev/__init__.py tests/test_dev_public_api.py evals/LOADOUT-DEV-v0.md README.md
git commit -m "docs: seal LOADOUT.dev v0 conformance floor"
```

- [ ] **Step 12: Perform post-commit fresh verification before claiming completion**

```bash
python -m pytest -q
python -m compileall -q loadout
git status --short
```

Expected:

- full pytest suite passes;
- compileall exits 0;
- `git status --short` is empty.

Only after these fresh post-commit witnesses may the implementation be described as complete or green.

---

## Spec Coverage Map

| Spec requirement | Plan task(s) |
| --- | --- |
| provider-independent developer compile model | Tasks 1–2 |
| typed capability/effect/fence representation | Tasks 1–3 |
| exact target cut before mutation | Tasks 2–3 |
| immutable adapter/body attribution | Tasks 1–3 |
| exact replay body pin / no latest-wins | Task 2 |
| inert `EffectIntent` / `EffectReceipt` | Tasks 1, 3 |
| adapter interface + deterministic fake adapter | Task 3 |
| GitHub/GitBook/Wolfram-shaped conformance fixtures | Task 2 |
| read/effect non-laundering | Task 3 |
| state-bound verification/readiness/admission | Task 4 |
| head/state drift invalidation | Task 4 |
| design gate | Task 5 |
| TDD RED-before-mutation gate | Task 5 |
| root-cause-before-repair gate | Task 5 |
| review scope preservation | Task 5 |
| proposal-before-publication gate | Task 5 |
| provider request != observed landing | Task 6 |
| successful execution != semantic authority | Task 3 |
| complete hostile conformance corpus | Tasks 2–7 |
| no live credentials/network required | Tasks 2–7 |
| public v0 API and durable witness documentation | Task 7 |
| CLI only if needed | deliberately deferred; not needed for this conformance floor |
| Dogram lowering | deliberately deferred per spec Phase B+ |

## Execution Notes

- Implement on an isolated worktree created with the `superpowers:using-git-worktrees` skill before Task 1.
- Use one fresh review gate per task. A reviewer should be able to reject a task without forcing unrelated later changes.
- Do not pre-create production files for later tasks. TDD requires each task's failing test to exist and be observed failing before that task's production implementation.
- Do not replace fake adapters with live GitHub/GitBook/Wolfram calls in this plan.
- Do not add a generic plugin discovery system. `available_bodies` is explicit input to `CompileRequest` in v0.
- Do not add a generalized effect-ranking lattice. Exact effect-class matching is intentionally easier to audit and sufficient for the hostile corpus.
- Do not add secrets/configuration storage. Runtime credential/session material belongs outside the adapter body model.
- Do not report a provider request as final consequence unless the provider's returned observation actually carries that final state.
