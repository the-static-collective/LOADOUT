# LOADOUT.dev/v0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first deterministic executable floor for `LOADOUT.dev/v0`: provider-independent capability compilation, reachable-effect fencing, state-bound workflow gates, inert effect intents/receipts, deterministic fake adapters, and the complete hostile conformance corpus without live provider credentials.

**Architecture:** Implement LOADOUT.dev as a small Python 3.12 package. Adapter bodies declare semantic capabilities together with their reachable effect class; callers may request only those declared capability/effect pairs. Pure compiler/workflow logic remains separate from provider invocation, and every effect crosses one membrane that checks binding, target cut, exact effect class, immutable adapter-body identity, current-state preconditions, and owner-local gates. Dogram lowering remains deferred.

**Tech Stack:** Python >=3.12, standard library (`dataclasses`, `enum`, `typing`, `re`), setuptools, pytest. No runtime dependencies.

**Spec:** `docs/specs/2026-08-28-loadout-dev-native-developer-toolset.md`

## Global Constraints

- Preserve: **Knowledge may load. Capability may bind. Authority does not silently expand.**
- Product/provider names stay adapter-local; native workflow semantics stay provider-independent.
- `DISCOVER != invoke`, `SELECT != bind`, `BIND != authorize every operation`, `READY != ADMIT`, `ADMIT != LAND`, `RECEIPT != authority`.
- Classification follows reachable effects, not caller labels or provider branding.
- Adapter bodies carry `authority: none`; credentials/session grants are never body identity.
- Replay/historical adapter selection is exact-body pinned; no implicit newest-body resolution.
- Verification, readiness, and owner admission are exact-state bound and expire on relevant state drift.
- Review pressure may expose adjacent work but may not silently enlarge the current cut.
- GitBook-shaped publication must cross a proposal/change-request membrane before publication consequence.
- Arbitrary Wolfram-style evaluator execution is not equivalent to read/query computation.
- Provider success does not mint evidence, truth, publication authority, merge authority, or semantic admission.
- No live credentials, network calls, background watchers, merge/publication automation, arbitrary evaluator execution, remote adapter download, plugin installer, Dogram lowering, or credential storage in v0.
- TDD is mandatory: production behavior is written only after a test has been run and observed failing for the intended missing behavior.
- Every task ends green and with a focused commit; the final task performs fresh full-suite verification.

---

## File Structure

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

- `model.py` — immutable native vocabulary and receipt/intent transport types; no I/O or workflow policy.
- `compiler.py` — deterministic capability/effect/body selection for the bounded developer world.
- `adapters.py` — adapter protocol plus deterministic in-memory fake adapter only.
- `membrane.py` — only v0 route from inert `EffectIntent` to adapter invocation.
- `workflow.py` — pure state transitions, freshness invalidation, and named workflow policies.
- `tests/fixtures/*.json` — provider-shaped body declarations; no credentials.
- `evals/LOADOUT-DEV-v0.md` — durable hostile-ID to pytest-witness map.

No CLI is added: the spec makes CLI conditional on needing cross-process proof, and the v0 conformance floor does not need it.

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
- Produces `Disposition`, `EffectClass`, `Verb`, `EvidenceKind`, `RefusalReason`.
- Produces immutable `CapabilitySpec`, `AdapterBody`, `CapabilityRequest`, `Binding`, `CompileRequest`, `CompileReceipt`, `EffectIntent`, `OwnerGate`, `EffectReceipt`, `WorkflowEvent`.
- `AdapterBody.capabilities` is a tuple of `CapabilitySpec(name, effect)`, so reachable effects are body-declared rather than caller-invented.

- [ ] **Step 1: Write the failing model tests**

Create `tests/test_dev_model.py`:

```python
from dataclasses import FrozenInstanceError

import pytest

from loadout.dev.model import AdapterBody, CapabilitySpec, EffectClass, RefusalReason


def test_adapter_body_binds_exact_sha_and_declared_effects():
    sha = "a" * 40
    body = AdapterBody(
        adapter_id="github-adapter",
        body_time_id=f"github-adapter@{sha}",
        source_sha=sha,
        capabilities=(CapabilitySpec("repo.inspect", EffectClass.OBSERVE),),
    )
    assert body.authority == "none"
    assert body.capabilities[0].effect == EffectClass.OBSERVE


def test_adapter_body_rejects_non_exact_sha():
    with pytest.raises(ValueError, match="40 lowercase hexadecimal"):
        AdapterBody(
            adapter_id="github-adapter",
            body_time_id="github-adapter@abc",
            source_sha="abc",
            capabilities=(),
        )


def test_adapter_body_rejects_body_time_mismatch():
    sha = "b" * 40
    with pytest.raises(ValueError, match="body_time_id"):
        AdapterBody(
            adapter_id="github-adapter",
            body_time_id=f"other@{sha}",
            source_sha=sha,
            capabilities=(),
        )


def test_adapter_body_rejects_authority_laundering():
    sha = "c" * 40
    with pytest.raises(ValueError, match="authority: none"):
        AdapterBody(
            adapter_id="gitbook-adapter",
            body_time_id=f"gitbook-adapter@{sha}",
            source_sha=sha,
            capabilities=(),
            authority="publish",
        )


def test_adapter_body_is_immutable():
    sha = "d" * 40
    body = AdapterBody(
        adapter_id="fixture",
        body_time_id=f"fixture@{sha}",
        source_sha=sha,
        capabilities=(),
    )
    with pytest.raises(FrozenInstanceError):
        body.authority = "merge"  # type: ignore[misc]


def test_refusal_reason_names_are_stable():
    assert RefusalReason.BODY_PIN_REQUIRED.value == "BODY_PIN_REQUIRED"
    assert RefusalReason.EFFECT_OUTSIDE_FENCE.value == "EFFECT_OUTSIDE_FENCE"
    assert RefusalReason.OWNER_GATE_STALE.value == "OWNER_GATE_STALE"
```

- [ ] **Step 2: Run RED**

```bash
python -m pytest tests/test_dev_model.py -q
```

Expected: import/collection failure because `loadout.dev.model` does not exist.

- [ ] **Step 3: Add package metadata**

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

