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
