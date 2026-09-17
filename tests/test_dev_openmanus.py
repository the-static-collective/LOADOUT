from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from loadout.dev.compiler import compile_world
from loadout.dev.membrane import invoke_effect
from loadout.dev.model import (
    AdapterBody,
    CapabilityRequest,
    CapabilitySpec,
    CompileRequest,
    EffectClass,
    EffectIntent,
    RefusalReason,
)
from loadout.dev.openmanus import (
    OPENMANUS_ADAPTER_ID,
    OPENMANUS_ENVELOPE_SCHEMA,
    OpenManusJsonStdioAdapter,
)

UPSTREAM_SHA = "3309bf4e416fb1c74b008f3e86494439a31bad53"
BODY_ID = f"{OPENMANUS_ADAPTER_ID}@{UPSTREAM_SHA}"
FAKE_PROVIDER = Path(__file__).parent / "fixtures" / "fake_openmanus_provider.py"
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


def _adapter(tmp_path: Path, **kwargs) -> OpenManusJsonStdioAdapter:
    return OpenManusJsonStdioAdapter(
        provider_command=(sys.executable, str(FAKE_PROVIDER)),
        workspace_root=tmp_path,
        body_time_id=BODY_ID,
        **kwargs,
    )


def _compiled(capability: str, effect: EffectClass):
    return compile_world(
        CompileRequest(
            task_id="OPENMANUS-BIND-001",
            task_text="bounded worker specimen",
            cut_targets=frozenset({"workspace:fixture"}),
            requested_capabilities=(
                CapabilityRequest(
                    capability,
                    effect,
                    "workspace:fixture",
                    body_time_id=BODY_ID,
                ),
            ),
            available_bodies=(BODY,),
        )
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


def test_child_environment_is_allowlisted_not_parent_inherited(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LOADOUT_SECRET", "parent-secret")
    adapter = _adapter(tmp_path, child_env={"LOADOUT_ALLOWED": "yes"})
    adapter.invoke(_intent())
    observation = adapter.provider_receipts[-1].observations[0]
    assert observation["allowed_env"] == "yes"
    assert observation["secret_env"] is None


@pytest.mark.parametrize("mode", ["malformed", "multi", "wrong-schema"])
def test_invalid_provider_stdout_is_typed_provider_error(
    tmp_path: Path, mode: str
) -> None:
    adapter = _adapter(tmp_path)
    disposition, post_state = adapter.invoke(_intent(fixture_mode=mode))
    assert disposition == "ERROR"
    assert post_state is None
    assert adapter.provider_receipts[-1].disposition == "ERROR"


def test_provider_timeout_is_typed_provider_error(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path, timeout_seconds=0.05)
    assert adapter.invoke(_intent(fixture_mode="timeout")) == ("ERROR", None)
    assert adapter.provider_receipts[-1].termination == "TIMEOUT"


def test_unsupported_effect_refuses_before_subprocess_launch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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


def test_remote_mutation_binding_is_refused_before_openmanus_launch(tmp_path: Path) -> None:
    compiled = _compiled("worker.perform", EffectClass.OBSERVE)
    adapter = _adapter(tmp_path)
    receipt = invoke_effect(
        compiled,
        _intent(EffectClass.REMOTE_MUTATE),
        {BODY_ID: adapter},
        current_state="state:0",
    )
    assert receipt.reason == RefusalReason.EFFECT_OUTSIDE_FENCE
    assert adapter.provider_receipts == ()


def test_target_outside_cut_is_refused_before_openmanus_launch(tmp_path: Path) -> None:
    compiled = _compiled("worker.perform", EffectClass.OBSERVE)
    adapter = _adapter(tmp_path)
    intent = EffectIntent(
        "worker.perform",
        EffectClass.OBSERVE,
        "workspace:other",
        BODY_ID,
        "state:0",
        "sha256:" + "2" * 64,
    )
    receipt = invoke_effect(
        compiled,
        intent,
        {BODY_ID: adapter},
        current_state="state:0",
    )
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


def test_successful_openmanus_execution_never_mints_semantic_authority(tmp_path: Path) -> None:
    compiled = _compiled("worker.perform", EffectClass.OBSERVE)
    adapter = _adapter(tmp_path)
    receipt = invoke_effect(
        compiled,
        _intent(),
        {BODY_ID: adapter},
        current_state="state:0",
    )
    assert receipt.provider_disposition == "COMPLETED"
    assert receipt.observed_post_state == "state:1"
    assert receipt.semantic_authority is False
    assert receipt.reason is None
    assert len(adapter.provider_receipts) == 1


def test_published_openmanus_schemas_match_runtime_contract_names() -> None:
    repo_root = Path(__file__).parents[1]
    envelope_schema = json.loads(
        (repo_root / "schemas" / "openmanus-worker-envelope-v0.schema.json").read_text()
    )
    result_schema = json.loads(
        (repo_root / "schemas" / "openmanus-worker-result-v0.schema.json").read_text()
    )
    assert envelope_schema["properties"]["schema"]["const"] == OPENMANUS_ENVELOPE_SCHEMA
    assert result_schema["properties"]["schema"]["const"] == "loadout.openmanus-worker-result/v0"
    assert set(envelope_schema["properties"]["effect"]["enum"]) == {
        "OBSERVE",
        "LOCAL_COMPUTE",
        "LOCAL_MUTATE",
    }
