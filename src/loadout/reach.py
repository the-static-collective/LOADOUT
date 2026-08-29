from __future__ import annotations


def reachable_effects(capability: dict) -> tuple[str, ...] | None:
    effects = capability.get("reachable_effects")
    if effects is None:
        return None
    if not isinstance(effects, list) or not all(isinstance(effect, str) and effect for effect in effects):
        return None
    return tuple(sorted(set(effects)))