Create empty `loadout/__init__.py`, `loadout/dev/__init__.py`, and `tests/__init__.py`.

- [ ] **Step 4: Implement the minimal model**

Create `loadout/dev/model.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
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
class CapabilitySpec:
    name: str
    effect: EffectClass


@dataclass(frozen=True)
class AdapterBody:
    adapter_id: str
    body_time_id: str
    source_sha: str
    capabilities: tuple[CapabilitySpec, ...]
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

- [ ] **Step 5: Run GREEN**

```bash
python -m pytest tests/test_dev_model.py -q
```

Expected: all pass.

- [ ] **Step 6: Commit Task 1**

```bash
git add pyproject.toml loadout tests/test_dev_model.py tests/__init__.py
git commit -m "feat: add LOADOUT.dev native model"
```

---

### Task 2: Deterministic Compiler and Provider-Shaped Body Fixtures

**Files:**
- Create: `loadout/dev/compiler.py`
- Create: `tests/test_dev_compiler.py`
- Create: `tests/fixtures/github_adapter_body.json`
- Create: `tests/fixtures/gitbook_adapter_body.json`
- Create: `tests/fixtures/wolfram_read_adapter_body.json`
- Create: `tests/fixtures/wolfram_eval_adapter_body.json`

**Interfaces:**
- Produces `compile_world(request: CompileRequest) -> CompileReceipt`.
- Candidate bodies must declare the exact requested `CapabilitySpec(name, effect)`.
- A body declaring the capability name under a different effect class causes `EFFECT_OUTSIDE_FENCE`, not caller-driven reclassification.
- Replay without `body_time_id` refuses.
- More than one exact unpinned body refuses as ambiguous; no newest-body tie-break.

- [ ] **Step 1: Add fixtures**

`tests/fixtures/github_adapter_body.json`:

```json
{"adapter_id":"github-adapter","body_time_id":"github-adapter@1111111111111111111111111111111111111111","source_sha":"1111111111111111111111111111111111111111","capabilities":[{"name":"repo.inspect","effect":"OBSERVE"},{"name":"repo.file.write","effect":"REMOTE_MUTATE"},{"name":"proposal.create","effect":"REMOTE_PROPOSE"},{"name":"landing.request","effect":"LAND"}]}
```

`tests/fixtures/gitbook_adapter_body.json`:

```json
{"adapter_id":"gitbook-adapter","body_time_id":"gitbook-adapter@2222222222222222222222222222222222222222","source_sha":"2222222222222222222222222222222222222222","capabilities":[{"name":"docs.inspect","effect":"OBSERVE"},{"name":"docs.propose","effect":"REMOTE_PROPOSE"},{"name":"docs.publish","effect":"PUBLISH"}]}
```

`tests/fixtures/wolfram_read_adapter_body.json`:

```json
{"adapter_id":"wolfram-read-adapter","body_time_id":"wolfram-read-adapter@3333333333333333333333333333333333333333","source_sha":"3333333333333333333333333333333333333333","capabilities":[{"name":"math.inspect","effect":"OBSERVE"},{"name":"math.compute","effect":"LOCAL_COMPUTE"}]}
```

`tests/fixtures/wolfram_eval_adapter_body.json`:

```json
{"adapter_id":"wolfram-eval-adapter","body_time_id":"wolfram-eval-adapter@4444444444444444444444444444444444444444","source_sha":"4444444444444444444444444444444444444444","capabilities":[{"name":"math.evaluate","effect":"REMOTE_MUTATE"}]}
```

The evaluator fixture is deliberately conservative: arbitrary evaluator capability is classified as effectful and cannot be obtained through the read/query body.

- [ ] **Step 2: Write failing compiler tests**

Create `tests/test_dev_compiler.py` with a fixture loader plus these tests:

```python
import json
from pathlib import Path

from loadout.dev.compiler import compile_world
from loadout.dev.model import (
    AdapterBody, CapabilityRequest, CapabilitySpec, CompileRequest,
    Disposition, EffectClass, RefusalReason,
)

FIXTURES = Path(__file__).parent / "fixtures"


def load_body(name: str) -> AdapterBody:
    data = json.loads((FIXTURES / name).read_text())
    return AdapterBody(
        adapter_id=data["adapter_id"],
        body_time_id=data["body_time_id"],
        source_sha=data["source_sha"],
        capabilities=tuple(
            CapabilitySpec(item["name"], EffectClass(item["effect"]))
            for item in data["capabilities"]
        ),
    )


def test_mention_bind_001_provider_mention_does_not_bind():
    github = load_body("github_adapter_body.json")
    receipt = compile_world(CompileRequest(
        task_id="MENTION-BIND-001",
        task_text="Mention GitHub in the explanation.",
        cut_targets=frozenset({"repo:LOADOUT"}),
        requested_capabilities=(),
        available_bodies=(github,),
    ))
    assert receipt.disposition == Disposition.COMPILED
    assert receipt.bindings == ()


def test_caller_cannot_relabel_read_capability_as_mutation():
    github = load_body("github_adapter_body.json")
    receipt = compile_world(CompileRequest(
        task_id="effect-declaration",
        task_text="Inspect repo.",
        cut_targets=frozenset({"repo:LOADOUT"}),
        requested_capabilities=(
            CapabilityRequest("repo.inspect", EffectClass.REMOTE_MUTATE, "repo:LOADOUT"),
        ),
        available_bodies=(github,),
    ))
    assert receipt.disposition == Disposition.REFUSED
    assert receipt.reasons == (RefusalReason.EFFECT_OUTSIDE_FENCE,)


def test_body_pin_001_replay_requires_exact_pin():
    github = load_body("github_adapter_body.json")
    receipt = compile_world(CompileRequest(
        task_id="BODY-PIN-001",
        task_text="Replay inspection.",
        cut_targets=frozenset({"repo:LOADOUT"}),
        requested_capabilities=(
            CapabilityRequest("repo.inspect", EffectClass.OBSERVE, "repo:LOADOUT", replay=True),
        ),
        available_bodies=(github,),
    ))
    assert receipt.disposition == Disposition.REFUSED
    assert receipt.reasons == (RefusalReason.BODY_PIN_REQUIRED,)


