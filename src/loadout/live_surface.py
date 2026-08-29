from __future__ import annotations

import re

MANIFEST_SCHEMA = "static-collective/current-organ/v0"
RECEIPT_SCHEMA = "static-collective/live-surface-receipt/v0"

_ALLOWED_MANIFEST_FIELDS = {
    "schema",
    "organ",
    "owner",
    "entrypoint",
    "state",
    "allowed_roots",
    "orientation",
    "resolution",
    "fallback",
}
_REQUIRED_MANIFEST_FIELDS = (
    "schema",
    "organ",
    "owner",
    "entrypoint",
    "allowed_roots",
    "resolution",
    "fallback",
)
_OWNER_RE = re.compile(r"^[^/\s]+/[^/\s]+$")
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def normalize_repo_path(path: str) -> str:
    if not isinstance(path, str) or not path:
        raise ValueError("unsafe repository path")
    normalized = path.replace("\\", "/")
    if normalized.startswith("/"):
        raise ValueError("unsafe repository path")
    parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("unsafe repository path")
    return "/".join(parts)


def _safe_path(path: object) -> bool:
    if not isinstance(path, str):
        return False
    try:
        normalize_repo_path(path)
    except ValueError:
        return False
    return True


def validate_current_organ_manifest(manifest: dict) -> list[str]:
    if not isinstance(manifest, dict):
        return ["manifest must be an object"]

    errors: list[str] = []

    for field in sorted(set(manifest) - _ALLOWED_MANIFEST_FIELDS):
        errors.append(f"unknown field: {field}")

    for field in _REQUIRED_MANIFEST_FIELDS:
        if field not in manifest:
            errors.append(f"missing field: {field}")

    if manifest.get("schema") != MANIFEST_SCHEMA:
        errors.append("unsupported schema")

    organ = manifest.get("organ")
    if not isinstance(organ, str) or not organ.strip():
        errors.append("organ must be a non-empty string")

    owner = manifest.get("owner")
    if not isinstance(owner, str) or _OWNER_RE.fullmatch(owner) is None:
        errors.append("owner must be repository owner/name")

    if "entrypoint" in manifest and not _safe_path(manifest.get("entrypoint")):
        errors.append("entrypoint is not a safe repository-relative path")

    state = manifest.get("state")
    if state is not None and not _safe_path(state):
        errors.append("state is not a safe repository-relative path")

    roots = manifest.get("allowed_roots")
    if not isinstance(roots, list) or not roots:
        errors.append("allowed_roots must be a non-empty list")
    elif any(not _safe_path(root) for root in roots):
        errors.append("allowed_roots contains an unsafe repository path")
    elif len(set(roots)) != len(roots):
        errors.append("allowed_roots must not contain duplicates")

    if manifest.get("resolution") != "default-branch-head-then-pin":
        errors.append("unsupported resolution policy")

    if manifest.get("fallback") != "embedded-bootstrap":
        errors.append("unsupported fallback policy")

    return errors


def _path_is_allowed(path: str, roots: list[str]) -> bool:
    return any(path == root or path.startswith(f"{root}/") for root in roots)


def _refuse(reason: str) -> dict:
    return {"status": "REFUSE", "reasons": [reason], "documents": {}, "receipt": None}


def unresolved_current_organ(
    manifest: dict,
    *,
    reason: str,
    embedded_entrypoint: str | None = None,
) -> dict:
    entrypoint = manifest.get("entrypoint") if isinstance(manifest, dict) else None
    documents = {}
    loaded: list[str] = []
    if embedded_entrypoint is not None and isinstance(entrypoint, str):
        documents[entrypoint] = embedded_entrypoint
        loaded.append(entrypoint)

    receipt = {
        "schema": RECEIPT_SCHEMA,
        "organ": manifest.get("organ") if isinstance(manifest, dict) else None,
        "owner": manifest.get("owner") if isinstance(manifest, dict) else None,
        "resolved_ref": None,
        "resolved_sha": None,
        "manifest_path": ".live/current-organ.json",
        "entrypoint": entrypoint,
        "loaded": loaded,
        "freshness": "UNRESOLVED",
        "fallback_used": embedded_entrypoint is not None,
    }
    return {
        "status": "UNRESOLVED",
        "reasons": [reason],
        "documents": documents,
        "receipt": receipt,
    }


def resolve_current_organ(
    manifest: dict,
    evidence: dict | None,
    *,
    requested_paths: list[str] | None = None,
) -> dict:
    manifest_errors = validate_current_organ_manifest(manifest)
    if manifest_errors:
        return {
            "status": "REFUSE",
            "reasons": manifest_errors,
            "documents": {},
            "receipt": None,
        }

    if evidence is None:
        return unresolved_current_organ(manifest, reason="repository evidence unavailable")
    if not isinstance(evidence, dict):
        return _refuse("repository evidence must be an object")

    resolved_ref = evidence.get("resolved_ref")
    if not isinstance(resolved_ref, str) or not resolved_ref:
        return _refuse("resolved_ref must be a non-empty string")

    resolved_sha = evidence.get("resolved_sha")
    if not isinstance(resolved_sha, str) or _SHA_RE.fullmatch(resolved_sha) is None:
        return _refuse("resolved_sha must be a lowercase 40-hex commit SHA")

    files = evidence.get("files")
    if files is None:
        return unresolved_current_organ(manifest, reason="repository files unavailable")
    if not isinstance(files, dict):
        return _refuse("files must be an object")

    load_paths = [manifest["entrypoint"]]
    for requested in requested_paths or []:
        try:
            path = normalize_repo_path(requested)
        except ValueError:
            return _refuse(f"unsafe requested path: {requested}")
        if path not in load_paths:
            load_paths.append(path)

    roots = [normalize_repo_path(root) for root in manifest["allowed_roots"]]
    for path in load_paths:
        if not _path_is_allowed(path, roots):
            return _refuse(f"path outside allowed roots: {path}")
        if path not in files:
            return unresolved_current_organ(
                manifest, reason=f"missing file at resolved SHA: {path}"
            )
        if not isinstance(files[path], str):
            return _refuse(f"file content must be text: {path}")

    documents = {path: files[path] for path in load_paths}
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "organ": manifest["organ"],
        "owner": manifest["owner"],
        "resolved_ref": resolved_ref,
        "resolved_sha": resolved_sha,
        "manifest_path": ".live/current-organ.json",
        "entrypoint": manifest["entrypoint"],
        "loaded": list(load_paths),
        "freshness": "RESOLVED",
        "fallback_used": False,
    }
    return {
        "status": "RESOLVED",
        "reasons": [],
        "documents": documents,
        "receipt": receipt,
    }
