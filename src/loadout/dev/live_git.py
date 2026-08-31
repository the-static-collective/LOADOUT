from __future__ import annotations

import json
from typing import Iterable

from loadout.dev.local_git import LocalGitReadAdapter
from loadout.dev.model import EffectClass, EffectIntent
from loadout.live_surface import (
    MANIFEST_PATH,
    normalize_repo_path,
    resolve_current_organ,
    unresolved_current_organ,
)


_PARAMETERS_DIGEST = "sha256:" + "0" * 64


def _intent(
    adapter: LocalGitReadAdapter,
    capability: str,
    parameters: Iterable[tuple[str, str]],
) -> EffectIntent:
    return EffectIntent(
        capability,
        EffectClass.OBSERVE,
        "repo:local",
        adapter.body_time_id,
        "state:live-surface",
        _PARAMETERS_DIGEST,
        parameters=tuple(parameters),
    )


def _read_result_text(
    adapter: LocalGitReadAdapter,
    capability: str,
    parameters: Iterable[tuple[str, str]],
) -> tuple[str, str]:
    status, result_ref = adapter.invoke(_intent(adapter, capability, parameters))
    if status != "RESOLVED" or result_ref is None:
        return status, result_ref or "UNRESOLVED"
    try:
        return "RESOLVED", adapter.read_result(result_ref).decode("utf-8")
    except UnicodeDecodeError:
        return "UNRESOLVED", "NON_UTF8_BLOB"


def _unresolved_without_manifest(reason: str) -> dict[str, object]:
    return unresolved_current_organ({}, reason=reason)


def resolve_current_organ_from_git(
    adapter: LocalGitReadAdapter,
    *,
    ref: str = "HEAD",
    requested_paths: Iterable[str] = (),
) -> dict[str, object]:
    """Resolve one CURRENT-ORGAN occurrence entirely through a read-only adapter."""

    status, resolved_text = _read_result_text(
        adapter,
        "git.resolve_ref",
        (("ref", ref),),
    )
    if status != "RESOLVED":
        return _unresolved_without_manifest(f"git.resolve_ref {status}: {resolved_text}")
    resolved_sha = resolved_text.strip()

    status, manifest_text = _read_result_text(
        adapter,
        "git.read_blob",
        (("commit_sha", resolved_sha), ("path", MANIFEST_PATH), ("text", "true")),
    )
    if status != "RESOLVED":
        return _unresolved_without_manifest(f"current-organ manifest {status}: {manifest_text}")

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError:
        return {
            "status": "REFUSE",
            "reasons": ["manifest content at resolved SHA is not valid JSON"],
            "documents": {},
            "receipt": None,
        }

    paths = [manifest.get("entrypoint")]
    for raw_path in requested_paths:
        try:
            path = normalize_repo_path(raw_path)
        except ValueError:
            path = raw_path
        if path not in paths:
            paths.append(path)

    evidence: dict[str, object] = {
        "owner": manifest.get("owner"),
        "resolved_ref": ref,
        "resolved_sha": resolved_sha,
        "files": {MANIFEST_PATH: manifest_text},
    }

    preflight = resolve_current_organ(
        manifest,
        evidence,
        requested_paths=list(requested_paths),
    )
    if preflight["status"] == "REFUSE":
        return preflight

    files = evidence["files"]
    assert isinstance(files, dict)
    for path in paths:
        if not isinstance(path, str):
            return resolve_current_organ(
                manifest,
                evidence,
                requested_paths=list(requested_paths),
            )
        status, body = _read_result_text(
            adapter,
            "git.read_blob",
            (("commit_sha", resolved_sha), ("path", path), ("text", "true")),
        )
        if status != "RESOLVED":
            return unresolved_current_organ(
                manifest,
                reason=f"local git read {status}: {path}: {body}",
            )
        files[path] = body

    return resolve_current_organ(
        manifest,
        evidence,
        requested_paths=list(requested_paths),
    )


__all__ = ["resolve_current_organ_from_git"]