def test_unpinned_ambiguity_refuses_instead_of_latest_wins():
    cap = (CapabilitySpec("repo.inspect", EffectClass.OBSERVE),)
    a = AdapterBody("a", f"a@{'a'*40}", "a"*40, cap)
    b = AdapterBody("b", f"b@{'b'*40}", "b"*40, cap)
    receipt = compile_world(CompileRequest(
        task_id="ambiguous",
        task_text="Inspect.",
        cut_targets=frozenset({"repo:LOADOUT"}),
        requested_capabilities=(CapabilityRequest("repo.inspect", EffectClass.OBSERVE, "repo:LOADOUT"),),
        available_bodies=(b, a),
    ))
    assert receipt.disposition == Disposition.REFUSED
    assert receipt.reasons == (RefusalReason.BODY_AMBIGUOUS,)


def test_same_native_request_compiles_against_replaceable_pinned_bodies():
    cap = (CapabilitySpec("proposal.create", EffectClass.REMOTE_PROPOSE),)
    bodies = (
        AdapterBody("provider-a", f"provider-a@{'a'*40}", "a"*40, cap),
        AdapterBody("provider-b", f"provider-b@{'b'*40}", "b"*40, cap),
    )
    for body in bodies:
        receipt = compile_world(CompileRequest(
            task_id="portable",
            task_text="Propose change.",
            cut_targets=frozenset({"proposal:1"}),
            requested_capabilities=(CapabilityRequest(
                "proposal.create", EffectClass.REMOTE_PROPOSE, "proposal:1",
                body_time_id=body.body_time_id,
            ),),
            available_bodies=bodies,
        ))
        assert receipt.disposition == Disposition.COMPILED
        assert receipt.bindings[0].capability == "proposal.create"
        assert receipt.bindings[0].effect == EffectClass.REMOTE_PROPOSE
        assert receipt.bindings[0].body_time_id == body.body_time_id
```

- [ ] **Step 3: Run RED**

```bash
python -m pytest tests/test_dev_compiler.py -q
```

Expected: import failure because `compiler.py` does not exist.

- [ ] **Step 4: Implement minimal deterministic compilation**

Create `loadout/dev/compiler.py`:

```python
from loadout.dev.model import (
    Binding, CapabilitySpec, CompileReceipt, CompileRequest,
    Disposition, RefusalReason,
)


def compile_world(request: CompileRequest) -> CompileReceipt:
    bindings: list[Binding] = []

    for requested in request.requested_capabilities:
        if requested.target not in request.cut_targets:
            return CompileReceipt(Disposition.REFUSED, request.task_id, reasons=(RefusalReason.TARGET_OUTSIDE_CUT,))
        if requested.replay and requested.body_time_id is None:
            return CompileReceipt(Disposition.REFUSED, request.task_id, reasons=(RefusalReason.BODY_PIN_REQUIRED,))

        named = [
            body for body in request.available_bodies
            if any(cap.name == requested.capability for cap in body.capabilities)
            and (requested.body_time_id is None or body.body_time_id == requested.body_time_id)
        ]
        exact_spec = CapabilitySpec(requested.capability, requested.effect)
        exact = [body for body in named if exact_spec in body.capabilities]

        if named and not exact:
            return CompileReceipt(Disposition.REFUSED, request.task_id, reasons=(RefusalReason.EFFECT_OUTSIDE_FENCE,))
        if not exact:
            return CompileReceipt(Disposition.CAPABILITY_GAP, request.task_id, reasons=(RefusalReason.CAPABILITY_UNAVAILABLE,))
        if len(exact) != 1:
            return CompileReceipt(Disposition.REFUSED, request.task_id, reasons=(RefusalReason.BODY_AMBIGUOUS,))

        body = exact[0]
        bindings.append(Binding(
            capability=requested.capability,
            effect=requested.effect,
            target=requested.target,
            body_time_id=body.body_time_id,
        ))

    return CompileReceipt(Disposition.COMPILED, request.task_id, bindings=tuple(bindings))
```

Do not parse `task_text` for tool/provider mentions. Binding is driven only by explicit requested semantic capabilities.

- [ ] **Step 5: Run GREEN and regression**

```bash
python -m pytest tests/test_dev_model.py tests/test_dev_compiler.py -q
```

Expected: all pass.

- [ ] **Step 6: Commit Task 2**

```bash
git add loadout/dev/compiler.py tests/test_dev_compiler.py tests/fixtures
git commit -m "feat: compile bounded developer capabilities"
```

---

### Task 3: Effect Membrane and Deterministic Fake Adapter

**Files:**
- Create: `loadout/dev/adapters.py`
- Create: `loadout/dev/membrane.py`
- Create: `tests/test_dev_membrane.py`

**Interfaces:**
- Produces `Adapter` protocol and `FakeAdapter`.
- Produces `invoke_effect(compiled, intent, adapters, current_state, owner_gate=None) -> EffectReceipt`.
- `PUBLISH` and `LAND` require an exact state-bound `OwnerGate`.
- Effect matching is exact; v0 deliberately avoids a generalized effect-ranking lattice.

- [ ] **Step 1: Write failing membrane tests including `EFFECT-FENCE-001`, `WOLFRAM-FENCE-001`, `RESULT-LAUNDER-001`, and `LAND-OBSERVE-001`**

Create `tests/test_dev_membrane.py`:

```python
from loadout.dev.adapters import FakeAdapter
from loadout.dev.compiler import compile_world
from loadout.dev.membrane import invoke_effect
from loadout.dev.model import (
    AdapterBody, CapabilityRequest, CapabilitySpec, CompileRequest,
    EffectClass, EffectIntent, OwnerGate, RefusalReason,
)

SHA = "5" * 40
BODY_ID = f"fixture@{SHA}"
BODY = AdapterBody(
    "fixture", BODY_ID, SHA,
    (
        CapabilitySpec("repo.inspect", EffectClass.OBSERVE),
        CapabilitySpec("math.inspect", EffectClass.OBSERVE),
        CapabilitySpec("landing.request", EffectClass.LAND),
    ),
)


