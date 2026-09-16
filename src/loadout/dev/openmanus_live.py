from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Mapping

from loadout.dev.openmanus import OPENMANUS_ADAPTER_ID, OpenManusProviderReceipt

PINNED_OPENMANUS_SHA = "3309bf4e416fb1c74b008f3e86494439a31bad53"
PINNED_BODY_ID = f"{OPENMANUS_ADAPTER_ID}@{PINNED_OPENMANUS_SHA}"
LIVE_BUNDLE_SCHEMA = "loadout.openmanus-live-001/v0"
SPECIMEN_INPUT_PATH = "specimen/input.txt"
SPECIMEN_OUTPUT_PATH = "specimen/output.txt"
SPECIMEN_INPUT_BYTES = b"OPENMANUS-LIVE-001 INPUT" + bytes([10])
SPECIMEN_OUTPUT_BYTES = b"OPENMANUS-LIVE-001 OUTPUT" + bytes([10])

_EXPECTED_BUNDLE_KEYS = frozenset(
    {
        "schema",
        "provider",
        "specimen",
        "before",
        "after",
        "provider_receipt",
        "effect_receipt",
        "runtime",
    }
)
_SHA40 = re.compile(r"^[0-9a-f]{40}$")


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def snapshot_workspace(root: Path) -> dict[str, str]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError("workspace root must exist")
    result: dict[str, str] = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        result[path.relative_to(root).as_posix()] = _sha256(path.read_bytes())
    return result


def workspace_state_id(snapshot: Mapping[str, str]) -> str:
    payload = json.dumps(
        dict(sorted(snapshot.items())), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "workspace-state:" + _sha256(payload)


def resolve_git_head(repo: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo.resolve()), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
        shell=False,
    )
    value = completed.stdout.strip()
    if completed.returncode != 0 or _SHA40.fullmatch(value) is None:
        raise ValueError("provider checkout identity unavailable")
    return value


def provider_tracked_tree_clean(repo: Path) -> bool:
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(repo.resolve()),
            "status",
            "--porcelain=v1",
            "--untracked-files=no",
        ],
        check=False,
        capture_output=True,
        text=True,
        shell=False,
    )
    if completed.returncode != 0:
        raise ValueError("provider checkout status unavailable")
    return completed.stdout == ""


def build_child_env(
    provider_checkout: Path,
    forwarded_names: tuple[str, ...],
    source_env: Mapping[str, str],
) -> dict[str, str]:
    env = {"PYTHONPATH": str(provider_checkout.resolve())}
    for name in sorted(set(forwarded_names)):
        if not name or "=" in name or name not in source_env:
            raise ValueError(f"missing explicit environment variable: {name}")
        env[name] = source_env[name]
    return env


def safe_provider_receipt(receipt: OpenManusProviderReceipt) -> dict[str, object]:
    artifact_paths: list[str] = []
    for artifact in receipt.artifacts:
        if isinstance(artifact, dict) and isinstance(artifact.get("path"), str):
            artifact_paths.append(artifact["path"])

    observation_tools: list[str] = []
    for observation in receipt.observations:
        if isinstance(observation, dict) and isinstance(observation.get("tool"), str):
            observation_tools.append(observation["tool"])

    return {
        "body_time_id": receipt.body_time_id,
        "capability": receipt.capability,
        "effect": receipt.effect.value,
        "target": receipt.target,
        "precondition_state": receipt.precondition_state,
        "disposition": receipt.disposition,
        "observed_post_state": receipt.observed_post_state,
        "artifact_paths": artifact_paths,
        "observation_tools": observation_tools,
        "steps_executed": receipt.steps_executed,
        "termination": receipt.termination,
        "stderr_present": bool(receipt.stderr),
    }


def _as_dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _append_once(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def verify_live_bundle(
    bundle_path: Path,
    workspace_root: Path,
) -> tuple[bool, tuple[str, ...]]:
    try:
        value = json.loads(bundle_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("live bundle must be readable JSON") from error
    if not isinstance(value, dict):
        raise ValueError("live bundle must be a JSON object")

    reasons: list[str] = []
    if set(value) != _EXPECTED_BUNDLE_KEYS or value.get("schema") != LIVE_BUNDLE_SCHEMA:
        _append_once(reasons, "WRONG_SCHEMA")

    provider = _as_dict(value.get("provider"))
    if (
        provider.get("checkout_sha") != PINNED_OPENMANUS_SHA
        or provider.get("body_time_id") != PINNED_BODY_ID
    ):
        _append_once(reasons, "PIN_MISMATCH")

    specimen = _as_dict(value.get("specimen"))
    if specimen.get("effect") != "LOCAL_MUTATE":
        _append_once(reasons, "WRONG_EFFECT")
    if specimen.get("target") != "workspace:specimen":
        _append_once(reasons, "WRONG_TARGET")
    if specimen.get("input_path") != SPECIMEN_INPUT_PATH:
        _append_once(reasons, "WRONG_INPUT")
    if specimen.get("output_path") != SPECIMEN_OUTPUT_PATH:
        _append_once(reasons, "WRONG_OUTPUT")

    workspace = workspace_root.resolve()
    input_path = workspace / SPECIMEN_INPUT_PATH
    output_path = workspace / SPECIMEN_OUTPUT_PATH
    try:
        input_bytes = input_path.read_bytes()
    except OSError:
        input_bytes = None
    try:
        output_bytes = output_path.read_bytes()
    except OSError:
        output_bytes = None
    if input_bytes != SPECIMEN_INPUT_BYTES:
        _append_once(reasons, "WRONG_INPUT")
    if output_bytes != SPECIMEN_OUTPUT_BYTES:
        _append_once(reasons, "WRONG_OUTPUT")

    before = _as_dict(value.get("before"))
    after = _as_dict(value.get("after"))
    observed_after = snapshot_workspace(workspace)
    if after != observed_after:
        _append_once(reasons, "SNAPSHOT_MISMATCH")

    changed = {
        path
        for path in set(before) | set(after)
        if before.get(path) != after.get(path)
    }
    if changed != {SPECIMEN_OUTPUT_PATH}:
        _append_once(reasons, "UNEXPECTED_DELTA")

    provider_receipt = _as_dict(value.get("provider_receipt"))
    if provider_receipt.get("body_time_id") != PINNED_BODY_ID:
        _append_once(reasons, "PROVIDER_RECEIPT_IDENTITY_MISMATCH")
    if provider_receipt.get("disposition") != "COMPLETED":
        _append_once(reasons, "PROVIDER_NOT_COMPLETED")

    runtime = _as_dict(value.get("runtime"))
    steps = provider_receipt.get("steps_executed")
    max_steps = runtime.get("max_steps")
    if (
        isinstance(steps, bool)
        or not isinstance(steps, int)
        or isinstance(max_steps, bool)
        or not isinstance(max_steps, int)
        or steps < 0
        or steps > max_steps
    ):
        _append_once(reasons, "INVALID_STEP_COUNT")

    effect_receipt = _as_dict(value.get("effect_receipt"))
    if effect_receipt.get("provider_disposition") != "COMPLETED":
        _append_once(reasons, "EFFECT_RECEIPT_NOT_COMPLETED")
    if effect_receipt.get("semantic_authority") is not False:
        _append_once(reasons, "SEMANTIC_AUTHORITY_WIDENED")

    return not reasons, tuple(reasons)
