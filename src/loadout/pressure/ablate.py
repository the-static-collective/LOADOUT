from __future__ import annotations

import copy

from loadout.compile import compile_payload_digest

_REQUIRED_PREFIX = "required-capability:"


def _required_capabilities(compile_record: dict) -> list[str]:
    invariants = compile_record.get("compile_trace", {}).get("preserved_invariants", [])
    required = [
        item[len(_REQUIRED_PREFIX):]
        for item in invariants
        if isinstance(item, str) and item.startswith(_REQUIRED_PREFIX)
    ]
    return sorted(set(required))


def task_reachable(compile_record: dict) -> dict:
    available = {
        binding.get("capability")
        for binding in compile_record.get("capability_bindings", [])
        if isinstance(binding, dict) and binding.get("status") == "available"
    }
    missing = [capability for capability in _required_capabilities(compile_record) if capability not in available]
    return {"reachable": not missing, "missing_capabilities": missing}


def ablate_binding(compile_record: dict, capability: str, new_compile_id: str) -> dict:
    child = copy.deepcopy(compile_record)
    child["parent_compile_id"] = compile_record["compile_id"]
    child["compile_id"] = new_compile_id
    child["capability_bindings"] = [
        binding
        for binding in child.get("capability_bindings", [])
        if binding.get("capability") != capability
    ]
    trace = child["compile_trace"]
    trace["id"] = f"{trace['id']}:ablate:{capability}"
    trace["operation"] = f"ablate-binding:{capability}"
    losses = list(trace.get("declared_loss", []))
    losses.append(f"ablated-capability:{capability}")
    trace["declared_loss"] = list(dict.fromkeys(losses))
    child["compile_digest"] = compile_payload_digest(child)
    return child
