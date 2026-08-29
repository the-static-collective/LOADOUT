from loadout.compile import compile_loadout
from loadout.decay import decay_reasons
from loadout.pressure.recompile import (
    apply_recompile_proposal,
    gate_recompile_proposal,
    propose_recompile,
)


def base_compile():
    return compile_loadout({
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
            "declared_loss": [],
            "producer": "loadout.kernel/v0",
            "freshness": "2026-08-29T03:00:00+00:00",
        },
        "capabilities": [
            {"capability": "repo.read", "operation": "inspect", "reachable_effects": [], "parameters": {}}
        ],
        "effect_fence": [],
        "effect_fence_ref": "fence:1",
        "owner_evidence_digest": "sha256:" + "a" * 64,
        "egress_policy_ref": "egress:1",
    })


def test_expired_compile_and_external_decay_signals_are_explicit():
    record = base_compile()
    reasons = decay_reasons(record, "2026-08-29T05:00:00+00:00", {"head_changed": True})
    assert reasons == ["COMPILE_EXPIRED", "HEAD_CHANGED"]


def test_recompile_proposal_cannot_apply_without_matching_admitted_gate():
    base = base_compile()
    proposal = propose_recompile(
        base,
        {"context_pack_ref": "context:2"},
        reason="context-freshness",
        proposal_id="proposal-1",
        proposed_compile_id="compile-2",
    )
    try:
        apply_recompile_proposal(base, proposal, {"disposition": "ADMIT"})
    except ValueError as exc:
        assert str(exc) == "recompile gate receipt invalid"
    else:
        raise AssertionError("proposal applied without attributable gate")

    gate = gate_recompile_proposal(base, proposal)
    assert gate["disposition"] == "ADMIT"
    child = apply_recompile_proposal(base, proposal, gate)
    assert child["compile_id"] == "compile-2"
    assert child["parent_compile_id"] == "compile-1"
    assert child["context_pack_ref"] == "context:2"
    assert child["compile_digest"] != base["compile_digest"]


def test_meta_gate_refuses_authority_expansion():
    base = base_compile()
    proposal = propose_recompile(
        base,
        {
            "effective_effects": [{
                "effect": "repo.branch.write",
                "status": "allowed",
                "authorization_source_ref": "invented",
                "scope": "repo.branch.write",
                "valid_from": "2026-08-29T03:00:00+00:00",
                "expires_at": "2026-08-29T04:00:00+00:00",
                "revocation_ref": None,
                "owner_gate_ref": "invented",
            }]
        },
        reason="meta-wants-write",
        proposal_id="proposal-2",
        proposed_compile_id="compile-3",
    )
    gate = gate_recompile_proposal(base, proposal)
    assert gate["disposition"] == "REFUSE"
    assert gate["reason_code"] == "AUTHORITY_EXPANSION_FORBIDDEN"


def test_meta_gate_rejects_tampered_proposal_digest():
    base = base_compile()
    proposal = propose_recompile(
        base,
        {"context_pack_ref": "context:2"},
        reason="freshness",
        proposal_id="proposal-tamper",
        proposed_compile_id="compile-tamper",
    )
    proposal["patch"]["context_pack_ref"] = "context:evil"
    gate = gate_recompile_proposal(base, proposal)
    assert gate["disposition"] == "REFUSE"
    assert gate["reason_code"] == "PROPOSAL_DIGEST_MISMATCH"


def test_meta_gate_cannot_extend_compile_expiry():
    base = base_compile()
    proposal = propose_recompile(
        base,
        {"expires_at": "2026-08-29T06:00:00+00:00"},
        reason="keep-going",
        proposal_id="proposal-expiry",
        proposed_compile_id="compile-expiry",
    )
    gate = gate_recompile_proposal(base, proposal)
    assert gate["disposition"] == "REFUSE"
    assert gate["reason_code"] == "EXPIRY_EXTENSION_FORBIDDEN"


def test_meta_gate_cannot_change_effect_fence_reference():
    base = base_compile()
    proposal = propose_recompile(
        base,
        {"effect_fence_ref": "fence:wider"},
        reason="widen-fence",
        proposal_id="proposal-fence",
        proposed_compile_id="compile-fence",
    )
    gate = gate_recompile_proposal(base, proposal)
    assert gate["disposition"] == "REFUSE"
    assert gate["reason_code"] == "FENCE_CHANGE_REQUIRES_OWNER_GATE"


def test_meta_gate_cannot_change_egress_policy_reference():
    base = base_compile()
    proposal = propose_recompile(
        base,
        {"egress_policy_ref": "egress:wider"},
        reason="widen-egress",
        proposal_id="proposal-egress",
        proposed_compile_id="compile-egress",
    )
    gate = gate_recompile_proposal(base, proposal)
    assert gate["disposition"] == "REFUSE"
    assert gate["reason_code"] == "EGRESS_CHANGE_REQUIRES_OWNER_GATE"


def test_meta_gate_cannot_rewrite_existing_effect_authorization_provenance():
    base = compile_loadout({
        "compile_id": "compile-effect-base",
        "parent_compile_id": None,
        "issued_at": "2026-08-29T03:00:00+00:00",
        "expires_at": "2026-08-29T04:00:00+00:00",
        "world_cut_ref": "world:1",
        "context_pack_ref": "context:1",
        "compile_trace": {
            "id": "trace:effect",
            "source_world_ref": "world:0",
            "operation": "bounded-compile",
            "preserved_invariants": [],
            "declared_loss": [],
            "producer": "loadout.kernel/v0",
            "freshness": "2026-08-29T03:00:00+00:00",
        },
        "capabilities": [
            {
                "capability": "repo.write",
                "operation": "intervene",
                "reachable_effects": ["repo.branch.write"],
                "parameters": {},
            }
        ],
        "effect_fence": ["repo.branch.write"],
        "effect_fence_ref": "fence:1",
        "effect_authorizations": {
            "repo.branch.write": {
                "authorization_source_ref": "owner-receipt:real",
                "owner_gate_ref": "owner-gate:real",
                "scope": "repo.branch.write",
                "valid_from": "2026-08-29T03:00:00+00:00",
                "expires_at": "2026-08-29T04:00:00+00:00",
                "revocation_ref": None,
            }
        },
        "owner_evidence_digest": "sha256:" + "a" * 64,
        "egress_policy_ref": "egress:1",
    })
    rewritten = [dict(base["effective_effects"][0], authorization_source_ref="owner-receipt:invented")]
    proposal = propose_recompile(
        base,
        {"effective_effects": rewritten},
        reason="rewrite-provenance",
        proposal_id="proposal-provenance",
        proposed_compile_id="compile-provenance",
    )
    gate = gate_recompile_proposal(base, proposal)
    assert gate["disposition"] == "REFUSE"
    assert gate["reason_code"] == "AUTHORIZATION_PROVENANCE_CHANGE_FORBIDDEN"
