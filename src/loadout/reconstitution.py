from __future__ import annotations

import copy

from loadout.canonical import sha256_json
from loadout.compile import compile_loadout


LIFTABLE = {"LIFT", "DEGRADED"}


def _lane_modes(continuity_claim: dict) -> dict[str, str]:
    return {
        lane["lane"]: lane["mode"]
        for lane in continuity_claim.get("lanes", [])
        if isinstance(lane, dict) and isinstance(lane.get("lane"), str)
    }


def _local_proposals(handoff: dict, request: dict) -> list[dict]:
    adopted = set(request.get("adopt_source_proposals", []))
    records = []
    for source in handoff.get("source_open_proposals", []):
        source_ref = source.get("sourceProposalRef")
        if source_ref not in adopted:
            continue
        body = {
            "schema": "loadout.local-proposal/v0",
            "source_proposal_ref": source_ref,
            "kind": source.get("kind"),
            "threshold_id": request["threshold_id"],
        }
        body["proposal_id"] = "proposal-local:" + sha256_json(body).removeprefix("sha256:")
        records.append(body)
    return sorted(records, key=lambda item: item["proposal_id"])


def evaluate_reconstitution_threshold(handoff: dict, request: dict) -> dict:
    modes = _lane_modes(handoff["continuity_claim"])
    requirements = request.get("continuity_requirements", {})

    failed_lanes = sorted(
        lane
        for lane, allowed in requirements.items()
        if modes.get(lane) not in set(allowed)
    )
    missing = sorted(set(request.get("missing_evidence_refs", [])))
    fatal_missing = sorted(set(request.get("fatal_missing_refs", [])) & set(missing))

    if request.get("refuse_reason"):
        home_check = "REFUSE"
        disposition = "REFUSE"
        reason_code = request["refuse_reason"]
    elif failed_lanes or fatal_missing:
        home_check = "REFUSE"
        disposition = "REFUSE"
        reason_code = "HOME_REQUIREMENT_REFUSED"
    elif missing:
        home_check = "DEGRADED"
        disposition = "HOLD" if request.get("hold") else "DEGRADED"
        reason_code = "HOME_EVIDENCE_DEGRADED"
    else:
        home_check = "PASS"
        disposition = "HOLD" if request.get("hold") else "LIFT"
        reason_code = (
            "RECONSTITUTION_HELD"
            if disposition == "HOLD"
            else "RECONSTITUTION_LIFTABLE"
        )

    protected = sorted(
        set(request.get("protect_refs", []))
        & set(handoff.get("protected_requests", []))
    )

    record = {
        "schema": "loadout.reconstitution-threshold/v0",
        "threshold_id": request["threshold_id"],
        "source_handoff_digest": handoff["handoff_digest"],
        "receiving_constitution_ref": request["receiving_constitution_ref"],
        "continuity_requirements": copy.deepcopy(requirements),
        "failed_lanes": failed_lanes,
        "missing_evidence_refs": missing,
        "source_authority_refs": copy.deepcopy(handoff.get("source_authority_refs", [])),
        "authority_decision": "REAUTHORIZE_LOCALLY",
        "locally_protected_refs": protected,
        "local_proposals": _local_proposals(handoff, request),
        "home_check": home_check,
        "disposition": disposition,
        "reason_code": reason_code,
    }
    record["threshold_digest"] = sha256_json(record)
    return record


def reconstitute_world(
    handoff: dict,
    threshold: dict,
    compile_spec: dict,
    *,
    world_id: str,
    occurred_at: str,
    resolved_bodies: list[dict],
) -> dict:
    if threshold.get("disposition") not in LIFTABLE:
        raise ValueError("threshold is not liftable")
    if threshold.get("source_handoff_digest") != handoff.get("handoff_digest"):
        raise ValueError("threshold source mismatch")

    compile_record = compile_loadout(copy.deepcopy(compile_spec))
    local_authorization_refs = sorted({
        item["authorization_source_ref"]
        for item in compile_record.get("effective_effects", [])
        if item.get("status") == "allowed" and item.get("authorization_source_ref")
    })
    refused_bindings = sorted(
        item["capability"]
        for item in compile_record.get("capability_bindings", [])
        if item.get("status") != "available"
    )

    receipt = {
        "schema": "loadout.world-birth/v0",
        "world_id": world_id,
        "source_handoff_digest": handoff["handoff_digest"],
        "threshold_digest": threshold["threshold_digest"],
        "local_constitution_ref": threshold["receiving_constitution_ref"],
        "compile_digest": compile_record["compile_digest"],
        "historical_producer_refs": sorted(handoff.get("historical_producer_refs", [])),
        "resolved_bodies": sorted(copy.deepcopy(resolved_bodies), key=lambda item: item["logical_ref"]),
        "local_authorization_refs": local_authorization_refs,
        "refused_bindings": refused_bindings,
        "home_check": threshold["home_check"],
        "protected_refs": copy.deepcopy(threshold["locally_protected_refs"]),
        "local_proposal_refs": sorted(item["proposal_id"] for item in threshold["local_proposals"]),
        "occurred_at": occurred_at,
    }
    receipt["birth_digest"] = sha256_json(receipt)
    return {"compile": compile_record, "birth_receipt": receipt}
