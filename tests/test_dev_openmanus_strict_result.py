from __future__ import annotations

import sys
from pathlib import Path

import pytest

from loadout.dev.model import EffectClass, EffectIntent
from loadout.dev.openmanus import OPENMANUS_ADAPTER_ID, OpenManusJsonStdioAdapter

UPSTREAM_SHA = "3309bf4e416fb1c74b008f3e86494439a31bad53"
BODY_ID = f"{OPENMANUS_ADAPTER_ID}@{UPSTREAM_SHA}"
FAKE_PROVIDER = Path(__file__).parent / "fixtures" / "fake_openmanus_provider.py"


def _intent(mode: str) -> EffectIntent:
    return EffectIntent(
        capability="worker.perform",
        effect=EffectClass.OBSERVE,
        target="workspace:fixture",
        body_time_id=BODY_ID,
        precondition_state="state:0",
        parameters_digest="sha256:" + "3" * 64,
        parameters=(("fixture_mode", mode),),
    )


@pytest.mark.parametrize("mode", ["extra-top", "extra-receipt", "bool-steps"])
def test_result_must_match_published_schema_exactly(tmp_path: Path, mode: str) -> None:
    adapter = OpenManusJsonStdioAdapter(
        provider_command=(sys.executable, str(FAKE_PROVIDER)),
        workspace_root=tmp_path,
        body_time_id=BODY_ID,
    )
    assert adapter.invoke(_intent(mode)) == ("ERROR", None)
    assert adapter.provider_receipts[-1].disposition == "ERROR"
