from loadout.compile import compile_loadout, compile_payload_digest
from loadout.adapters.alex import to_alex_envelope


COMPILE_KEYS = {
    "schema", "compile_id", "parent_compile_id", "issued_at", "expires_at",
    "world_cut_ref", "context_pack_ref", "compile_trace", "capability_bindings",
    "effect_fence_ref", "effective_effects", "owner_evidence_digest",
    "egress_policy_ref", "compile_digest",
}

ENVELOPE_KEYS = {
    "schema", "run_id", "compile_id", "compile_digest", "compile_trace_ref",
    "phase", "expires_at", "question", "task_shape", "world_cut_ref",
    "context_pack_ref", "input_record_ids", "capability_bindings",
    "effect_fence_ref", "egress_policy_ref", "rule_profile", "stop_condition",
    "requested_outputs",
}


def base_spec():
    return {
        "compile_id": "compile-1",
        "parent_compile_id": None,
        "issued_at": "2026-08-29T03:00:00+00:00",
        "expires_at": "2026-08-29T04:00:00+00:00",
        "world_cut_ref": "world:1",
        "context_pack_ref": "context:1",
        "compile_trace": {
            "id": "trace:1",
            "source_world_ref": "world:0",
            "operation": "bounded-compile",
            "preserved_invariants": ["required-capability:repo.read"],
            "declared_loss": ["unloaded:unrelated-repos"],
            "producer": "loadout.kernel/v0",
            "freshness": "2026-08-29T03:00:00+00:00",
        },
        "capabilities": [
            {
                "capability": "repo.read",
                "operation": "inspect",
                "reachable_effects": [],
                "parameters": {"repo": "the-static-collective/LOADOUT"},
            },
            {
                "capability": "repo.write",
                "operation": "intervene",
                "reachable_effects": ["repo.branch.write"],
                "parameters": {"branch": "feat/x"},
            },
        ],
        "effect_fence": ["repo.branch.write"],
        "effect_fence_ref": "fence:1",
        "effect_authorizations": {
            "repo.branch.write": {
                "authorization_source_ref": "owner-receipt:1",
                "owner_gate_ref": "owner-gate:1",
                "scope": "repo.branch.write",
                "valid_from": "2026-08-29T03:00:00+00:00",
                "expires_at": "2026-08-29T04:00:00+00:00",
                "revocation_ref": None,
            }
        },
        "owner_evidence_digest": "sha256:" + "a" * 64,
        "egress_policy_ref": "egress:1",
    }


def test_compile_record_matches_alex_handshake_shape_and_digest():
    record = compile_loadout(base_spec())
    assert set(record) == COMPILE_KEYS
    assert record["schema"] == "loadout.compile/v0"
    assert record["compile_digest"] == compile_payload_digest(record)
    assert record["capability_bindings"] == [
        {"capability": "repo.read", "status": "available"},
        {"capability": "repo.write", "status": "available"},
    ]
    assert record["effective_effects"][0]["effect"] == "repo.branch.write"
    assert record["effective_effects"][0]["status"] == "allowed"
    assert record["effective_effects"][0]["authorization_source_ref"] == "owner-receipt:1"
    assert record["effective_effects"][0]["owner_gate_ref"] == "owner-gate:1"


def test_child_compile_does_not_inherit_effect_authority_without_new_fence():
    spec = base_spec()
    spec["compile_id"] = "compile-child"
    spec["parent_compile_id"] = "compile-parent"
    spec["effect_fence"] = []
    record = compile_loadout(spec)
    write = next(item for item in record["capability_bindings"] if item["capability"] == "repo.write")
    assert write["status"] == "unavailable"
    effect = record["effective_effects"][0]
    assert effect["status"] == "refused"
    assert effect["authorization_source_ref"] is None


def test_alex_envelope_is_exact_lowering_of_compile():
    record = compile_loadout(base_spec())
    envelope = to_alex_envelope(record, {
        "run_id": "run-1",
        "phase": "research",
        "question": "What changed?",
        "task_shape": "COMPARE",
        "input_record_ids": ["record:1"],
        "rule_profile": "alex.runtime/loadout-handshake-m0",
        "stop_condition": "Return the comparison receipt.",
        "requested_outputs": ["receipt"],
    })
    assert set(envelope) == ENVELOPE_KEYS
    assert envelope["schema"] == "alex.run-envelope/v0"
    assert envelope["compile_id"] == record["compile_id"]
    assert envelope["compile_digest"] == record["compile_digest"]
    assert envelope["compile_trace_ref"] == record["compile_trace"]["id"]
    assert envelope["effect_fence_ref"] == record["effect_fence_ref"]


def test_effect_fence_without_attributable_authorization_does_not_bind_effectful_capability():
    spec = base_spec()
    spec["effect_authorizations"] = {}
    record = compile_loadout(spec)
    write = next(item for item in record["capability_bindings"] if item["capability"] == "repo.write")
    assert write["status"] == "unavailable"
    effect = record["effective_effects"][0]
    assert effect["status"] == "refused"
    assert effect["owner_gate_ref"] is None
