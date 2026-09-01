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
