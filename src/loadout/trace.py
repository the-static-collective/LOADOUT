from __future__ import annotations


def trace_binding(binding_receipt: dict) -> list[dict]:
    return [
        {"step": "REACH", "value": binding_receipt.get("reachable_effects")},
        {"step": "FENCE", "value": binding_receipt.get("unfenced_effects")},
        {"step": "BIND", "value": binding_receipt.get("disposition")},
    ]
