from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
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
_EXPECTED_RESULT_KEYS = frozenset(
    {
        "schema",
        "disposition",
        "observed_post_state",
        "artifacts",
        "observations",
        "provider_receipt",
    }
)
_EXPECTED_PROVIDER_RECEIPT_KEYS = frozenset({"steps_executed", "termination"})


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

    def _validate_target(self, target: str) -> None:
        prefix = "workspace:"
        if not isinstance(target, str) or not target.startswith(prefix):
            raise ValueError("invalid OpenManus workspace target")
        suffix = target[len(prefix) :]
        if not suffix or "\\" in suffix:
            raise ValueError("invalid OpenManus workspace target")
        relative = PurePosixPath(suffix)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("invalid OpenManus workspace target")
        resolved = (self.workspace_root / Path(*relative.parts)).resolve()
        try:
            resolved.relative_to(self.workspace_root)
        except ValueError as error:
            raise ValueError("OpenManus target outside workspace") from error

    def _build_envelope(self, intent: EffectIntent) -> dict[str, object]:
        if intent.effect not in _ALLOWED_EFFECTS:
            raise ValueError("unsupported OpenManus effect")
        self._validate_target(intent.target)
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

    def _record_error(
        self,
        intent: EffectIntent,
        *,
        termination: str,
        stderr: str = "",
    ) -> tuple[str, None]:
        self._provider_receipts.append(
            OpenManusProviderReceipt(
                body_time_id=self.body_time_id,
                capability=intent.capability,
                effect=intent.effect,
                target=intent.target,
                precondition_state=intent.precondition_state,
                disposition="ERROR",
                observed_post_state=None,
                artifacts=(),
                observations=(),
                steps_executed=0,
                termination=termination,
                stderr=stderr,
            )
        )
        return "ERROR", None

    def _parse_result(
        self,
        intent: EffectIntent,
        stdout: str,
        stderr: str,
    ) -> tuple[str, str | None]:
        stripped = stdout.strip()
        try:
            value = json.loads(stripped)
        except (json.JSONDecodeError, TypeError):
            return self._record_error(
                intent,
                termination="MALFORMED_RESULT",
                stderr=stderr,
            )
        if not isinstance(value, dict) or value.get("schema") != OPENMANUS_RESULT_SCHEMA:
            return self._record_error(
                intent,
                termination="WRONG_RESULT_SCHEMA",
                stderr=stderr,
            )
        if set(value) != _EXPECTED_RESULT_KEYS:
            return self._record_error(
                intent,
                termination="INVALID_RESULT_SHAPE",
                stderr=stderr,
            )
        disposition = value.get("disposition")
        if disposition not in {"COMPLETED", "REFUSED", "ERROR"}:
            return self._record_error(
                intent,
                termination="INVALID_DISPOSITION",
                stderr=stderr,
            )
        post_state = value.get("observed_post_state")
        if post_state is not None and not isinstance(post_state, str):
            return self._record_error(
                intent,
                termination="INVALID_POST_STATE",
                stderr=stderr,
            )
        artifacts = value.get("artifacts")
        observations = value.get("observations")
        provider_receipt = value.get("provider_receipt")
        if (
            not isinstance(artifacts, list)
            or not isinstance(observations, list)
            or not isinstance(provider_receipt, dict)
        ):
            return self._record_error(
                intent,
                termination="INVALID_RESULT_SHAPE",
                stderr=stderr,
            )
        if set(provider_receipt) != _EXPECTED_PROVIDER_RECEIPT_KEYS:
            return self._record_error(
                intent,
                termination="INVALID_PROVIDER_RECEIPT",
                stderr=stderr,
            )
        steps = provider_receipt.get("steps_executed")
        termination = provider_receipt.get("termination")
        if (
            isinstance(steps, bool)
            or not isinstance(steps, int)
            or steps < 0
            or not isinstance(termination, str)
        ):
            return self._record_error(
                intent,
                termination="INVALID_PROVIDER_RECEIPT",
                stderr=stderr,
            )
        self._provider_receipts.append(
            OpenManusProviderReceipt(
                body_time_id=self.body_time_id,
                capability=intent.capability,
                effect=intent.effect,
                target=intent.target,
                precondition_state=intent.precondition_state,
                disposition=disposition,
                observed_post_state=post_state,
                artifacts=tuple(artifacts),
                observations=tuple(observations),
                steps_executed=steps,
                termination=termination,
                stderr=stderr,
            )
        )
        return disposition, post_state

    def invoke(self, intent: EffectIntent) -> tuple[str, str | None]:
        if intent.effect not in _ALLOWED_EFFECTS:
            return "REFUSE", None
        if intent.body_time_id != self.body_time_id:
            return "REFUSE", None
        try:
            envelope = self._build_envelope(intent)
        except ValueError:
            return "REFUSE", None
        payload = json.dumps(envelope, sort_keys=True, separators=(",", ":"))
        try:
            completed = subprocess.run(
                list(self.provider_command),
                input=payload,
                text=True,
                check=False,
                capture_output=True,
                env=dict(self.child_env),
                shell=False,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as error:
            stderr = error.stderr if isinstance(error.stderr, str) else ""
            return self._record_error(
                intent,
                termination="TIMEOUT",
                stderr=stderr,
            )
        except (FileNotFoundError, OSError) as error:
            return self._record_error(
                intent,
                termination="PROVIDER_UNAVAILABLE",
                stderr=str(error),
            )
        if completed.returncode != 0:
            return self._record_error(
                intent,
                termination=f"EXIT_{completed.returncode}",
                stderr=completed.stderr,
            )
        return self._parse_result(intent, completed.stdout, completed.stderr)


__all__ = [
    "OPENMANUS_ADAPTER_ID",
    "OPENMANUS_ENVELOPE_SCHEMA",
    "OPENMANUS_RESULT_SCHEMA",
    "OpenManusJsonStdioAdapter",
    "OpenManusProviderReceipt",
]
