from dataclasses import dataclass, replace
from loadout.dev.model import EffectClass, EvidenceKind, RefusalReason, Verb, WorkflowEvent


@dataclass(frozen=True)
class WorkflowPolicy:
    name: str
    require_design_admission_before_mutate: bool = False
    require_red_before_mutate: bool = False
    require_root_cause_before_repair: bool = False
    lock_repair_scope: bool = False
    require_proposal_before_publish: bool = False


@dataclass(frozen=True)
class WorkflowState:
    policy: WorkflowPolicy
    current_state_id: str
    scope: str
    design_admission_ref: str | None = None
    verified_state_id: str | None = None
    proposal_seen: bool = False
    ready_state_id: str | None = None
    admitted_state_id: str | None = None
    red_witnessed: bool = False
    root_cause_hypothesis: bool = False
    root_cause_probed: bool = False
    events: tuple[WorkflowEvent, ...] = ()


@dataclass(frozen=True)
class TransitionResult:
    state: WorkflowState
    reason: RefusalReason | None = None


DEV_LAND = WorkflowPolicy(name="dev.land@0")


def start_workflow(policy, *, current_state_id, scope, design_admission_ref=None):
    return WorkflowState(policy, current_state_id, scope, design_admission_ref)


def _refuse(state, reason):
    return TransitionResult(state, reason)


def transition(state: WorkflowState, event: WorkflowEvent) -> TransitionResult:
    if event.scope is not None and event.scope != state.scope and event.verb != Verb.PRESS:
        reason = RefusalReason.REVIEW_SCOPE_EXCEEDED if event.verb == Verb.REPAIR else RefusalReason.TARGET_OUTSIDE_CUT
        return _refuse(state, reason)

    if event.verb == Verb.PROPOSE:
        return TransitionResult(replace(state, proposal_seen=True, events=state.events + (event,)))
    if event.verb == Verb.VERIFY:
        if event.state_id != state.current_state_id:
            return _refuse(state, RefusalReason.STATE_STALE)
        return TransitionResult(replace(state, verified_state_id=event.state_id, events=state.events + (event,)))
    if event.verb == Verb.READY:
        if event.state_id != state.current_state_id or state.verified_state_id != event.state_id:
            return _refuse(state, RefusalReason.VERIFICATION_STALE)
        return TransitionResult(replace(state, ready_state_id=event.state_id, events=state.events + (event,)))
    if event.verb == Verb.ADMIT:
        if event.state_id != state.current_state_id or state.ready_state_id != event.state_id:
            return _refuse(state, RefusalReason.OWNER_GATE_STALE)
        return TransitionResult(replace(state, admitted_state_id=event.state_id, events=state.events + (event,)))
    if event.verb in {Verb.MUTATE, Verb.REPAIR}:
        return TransitionResult(replace(
            state,
            current_state_id=event.state_id,
            verified_state_id=None,
            ready_state_id=None,
            admitted_state_id=None,
            events=state.events + (event,),
        ))
    if event.verb == Verb.LAND:
        if event.state_id != state.current_state_id or state.admitted_state_id != event.state_id:
            return _refuse(state, RefusalReason.OWNER_GATE_STALE)
        return TransitionResult(replace(state, events=state.events + (event,)))
    return TransitionResult(replace(state, events=state.events + (event,)))
