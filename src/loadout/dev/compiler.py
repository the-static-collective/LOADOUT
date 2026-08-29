from loadout.dev.model import (
    Binding, CapabilitySpec, CompileReceipt, CompileRequest,
    Disposition, RefusalReason,
)


def compile_world(request: CompileRequest) -> CompileReceipt:
    bindings: list[Binding] = []

    for requested in request.requested_capabilities:
        if requested.target not in request.cut_targets:
            return CompileReceipt(Disposition.REFUSED, request.task_id, reasons=(RefusalReason.TARGET_OUTSIDE_CUT,))
        if requested.replay and requested.body_time_id is None:
            return CompileReceipt(Disposition.REFUSED, request.task_id, reasons=(RefusalReason.BODY_PIN_REQUIRED,))

        named = [
            body for body in request.available_bodies
            if any(cap.name == requested.capability for cap in body.capabilities)
            and (requested.body_time_id is None or body.body_time_id == requested.body_time_id)
        ]
        exact_spec = CapabilitySpec(requested.capability, requested.effect)
        exact = [body for body in named if exact_spec in body.capabilities]

        if named and not exact:
            return CompileReceipt(Disposition.REFUSED, request.task_id, reasons=(RefusalReason.EFFECT_OUTSIDE_FENCE,))
        if not exact:
            return CompileReceipt(Disposition.CAPABILITY_GAP, request.task_id, reasons=(RefusalReason.CAPABILITY_UNAVAILABLE,))
        if len(exact) != 1:
            return CompileReceipt(Disposition.REFUSED, request.task_id, reasons=(RefusalReason.BODY_AMBIGUOUS,))

        body = exact[0]
        bindings.append(Binding(
            capability=requested.capability,
            effect=requested.effect,
            target=requested.target,
            body_time_id=body.body_time_id,
        ))

    return CompileReceipt(Disposition.COMPILED, request.task_id, bindings=tuple(bindings))
