import json
from pathlib import Path

import pytest

from loadout.adapters.project0 import parse_project0_handoff
from loadout.reconstitution import evaluate_reconstitution_threshold

ROOT = Path(__file__).parents[1]


@pytest.fixture
def handoff():
    bundle = json.loads(
        (ROOT / "fixtures/phaselift/project0-CROSSING-001.json").read_text()
    )
    provenance = json.loads(
        (ROOT / "fixtures/phaselift/project0-CROSSING-001.provenance.json").read_text()
    )
    return parse_project0_handoff(bundle, provenance)


def base_request():
    return {
        "threshold_id": "threshold:B1",
        "receiving_constitution_ref": "constitution:loadout:B1",
        "continuity_requirements": {
            "identity": ["preserved", "transformed"],
            "protocol": ["preserved", "transformed", "reconstituted"],
            "purpose-meaning": ["preserved", "transformed"],
        },
        "missing_evidence_refs": [],
        "fatal_missing_refs": [],
        "protect_refs": ["artifact:odd-small-1"],
        "adopt_source_proposals": ["proposal:inspect-next"],
        "hold": False,
        "refuse_reason": None,
    }


def test_threshold_lifts_when_home_requirements_are_satisfied(handoff):
    result = evaluate_reconstitution_threshold(handoff, base_request())
    assert result["disposition"] == "LIFT"
    assert result["home_check"] == "PASS"
    assert result["locally_protected_refs"] == ["artifact:odd-small-1"]
    assert result["local_proposals"][0]["source_proposal_ref"] == "proposal:inspect-next"
    assert result["local_proposals"][0]["proposal_id"] != "proposal:inspect-next"


def test_threshold_degrades_when_nonfatal_evidence_is_missing(handoff):
    request = base_request()
    request["missing_evidence_refs"] = ["receipt:dogram:A1"]
    result = evaluate_reconstitution_threshold(handoff, request)
    assert result["disposition"] == "DEGRADED"
    assert result["home_check"] == "DEGRADED"


def test_threshold_holds_without_faking_world_birth(handoff):
    request = base_request()
    request["hold"] = True
    result = evaluate_reconstitution_threshold(handoff, request)
    assert result["disposition"] == "HOLD"


def test_threshold_refuses_failed_required_lane(handoff):
    request = base_request()
    request["continuity_requirements"]["protocol"] = ["preserved"]
    result = evaluate_reconstitution_threshold(handoff, request)
    assert result["disposition"] == "REFUSE"
    assert result["home_check"] == "REFUSE"