def compiled_for(capability, effect, target):
    return compile_world(CompileRequest(
        task_id="membrane", task_text="bounded", cut_targets=frozenset({target}),
        requested_capabilities=(CapabilityRequest(capability, effect, target, body_time_id=BODY_ID),),
        available_bodies=(BODY,),
    ))


def test_effect_fence_001_observe_binding_cannot_mutate():
    compiled = compiled_for("repo.inspect", EffectClass.OBSERVE, "repo:LOADOUT")
    intent = EffectIntent("repo.inspect", EffectClass.REMOTE_MUTATE, "repo:LOADOUT", BODY_ID, "H0", "p")
    adapter = FakeAdapter(BODY_ID, {"repo.inspect": ("OK", "H0")})
    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="H0")
    assert receipt.reason == RefusalReason.EFFECT_OUTSIDE_FENCE
    assert adapter.invocations == []


def test_wolfram_fence_001_inspect_binding_cannot_invoke_evaluate():
    compiled = compiled_for("math.inspect", EffectClass.OBSERVE, "calc:1")
    intent = EffectIntent("math.evaluate", EffectClass.REMOTE_MUTATE, "calc:1", BODY_ID, "C0", "expr")
    adapter = FakeAdapter(BODY_ID, {"math.evaluate": ("OK", "C1")})
    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="C0")
    assert receipt.reason == RefusalReason.CAPABILITY_NOT_BOUND
    assert adapter.invocations == []


def test_target_outside_binding_refuses_before_adapter():
    compiled = compiled_for("repo.inspect", EffectClass.OBSERVE, "repo:LOADOUT")
    intent = EffectIntent("repo.inspect", EffectClass.OBSERVE, "repo:OTHER", BODY_ID, "H0", "p")
    adapter = FakeAdapter(BODY_ID, {"repo.inspect": ("OK", "H0")})
    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="H0")
    assert receipt.reason == RefusalReason.TARGET_OUTSIDE_CUT
    assert adapter.invocations == []


def test_land_requires_fresh_owner_gate():
    compiled = compiled_for("landing.request", EffectClass.LAND, "pr:2")
    intent = EffectIntent("landing.request", EffectClass.LAND, "pr:2", BODY_ID, "H8", "merge")
    adapter = FakeAdapter(BODY_ID, {"landing.request": ("MERGED", "merged:H8")})
    stale = OwnerGate("pr:2", EffectClass.LAND, "H7", "approval:7")
    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="H8", owner_gate=stale)
    assert receipt.reason == RefusalReason.OWNER_GATE_STALE
    assert adapter.invocations == []


def test_result_launder_001_success_never_mints_semantic_authority():
    compiled = compiled_for("repo.inspect", EffectClass.OBSERVE, "repo:LOADOUT")
    intent = EffectIntent("repo.inspect", EffectClass.OBSERVE, "repo:LOADOUT", BODY_ID, "H0", "read")
    adapter = FakeAdapter(BODY_ID, {"repo.inspect": ("OK", "H0")})
    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="H0")
    assert receipt.provider_disposition == "OK"
    assert receipt.semantic_authority is False
    assert receipt.reason is None


def test_land_observe_001_queued_request_is_not_observed_merge():
    compiled = compiled_for("landing.request", EffectClass.LAND, "pr:2")
    intent = EffectIntent("landing.request", EffectClass.LAND, "pr:2", BODY_ID, "H9", "auto-merge")
    gate = OwnerGate("pr:2", EffectClass.LAND, "H9", "approval:9")
    adapter = FakeAdapter(BODY_ID, {"landing.request": ("QUEUED", None)})
    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="H9", owner_gate=gate)
    assert receipt.provider_disposition == "QUEUED"
    assert receipt.observed_post_state is None
    assert receipt.semantic_authority is False
```

- [ ] **Step 2: Run RED**

```bash
python -m pytest tests/test_dev_membrane.py -q
```

Expected: import failure because adapter/membrane modules do not exist.

- [ ] **Step 3: Implement fake adapter**

Create `loadout/dev/adapters.py`:

```python
from typing import Protocol
from loadout.dev.model import EffectIntent


class Adapter(Protocol):
    body_time_id: str
    def invoke(self, intent: EffectIntent) -> tuple[str, str | None]: ...


class FakeAdapter:
    def __init__(self, body_time_id: str, outcomes: dict[str, tuple[str, str | None]]) -> None:
        self.body_time_id = body_time_id
        self.outcomes = dict(outcomes)
        self.invocations: list[EffectIntent] = []

    def invoke(self, intent: EffectIntent) -> tuple[str, str | None]:
        self.invocations.append(intent)
        return self.outcomes[intent.capability]
```

- [ ] **Step 4: Implement fail-closed membrane**

Create `loadout/dev/membrane.py`:

```python
from collections.abc import Mapping
from loadout.dev.adapters import Adapter
from loadout.dev.model import (
    CompileReceipt, Disposition, EffectClass, EffectIntent, EffectReceipt,
    OwnerGate, RefusalReason,
)

_OWNER_GATED = frozenset({EffectClass.PUBLISH, EffectClass.LAND})


