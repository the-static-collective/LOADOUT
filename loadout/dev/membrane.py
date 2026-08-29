from collections.abc import Mapping
from loadout.dev.adapters import Adapter
from loadout.dev.model import (
    CompileReceipt, Disposition, EffectClass, EffectIntent, EffectReceipt,
    OwnerGate, RefusalReason,
)

_OWNER_GATED = frozenset({EffectClass.PUBLISH, EffectClass.LAND})


def _refuse(intent: EffectIntent, reason: RefusalReason) -> EffectReceipt:
    return EffectReceipt(
        intent.body_time_id, intent.capability, intent.effect, intent.target,
        intent.precondition_state, "REFUSED", None, False, reason,
    )


def invoke_effect(
    compiled: CompileReceipt,
    intent: EffectIntent,
    adapters: Mapping[str, Adapter],
    *,
    current_state: str,
    owner_gate: OwnerGate | None = None,
) -> EffectReceipt:
    if compiled.disposition != Disposition.COMPILED:
        return _refuse(intent, RefusalReason.CAPABILITY_NOT_BOUND)

    named = [b for b in compiled.bindings if b.capability == intent.capability]
    if not named:
        return _refuse(intent, RefusalReason.CAPABILITY_NOT_BOUND)
    targeted = [b for b in named if b.target == intent.target]
    if not targeted:
        return _refuse(intent, RefusalReason.TARGET_OUTSIDE_CUT)
    exact = [b for b in targeted if b.effect == intent.effect and b.body_time_id == intent.body_time_id]
    if not exact:
        return _refuse(intent, RefusalReason.EFFECT_OUTSIDE_FENCE)
    if intent.precondition_state != current_state:
        return _refuse(intent, RefusalReason.STATE_STALE)

    if intent.effect in _OWNER_GATED:
        if owner_gate is None:
            return _refuse(intent, RefusalReason.OWNER_GATE_REQUIRED)
        if (owner_gate.target, owner_gate.effect, owner_gate.state_id) != (intent.target, intent.effect, current_state):
            return _refuse(intent, RefusalReason.OWNER_GATE_STALE)

    adapter = adapters.get(intent.body_time_id)
    if adapter is None or adapter.body_time_id != intent.body_time_id:
        return _refuse(intent, RefusalReason.BODY_NOT_ELIGIBLE)

    disposition, post_state = adapter.invoke(intent)
    return EffectReceipt(
        intent.body_time_id, intent.capability, intent.effect, intent.target,
        intent.precondition_state, disposition, post_state, False, None,
    )
