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
