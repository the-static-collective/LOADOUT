import copy
import json
from pathlib import Path

from loadout.adapters.project0 import parse_project0_handoff
from loadout.reconstitution import evaluate_reconstitution_threshold, reconstitute_world

ROOT = Path(__file__).parents[1]


def load_handoff():
    bundle = json.loads(
        (ROOT / "fixtures/phaselift/project0-CROSSING-001.json").read_text()
    )
    provenance = json.loads(
        (ROOT / "fixtures/phaselift/project0-CROSSING-001.provenance.json").read_text()
    )
    return parse_project0_handoff(bundle, provenance)


def request(threshold_id):
    return {
        "threshold_id": threshold_id,
        "receiving_constitution_ref": "constitution:" + threshold_id,
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


def local_compile_spec(compile_id, world_ref):
    return {
        "compile_id": compile_id,
        "parent_compile_id": None,
        "issued_at": "2026-08-30T06:00:00+00:00",
        "expires_at": "2026-08-30T07:00:00+00:00",
        "world_cut_ref": world_ref,
        "context_pack_ref": "context:" + world_ref,
        "compile_trace": {
            "id": "trace:" + compile_id,
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
        "effect_fence_ref": "fence:" + world_ref,
        "effect_authorizations": {},
        "owner_evidence_digest": "sha256:" + "c" * 64,
        "egress_policy_ref": "egress:" + world_ref,
    }


def test_same_crossing_has_four_receiver_local_outcomes_without_mutation():
    handoff = load_handoff()
    before = copy.deepcopy(handoff)

    lift = request("B-lift")
    degraded = request("B-degraded")
    degraded["missing_evidence_refs"] = ["receipt:dogram:A1"]
    hold = request("B-hold")
    hold["hold"] = True
    refuse = request("B-refuse")
    refuse["refuse_reason"] = "LOCAL_POLICY_REFUSAL"

    results = [
        evaluate_reconstitution_threshold(handoff, item)
        for item in [lift, degraded, hold, refuse]
    ]
    assert [item["disposition"] for item in results] == [
        "LIFT",
        "DEGRADED",
        "HOLD",
        "REFUSE",
    ]
    assert handoff == before
    assert len({item["source_handoff_digest"] for item in results}) == 1


def test_two_lift_receivers_fork_without_collapsing_history_or_authority():
    handoff = load_handoff()

    threshold_a = evaluate_reconstitution_threshold(handoff, request("B-a"))
    threshold_b = evaluate_reconstitution_threshold(handoff, request("B-b"))

    birth_a = reconstitute_world(
        handoff,
        threshold_a,
        local_compile_spec("compile:B-a", "world:B-a"),
        world_id="world:B-a",
        occurred_at="2026-08-30T06:00:01+00:00",
        resolved_bodies=[
            {"logical_ref": "ALEX", "resolved_body": "alex:B-a"},
            {"logical_ref": "Dogram", "resolved_body": "dogram:B-a"},
        ],
    )["birth_receipt"]
    birth_b = reconstitute_world(
        handoff,
        threshold_b,
        local_compile_spec("compile:B-b", "world:B-b"),
        world_id="world:B-b",
        occurred_at="2026-08-30T06:00:02+00:00",
        resolved_bodies=[
            {"logical_ref": "ALEX", "resolved_body": "alex:B-b"},
            {"logical_ref": "Dogram", "resolved_body": "dogram:B-b"},
        ],
    )["birth_receipt"]

    assert birth_a["world_id"] != birth_b["world_id"]
    assert birth_a["source_handoff_digest"] == birth_b["source_handoff_digest"]
    assert birth_a["historical_producer_refs"] == birth_b["historical_producer_refs"]
    assert birth_a["resolved_bodies"] != birth_b["resolved_bodies"]
    assert "authority:source-repo-write" not in birth_a["local_authorization_refs"]
    assert "authority:source-repo-write" not in birth_b["local_authorization_refs"]

    proposal_a = threshold_a["local_proposals"][0]
    assert proposal_a["source_proposal_ref"] == "proposal:inspect-next"
    assert proposal_a["proposal_id"] != proposal_a["source_proposal_ref"]
    assert threshold_a["locally_protected_refs"] == ["artifact:odd-small-1"]
