from __future__ import annotations

import sys
from pathlib import Path

from loadout.dev.model import EffectClass, EffectIntent
from loadout.dev.openmanus import OPENMANUS_ADAPTER_ID, OpenManusJsonStdioAdapter


UPSTREAM_SHA = "3309bf4e416fb1c74b008f3e86494439a31bad53"
BODY_ID = f"{OPENMANUS_ADAPTER_ID}@{UPSTREAM_SHA}"


def test_workspace_traversal_target_refuses_before_provider_launch(
    tmp_path: Path, monkeypatch
) -> None:
    adapter = OpenManusJsonStdioAdapter(
        provider_command=(sys.executable, "-c", "pass"),
        workspace_root=tmp_path,
        body_time_id=BODY_ID,
    )
    intent = EffectIntent(
        capability="worker.perform",
        effect=EffectClass.OBSERVE,
        target="workspace:../outside",
        body_time_id=BODY_ID,
        precondition_state="state:0",
        parameters_digest="sha256:" + "1" * 64,
        parameters=(("request", "inspect the target"),),
    )
    launched = False

    def fail_if_called(*args, **kwargs):
        nonlocal launched
        launched = True
        raise AssertionError("provider must not launch for an escaped workspace target")

    monkeypatch.setattr("loadout.dev.openmanus.subprocess.run", fail_if_called)

    assert adapter.invoke(intent) == ("REFUSE", None)
    assert launched is False
    assert adapter.provider_receipts == ()
