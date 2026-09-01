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
FAKE_PROVIDER = Path(__file__).parent / "fixtures" / "fake_openmanus_provider.py"


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
