from __future__ import annotations


def unfenced_effects(reachable: tuple[str, ...], effect_fence: list[str]) -> tuple[str, ...]:
    allowed = {effect for effect in effect_fence if isinstance(effect, str) and effect}
    return tuple(effect for effect in reachable if effect not in allowed)
