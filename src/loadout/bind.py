from __future__ import annotations

from loadout.canonical import sha256_json
from loadout.fence import unfenced_effects
from loadout.reach import reachable_effects


def evaluate_binding(capability: dict, effect_fence: list[str]) -> dict:
    reachable = reachable_effects(capability)
    parameter_digest = sha256_json(capability.get("parameters", {}))

    if reachable is None:
        return {
            "capability": capability.get("capability"),
            "disposition": "UNRESOLVED",
            "reason_code": "REACHABILITY_UNRESOLVED",
            "reachable_effects": None,
            "unfenced_effects": None,
            "parameter_digest": parameter_digest,
            "authority_delta": "none",
            "probe_receipt_required": False,
        }

    unfenced = unfenced_effects(reachable, effect_fence)
    if unfenced:
        disposition = "REFUSE"
        reason_code = "UNFENCED_REACHABLE_EFFECT"
    else:
        disposition = "BIND"
        reason_code = None

    return {
        "capability": capability.get("capability"),
        "disposition": disposition,
        "reason_code": reason_code,
        "reachable_effects": list(reachable),
        "unfenced_effects": list(unfenced),
        "parameter_digest": parameter_digest,
        "authority_delta": "none",
        "probe_receipt_required": bool(reachable) and disposition == "BIND",
    }


def validate_execution_attempt(binding_receipt: dict, parameters: dict) -> dict:
    if binding_receipt.get("parameter_digest") != sha256_json(parameters):
        return {
            "disposition": "REFUSE",
            "reason_code": "PARAMETER_DRIFT",
            "recompile_required": True,
        }
    return {
        "disposition": binding_receipt.get("disposition"),
        "reason_code": binding_receipt.get("reason_code"),
        "recompile_required": False,
    }
