from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from loadout.dev.local_git import LocalGitReadAdapter
from loadout.dev.model import EffectClass, EffectIntent


def _git(root: Path, *args: str, text: bool = True):
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=text,
    )


def _repo(tmp_path: Path) -> tuple[Path, str, str]:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", str(root)], check=True, capture_output=True, text=True)
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "config", "user.name", "LOADOUT-Test")
    (root / "docs").mkdir()
    (root / "private").mkdir()
    (root / "docs" / "a.txt").write_text("one\n", encoding="utf-8")
    (root / "private" / "secret.txt").write_text("secret\n", encoding="utf-8")
    _git(root, "add", "docs/a.txt", "private/secret.txt")
    _git(root, "commit", "-m", "one")
    first = _git(root, "rev-parse", "HEAD").stdout.strip()

    (root / "docs" / "a.txt").write_text("two\n", encoding="utf-8")
    (root / "docs" / "binary.bin").write_bytes(b"\xff\xfe\x00")
    _git(root, "add", "docs/a.txt", "docs/binary.bin")
    _git(root, "commit", "-m", "two")
    second = _git(root, "rev-parse", "HEAD").stdout.strip()
    return root, first, second


def _intent(capability: str, **parameters: str) -> EffectIntent:
    return EffectIntent(
        capability,
        EffectClass.OBSERVE,
        "repo:local",
        "local-git@test-body",
        "state:0",
        "sha256:" + "0" * 64,
        parameters=tuple(parameters.items()),
    )


def test_resolves_ref_and_reads_historical_blob_after_worktree_drift(tmp_path: Path) -> None:
    root, first, second = _repo(tmp_path)
    adapter = LocalGitReadAdapter(root, body_time_id="local-git@test-body", allowed_roots=("docs",))

    status, result_ref = adapter.invoke(_intent("git.resolve_ref", ref="HEAD"))
    assert status == "RESOLVED"
    assert result_ref is not None
    assert adapter.read_result(result_ref).decode("ascii").strip() == second

    status, blob_ref = adapter.invoke(_intent("git.read_blob", commit_sha=first, path="docs/a.txt"))
    assert status == "RESOLVED"
    assert blob_ref is not None
    assert adapter.read_result(blob_ref) == b"one\n"

    (root / "docs" / "a.txt").write_text("working-tree-only\n", encoding="utf-8")
    status, replay_ref = adapter.invoke(_intent("git.read_blob", commit_sha=first, path="docs/a.txt"))
    assert status == "RESOLVED"
    assert replay_ref == blob_ref
    assert adapter.read_result(replay_ref) == b"one\n"


def test_write_shaped_capability_refuses() -> None:
    adapter = LocalGitReadAdapter(Path.cwd(), body_time_id="local-git@test-body")
    assert adapter.invoke(_intent("git.commit", message="nope")) == (
        "REFUSE",
        "CAPABILITY_NOT_ALLOWED",
    )


@pytest.mark.parametrize("path", ["/etc/passwd", "../secret", "docs/../secret", ""])
def test_unsafe_paths_refuse_before_git_invocation(tmp_path: Path, path: str) -> None:
    root, first, _ = _repo(tmp_path)
    adapter = LocalGitReadAdapter(root, body_time_id="local-git@test-body", allowed_roots=("docs",))
    with patch("loadout.dev.local_git.subprocess.run") as mocked:
        assert adapter.invoke(_intent("git.read_blob", commit_sha=first, path=path)) == (
            "REFUSE",
            "PATH_OUTSIDE_FENCE",
        )
        mocked.assert_not_called()


def test_path_outside_allowed_roots_refuses_before_git_invocation(tmp_path: Path) -> None:
    root, first, _ = _repo(tmp_path)
    adapter = LocalGitReadAdapter(root, body_time_id="local-git@test-body", allowed_roots=("docs",))
    with patch("loadout.dev.local_git.subprocess.run") as mocked:
        assert adapter.invoke(
            _intent("git.read_blob", commit_sha=first, path="private/secret.txt")
        ) == ("REFUSE", "PATH_OUTSIDE_FENCE")
        mocked.assert_not_called()


def test_missing_ref_is_typed_refusal(tmp_path: Path) -> None:
    root, _, _ = _repo(tmp_path)
    adapter = LocalGitReadAdapter(root, body_time_id="local-git@test-body")
    assert adapter.invoke(_intent("git.resolve_ref", ref="definitely-missing")) == (
        "REFUSE",
        "INVALID_REF",
    )


def test_missing_blob_is_unresolved(tmp_path: Path) -> None:
    root, first, _ = _repo(tmp_path)
    adapter = LocalGitReadAdapter(root, body_time_id="local-git@test-body", allowed_roots=("docs",))
    assert adapter.invoke(
        _intent("git.read_blob", commit_sha=first, path="docs/missing.txt")
    ) == ("UNRESOLVED", "OBJECT_NOT_FOUND")


def test_non_utf8_blob_is_unresolved_when_text_is_requested(tmp_path: Path) -> None:
    root, _, second = _repo(tmp_path)
    adapter = LocalGitReadAdapter(root, body_time_id="local-git@test-body", allowed_roots=("docs",))
    assert adapter.invoke(
        _intent("git.read_blob", commit_sha=second, path="docs/binary.bin", text="true")
    ) == ("UNRESOLVED", "NON_UTF8_BLOB")


def test_unknown_result_ref_refuses_local_read(tmp_path: Path) -> None:
    root, _, _ = _repo(tmp_path)
    adapter = LocalGitReadAdapter(root, body_time_id="local-git@test-body")
    with pytest.raises(KeyError, match="unknown result ref"):
        adapter.read_result("sha256:" + "0" * 64)


def test_ref_and_path_shell_metacharacters_remain_literal_argv(tmp_path: Path) -> None:
    root, first, _ = _repo(tmp_path)
    adapter = LocalGitReadAdapter(root, body_time_id="local-git@test-body", allowed_roots=("docs",))
    marker = tmp_path / "PWNED"
    bad_ref = f"HEAD;touch {marker}"
    assert adapter.invoke(_intent("git.resolve_ref", ref=bad_ref)) == ("REFUSE", "INVALID_REF")
    bad_path = f"docs/a.txt;touch {marker}"
    assert adapter.invoke(_intent("git.read_blob", commit_sha=first, path=bad_path)) == (
        "UNRESOLVED",
        "OBJECT_NOT_FOUND",
    )
    assert not marker.exists()


def test_adapter_source_exposes_only_read_subcommands() -> None:
    source = (
        Path(__file__).parents[1] / "src" / "loadout" / "dev" / "local_git.py"
    ).read_text(encoding="utf-8")
    for banned in ("checkout", "switch", "merge", "reset", "commit", "push", "fetch", "pull", "clone", "remote"):
        assert f'"{banned}"' not in source
        assert f"'{banned}'" not in source
    assert "shell=True" not in source
    for banned_import in ("urllib", "requests", "http.client", "import socket"):
        assert banned_import not in source
