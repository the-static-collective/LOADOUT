from __future__ import annotations

import copy
from datetime import datetime, timezone

from loadout.compile import compile_payload_digest
from loadout.canonical import sha256_json

_ALLOWED_PATCH_KEYS = {
    "context_pack_ref",
    "world_cut_ref",
    "capability_bindings",
    "effect_fence_ref",
    "effective_effects",
    "expires_at",
    "egress_policy_ref",
    "compile_trace",
}


def _parse_instant(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    instant = datetime.fromisoformat(normalized)
    if instant.tzinfo is None:
        raise ValueError("timestamp must be offset-aware")
    return instant.astimezone(timezone.utc)


def _proposal_payload_digest(proposal: dict) -> str:
    payload = copy.deepcopy(proposal)
    payload.pop("proposal_digest", None)
    return sha256_json(payload)


def propose_recompile(
    base_compile: dict,
    patch: dict,
    *,
    reason: str,
    proposal_id: str,
    proposed_compile_id: str,
) -> dict:
    proposal = {
        "schema": "loadout.recompile-proposal/v0",
        "proposal_id": proposal_id,
        "base_compile_id": base_compile["compile_id"],
        "base_compile_digest": base_compile["compile_digest"],
        "proposed_compile_id": proposed_compile_id,
        "reason": reason,
        "patch": copy.deepcopy(patch),
    }
    proposal["proposal_digest"] = _proposal_payload_digest(proposal)
    return proposal


def _allowed_effects(record: dict) -> set[str]:
    return {
        item.get("effect")
        for item in record.get("effective_effects", [])
        if isinstance(item, dict) and item.get("status") == "allowed"
    }


def _available_capabilities(record: dict) -> set[str]:
    return {
        item.get("capability")
        for item in record.get("capability_bindings", [])
        if isinstance(item, dict) and item.get("status") == "available"
    }


def gate_recompile_proposal(base_compile: dict, proposal: dict) -> dict:
    reason_code = None
    disposition = "ADMIT"
    patch = proposal.get("patch", {})

    if proposal.get("schema") != "loadout.recompile-proposal/v0":
        disposition, reason_code = "REFUSE", "PROPOSAL_SCHEMA_INVALID"
    elif proposal.get("proposal_digest") != _proposal_payload_digest(proposal):
        disposition, reason_code = "REFUSE", "PROPOSAL_DIGEST_MISMATCH"
    elif proposal.get("base_compile_id") != base_compile.get("compile_id") or proposal.get("base_compile_digest") != base_compile.get("compile_digest"):
        disposition, reason_code = "REFUSE", "BASE_COMPILE_MISMATCH"
    elif not isinstance(patch, dict) or not set(patch).issubset(_ALLOWED_PATCH_KEYS):
        disposition, reason_code = "REFUSE", "PATCH_SCOPE_INVALID"
    elif "effect_fence_ref" in patch and patch["effect_fence_ref"] != base_compile.get("effect_fence_ref"):
        disposition, reason_code = "REFUSE", "FENCE_CHANGE_REQUIRES_OWNER_GATE"
    elif "egress_policy_ref" in patch and patch["egress_policy_ref"] != base_compile.get("egress_policy_ref"):
        disposition, reason_code = "REFUSE", "EGRESS_CHANGE_REQUIRES_OWNER_GATE"
    elif "expires_at" in patch and _parse_instant(patch["expires_at"]) > _parse_instant(base_compile["expires_at"]):
        disposition, reason_code = "REFUSE", "EXPIRY_EXTENSION_FORBIDDEN"
    else:
        candidate = copy.deepcopy(base_compile)
        candidate.update(copy.deepcopy(patch))
        if not _allowed_effects(candidate).issubset(_allowed_effects(base_compile)):
            disposition, reason_code = "REFUSE", "AUTHORITY_EXPANSION_FORBIDDEN"
        elif not _available_capabilities(candidate).issubset(_available_capabilities(base_compile)):
            disposition, reason_code = "REFUSE", "CAPABILITY_EXPANSION_FORBIDDEN"

    receipt = {
        "schema": "loadout.recompile-gate/v0",
        "proposal_id": proposal.get("proposal_id"),
        "proposal_digest": proposal.get("proposal_digest"),
        "base_compile_digest": base_compile.get("compile_digest"),
        "disposition": disposition,
        "reason_code": reason_code,
    }
    receipt["gate_digest"] = sha256_json(receipt)
    return receipt


def apply_recompile_proposal(base_compile: dict, proposal: dict, gate_receipt: dict) -> dict:
    expected = gate_recompile_proposal(base_compile, proposal)
    required_matches = (
        gate_receipt.get("schema") == "loadout.recompile-gate/v0"
        and gate_receipt.get("proposal_id") == proposal.get("proposal_id")
        and gate_receipt.get("proposal_digest") == proposal.get("proposal_digest")
        and gate_receipt.get("base_compile_digest") == base_compile.get("compile_digest")
        and gate_receipt.get("disposition") == "ADMIT"
        and gate_receipt.get("gate_digest") == expected.get("gate_digest")
        and expected.get("disposition") == "ADMIT"
    )
    if not required_matches:
        raise ValueError("recompile gate receipt invalid")

    child = copy.deepcopy(base_compile)
    child.update(copy.deepcopy(proposal["patch"]))
    child["parent_compile_id"] = base_compile["compile_id"]
    child["compile_id"] = proposal["proposed_compile_id"]
    child["compile_digest"] = compile_payload_digest(child)
    return child
