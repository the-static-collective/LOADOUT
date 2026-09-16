from __future__ import annotations

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
    assert SPECIMEN_INPUT_BYTES == b"OPENMANUS-LIVE-001 INPUT" + bytes([10])
    assert SPECIMEN_OUTPUT_BYTES == b"OPENMANUS-LIVE-001 OUTPUT" + bytes([10])


def test_snapshot_is_stable_and_content_addressed(tmp_path: Path) -> None:
    (tmp_path / "z.txt").write_bytes(b"z")
    (tmp_path / "a.txt").write_bytes(b"a")

    first = snapshot_workspace(tmp_path)
    second = snapshot_workspace(tmp_path)

    assert list(first) == ["a.txt", "z.txt"]
    assert first == second
    assert workspace_state_id(first).startswith("workspace-state:sha256:")
