from typing import Protocol
from loadout.dev.model import EffectIntent


class Adapter(Protocol):
    body_time_id: str
    def invoke(self, intent: EffectIntent) -> tuple[str, str | None]: ...


class FakeAdapter:
    def __init__(self, body_time_id: str, outcomes: dict[str, tuple[str, str | None]]) -> None:
        self.body_time_id = body_time_id
        self.outcomes = dict(outcomes)
        self.invocations: list[EffectIntent] = []

    def invoke(self, intent: EffectIntent) -> tuple[str, str | None]:
        self.invocations.append(intent)
        return self.outcomes[intent.capability]
