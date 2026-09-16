from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from loadout.dev.model import EffectClass
from loadout.dev.openmanus import OpenManusProviderReceipt
from loadout.dev.openmanus_live import (
    LIVE_BUNDLE_SCHEMA,
    PINNED_BODY_ID,
    PINNED_OPENMANUS_SHA,
    SPECIMEN_INPUT_BYTES,
    SPECIMEN_INPUT_PATH,
    SPECIMEN_OUTPUT_BYTES,
    SPECIMEN_OUTPUT_PATH,
    build_child_env,
    provider_tracked_tree_clean,
    resolve_git_head,
    safe_provider_receipt,
    snapshot_workspace,
    verify_live_bundle,
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


def _write_bundle(tmp_path: Path) -> tuple[Path, Path]:
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
    return bundle_path, workspace


def _load_bundle(bundle_path: Path) -> dict[str, object]:
    return json.loads(bundle_path.read_text(encoding="utf-8"))


def _save_bundle(bundle_path: Path, bundle: dict[str, object]) -> None:
    bundle_path.write_text(json.dumps(bundle, sort_keys=True), encoding="utf-8")


def test_verifier_accepts_exact_expected_mutation(tmp_path: Path) -> None:
    bundle_path, workspace = _write_bundle(tmp_path)
    assert verify_live_bundle(bundle_path, workspace) == (True, ())


def test_verifier_rejects_wrong_output(tmp_path: Path) -> None:
    bundle_path, workspace = _write_bundle(tmp_path)
    (workspace / SPECIMEN_OUTPUT_PATH).write_bytes(b"WRONG" + bytes([10]))
    bundle = _load_bundle(bundle_path)
    bundle["after"] = snapshot_workspace(workspace)
    _save_bundle(bundle_path, bundle)
    passed, reasons = verify_live_bundle(bundle_path, workspace)
    assert passed is False
    assert "WRONG_OUTPUT" in reasons


def test_verifier_rejects_modified_input(tmp_path: Path) -> None:
    bundle_path, workspace = _write_bundle(tmp_path)
    (workspace / SPECIMEN_INPUT_PATH).write_bytes(b"CHANGED" + bytes([10]))
    bundle = _load_bundle(bundle_path)
    bundle["after"] = snapshot_workspace(workspace)
    _save_bundle(bundle_path, bundle)
    passed, reasons = verify_live_bundle(bundle_path, workspace)
    assert passed is False
    assert "WRONG_INPUT" in reasons


def test_verifier_rejects_unexpected_workspace_delta(tmp_path: Path) -> None:
    bundle_path, workspace = _write_bundle(tmp_path)
    (workspace / "specimen" / "rogue.txt").write_text("rogue", encoding="utf-8")
    bundle = _load_bundle(bundle_path)
    bundle["after"] = snapshot_workspace(workspace)
    _save_bundle(bundle_path, bundle)
    passed, reasons = verify_live_bundle(bundle_path, workspace)
    assert passed is False
    assert "UNEXPECTED_DELTA" in reasons


def test_verifier_rejects_wrong_provider_pin(tmp_path: Path) -> None:
    bundle_path, workspace = _write_bundle(tmp_path)
    bundle = _load_bundle(bundle_path)
    provider = bundle["provider"]
    assert isinstance(provider, dict)
    provider["checkout_sha"] = "2" * 40
    _save_bundle(bundle_path, bundle)
    passed, reasons = verify_live_bundle(bundle_path, workspace)
    assert passed is False
    assert "PIN_MISMATCH" in reasons


def test_verifier_rejects_provider_not_completed(tmp_path: Path) -> None:
    bundle_path, workspace = _write_bundle(tmp_path)
    bundle = _load_bundle(bundle_path)
    provider_receipt = bundle["provider_receipt"]
    assert isinstance(provider_receipt, dict)
    provider_receipt["disposition"] = "REFUSED"
    _save_bundle(bundle_path, bundle)
    passed, reasons = verify_live_bundle(bundle_path, workspace)
    assert passed is False
    assert "PROVIDER_NOT_COMPLETED" in reasons


def test_verifier_rejects_semantic_authority(tmp_path: Path) -> None:
    bundle_path, workspace = _write_bundle(tmp_path)
    bundle = _load_bundle(bundle_path)
    effect_receipt = bundle["effect_receipt"]
    assert isinstance(effect_receipt, dict)
    effect_receipt["semantic_authority"] = True
    _save_bundle(bundle_path, bundle)
    passed, reasons = verify_live_bundle(bundle_path, workspace)
    assert passed is False
    assert "SEMANTIC_AUTHORITY_WIDENED" in reasons


def test_verifier_rejects_bundle_snapshot_disagreement(tmp_path: Path) -> None:
    bundle_path, workspace = _write_bundle(tmp_path)
    bundle = _load_bundle(bundle_path)
    after = bundle["after"]
    assert isinstance(after, dict)
    after[SPECIMEN_OUTPUT_PATH] = "sha256:" + "f" * 64
    _save_bundle(bundle_path, bundle)
    passed, reasons = verify_live_bundle(bundle_path, workspace)
    assert passed is False
    assert "SNAPSHOT_MISMATCH" in reasons


def _init_git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "provider"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
    (repo / "tracked.txt").write_text("tracked", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "tracked.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "init"], check=True, capture_output=True)
    return repo


def test_resolve_git_head_returns_lowercase_sha40(tmp_path: Path) -> None:
    repo = _init_git_repo(tmp_path)
    head = resolve_git_head(repo)
    assert len(head) == 40
    assert head == head.lower()
    assert all(char in "0123456789abcdef" for char in head)


def test_provider_tracked_tree_clean_rejects_modified_tracked_file(tmp_path: Path) -> None:
    repo = _init_git_repo(tmp_path)
    (repo / "tracked.txt").write_text("changed", encoding="utf-8")
    assert provider_tracked_tree_clean(repo) is False


def test_provider_tracked_tree_clean_allows_untracked_config_file(tmp_path: Path) -> None:
    repo = _init_git_repo(tmp_path)
    config = repo / "config"
    config.mkdir()
    (config / "config.toml").write_text("secret = 'local-only'", encoding="utf-8")
    assert provider_tracked_tree_clean(repo) is True


def test_child_env_contains_only_pythonpath_and_forwarded_names(tmp_path: Path) -> None:
    checkout = tmp_path / "provider"
    checkout.mkdir()
    source = {
        "HTTPS_PROXY": "http://proxy.example",
        "HOME": "/secret/home",
        "PATH": "/secret/path",
        "API_KEY": "do-not-forward",
    }
    assert build_child_env(checkout, ("HTTPS_PROXY",), source) == {
        "PYTHONPATH": str(checkout.resolve()),
        "HTTPS_PROXY": "http://proxy.example",
    }


def test_child_env_refuses_missing_forwarded_name(tmp_path: Path) -> None:
    checkout = tmp_path / "provider"
    checkout.mkdir()
    with pytest.raises(ValueError, match="missing explicit environment variable"):
        build_child_env(checkout, ("MISSING",), {})


def test_safe_provider_receipt_drops_free_form_content_and_stderr() -> None:
    secret = "sk-super-secret-value"
    receipt = OpenManusProviderReceipt(
        body_time_id=PINNED_BODY_ID,
        capability="worker.mutate",
        effect=EffectClass.LOCAL_MUTATE,
        target="workspace:specimen",
        precondition_state="workspace-state:sha256:" + "1" * 64,
        disposition="COMPLETED",
        observed_post_state="state:1",
        artifacts=({"path": SPECIMEN_OUTPUT_PATH, "content": secret},),
        observations=(
            {"tool": "loadout_read_text", "content": secret},
            {"tool": "loadout_write_text", "relative_path": SPECIMEN_OUTPUT_PATH},
        ),
        steps_executed=2,
        termination="TERMINATE",
        stderr=f"provider diagnostic {secret}",
    )

    safe = safe_provider_receipt(receipt)

    assert safe == {
        "body_time_id": PINNED_BODY_ID,
        "capability": "worker.mutate",
        "effect": "LOCAL_MUTATE",
        "target": "workspace:specimen",
        "precondition_state": "workspace-state:sha256:" + "1" * 64,
        "disposition": "COMPLETED",
        "observed_post_state": "state:1",
        "artifact_paths": [SPECIMEN_OUTPUT_PATH],
        "observation_tools": ["loadout_read_text", "loadout_write_text"],
        "steps_executed": 2,
        "termination": "TERMINATE",
        "stderr_present": True,
    }
    serialized = json.dumps(safe, sort_keys=True)
    assert secret not in serialized
