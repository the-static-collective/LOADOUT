from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import subprocess
from typing import Iterable

from loadout.dev.model import EffectClass, EffectIntent, parameter_map


_ALLOWED_CAPABILITIES = frozenset({"git.resolve_ref", "git.read_blob"})
_SHA40 = re.compile(r"^[0-9a-f]{40}$")


def _normalize_repo_path(path: str) -> str:
    if not isinstance(path, str) or not path or "\x00" in path:
        raise ValueError("unsafe repository path")
    normalized = path.replace("\\", "/")
    if normalized.startswith("/"):
        raise ValueError("unsafe repository path")
    parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("unsafe repository path")
    return "/".join(parts)


def _path_is_allowed(path: str, roots: tuple[str, ...]) -> bool:
    if not roots:
        return True
    return any(path == root or path.startswith(f"{root}/") for root in roots)


def _minimal_env() -> dict[str, str]:
    env = {
        "GIT_EDITOR": "true",
        "GIT_PAGER": "cat",
        "GIT_TERMINAL_PROMPT": "0",
        "LC_ALL": "C",
        "PAGER": "cat",
    }
    path = os.environ.get("PATH")
    if path is not None:
        env["PATH"] = path
    return env


class LocalGitReadAdapter:
    """Read exact local Git objects through a two-capability observer surface."""

    def __init__(
        self,
        repo_root: str | Path,
        *,
        body_time_id: str,
        allowed_roots: Iterable[str] = (),
    ) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.body_time_id = body_time_id
        self.allowed_roots = tuple(_normalize_repo_path(root) for root in allowed_roots)
        self._results: dict[str, bytes] = {}

    def _store(self, payload: bytes) -> str:
        result_ref = f"sha256:{hashlib.sha256(payload).hexdigest()}"
        self._results[result_ref] = payload
        return result_ref

    def read_result(self, result_ref: str) -> bytes:
        try:
            return self._results[result_ref]
        except KeyError as error:
            raise KeyError(f"unknown result ref: {result_ref}") from error

    def _run(self, *argv: str) -> subprocess.CompletedProcess[bytes] | None:
        if not self.repo_root.is_dir():
            return None
        try:
            return subprocess.run(
                ["git", "-C", str(self.repo_root), *argv],
                check=False,
                capture_output=True,
                env=_minimal_env(),
                shell=False,
                timeout=10,
            )
        except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
            return None

    def _resolve_ref(self, params: dict[str, str]) -> tuple[str, str | None]:
        ref = params.get("ref")
        if not isinstance(ref, str) or not ref or "\x00" in ref:
            return "REFUSE", "INVALID_REF"
        completed = self._run("rev-parse", "--verify", f"{ref}^{{commit}}")
        if completed is None:
            return "UNRESOLVED", "GIT_UNAVAILABLE"
        if completed.returncode != 0:
            return "REFUSE", "INVALID_REF"
        try:
            resolved = completed.stdout.decode("ascii").strip()
        except UnicodeDecodeError:
            return "REFUSE", "INVALID_REF"
        if _SHA40.fullmatch(resolved) is None:
            return "REFUSE", "INVALID_REF"
        payload = f"{resolved}\n".encode("ascii")
        return "RESOLVED", self._store(payload)

    def _read_blob(self, params: dict[str, str]) -> tuple[str, str | None]:
        object_sha = params.get("commit_sha")
        if not isinstance(object_sha, str) or _SHA40.fullmatch(object_sha) is None:
            return "REFUSE", "INVALID_REF"

        raw_path = params.get("path")
        try:
            path = _normalize_repo_path(raw_path)  # type: ignore[arg-type]
        except ValueError:
            return "REFUSE", "PATH_OUTSIDE_FENCE"
        if not _path_is_allowed(path, self.allowed_roots):
            return "REFUSE", "PATH_OUTSIDE_FENCE"

        completed = self._run("show", f"{object_sha}:{path}")
        if completed is None:
            return "UNRESOLVED", "GIT_UNAVAILABLE"
        if completed.returncode != 0:
            return "UNRESOLVED", "OBJECT_NOT_FOUND"

        payload = completed.stdout
        if params.get("text") == "true":
            try:
                payload.decode("utf-8")
            except UnicodeDecodeError:
                return "UNRESOLVED", "NON_UTF8_BLOB"
        return "RESOLVED", self._store(payload)

    def invoke(self, intent: EffectIntent) -> tuple[str, str | None]:
        if intent.capability not in _ALLOWED_CAPABILITIES:
            return "REFUSE", "CAPABILITY_NOT_ALLOWED"
        if intent.effect != EffectClass.OBSERVE:
            return "REFUSE", "CAPABILITY_NOT_ALLOWED"
        try:
            params = parameter_map(intent)
        except ValueError:
            return "REFUSE", "TARGET_OUTSIDE_CUT"

        if intent.capability == "git.resolve_ref":
            return self._resolve_ref(params)
        if intent.capability == "git.read_blob":
            return self._read_blob(params)
        raise AssertionError("unreachable capability dispatch")


__all__ = ["LocalGitReadAdapter"]
