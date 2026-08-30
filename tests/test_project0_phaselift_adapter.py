import hashlib
import json
from pathlib import Path

from loadout.adapters.project0 import parse_project0_handoff

ROOT = Path(__file__).parents[1]


def fixture_bytes():
    return (ROOT / "fixtures/phaselift/project0-CROSSING-001.json").read_bytes()


def fixture_bundle():
    return json.loads(fixture_bytes())


def provenance():
    return json.loads(
        (ROOT / "fixtures/phaselift/project0-CROSSING-001.provenance.json").read_text()
    )


def test_project0_fixture_pin_matches_exact_bytes():
    digest = "sha256:" + hashlib.sha256(fixture_bytes()).hexdigest()
    assert digest == provenance()["source_sha256"]


def test_adapter_preserves_source_authority_as_history_only():
    handoff = parse_project0_handoff(fixture_bundle(), provenance())
    assert handoff["schema"] == "loadout.project0-handoff/v0"
    assert handoff["source_authority_refs"] == ["authority:source-repo-write"]
    assert "effect_authorizations" not in handoff
    assert handoff["historical_producer_refs"] == ["producer:alex:A1", "producer:dogram:A1"]
    assert handoff["protected_requests"] == ["artifact:odd-small-1"]
    assert handoff["source_open_proposals"][0]["sourceProposalRef"] == "proposal:inspect-next"
