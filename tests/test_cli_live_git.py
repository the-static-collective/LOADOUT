import json
import subprocess
from pathlib import Path

from loadout.cli import main


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_resolve_live_git_reads_one_pinned_local_occurrence(tmp_path, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "loadout@example.invalid")
    _git(repo, "config", "user.name", "LOADOUT test")

    manifest = {
        "schema": "static-collective/current-organ/v0",
        "organ": "loadout-test",
        "owner": "the-static-collective/LOADOUT",
        "entrypoint": "skills/loadout/SKILL.md",
        "state": None,
        "allowed_roots": ["skills/loadout", "docs"],
        "resolution": "default-branch-head-then-pin",
        "fallback": "embedded-bootstrap",
    }
    (repo / ".live").mkdir()
    (repo / "skills/loadout").mkdir(parents=True)
    (repo / "docs").mkdir()
    (repo / ".live/current-organ.json").write_text(json.dumps(manifest), encoding="utf-8")
    (repo / "skills/loadout/SKILL.md").write_text("# current skill\n", encoding="utf-8")
    (repo / "docs/needed.md").write_text("needed\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "fixture")
    pinned_sha = _git(repo, "rev-parse", "HEAD")

    assert main([
        "resolve-live-git",
        str(repo),
        "--body-time-id",
        "body:test-cli-live-git",
        "--ref",
        "HEAD",
        "--path",
        "docs/needed.md",
    ]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "RESOLVED"
    assert output["receipt"]["resolved_sha"] == pinned_sha
    assert output["receipt"]["loaded"] == ["skills/loadout/SKILL.md", "docs/needed.md"]
    assert output["documents"]["docs/needed.md"] == "needed\n"
