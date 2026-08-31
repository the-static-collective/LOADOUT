from __future__ import annotations

import json
import subprocess
from pathlib import Path

from loadout.dev.live_git import resolve_current_organ_from_git
from loadout.dev.local_git import LocalGitReadAdapter
from loadout.dev.model import EffectClass, EffectIntent


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _commit(root: Path, message: str) -> str:
    _git(root, "add", ".")
    _git(root, "commit", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def _manifest() -> dict[str, object]:
    return {
        "schema": "static-collective/current-organ/v0",
        "organ": "fixture-organ",
        "owner": "fixture/local-organ",
        "entrypoint": "skills/loadout/SKILL.md",
        "state": None,
        "allowed_roots": ["skills/loadout"],
        "resolution": "default-branch-head-then-pin",
        "fallback": "embedded-bootstrap",
    }


def _read_blob(adapter: LocalGitReadAdapter, sha: str, path: str) -> bytes:
    intent = EffectIntent(
        "git.read_blob",
        EffectClass.OBSERVE,
        "repo:local",
        adapter.body_time_id,
        "state:integration",
        "sha256:" + "0" * 64,
        parameters=(("commit_sha", sha), ("path", path), ("text", "true")),
    )
    status, result_ref = adapter.invoke(intent)
    assert status == "RESOLVED"
    assert result_ref is not None
    return adapter.read_result(result_ref)


def test_current_organ_resolves_live_but_stays_pinned_within_occurrence(tmp_path: Path) -> None:
    root = tmp_path / "organ"
    root.mkdir()
    subprocess.run(["git", "init", str(root)], check=True, capture_output=True, text=True)
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "config", "user.name", "LOADOUT-Test")
    (root / ".live").mkdir()
    (root / "skills" / "loadout").mkdir(parents=True)
    manifest = _manifest()
    (root / ".live" / "current-organ.json").write_text(
        json.dumps(manifest, sort_keys=True), encoding="utf-8"
    )
    skill = root / "skills" / "loadout" / "SKILL.md"
    skill.write_text("skill-v1\n", encoding="utf-8")
    first_sha = _commit(root, "first")

    adapter = LocalGitReadAdapter(
        root,
        body_time_id="local-git@integration",
        allowed_roots=(".live", "skills/loadout"),
    )
    first = resolve_current_organ_from_git(adapter, ref="HEAD")
    assert first["status"] == "RESOLVED"
    assert first["receipt"]["resolved_sha"] == first_sha
    assert first["receipt"]["loaded"] == ["skills/loadout/SKILL.md"]
    assert first["documents"] == {"skills/loadout/SKILL.md": "skill-v1\n"}

    skill.write_text("skill-v2\n", encoding="utf-8")
    second_sha = _commit(root, "second")
    second = resolve_current_organ_from_git(adapter, ref="HEAD")
    assert second["status"] == "RESOLVED"
    assert second["receipt"]["resolved_sha"] == second_sha
    assert second["documents"] == {"skills/loadout/SKILL.md": "skill-v2\n"}

    assert first["receipt"]["resolved_sha"] == first_sha
    assert first["documents"] == {"skills/loadout/SKILL.md": "skill-v1\n"}
    assert _read_blob(adapter, first_sha, "skills/loadout/SKILL.md") == b"skill-v1\n"


def test_current_organ_integration_uses_adapter_not_a_second_git_surface() -> None:
    source = (
        Path(__file__).parents[1] / "src" / "loadout" / "dev" / "live_git.py"
    ).read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert "os.system" not in source
    assert "shell=" not in source
