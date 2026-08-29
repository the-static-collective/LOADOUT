from __future__ import annotations


def validate_historical_manifest(manifest: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["MANIFEST_NOT_OBJECT"]
    if manifest.get("schema") != "loadout.manifest/v0":
        errors.append("MANIFEST_SCHEMA_INVALID")
    if manifest.get("authority") != "none":
        errors.append("HISTORICAL_AUTHORITY_MUST_BE_NONE")
    if manifest.get("promotion") != "none":
        errors.append("HISTORICAL_PROMOTION_MUST_BE_NONE")
    lifecycle = manifest.get("lifecycle")
    if not isinstance(lifecycle, dict):
        errors.append("LIFECYCLE_REQUIRED")
    elif lifecycle.get("inherits_permissions") is not False:
        errors.append("HISTORICAL_PERMISSION_INHERITANCE_FORBIDDEN")
    if not isinstance(manifest.get("compile_id"), str) or not manifest["compile_id"]:
        errors.append("COMPILE_ID_REQUIRED")
    if not isinstance(manifest.get("receipt"), dict):
        errors.append("RECEIPT_REQUIRED")
    return errors
