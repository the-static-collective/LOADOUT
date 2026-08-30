import json
from pathlib import Path

import pytest

from loadout.adapters.project0 import parse_project0_handoff
from loadout.reconstitution import evaluate_reconstitution_threshold, reconstitute_world

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


def local_compile_spec():
    return {
        "compile_id": "compile:B1",
        "parent_compile_id": None,
        "issued_at": "2026-08-30T06:00:00+00:00",
        "expires_at": "2026-08-30T07:00:00+00:00",
        "world_cut_ref": "world:B1",
        "context_pack_ref": "context:B1",
        "compile_trace": {
            "id": "trace:B1",
            "source_world_ref": "world:A",
            "operation": "reconstitute-from-crossing",
            "preserved_invariants": ["required-capability:repo.read"],
            "declared_loss": [],
            "producer": "loadout.kernel/v0",
            "freshness": "2026-08-30T06:00:00+00:00",
        },
        "capabilities": [
            {
                "capability": "repo.read",
                "operation": "inspect",
                "reachable_effects": [],
                "parameters": {},
            },
            {
                "capability": "repo.write",
                "operation": "intervene",
                "reachable_effects": ["repo.branch.write"],
                "parameters": {},
            },
        ],
        "effect_fence": ["repo.branch.write"],
        "effect_fence_ref": "fence:B1",
        "effect_authorizations": {},
        "owner_evidence_digest": "sha256:" + "b" * 64,
        "egress_policy_ref": "egress:B1",
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


def test_world_birth_reauthorizes_locally_and_preserves_historical_producers(handoff):
    threshold = evaluate_reconstitution_threshold(handoff, base_request())
    result = reconstitute_world(
        handoff,
        threshold,
        local_compile_spec(),
        world_id="world:B1",
        occurred_at="2026-08-30T06:00:01+00:00",
        resolved_bodies=[
            {"logical_ref": "Dogram", "resolved_body": "dogram:B1"},
            {"logical_ref": "ALEX", "resolved_body": "alex:B1"},
        ],
    )

    compile_record = result["compile"]
    receipt = result["birth_receipt"]
    write = next(
        item
        for item in compile_record["effective_effects"]
        if item["effect"] == "repo.branch.write"
    )

    assert write["status"] == "refused"
    assert receipt["historical_producer_refs"] == ["producer:alex:A1", "producer:dogram:A1"]
    assert receipt["resolved_bodies"][0]["resolved_body"] in {"alex:B1", "dogram:B1"}
    assert "authority:source-repo-write" not in receipt["local_authorization_refs"]
    assert receipt["world_id"] == "world:B1"


def test_hold_and_refuse_cannot_emit_world_birth(handoff):
    for request_patch in ({"hold": True}, {"refuse_reason": "LOCAL_POLICY_REFUSAL"}):
        request = base_request()
        request.update(request_patch)
        threshold = evaluate_reconstitution_threshold(handoff, request)
        with pytest.raises(ValueError, match="threshold is not liftable"):
            reconstitute_world(
                handoff,
                threshold,
                local_compile_spec(),
                world_id="world:forbidden",
                occurred_at="2026-08-30T06:00:01+00:00",
                resolved_bodies=[],
            )
