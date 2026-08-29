from loadout.dev.adapters import FakeAdapter
from loadout.dev.compiler import compile_world
from loadout.dev.membrane import invoke_effect
from loadout.dev.model import (
    AdapterBody, CapabilityRequest, CapabilitySpec, CompileRequest,
    EffectClass, EffectIntent, OwnerGate, RefusalReason,
)

SHA = "5" * 40
BODY_ID = f"fixture@{SHA}"
BODY = AdapterBody(
    "fixture", BODY_ID, SHA,
    (
        CapabilitySpec("repo.inspect", EffectClass.OBSERVE),
        CapabilitySpec("math.inspect", EffectClass.OBSERVE),
        CapabilitySpec("landing.request", EffectClass.LAND),
    ),
)


def compiled_for(capability, effect, target):
    return compile_world(CompileRequest(
        task_id="membrane", task_text="bounded", cut_targets=frozenset({target}),
        requested_capabilities=(CapabilityRequest(capability, effect, target, body_time_id=BODY_ID),),
        available_bodies=(BODY,),
    ))


def test_effect_fence_001_observe_binding_cannot_mutate():
    compiled = compiled_for("repo.inspect", EffectClass.OBSERVE, "repo:LOADOUT")
    intent = EffectIntent("repo.inspect", EffectClass.REMOTE_MUTATE, "repo:LOADOUT", BODY_ID, "H0", "p")
    adapter = FakeAdapter(BODY_ID, {"repo.inspect": ("OK", "H0")})
    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="H0")
    assert receipt.reason == RefusalReason.EFFECT_OUTSIDE_FENCE
    assert adapter.invocations == []


def test_wolfram_fence_001_inspect_binding_cannot_invoke_evaluate():
    compiled = compiled_for("math.inspect", EffectClass.OBSERVE, "calc:1")
    intent = EffectIntent("math.evaluate", EffectClass.REMOTE_MUTATE, "calc:1", BODY_ID, "C0", "expr")
    adapter = FakeAdapter(BODY_ID, {"math.evaluate": ("OK", "C1")})
    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="C0")
    assert receipt.reason == RefusalReason.CAPABILITY_NOT_BOUND
    assert adapter.invocations == []


def test_target_outside_binding_refuses_before_adapter():
    compiled = compiled_for("repo.inspect", EffectClass.OBSERVE, "repo:LOADOUT")
    intent = EffectIntent("repo.inspect", EffectClass.OBSERVE, "repo:OTHER", BODY_ID, "H0", "p")
    adapter = FakeAdapter(BODY_ID, {"repo.inspect": ("OK", "H0")})
    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="H0")
    assert receipt.reason == RefusalReason.TARGET_OUTSIDE_CUT
    assert adapter.invocations == []


def test_land_requires_fresh_owner_gate():
    compiled = compiled_for("landing.request", EffectClass.LAND, "pr:2")
    intent = EffectIntent("landing.request", EffectClass.LAND, "pr:2", BODY_ID, "H8", "merge")
    adapter = FakeAdapter(BODY_ID, {"landing.request": ("MERGED", "merged:H8")})
    stale = OwnerGate("pr:2", EffectClass.LAND, "H7", "approval:7")
    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="H8", owner_gate=stale)
    assert receipt.reason == RefusalReason.OWNER_GATE_STALE
    assert adapter.invocations == []


def test_result_launder_001_success_never_mints_semantic_authority():
    compiled = compiled_for("repo.inspect", EffectClass.OBSERVE, "repo:LOADOUT")
    intent = EffectIntent("repo.inspect", EffectClass.OBSERVE, "repo:LOADOUT", BODY_ID, "H0", "read")
    adapter = FakeAdapter(BODY_ID, {"repo.inspect": ("OK", "H0")})
    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="H0")
    assert receipt.provider_disposition == "OK"
    assert receipt.semantic_authority is False
    assert receipt.reason is None


def test_land_observe_001_queued_request_is_not_observed_merge():
    compiled = compiled_for("landing.request", EffectClass.LAND, "pr:2")
    intent = EffectIntent("landing.request", EffectClass.LAND, "pr:2", BODY_ID, "H9", "auto-merge")
    gate = OwnerGate("pr:2", EffectClass.LAND, "H9", "approval:9")
    adapter = FakeAdapter(BODY_ID, {"landing.request": ("QUEUED", None)})
    receipt = invoke_effect(compiled, intent, {BODY_ID: adapter}, current_state="H9", owner_gate=gate)
    assert receipt.provider_disposition == "QUEUED"
    assert receipt.observed_post_state is None
    assert receipt.semantic_authority is False
