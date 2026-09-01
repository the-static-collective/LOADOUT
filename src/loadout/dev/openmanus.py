from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Mapping, Sequence

from loadout.dev.model import EffectClass, EffectIntent, parameter_map

OPENMANUS_ADAPTER_ID = "openmanus.worker.json-stdio/v0"
OPENMANUS_ENVELOPE_SCHEMA = "loadout.openmanus-worker-envelope/v0"
OPENMANUS_RESULT_SCHEMA = "loadout.openmanus-worker-result/v0"

_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_ALLOWED_EFFECTS = frozenset(
    {
        EffectClass.OBSERVE,
        EffectClass.LOCAL_COMPUTE,
        EffectClass.LOCAL_MUTATE,
    }
)


@dataclass(frozen=True)
class OpenManusProviderReceipt:
    body_time_id: str
    capability: str
    effect: EffectClass
    target: str
    precondition_state: str
    disposition: str
    observed_post_state: str | None
    artifacts: tuple[object, ...]
    observations: tuple[object, ...]
    steps_executed: int
    termination: str
    stderr: str


class OpenManusJsonStdioAdapter:
    def __init__(
        self,
        *,
        provider_command: Sequence[str],
        workspace_root: str | Path,
        body_time_id: str,
        child_env: Mapping[str, str] | None = None,
        timeout_seconds: float = 30.0,
        max_steps: int = 20,
    ) -> None:
        prefix = f"{OPENMANUS_ADAPTER_ID}@"
        source_sha = body_time_id[len(prefix) :] if body_time_id.startswith(prefix) else ""
        if _SHA40.fullmatch(source_sha) is None:
            raise ValueError("body_time_id must be openmanus adapter id plus exact sha40")
        if not provider_command or any(
            not isinstance(part, str) or not part for part in provider_command
        ):
            raise ValueError("provider_command must be a non-empty argv sequence")
        root = Path(workspace_root).resolve()
        if not root.is_dir():
            raise ValueError("workspace_root must exist and be a directory")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if max_steps <= 0:
            raise ValueError("max_steps must be positive")
        self.provider_command = tuple(provider_command)
        self.workspace_root = root
        self.body_time_id = body_time_id
        self.child_env = dict(child_env or {})
        self.timeout_seconds = float(timeout_seconds)
        self.max_steps = int(max_steps)
        self._provider_receipts: list[OpenManusProviderReceipt] = []

    @property
    def provider_receipts(self) -> tuple[OpenManusProviderReceipt, ...]:
        return tuple(self._provider_receipts)

    def _build_envelope(self, intent: EffectIntent) -> dict[str, object]:
        if intent.effect not in _ALLOWED_EFFECTS:
            raise ValueError("unsupported OpenManus effect")
        params = parameter_map(intent)
        return {
            "schema": OPENMANUS_ENVELOPE_SCHEMA,
            "body_time_id": self.body_time_id,
            "capability": intent.capability,
            "effect": intent.effect.value,
            "target": intent.target,
            "precondition_state": intent.precondition_state,
            "parameters_digest": intent.parameters_digest,
            "parameters": params,
            "workspace_root": str(self.workspace_root),
            "max_steps": self.max_steps,
        }
