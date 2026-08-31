from loadout.dev.model import EffectClass, RefusalReason, Verb, WorkflowEvent
from loadout.dev.workflow import DEV_LAND, start_workflow, transition


def accept(state, event):
    result = transition(state, event)
    assert result.reason is None
    return result.state


def test_verify_fresh_001_mutation_expires_prior_verification():
    state = start_workflow(DEV_LAND, current_state_id="H0", scope="pr:2")
    state = accept(state, WorkflowEvent(Verb.PROPOSE, "H0", scope="pr:2"))
    state = accept(state, WorkflowEvent(Verb.VERIFY, "H0", scope="pr:2"))
    state = accept(state, WorkflowEvent(Verb.MUTATE, "H1", scope="pr:2", effect=EffectClass.REMOTE_PROPOSE))
    assert state.current_state_id == "H1"
    assert state.verified_state_id is None
    assert state.ready_state_id is None
    assert state.admitted_state_id is None


def test_ready_requires_current_state_verification():
    state = start_workflow(DEV_LAND, current_state_id="H0", scope="pr:2")
    state = accept(state, WorkflowEvent(Verb.PROPOSE, "H0", scope="pr:2"))
    result = transition(state, WorkflowEvent(Verb.READY, "H0", scope="pr:2"))
    assert result.reason == RefusalReason.VERIFICATION_STALE


def test_head_drift_001_invalidates_ready_and_owner_admission():
    state = start_workflow(DEV_LAND, current_state_id="H0", scope="pr:2")
    for verb in (Verb.PROPOSE, Verb.VERIFY, Verb.READY, Verb.ADMIT):
        state = accept(state, WorkflowEvent(verb, "H0", scope="pr:2"))
    state = accept(state, WorkflowEvent(Verb.MUTATE, "H1", scope="pr:2", effect=EffectClass.REMOTE_PROPOSE))
    result = transition(state, WorkflowEvent(Verb.LAND, "H1", scope="pr:2", effect=EffectClass.LAND))
    assert result.reason == RefusalReason.OWNER_GATE_STALE
