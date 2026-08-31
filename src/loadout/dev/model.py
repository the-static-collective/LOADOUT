from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re

_SHA40 = re.compile(r"^[0-9a-f]{40}$")


class Disposition(StrEnum):
    COMPILED = "COMPILED"
    REFUSED = "REFUSED"
    CAPABILITY_GAP = "CAPABILITY_GAP"
    OWNER_GATE = "OWNER_GATE"


class EffectClass(StrEnum):
    OBSERVE = "OBSERVE"
    REPRESENT = "REPRESENT"
    LOCAL_COMPUTE = "LOCAL_COMPUTE"
    LOCAL_MUTATE = "LOCAL_MUTATE"
    REMOTE_PROPOSE = "REMOTE_PROPOSE"
    REMOTE_MUTATE = "REMOTE_MUTATE"
    PUBLISH = "PUBLISH"
    LAND = "LAND"


class Verb(StrEnum):
    CUT = "CUT"
    CONTRACT = "CONTRACT"
    BIND = "BIND"
    FENCE = "FENCE"
    PROBE = "PROBE"
    WITNESS = "WITNESS"
    MUTATE = "MUTATE"
    VERIFY = "VERIFY"
    PROPOSE = "PROPOSE"
    PRESS = "PRESS"
    REPAIR = "REPAIR"
    READY = "READY"
    ADMIT = "ADMIT"
    LAND = "LAND"
    RECEIPT = "RECEIPT"
    REFUSE = "REFUSE"


class EvidenceKind(StrEnum):
    TEST_RED = "TEST_RED"
    TEST_GREEN = "TEST_GREEN"
    ROOT_CAUSE_HYPOTHESIS = "ROOT_CAUSE_HYPOTHESIS"
    ROOT_CAUSE_PROBE = "ROOT_CAUSE_PROBE"
    REVIEW_FINDING = "REVIEW_FINDING"
    CHECK = "CHECK"


class RefusalReason(StrEnum):
    CAPABILITY_UNAVAILABLE = "CAPABILITY_UNAVAILABLE"
    CAPABILITY_NOT_BOUND = "CAPABILITY_NOT_BOUND"
    BODY_AMBIGUOUS = "BODY_AMBIGUOUS"
    BODY_PIN_REQUIRED = "BODY_PIN_REQUIRED"
    BODY_NOT_ELIGIBLE = "BODY_NOT_ELIGIBLE"
    EFFECT_OUTSIDE_FENCE = "EFFECT_OUTSIDE_FENCE"
    TARGET_OUTSIDE_CUT = "TARGET_OUTSIDE_CUT"
    STATE_STALE = "STATE_STALE"
    VERIFICATION_STALE = "VERIFICATION_STALE"
    WITNESS_REQUIRED = "WITNESS_REQUIRED"
    DESIGN_GATE_REQUIRED = "DESIGN_GATE_REQUIRED"
    ROOT_CAUSE_REQUIRED = "ROOT_CAUSE_REQUIRED"
    REVIEW_SCOPE_EXCEEDED = "REVIEW_SCOPE_EXCEEDED"
    PROPOSAL_REQUIRED = "PROPOSAL_REQUIRED"
    OWNER_GATE_REQUIRED = "OWNER_GATE_REQUIRED"
    OWNER_GATE_STALE = "OWNER_GATE_STALE"
    PROVIDER_REFUSED = "PROVIDER_REFUSED"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"


@dataclass(frozen=True)
class CapabilitySpec:
    name: str
    effect: EffectClass


@dataclass(frozen=True)
class AdapterBody:
    adapter_id: str
    body_time_id: str
    source_sha: str
    capabilities: tuple[CapabilitySpec, ...]
    authority: str = "none"

    def __post_init__(self) -> None:
        if not _SHA40.fullmatch(self.source_sha):
            raise ValueError("source_sha must be 40 lowercase hexadecimal characters")
        expected = f"{self.adapter_id}@{self.source_sha}"
        if self.body_time_id != expected:
            raise ValueError(f"body_time_id must equal {expected}")
        if self.authority != "none":
            raise ValueError("adapter bodies must carry authority: none")


@dataclass(frozen=True)
class CapabilityRequest:
    capability: str
    effect: EffectClass
    target: str
    body_time_id: str | None = None
    replay: bool = False


@dataclass(frozen=True)
class Binding:
    capability: str
    effect: EffectClass
    target: str
    body_time_id: str


@dataclass(frozen=True)
class CompileRequest:
    task_id: str
    task_text: str
    cut_targets: frozenset[str]
    requested_capabilities: tuple[CapabilityRequest, ...]
    available_bodies: tuple[AdapterBody, ...]


@dataclass(frozen=True)
class CompileReceipt:
    disposition: Disposition
    task_id: str
    bindings: tuple[Binding, ...] = ()
    reasons: tuple[RefusalReason, ...] = ()


@dataclass(frozen=True)
class EffectIntent:
    capability: str
    effect: EffectClass
    target: str
    body_time_id: str
    precondition_state: str
    parameters_digest: str
    parameters: tuple[tuple[str, str], ...] = ()


def parameter_map(intent: EffectIntent) -> dict[str, str]:
    """Return bounded string parameters, refusing duplicate keys."""

    result: dict[str, str] = {}
    for pair in intent.parameters:
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise ValueError("parameters must be key/value pairs")
        key, value = pair
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("parameter keys and values must be strings")
        if key in result:
            raise ValueError(f"duplicate parameter key: {key}")
        result[key] = value
    return result


@dataclass(frozen=True)
class OwnerGate:
    target: str
    effect: EffectClass
    state_id: str
    approval_ref: str


@dataclass(frozen=True)
class EffectReceipt:
    body_time_id: str
    capability: str
    effect: EffectClass
    target: str
    precondition_state: str
    provider_disposition: str
    observed_post_state: str | None
    semantic_authority: bool = False
    reason: RefusalReason | None = None


@dataclass(frozen=True)
class WorkflowEvent:
    verb: Verb
    state_id: str
    evidence: EvidenceKind | None = None
    scope: str | None = None
    effect: EffectClass | None = None
    note: str = ""
