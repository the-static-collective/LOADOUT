from __future__ import annotations


TASK_SHAPES = {"FIND", "READ", "COMPARE", "TRACE", "DOSSIER", "AUDIT", "PRESSURE"}


def to_alex_envelope(compile_record: dict, request: dict) -> dict:
    task_shape = request["task_shape"]
    if task_shape not in TASK_SHAPES:
        raise ValueError(f"unsupported ALEX task shape: {task_shape}")
    return {
        "schema": "alex.run-envelope/v0",
        "run_id": request["run_id"],
        "compile_id": compile_record["compile_id"],
        "compile_digest": compile_record["compile_digest"],
        "compile_trace_ref": compile_record["compile_trace"]["id"],
        "phase": request["phase"],
        "expires_at": compile_record["expires_at"],
        "question": request["question"],
        "task_shape": task_shape,
        "world_cut_ref": compile_record["world_cut_ref"],
        "context_pack_ref": compile_record["context_pack_ref"],
        "input_record_ids": list(request.get("input_record_ids", [])),
        "capability_bindings": compile_record["capability_bindings"],
        "effect_fence_ref": compile_record["effect_fence_ref"],
        "egress_policy_ref": compile_record["egress_policy_ref"],
        "rule_profile": request["rule_profile"],
        "stop_condition": request["stop_condition"],
        "requested_outputs": list(request.get("requested_outputs", [])),
    }
