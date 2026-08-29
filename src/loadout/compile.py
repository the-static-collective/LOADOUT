from __future__ import annotations

import copy

from loadout.bind import evaluate_binding
from loadout.canonical import sha256_json


def compile_payload_digest(compile_record: dict) -> str:
    payload = copy.deepcopy(compile_record)
    payload.pop("compile_digest", None)
    return sha256_json(payload)


def _authorization_for(effect: str, spec: dict) -> dict | None:
    authorizations = spec.get("effect_authorizations", {})
    auth = authorizations.get(effect) if isinstance(authorizations, dict) else None
    if not isinstance(auth, dict):
        return None
    if not auth.get("authorization_source_ref") or not auth.get("owner_gate_ref"):
        return None
    if auth.get("revocation_ref") is not None:
        return None
    return auth


def _effective_effect(effect: str, allowed: bool, spec: dict) -> dict:
    auth = _authorization_for(effect, spec) if allowed else None
    admitted = auth is not None
    return {
        "effect": effect,
        "status": "allowed" if admitted else "refused",
        "authorization_source_ref": auth.get("authorization_source_ref") if admitted else None,
        "scope": auth.get("scope", effect) if admitted else effect,
        "valid_from": auth.get("valid_from", spec["issued_at"]) if admitted else None,
        "expires_at": auth.get("expires_at", spec["expires_at"]) if admitted else None,
        "revocation_ref": None,
        "owner_gate_ref": auth.get("owner_gate_ref") if admitted else None,
    }


def compile_loadout(spec: dict) -> dict:
    effect_fence = list(spec.get("effect_fence", []))
    capability_bindings: list[dict] = []
    effect_status: dict[str, bool] = {}

    for capability in spec.get("capabilities", []):
        receipt = evaluate_binding(capability, effect_fence)
        reachable = receipt.get("reachable_effects") or []
        authorized = all(_authorization_for(effect, spec) is not None for effect in reachable)
        available = receipt["disposition"] == "BIND" and authorized
        capability_bindings.append({
            "capability": capability["capability"],
            "status": "available" if available else "unavailable",
        })
        for effect in reachable:
            effect_status[effect] = (
                effect_status.get(effect, True)
                and effect in effect_fence
                and _authorization_for(effect, spec) is not None
            )

    record = {
        "schema": "loadout.compile/v0",
        "compile_id": spec["compile_id"],
        "parent_compile_id": spec.get("parent_compile_id"),
        "issued_at": spec["issued_at"],
        "expires_at": spec["expires_at"],
        "world_cut_ref": spec["world_cut_ref"],
        "context_pack_ref": spec["context_pack_ref"],
        "compile_trace": copy.deepcopy(spec["compile_trace"]),
        "capability_bindings": capability_bindings,
        "effect_fence_ref": spec["effect_fence_ref"],
        "effective_effects": [
            _effective_effect(effect, effect_status[effect], spec)
            for effect in sorted(effect_status)
        ],
        "owner_evidence_digest": spec["owner_evidence_digest"],
        "egress_policy_ref": spec["egress_policy_ref"],
    }
    record["compile_digest"] = compile_payload_digest(record)
    return record
