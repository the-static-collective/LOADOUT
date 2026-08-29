import json
from pathlib import Path

from loadout.history import validate_historical_manifest


def test_3rdi_historical_manifest_is_valid_witness_not_compile():
    fixture = Path("fixtures/3rdi/loadout.manifest.json")
    manifest = json.loads(fixture.read_text())
    assert validate_historical_manifest(manifest) == []
    assert manifest["schema"] == "loadout.manifest/v0"
    assert manifest["schema"] != "loadout.compile/v0"
    assert manifest["authority"] == "none"
    assert manifest["promotion"] == "none"
    assert manifest["lifecycle"]["inherits_permissions"] is False
