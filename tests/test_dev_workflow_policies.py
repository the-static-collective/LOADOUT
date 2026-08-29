from loadout.dev.model import EffectClass, EvidenceKind, RefusalReason, Verb, WorkflowEvent
from loadout.dev.workflow import DEV_DEBUG, DEV_DOCS, DEV_IMPLEMENT, DEV_REVIEW, start_workflow, transition


def accept(state, event):
    result = transition(state, event)
    assert result.reason is None
    return result.state


def test_design_gate_001_requires_attributed_design_admission():
    state = start_workflow(DEV_IMPLEMENT, current_state_id="W0", scope="repo:LOADOUT")
    result = transition(state, WorkflowEvent(Verb.MUTATE, "W1", scope="repo:LOADOUT", effect=EffectClass.LOCAL_MUTATE))
    assert result.reason == RefusalReason.DESIGN_GATE_REQUIRED


def test_red_first_001_red_witness_precedes_mutation():
    state = start_workflow(DEV_IMPLEMENT, current_state_id="W0", scope="repo:LOADOUT", design_admission_ref="design:approved")
    result = transition(state, WorkflowEvent(Verb.MUTATE, "W1", scope="repo:LOADOUT", effect=EffectClass.LOCAL_MUTATE))
    assert result.reason == RefusalReason.WITNESS_REQUIRED
    state = accept(state, WorkflowEvent(Verb.WITNESS, "W0", evidence=EvidenceKind.TEST_RED, scope="repo:LOADOUT"))
    assert transition(state, WorkflowEvent(Verb.MUTATE, "W1", scope="repo:LOADOUT", effect=EffectClass.LOCAL_MUTATE)).reason is None


def test_root_cause_001_requires_hypothesis_and_probe_before_repair():
    state = start_workflow(DEV_DEBUG, current_state_id="B0", scope="repo:LOADOUT")
    state = accept(state, WorkflowEvent(Verb.CONTRACT, "B0", evidence=EvidenceKind.ROOT_CAUSE_HYPOTHESIS, scope="repo:LOADOUT"))
    assert transition(state, WorkflowEvent(Verb.REPAIR, "B1", scope="repo:LOADOUT", effect=EffectClass.LOCAL_MUTATE)).reason == RefusalReason.ROOT_CAUSE_REQUIRED
    state = accept(state, WorkflowEvent(Verb.PROBE, "B0", evidence=EvidenceKind.ROOT_CAUSE_PROBE, scope="repo:LOADOUT"))
    assert transition(state, WorkflowEvent(Verb.REPAIR, "B1", scope="repo:LOADOUT", effect=EffectClass.LOCAL_MUTATE)).reason is None


def test_review_scope_001_out_of_scope_pressure_cannot_expand_repair():
    state = start_workflow(DEV_REVIEW, current_state_id="R0", scope="repo:LOADOUT")
    state = accept(state, WorkflowEvent(Verb.PRESS, "R0", evidence=EvidenceKind.REVIEW_FINDING, scope="repo:OTHER"))
    result = transition(state, WorkflowEvent(Verb.REPAIR, "R1", scope="repo:OTHER", effect=EffectClass.LOCAL_MUTATE))
    assert result.reason == RefusalReason.REVIEW_SCOPE_EXCEEDED
    assert result.state.scope == "repo:LOADOUT"


def test_doc_publish_001_publish_requires_prior_proposal():
    state = start_workflow(DEV_DOCS, current_state_id="D0", scope="docs:front-room")
    assert transition(state, WorkflowEvent(Verb.LAND, "D0", scope="docs:front-room", effect=EffectClass.PUBLISH)).reason == RefusalReason.PROPOSAL_REQUIRED
    state = accept(state, WorkflowEvent(Verb.PROPOSE, "D0", scope="docs:front-room"))
    state = accept(state, WorkflowEvent(Verb.VERIFY, "D0", scope="docs:front-room"))
    state = accept(state, WorkflowEvent(Verb.READY, "D0", scope="docs:front-room"))
    state = accept(state, WorkflowEvent(Verb.ADMIT, "D0", scope="docs:front-room"))
    assert transition(state, WorkflowEvent(Verb.LAND, "D0", scope="docs:front-room", effect=EffectClass.PUBLISH)).reason is None
