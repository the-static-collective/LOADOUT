import pytest

from loadout.live_surface import normalize_repo_path, validate_current_organ_manifest


def valid_manifest():
    return {
        "schema": "static-collective/current-organ/v0",
        "organ": "loadout",
        "owner": "the-static-collective/LOADOUT",
        "entrypoint": "skills/loadout/SKILL.md",
        "state": None,
        "allowed_roots": ["skills/loadout", "docs", "schemas"],
        "resolution": "default-branch-head-then-pin",
        "fallback": "embedded-bootstrap",
    }


def test_valid_manifest_has_no_errors():
    assert validate_current_organ_manifest(valid_manifest()) == []


def test_manifest_rejects_wrong_schema_and_unsafe_entrypoint():
    manifest = valid_manifest()
    manifest["schema"] = "wrong"
    manifest["entrypoint"] = "../ALEX/SKILL.md"
    errors = validate_current_organ_manifest(manifest)
    assert "unsupported schema" in errors
    assert "entrypoint is not a safe repository-relative path" in errors


def test_normalize_repo_path_refuses_escape():
    with pytest.raises(ValueError, match="unsafe repository path"):
        normalize_repo_path("skills/loadout/../../secret")


def test_manifest_rejects_unknown_top_level_fields():
    manifest = valid_manifest()
    manifest["write_authority"] = True
    assert validate_current_organ_manifest(manifest) == ["unknown field: write_authority"]
