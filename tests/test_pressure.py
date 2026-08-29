import copy

from loadout.compile import compile_loadout
from loadout.delta import record_delta
from loadout.pressure.ablate import ablate_binding, task_reachable


def compiled():
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
            "preserved_invariants": [
                "required-capability:repo.read",
                "required-capability:repo.write",
            ],
            "declared_loss": [],
            "producer": "loadout.kernel/v0",
            "freshness": "2026-08-29T03:00:00+00:00",
        },
        "capabilities": [
            {"capability": "repo.read", "operation": "inspect", "reachable_effects": [], "parameters": {}},
            {"capability": "repo.write", "operation": "intervene", "reachable_effects": ["repo.branch.write"], "parameters": {}},
        ],
        "effect_fence": ["repo.branch.write"],
        "effect_fence_ref": "fence:1",
        "effect_authorizations": {
            "repo.branch.write": {
                "authorization_source_ref": "owner-receipt:pressure-1",
                "owner_gate_ref": "owner-gate:pressure-1",
                "scope": "repo.branch.write",
                "valid_from": "2026-08-29T03:00:00+00:00",
                "expires_at": "2026-08-29T04:00:00+00:00",
                "revocation_ref": None
            }
        },
        "owner_evidence_digest": "sha256:" + "a" * 64,
        "egress_policy_ref": "egress:1",
    })


def test_ablation_changes_task_reachability_without_mutating_parent():
    parent = compiled()
    snapshot = copy.deepcopy(parent)
    assert task_reachable(parent) == {"reachable": True, "missing_capabilities": []}
    child = ablate_binding(parent, "repo.write", "compile-2")
    assert parent == snapshot
    assert child["parent_compile_id"] == "compile-1"
    assert child["compile_id"] == "compile-2"
    assert task_reachable(child) == {"reachable": False, "missing_capabilities": ["repo.write"]}


def test_record_delta_is_deterministic_and_path_addressed():
    parent = compiled()
    child = ablate_binding(parent, "repo.write", "compile-2")
    first = record_delta(parent, child)
    second = record_delta(parent, child)
    assert first == second
    paths = [entry["path"] for entry in first]
    assert paths == sorted(paths)
    assert "compile_id" in paths
    assert "capability_bindings" in paths
