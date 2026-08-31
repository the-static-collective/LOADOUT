import json
from pathlib import Path

from loadout.dev.compiler import compile_world
from loadout.dev.model import (
    AdapterBody, CapabilityRequest, CapabilitySpec, CompileRequest,
    Disposition, EffectClass, RefusalReason,
)

FIXTURES = Path(__file__).parent / "fixtures"


def load_body(name: str) -> AdapterBody:
    data = json.loads((FIXTURES / name).read_text())
    return AdapterBody(
        adapter_id=data["adapter_id"],
        body_time_id=data["body_time_id"],
        source_sha=data["source_sha"],
        capabilities=tuple(
            CapabilitySpec(item["name"], EffectClass(item["effect"]))
            for item in data["capabilities"]
        ),
    )


def test_mention_bind_001_provider_mention_does_not_bind():
    github = load_body("github_adapter_body.json")
    receipt = compile_world(CompileRequest(
        task_id="MENTION-BIND-001",
        task_text="Mention GitHub in the explanation.",
        cut_targets=frozenset({"repo:LOADOUT"}),
        requested_capabilities=(),
        available_bodies=(github,),
    ))
    assert receipt.disposition == Disposition.COMPILED
    assert receipt.bindings == ()


def test_caller_cannot_relabel_read_capability_as_mutation():
    github = load_body("github_adapter_body.json")
    receipt = compile_world(CompileRequest(
        task_id="effect-declaration",
        task_text="Inspect repo.",
        cut_targets=frozenset({"repo:LOADOUT"}),
        requested_capabilities=(
            CapabilityRequest("repo.inspect", EffectClass.REMOTE_MUTATE, "repo:LOADOUT"),
        ),
        available_bodies=(github,),
    ))
    assert receipt.disposition == Disposition.REFUSED
    assert receipt.reasons == (RefusalReason.EFFECT_OUTSIDE_FENCE,)


def test_body_pin_001_replay_requires_exact_pin():
    github = load_body("github_adapter_body.json")
    receipt = compile_world(CompileRequest(
        task_id="BODY-PIN-001",
        task_text="Replay inspection.",
        cut_targets=frozenset({"repo:LOADOUT"}),
        requested_capabilities=(
            CapabilityRequest("repo.inspect", EffectClass.OBSERVE, "repo:LOADOUT", replay=True),
        ),
        available_bodies=(github,),
    ))
    assert receipt.disposition == Disposition.REFUSED
    assert receipt.reasons == (RefusalReason.BODY_PIN_REQUIRED,)


def test_unpinned_ambiguity_refuses_instead_of_latest_wins():
    cap = (CapabilitySpec("repo.inspect", EffectClass.OBSERVE),)
    a = AdapterBody("a", f"a@{'a'*40}", "a"*40, cap)
    b = AdapterBody("b", f"b@{'b'*40}", "b"*40, cap)
    receipt = compile_world(CompileRequest(
        task_id="ambiguous",
        task_text="Inspect.",
        cut_targets=frozenset({"repo:LOADOUT"}),
        requested_capabilities=(CapabilityRequest("repo.inspect", EffectClass.OBSERVE, "repo:LOADOUT"),),
        available_bodies=(b, a),
    ))
    assert receipt.disposition == Disposition.REFUSED
    assert receipt.reasons == (RefusalReason.BODY_AMBIGUOUS,)


def test_same_native_request_compiles_against_replaceable_pinned_bodies():
    cap = (CapabilitySpec("proposal.create", EffectClass.REMOTE_PROPOSE),)
    bodies = (
        AdapterBody("provider-a", f"provider-a@{'a'*40}", "a"*40, cap),
        AdapterBody("provider-b", f"provider-b@{'b'*40}", "b"*40, cap),
    )
    for body in bodies:
        receipt = compile_world(CompileRequest(
            task_id="portable",
            task_text="Propose change.",
            cut_targets=frozenset({"proposal:1"}),
            requested_capabilities=(CapabilityRequest(
                "proposal.create", EffectClass.REMOTE_PROPOSE, "proposal:1",
                body_time_id=body.body_time_id,
            ),),
            available_bodies=bodies,
        ))
        assert receipt.disposition == Disposition.COMPILED
        assert receipt.bindings[0].capability == "proposal.create"
        assert receipt.bindings[0].effect == EffectClass.REMOTE_PROPOSE
        assert receipt.bindings[0].body_time_id == body.body_time_id
