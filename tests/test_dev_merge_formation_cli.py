from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "merge_formation" / "safe-disjoint.json"
MODULE = ROOT / "src" / "loadout" / "dev" / "merge_formation.py"


def test_merge_formation_cli_emits_one_canonical_receipt() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "loadout.dev.merge_formation", str(FIXTURE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    receipt = json.loads(result.stdout)
    assert receipt["schema"] == "loadout.merge-formation-receipt/v0"
    assert receipt["classification"] == "SAFE_CONTENT_COMPOSITION"
    assert result.stdout.count("\n") == 1


def test_merge_formation_cli_refuses_wrong_schema_with_exit_2(tmp_path: Path) -> None:
    packet = json.loads(FIXTURE.read_text(encoding="utf-8"))
    packet["schema"] = "wrong"
    path = tmp_path / "wrong.json"
    path.write_text(json.dumps(packet), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "loadout.dev.merge_formation", str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "WRONG_SCHEMA" in result.stderr
    assert result.stdout == ""


def test_merge_formation_module_has_no_host_access_imports() -> None:
    source = MODULE.read_text(encoding="utf-8")
    for forbidden in ("import subprocess", "import urllib", "import requests", "import socket", "github"):
        assert forbidden not in source.lower()
