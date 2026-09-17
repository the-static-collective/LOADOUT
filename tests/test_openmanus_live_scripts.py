from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

from loadout.dev.openmanus_live import (
    LIVE_BUNDLE_SCHEMA,
    PINNED_BODY_ID,
    PINNED_OPENMANUS_SHA,
    SPECIMEN_INPUT_BYTES,
    SPECIMEN_INPUT_PATH,
    SPECIMEN_OUTPUT_BYTES,
    SPECIMEN_OUTPUT_PATH,
    snapshot_workspace,
    workspace_state_id,
)

REPO_ROOT = Path(__file__).parents[1]
BUILD_SCRIPT = REPO_ROOT / "scripts" / "openmanus-live-001.py"
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "verify-openmanus-live-001.py"


def _base_build_args(tmp_path: Path) -> list[str]:
    provider = tmp_path / "provider"
    workspace = tmp_path / "workspace"
    output = tmp_path / "receipts"
    provider.mkdir()
    workspace.mkdir()
    output.mkdir()
    return [
        sys.executable,
        str(BUILD_SCRIPT),
        "--provider-checkout",
        str(provider),
        "--provider-python",
        sys.executable,
        "--workspace",
        str(workspace),
        "--output",
        str(output),
        "--model-config-class",
        "test/model-class",
    ]


@pytest.mark.parametrize(
    ("flag", "relative_value"),
    [
        ("--provider-checkout", "relative/provider"),
        ("--provider-python", "relative/python"),
        ("--workspace", "relative/workspace"),
        ("--output", "relative/output"),
    ],
)
def test_build_requires_absolute_paths(
    tmp_path: Path,
    flag: str,
    relative_value: str,
) -> None:
    args = _base_build_args(tmp_path)
    index = args.index(flag) + 1
    args[index] = relative_value
    completed = subprocess.run(args, capture_output=True, text=True, check=False)
    assert completed.returncode == 2
    assert "must be absolute" in completed.stderr


def test_build_requires_nonempty_model_config_class(tmp_path: Path) -> None:
    args = _base_build_args(tmp_path)
    index = args.index("--model-config-class") + 1
    args[index] = ""
    completed = subprocess.run(args, capture_output=True, text=True, check=False)
    assert completed.returncode == 2
    assert "model-config-class" in completed.stderr


def test_build_refuses_output_inside_workspace(tmp_path: Path) -> None:
    args = _base_build_args(tmp_path)
    workspace = Path(args[args.index("--workspace") + 1])
    nested = workspace / "receipts"
    nested.mkdir()
    args[args.index("--output") + 1] = str(nested)
    completed = subprocess.run(args, capture_output=True, text=True, check=False)
    assert completed.returncode == 2
    assert "outside workspace" in completed.stderr


def _write_valid_bundle(tmp_path: Path) -> tuple[Path, Path]:
    workspace = tmp_path / "workspace"
    specimen = workspace / "specimen"
    receipts = tmp_path / "receipts"
    specimen.mkdir(parents=True)
    receipts.mkdir()
    (specimen / "input.txt").write_bytes(SPECIMEN_INPUT_BYTES)
    before = snapshot_workspace(workspace)
    (specimen / "output.txt").write_bytes(SPECIMEN_OUTPUT_BYTES)
    after = snapshot_workspace(workspace)
    state = workspace_state_id(before)
    bundle = {
        "schema": LIVE_BUNDLE_SCHEMA,
        "provider": {
            "checkout_sha": PINNED_OPENMANUS_SHA,
            "body_time_id": PINNED_BODY_ID,
            "tracked_tree_clean": True,
            "config_source": "config/config.toml",
            "model_config_class": "test/fake",
        },
        "specimen": {
            "effect": "LOCAL_MUTATE",
            "target": "workspace:specimen",
            "input_path": SPECIMEN_INPUT_PATH,
            "output_path": SPECIMEN_OUTPUT_PATH,
        },
        "before": before,
        "after": after,
        "provider_receipt": {
            "body_time_id": PINNED_BODY_ID,
            "capability": "worker.mutate",
            "effect": "LOCAL_MUTATE",
            "target": "workspace:specimen",
            "precondition_state": state,
            "disposition": "COMPLETED",
            "observed_post_state": "fake-live:state:1",
            "artifact_paths": [SPECIMEN_OUTPUT_PATH],
            "observation_tools": ["loadout_read_text", "loadout_write_text"],
            "steps_executed": 2,
            "termination": "FAKE_LIVE_COMPLETE",
            "stderr_present": False,
        },
        "effect_receipt": {
            "body_time_id": PINNED_BODY_ID,
            "capability": "worker.mutate",
            "effect": "LOCAL_MUTATE",
            "target": "workspace:specimen",
            "precondition_state": state,
            "provider_disposition": "COMPLETED",
            "observed_post_state": "fake-live:state:1",
            "semantic_authority": False,
            "reason": None,
        },
        "runtime": {
            "python": "3.11",
            "loadout_head": "1" * 40,
            "max_steps": 20,
            "timeout_seconds": 30.0,
            "forwarded_env_names": [],
            "cleanup": "provider_process_exited",
        },
    }
    bundle_path = receipts / "openmanus-live-001.json"
    bundle_path.write_text(json.dumps(bundle, sort_keys=True), encoding="utf-8")
    return workspace, bundle_path


def test_verify_script_returns_zero_for_independently_verified_bundle(tmp_path: Path) -> None:
    workspace, bundle = _write_valid_bundle(tmp_path)
    completed = subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT),
            "--workspace",
            str(workspace),
            "--bundle",
            str(bundle),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0
    assert "OPENMANUS-LIVE-001 VERIFIED" in completed.stdout


def test_verify_script_returns_hold_reasons_for_failed_evidence(tmp_path: Path) -> None:
    workspace, bundle = _write_valid_bundle(tmp_path)
    (workspace / SPECIMEN_OUTPUT_PATH).write_bytes(b"WRONG" + bytes([10]))
    value = json.loads(bundle.read_text(encoding="utf-8"))
    value["after"] = snapshot_workspace(workspace)
    bundle.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT),
            "--workspace",
            str(workspace),
            "--bundle",
            str(bundle),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 1
    assert "OPENMANUS-LIVE-001 HOLD" in completed.stderr
    assert "WRONG_OUTPUT" in completed.stderr