def _refuse(intent: EffectIntent, reason: RefusalReason) -> EffectReceipt:
    return EffectReceipt(
        intent.body_time_id, intent.capability, intent.effect, intent.target,
        intent.precondition_state, "REFUSED", None, False, reason,
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

    named = [b for b in compiled.bindings if b.capability == intent.capability]
    if not named:
        return _refuse(intent, RefusalReason.CAPABILITY_NOT_BOUND)
    targeted = [b for b in named if b.target == intent.target]
    if not targeted:
        return _refuse(intent, RefusalReason.TARGET_OUTSIDE_CUT)
    exact = [b for b in targeted if b.effect == intent.effect and b.body_time_id == intent.body_time_id]
    if not exact:
        return _refuse(intent, RefusalReason.EFFECT_OUTSIDE_FENCE)
    if intent.precondition_state != current_state:
        return _refuse(intent, RefusalReason.STATE_STALE)

    if intent.effect in _OWNER_GATED:
        if owner_gate is None:
            return _refuse(intent, RefusalReason.OWNER_GATE_REQUIRED)
        if (owner_gate.target, owner_gate.effect, owner_gate.state_id) != (intent.target, intent.effect, current_state):
            return _refuse(intent, RefusalReason.OWNER_GATE_STALE)

    adapter = adapters.get(intent.body_time_id)
    if adapter is None or adapter.body_time_id != intent.body_time_id:
        return _refuse(intent, RefusalReason.BODY_NOT_ELIGIBLE)

    disposition, post_state = adapter.invoke(intent)
    return EffectReceipt(
        intent.body_time_id, intent.capability, intent.effect, intent.target,
        intent.precondition_state, disposition, post_state, False, None,
    )
```

Do not infer finality: if provider returns `QUEUED, None`, the receipt stays `QUEUED` with no observed merged state.

- [ ] **Step 5: Run GREEN and regression**

```bash
python -m pytest tests/test_dev_compiler.py tests/test_dev_membrane.py -q
```

Expected: all pass.

- [ ] **Step 6: Commit Task 3**

```bash
git add loadout/dev/adapters.py loadout/dev/membrane.py tests/test_dev_membrane.py
git commit -m "feat: fence developer effects behind membrane"
```

---

### Task 4: Workflow Freshness and Exact-State Consequence Gates

**Files:**
- Create: `loadout/dev/workflow.py`
- Create: `tests/test_dev_workflow_state.py`

**Interfaces:**
- Produces `WorkflowPolicy`, `WorkflowState`, `TransitionResult`.
- Produces `DEV_LAND`, `start_workflow(...)`, `transition(...)`.
- `start_workflow` receives `design_admission_ref: str | None`, never an unattributed boolean.
- Accepted `MUTATE`/`REPAIR` to a new state clears verification/readiness/admission.

- [ ] **Step 1: Write failing `VERIFY-FRESH-001` and `HEAD-DRIFT-001` tests**

Create `tests/test_dev_workflow_state.py`:

```python
from loadout.dev.model import EffectClass, RefusalReason, Verb, WorkflowEvent
from loadout.dev.workflow import DEV_LAND, start_workflow, transition


def accept(state, event):
    result = transition(state, event)
    assert result.reason is None
    return result.state


def test_verify_fresh_001_mutation_expires_prior_verification():
    state = start_workflow(DEV_LAND, current_state_id="H0", scope="pr:2")
    state = accept(state, WorkflowEvent(Verb.PROPOSE, "H0", scope="pr:2"))
    state = accept(state, WorkflowEvent(Verb.VERIFY, "H0", scope="pr:2"))
    state = accept(state, WorkflowEvent(Verb.MUTATE, "H1", scope="pr:2", effect=EffectClass.REMOTE_PROPOSE))
    assert state.current_state_id == "H1"
    assert state.verified_state_id is None
    assert state.ready_state_id is None
    assert state.admitted_state_id is None


def test_ready_requires_current_state_verification():
    state = start_workflow(DEV_LAND, current_state_id="H0", scope="pr:2")
    state = accept(state, WorkflowEvent(Verb.PROPOSE, "H0", scope="pr:2"))
    result = transition(state, WorkflowEvent(Verb.READY, "H0", scope="pr:2"))
    assert result.reason == RefusalReason.VERIFICATION_STALE


def test_head_drift_001_invalidates_ready_and_owner_admission():
    state = start_workflow(DEV_LAND, current_state_id="H0", scope="pr:2")
    for verb in (Verb.PROPOSE, Verb.VERIFY, Verb.READY, Verb.ADMIT):
        state = accept(state, WorkflowEvent(verb, "H0", scope="pr:2"))
    state = accept(state, WorkflowEvent(Verb.MUTATE, "H1", scope="pr:2", effect=EffectClass.REMOTE_PROPOSE))
    result = transition(state, WorkflowEvent(Verb.LAND, "H1", scope="pr:2", effect=EffectClass.LAND))
    assert result.reason == RefusalReason.OWNER_GATE_STALE
```

- [ ] **Step 2: Run RED**

```bash
python -m pytest tests/test_dev_workflow_state.py -q
```

Expected: import failure because `workflow.py` does not exist.

- [ ] **Step 3: Implement baseline workflow state**

Create `loadout/dev/workflow.py`:

```python
from dataclasses import dataclass, replace
from loadout.dev.model import EffectClass, EvidenceKind, RefusalReason, Verb, WorkflowEvent


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
    design_admission_ref: str | None = None
    verified_state_id: str | None = None
    proposal_seen: bool = False
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


def start_workflow(policy, *, current_state_id, scope, design_admission_ref=None):
    return WorkflowState(policy, current_state_id, scope, design_admission_ref)


def _refuse(state, reason):
    return TransitionResult(state, reason)


def transition(state: WorkflowState, event: WorkflowEvent) -> TransitionResult:
    if event.scope is not None and event.scope != state.scope and event.verb != Verb.PRESS:
        reason = RefusalReason.REVIEW_SCOPE_EXCEEDED if event.verb == Verb.REPAIR else RefusalReason.TARGET_OUTSIDE_CUT
        return _refuse(state, reason)

    if event.verb == Verb.PROPOSE:
        return TransitionResult(replace(state, proposal_seen=True, events=state.events + (event,)))
    if event.verb == Verb.VERIFY:
        if event.state_id != state.current_state_id:
            return _refuse(state, RefusalReason.STATE_STALE)
        return TransitionResult(replace(state, verified_state_id=event.state_id, events=state.events + (event,)))
    if event.verb == Verb.READY:
        if event.state_id != state.current_state_id or state.verified_state_id != event.state_id:
            return _refuse(state, RefusalReason.VERIFICATION_STALE)
        return TransitionResult(replace(state, ready_state_id=event.state_id, events=state.events + (event,)))
    if event.verb == Verb.ADMIT:
        if event.state_id != state.current_state_id or state.ready_state_id != event.state_id:
            return _refuse(state, RefusalReason.OWNER_GATE_STALE)
        return TransitionResult(replace(state, admitted_state_id=event.state_id, events=state.events + (event,)))
    if event.verb in {Verb.MUTATE, Verb.REPAIR}:
        return TransitionResult(replace(
            state,
            current_state_id=event.state_id,
            verified_state_id=None,
            ready_state_id=None,
            admitted_state_id=None,
            events=state.events + (event,),
        ))
    if event.verb == Verb.LAND:
        if event.state_id != state.current_state_id or state.admitted_state_id != event.state_id:
            return _refuse(state, RefusalReason.OWNER_GATE_STALE)
        return TransitionResult(replace(state, events=state.events + (event,)))
    return TransitionResult(replace(state, events=state.events + (event,)))
```

- [ ] **Step 4: Run GREEN and regression**

```bash
python -m pytest tests/test_dev_workflow_state.py -q
python -m pytest tests/test_dev_model.py tests/test_dev_compiler.py tests/test_dev_membrane.py tests/test_dev_workflow_state.py -q
```

Expected: all pass.

- [ ] **Step 5: Commit Task 4**

```bash
git add loadout/dev/workflow.py tests/test_dev_workflow_state.py
git commit -m "feat: bind workflow gates to exact state"
```

---

### Task 5: Named Workflow Policies and Hostile Sequence Gates

**Files:**
- Modify: `loadout/dev/workflow.py`
- Create: `tests/test_dev_workflow_policies.py`

**Interfaces:**
- Produces `DEV_IMPLEMENT`, `DEV_DEBUG`, `DEV_REVIEW`, `DEV_DOCS`.
- Policy checks happen before generic mutation/repair/land acceptance.

- [ ] **Step 1: Write failing policy tests**

Create `tests/test_dev_workflow_policies.py`:

```python
from loadout.dev.model import EffectClass, EvidenceKind, RefusalReason, Verb, WorkflowEvent
from loadout.dev.workflow import DEV_DEBUG, DEV_DOCS, DEV_IMPLEMENT, DEV_REVIEW, start_workflow, transition


def accept(state, event):
    result = transition(state, event)
    assert result.reason is None
    return result.state


def test_design_gate_001_requires_attributed_design_admission():
    state = start_workflow(DEV_IMPLEMENT, current_state_id="W0", scope="repo:LOADOUT")
    result = transition(state, WorkflowEvent(Verb.MUTATE, "W1", scope="repo:LOADOUT", effect=EffectClass.LOCAL_MUTATE))
    assert result.reason == RefusalReason.DESIGN_GATE_REQUIRED


def test_red_first_001_red_witness_precedes_mutation():
    state = start_workflow(DEV_IMPLEMENT, current_state_id="W0", scope="repo:LOADOUT", design_admission_ref="design:approved")
    result = transition(state, WorkflowEvent(Verb.MUTATE, "W1", scope="repo:LOADOUT", effect=EffectClass.LOCAL_MUTATE))
    assert result.reason == RefusalReason.WITNESS_REQUIRED
    state = accept(state, WorkflowEvent(Verb.WITNESS, "W0", evidence=EvidenceKind.TEST_RED, scope="repo:LOADOUT"))
    assert transition(state, WorkflowEvent(Verb.MUTATE, "W1", scope="repo:LOADOUT", effect=EffectClass.LOCAL_MUTATE)).reason is None


def test_root_cause_001_requires_hypothesis_and_probe_before_repair():
    state = start_workflow(DEV_DEBUG, current_state_id="B0", scope="repo:LOADOUT")
    state = accept(state, WorkflowEvent(Verb.CONTRACT, "B0", evidence=EvidenceKind.ROOT_CAUSE_HYPOTHESIS, scope="repo:LOADOUT"))
    assert transition(state, WorkflowEvent(Verb.REPAIR, "B1", scope="repo:LOADOUT", effect=EffectClass.LOCAL_MUTATE)).reason == RefusalReason.ROOT_CAUSE_REQUIRED
    state = accept(state, WorkflowEvent(Verb.PROBE, "B0", evidence=EvidenceKind.ROOT_CAUSE_PROBE, scope="repo:LOADOUT"))
    assert transition(state, WorkflowEvent(Verb.REPAIR, "B1", scope="repo:LOADOUT", effect=EffectClass.LOCAL_MUTATE)).reason is None


def test_review_scope_001_out_of_scope_pressure_cannot_expand_repair():
    state = start_workflow(DEV_REVIEW, current_state_id="R0", scope="repo:LOADOUT")
    state = accept(state, WorkflowEvent(Verb.PRESS, "R0", evidence=EvidenceKind.REVIEW_FINDING, scope="repo:OTHER"))
    result = transition(state, WorkflowEvent(Verb.REPAIR, "R1", scope="repo:OTHER", effect=EffectClass.LOCAL_MUTATE))
    assert result.reason == RefusalReason.REVIEW_SCOPE_EXCEEDED
    assert result.state.scope == "repo:LOADOUT"


def test_doc_publish_001_publish_requires_prior_proposal():
    state = start_workflow(DEV_DOCS, current_state_id="D0", scope="docs:front-room")
    assert transition(state, WorkflowEvent(Verb.LAND, "D0", scope="docs:front-room", effect=EffectClass.PUBLISH)).reason == RefusalReason.PROPOSAL_REQUIRED
    state = accept(state, WorkflowEvent(Verb.PROPOSE, "D0", scope="docs:front-room"))
    state = accept(state, WorkflowEvent(Verb.VERIFY, "D0", scope="docs:front-room"))
    state = accept(state, WorkflowEvent(Verb.READY, "D0", scope="docs:front-room"))
    state = accept(state, WorkflowEvent(Verb.ADMIT, "D0", scope="docs:front-room"))
    assert transition(state, WorkflowEvent(Verb.LAND, "D0", scope="docs:front-room", effect=EffectClass.PUBLISH)).reason is None
```

- [ ] **Step 2: Run RED**

```bash
python -m pytest tests/test_dev_workflow_policies.py -q
```

Expected: missing policy constants or failing policy assertions.

- [ ] **Step 3: Add named policies**

Add after `DEV_LAND`:

```python
DEV_IMPLEMENT = WorkflowPolicy("dev.implement@0", require_design_admission_before_mutate=True, require_red_before_mutate=True)
DEV_DEBUG = WorkflowPolicy("dev.debug@0", require_root_cause_before_repair=True)
DEV_REVIEW = WorkflowPolicy("dev.review@0", lock_repair_scope=True)
DEV_DOCS = WorkflowPolicy("dev.docs@0", require_proposal_before_publish=True)
```

- [ ] **Step 4: Record typed witness/hypothesis/probe state**

Before generic mutation handling, add:

```python
    if event.verb == Verb.WITNESS:
        next_state = replace(state, red_witnessed=True) if event.evidence == EvidenceKind.TEST_RED else state
        return TransitionResult(replace(next_state, events=next_state.events + (event,)))
    if event.verb == Verb.CONTRACT:
        next_state = replace(state, root_cause_hypothesis=True) if event.evidence == EvidenceKind.ROOT_CAUSE_HYPOTHESIS else state
        return TransitionResult(replace(next_state, events=next_state.events + (event,)))
    if event.verb == Verb.PROBE:
        next_state = replace(state, root_cause_probed=True) if event.evidence == EvidenceKind.ROOT_CAUSE_PROBE else state
        return TransitionResult(replace(next_state, events=next_state.events + (event,)))
```

- [ ] **Step 5: Enforce policy gates before generic acceptance**

Add before generic `MUTATE`/`REPAIR`/`LAND` cases:

```python
    if event.verb == Verb.MUTATE:
        if state.policy.require_design_admission_before_mutate and state.design_admission_ref is None:
            return _refuse(state, RefusalReason.DESIGN_GATE_REQUIRED)
        if state.policy.require_red_before_mutate and not state.red_witnessed:
            return _refuse(state, RefusalReason.WITNESS_REQUIRED)

    if event.verb == Verb.REPAIR:
        if state.policy.lock_repair_scope and event.scope != state.scope:
            return _refuse(state, RefusalReason.REVIEW_SCOPE_EXCEEDED)
        if state.policy.require_root_cause_before_repair and not (state.root_cause_hypothesis and state.root_cause_probed):
            return _refuse(state, RefusalReason.ROOT_CAUSE_REQUIRED)

    if (
        event.verb == Verb.LAND
        and event.effect == EffectClass.PUBLISH
        and state.policy.require_proposal_before_publish
        and not state.proposal_seen
    ):
        return _refuse(state, RefusalReason.PROPOSAL_REQUIRED)
```

- [ ] **Step 6: Run GREEN and workflow regression**

```bash
python -m pytest tests/test_dev_workflow_policies.py -q
python -m pytest tests/test_dev_workflow_state.py tests/test_dev_workflow_policies.py -q
```

Expected: all pass.

- [ ] **Step 7: Commit Task 5**

```bash
git add loadout/dev/workflow.py tests/test_dev_workflow_policies.py
git commit -m "feat: encode native developer workflow gates"
```

---

### Task 6: Public API, Hostile Witness Map, README, and Fresh Verification

**Files:**
- Modify: `loadout/dev/__init__.py`
- Create: `tests/test_dev_public_api.py`
- Create: `evals/LOADOUT-DEV-v0.md`
- Modify: `README.md`

**Interfaces:**
- Exposes model types, `compile_world`, adapter protocol/fake, `invoke_effect`, named workflow policies, `start_workflow`, and `transition` from `loadout.dev`.

- [ ] **Step 1: Write failing public API test**

Create `tests/test_dev_public_api.py`:

```python
import loadout.dev as dev


def test_public_api_exports_v0_surface():
    expected = {
        "AdapterBody", "CapabilityRequest", "CapabilitySpec", "CompileRequest", "CompileReceipt",
        "EffectClass", "EffectIntent", "EffectReceipt", "OwnerGate", "RefusalReason", "WorkflowEvent",
        "compile_world", "Adapter", "FakeAdapter", "invoke_effect",
        "DEV_IMPLEMENT", "DEV_DEBUG", "DEV_REVIEW", "DEV_LAND", "DEV_DOCS",
        "start_workflow", "transition",
    }
    assert expected <= set(dev.__all__)
    for name in expected:
        assert hasattr(dev, name)
```

- [ ] **Step 2: Run RED**

```bash
python -m pytest tests/test_dev_public_api.py -q
```

Expected: failure because `loadout.dev` has not exported the runtime surface.

- [ ] **Step 3: Export the exact v0 surface**

Replace `loadout/dev/__init__.py` with:

```python
from loadout.dev.adapters import Adapter, FakeAdapter
from loadout.dev.compiler import compile_world
from loadout.dev.membrane import invoke_effect
from loadout.dev.model import (
    AdapterBody,
    CapabilityRequest,
    CapabilitySpec,
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
    "Adapter", "AdapterBody", "CapabilityRequest", "CapabilitySpec", "CompileReceipt", "CompileRequest",
    "DEV_DEBUG", "DEV_DOCS", "DEV_IMPLEMENT", "DEV_LAND", "DEV_REVIEW",
    "EffectClass", "EffectIntent", "EffectReceipt", "FakeAdapter", "OwnerGate", "RefusalReason",
    "WorkflowEvent", "compile_world", "invoke_effect", "start_workflow", "transition",
]
```

Do not export internal helpers such as `_refuse` or `_OWNER_GATED`.

- [ ] **Step 4: Run public API GREEN**

```bash
python -m pytest tests/test_dev_public_api.py -q
```

Expected: PASS.

- [ ] **Step 5: Create hostile conformance witness map**

Create `evals/LOADOUT-DEV-v0.md` with this table:

```markdown
# LOADOUT.dev/v0 Hostile Conformance Witness

| ID | Pytest witness |
| --- | --- |
| `MENTION-BIND-001` | `tests/test_dev_compiler.py::test_mention_bind_001_provider_mention_does_not_bind` |
| `DESIGN-GATE-001` | `tests/test_dev_workflow_policies.py::test_design_gate_001_requires_attributed_design_admission` |
| `RED-FIRST-001` | `tests/test_dev_workflow_policies.py::test_red_first_001_red_witness_precedes_mutation` |
| `ROOT-CAUSE-001` | `tests/test_dev_workflow_policies.py::test_root_cause_001_requires_hypothesis_and_probe_before_repair` |
| `VERIFY-FRESH-001` | `tests/test_dev_workflow_state.py::test_verify_fresh_001_mutation_expires_prior_verification` |
| `HEAD-DRIFT-001` | `tests/test_dev_workflow_state.py::test_head_drift_001_invalidates_ready_and_owner_admission` |
| `EFFECT-FENCE-001` | `tests/test_dev_membrane.py::test_effect_fence_001_observe_binding_cannot_mutate` |
| `REVIEW-SCOPE-001` | `tests/test_dev_workflow_policies.py::test_review_scope_001_out_of_scope_pressure_cannot_expand_repair` |
| `DOC-PUBLISH-001` | `tests/test_dev_workflow_policies.py::test_doc_publish_001_publish_requires_prior_proposal` |
| `WOLFRAM-FENCE-001` | `tests/test_dev_membrane.py::test_wolfram_fence_001_inspect_binding_cannot_invoke_evaluate` |
| `BODY-PIN-001` | `tests/test_dev_compiler.py::test_body_pin_001_replay_requires_exact_pin` |
| `RESULT-LAUNDER-001` | `tests/test_dev_membrane.py::test_result_launder_001_success_never_mints_semantic_authority` |
| `LAND-OBSERVE-001` | `tests/test_dev_membrane.py::test_land_observe_001_queued_request_is_not_observed_merge` |

Run all witnesses with `python -m pytest -q`. No live credentials or network access are involved.
```

- [ ] **Step 6: Update README status without overstating capability**

Replace the current `## Status` paragraph with:

```markdown
## Status

`LOADOUT.dev/v0` has a deterministic executable conformance floor for provider-independent capability compilation, body-declared reachable effects, exact adapter-body attribution, effect fencing, state-bound workflow gates, inert effect intents/receipts, and fake-adapter hostile tests.

It does **not** yet claim live provider orchestration, credential storage, merge/publication automation, background watching, full Dogram lowering, a production daemon, network authority, or a master ontology.

See `docs/specs/2026-08-28-loadout-dev-native-developer-toolset.md`, `docs/superpowers/plans/2026-08-28-loadout-dev-v0.md`, and `evals/LOADOUT-DEV-v0.md`.
```

- [ ] **Step 7: Fresh full-suite verification**

```bash
python -m pytest -q
python -m compileall -q loadout
```

Expected: pytest passes fully; compileall exits 0 with no output.

- [ ] **Step 8: Verify hostile corpus completeness**

```bash
python - <<'PY'
from pathlib import Path
required = {
    "MENTION-BIND-001", "DESIGN-GATE-001", "RED-FIRST-001", "ROOT-CAUSE-001",
    "VERIFY-FRESH-001", "HEAD-DRIFT-001", "EFFECT-FENCE-001", "REVIEW-SCOPE-001",
    "DOC-PUBLISH-001", "WOLFRAM-FENCE-001", "BODY-PIN-001", "RESULT-LAUNDER-001",
    "LAND-OBSERVE-001",
}
text = Path("evals/LOADOUT-DEV-v0.md").read_text()
missing = sorted(case for case in required if case not in text)
assert not missing, missing
print("hostile-corpus:13/13")
PY
```

Expected: `hostile-corpus:13/13`.

- [ ] **Step 9: Inspect diff and forbidden scope**

```bash
git diff --check
git status --short
git diff --stat $(git merge-base HEAD main)..HEAD
```

Verify there are no credential files, live provider SDKs/calls, network clients, daemons, Dogram runtime changes, plugin installers, or unrelated edits.

- [ ] **Step 10: Commit Task 6**

```bash
git add loadout/dev/__init__.py tests/test_dev_public_api.py evals/LOADOUT-DEV-v0.md README.md
git commit -m "docs: seal LOADOUT.dev v0 conformance floor"
```

- [ ] **Step 11: Post-commit verification before any completion claim**

```bash
python -m pytest -q
python -m compileall -q loadout
git status --short
```

Expected: full suite green, compileall exit 0, clean worktree.

---

## Spec Coverage Map

| Spec requirement | Plan task(s) |
| --- | --- |
| provider-independent compile model | 1–2 |
| body-declared capability + reachable-effect classification | 1–2 |
| exact target cut | 2–3 |
| exact adapter/body attribution | 1–3 |
| replay pin / no latest wins | 2 |
| same native semantic request across replaceable adapters | 2 |
| inert intent/receipt | 1, 3 |
| adapter protocol + deterministic fake adapter | 3 |
| GitHub/GitBook/Wolfram-shaped fixtures | 2 |
| read/effect non-laundering | 2–3 |
| Wolfram inspect/evaluate separation | 2–3 |
| state-bound verification/readiness/admission | 4 |
| head/state drift invalidation | 4 |
| design gate | 5 |
| RED-before-mutation gate | 5 |
| root-cause-before-repair gate | 5 |
| review scope preservation | 5 |
| proposal-before-publication gate | 5 |
| provider request != observed landing | 3 |
| successful execution != semantic authority | 3 |
| complete hostile corpus | 2–6 |
| no live provider credentials/network | all |
| public v0 API and durable witness map | 6 |
| CLI | deliberately deferred; not required for v0 proof |
| Dogram lowering | deliberately deferred per design Phase B+ |

## Execution Notes

- Before Task 1, create an isolated worktree using `superpowers:using-git-worktrees`.
- Implement one task at a time. Do not pre-create later production files.
- Each task gets its own RED → observed failure → minimal GREEN → focused regression → commit cycle.
- Use one fresh review gate per task; a reviewer should be able to reject one task independently.
- Keep `available_bodies` explicit input in v0; do not add a plugin discovery framework.
- Keep effect matching exact; do not add a generalized effect hierarchy.
- Keep credentials outside all body/receipt types.
- Do not substitute live GitHub/GitBook/Wolfram calls for the fake adapter in this plan.
- Do not claim completion from focused tests; only the final fresh full-suite and post-commit verification authorize a completion statement.

## Execution Handoff

Implementation is intentionally not admitted by this plan alone. After review, choose either:

1. **Subagent-Driven (recommended)** — execute one task at a time with a fresh worker/review gate per task.
2. **Inline Execution** — execute the same plan in-session with explicit checkpoints.
