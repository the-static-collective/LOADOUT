import pytest

from loadout.live_surface import (
    normalize_repo_path,
    resolve_current_organ,
    validate_current_organ_manifest,
)


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


def evidence(*, sha="0123456789abcdef0123456789abcdef01234567"):
    return {
        "resolved_ref": "main",
        "resolved_sha": sha,
        "files": {
            "skills/loadout/SKILL.md": "skill",
            "docs/extra.md": "extra",
            "docs/unrequested.md": "do not load",
            "src/loadout/cli.py": "code",
        },
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


def test_resolver_pins_exact_sha_and_loads_entrypoint_only_by_default():
    result = resolve_current_organ(valid_manifest(), evidence())
    assert result["status"] == "RESOLVED"
    assert result["receipt"]["resolved_sha"] == evidence()["resolved_sha"]
    assert result["receipt"]["loaded"] == ["skills/loadout/SKILL.md"]
    assert result["documents"] == {"skills/loadout/SKILL.md": "skill"}


def test_requested_path_outside_allowed_roots_is_refused():
    result = resolve_current_organ(
        valid_manifest(), evidence(), requested_paths=["src/loadout/cli.py"]
    )
    assert result["status"] == "REFUSE"
    assert result["reasons"] == ["path outside allowed roots: src/loadout/cli.py"]


def test_live_surface_002_head_move_does_not_mutate_prior_receipt():
    first = resolve_current_organ(valid_manifest(), evidence(sha="a" * 40))
    second = resolve_current_organ(valid_manifest(), evidence(sha="b" * 40))
    assert first["receipt"]["resolved_sha"] == "a" * 40
    assert second["receipt"]["resolved_sha"] == "b" * 40


def test_live_surface_007_does_not_overfetch_unrequested_files():
    result = resolve_current_organ(
        valid_manifest(), evidence(), requested_paths=["docs/extra.md"]
    )
    assert result["receipt"]["loaded"] == [
        "skills/loadout/SKILL.md",
        "docs/extra.md",
    ]
    assert "docs/unrequested.md" not in result["documents"]


def test_live_surface_008_same_branch_name_is_not_replay_identity():
    first = resolve_current_organ(valid_manifest(), evidence(sha="1" * 40))
    second = resolve_current_organ(valid_manifest(), evidence(sha="2" * 40))
    assert first["receipt"]["resolved_ref"] == second["receipt"]["resolved_ref"] == "main"
    assert first["receipt"]["resolved_sha"] != second["receipt"]["resolved_sha"]
