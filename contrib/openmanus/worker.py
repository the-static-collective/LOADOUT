from __future__ import annotations

import asyncio
from contextlib import redirect_stdout
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from bounded_ops import evaluate_arithmetic, read_text, write_text

ENVELOPE_SCHEMA = "loadout.openmanus-worker-envelope/v0"
RESULT_SCHEMA = "loadout.openmanus-worker-result/v0"
_ALLOWED_EFFECTS = {"OBSERVE", "LOCAL_COMPUTE", "LOCAL_MUTATE"}

_SYSTEM_PROMPT = """You are a bounded worker inside a LOADOUT-constituted occurrence.
Use only the supplied tools.
Do not claim authority, publication, external mutation, or access beyond the declared workspace.
Finish with Terminate when the bounded request is complete or cannot be completed.
"""


def _result(
    disposition: str,
    *,
    observed_post_state: str | None = None,
    artifacts: list[object] | None = None,
    observations: list[object] | None = None,
    steps_executed: int = 0,
    termination: str,
) -> dict[str, object]:
    return {
        "schema": RESULT_SCHEMA,
        "disposition": disposition,
        "observed_post_state": observed_post_state,
        "artifacts": artifacts or [],
        "observations": observations or [],
        "provider_receipt": {
            "steps_executed": steps_executed,
            "termination": termination,
        },
    }


def _validate_envelope(value: object) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(value, dict) or value.get("schema") != ENVELOPE_SCHEMA:
        return None, "INVALID_ENVELOPE"
    effect = value.get("effect")
    workspace_root = value.get("workspace_root")
    parameters = value.get("parameters")
    max_steps = value.get("max_steps")
    if effect not in _ALLOWED_EFFECTS:
        return None, "INVALID_ENVELOPE"
    if not isinstance(workspace_root, str) or not Path(workspace_root).is_dir():
        return None, "INVALID_ENVELOPE"
    if not isinstance(parameters, dict) or not all(
        isinstance(key, str) and isinstance(item, str)
        for key, item in parameters.items()
    ):
        return None, "INVALID_ENVELOPE"
    request = parameters.get("request")
    if not isinstance(request, str) or not request.strip():
        return None, "INVALID_ENVELOPE"
    if not isinstance(max_steps, int) or isinstance(max_steps, bool) or max_steps < 1:
        return None, "INVALID_ENVELOPE"
    for field in (
        "body_time_id",
        "capability",
        "target",
        "precondition_state",
        "parameters_digest",
    ):
        if not isinstance(value.get(field), str) or not value[field]:
            return None, "INVALID_ENVELOPE"
    return value, None


def _artifact_state(workspace_root: Path, artifact_paths: list[str]) -> str | None:
    if not artifact_paths:
        return None
    digest = hashlib.sha256()
    for relative_path in sorted(set(artifact_paths)):
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        try:
            content = read_text(workspace_root, relative_path)
        except (OSError, ValueError):
            content = "<unreadable>"
        digest.update(content.encode("utf-8"))
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


async def _run_openmanus(envelope: dict[str, Any]) -> dict[str, object]:
    try:
        from app.agent.toolcall import ToolCallAgent
        from app.tool.base import BaseTool
        from app.tool.terminate import Terminate
        from app.tool.tool_collection import ToolCollection
    except Exception as error:
        print(f"OpenManus provider import failed: {error}", file=sys.stderr)
        return _result("ERROR", termination="PROVIDER_UNAVAILABLE")

    workspace_root = Path(envelope["workspace_root"]).resolve()
    effect = envelope["effect"]
    request = envelope["parameters"]["request"]
    observations: list[object] = []
    artifacts: list[str] = []

    class LoadoutReadText(BaseTool):
        name: str = "loadout_read_text"
        description: str = "Read one UTF-8 text file by path relative to the declared LOADOUT workspace."
        parameters: dict = {
            "type": "object",
            "properties": {
                "relative_path": {"type": "string", "description": "Path relative to the declared workspace root."}
            },
            "required": ["relative_path"],
        }

        async def execute(self, relative_path: str):
            try:
                content = read_text(workspace_root, relative_path)
            except (OSError, ValueError) as error:
                return self.fail_response(str(error))
            observation = {"tool": self.name, "relative_path": relative_path, "content": content}
            observations.append(observation)
            return self.success_response(observation)

    class LoadoutCalculate(BaseTool):
        name: str = "loadout_calculate"
        description: str = "Evaluate bounded basic arithmetic only. No names, calls, comprehensions, powers, or Python execution."
        parameters: dict = {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Basic bounded arithmetic expression."}
            },
            "required": ["expression"],
        }

        async def execute(self, expression: str):
            try:
                value = evaluate_arithmetic(expression)
            except ValueError as error:
                return self.fail_response(str(error))
            observation = {"tool": self.name, "expression": expression, "value": value}
            observations.append(observation)
            return self.success_response(observation)

    class LoadoutWriteText(BaseTool):
        name: str = "loadout_write_text"
        description: str = "Write UTF-8 text only to a path relative to the declared LOADOUT workspace."
        parameters: dict = {
            "type": "object",
            "properties": {
                "relative_path": {"type": "string", "description": "Path relative to the declared workspace root."},
                "content": {"type": "string", "description": "Complete UTF-8 text content to write."},
            },
            "required": ["relative_path", "content"],
        }

        async def execute(self, relative_path: str, content: str):
            try:
                written = write_text(workspace_root, relative_path, content)
            except (OSError, ValueError) as error:
                return self.fail_response(str(error))
            if written not in artifacts:
                artifacts.append(written)
            observation = {"tool": self.name, "relative_path": written, "written": True}
            observations.append(observation)
            return self.success_response(observation)

    tools: list[Any]
    if effect == "OBSERVE":
        tools = [LoadoutReadText()]
    elif effect == "LOCAL_COMPUTE":
        tools = [LoadoutCalculate()]
    else:
        tools = [LoadoutReadText(), LoadoutWriteText()]

    terminate = Terminate()
    tools.append(terminate)
    agent = ToolCallAgent(
        name="loadout_openmanus_worker",
        description="A mortal bounded worker constituted by LOADOUT.",
        system_prompt=_SYSTEM_PROMPT,
        next_step_prompt="Work only inside the declared request and supplied tool surface.",
        available_tools=ToolCollection(*tools),
        special_tool_names=[terminate.name],
        max_steps=envelope["max_steps"],
    )

    try:
        run_output = await agent.run(request)
    except Exception as error:
        print(f"OpenManus worker error: {error}", file=sys.stderr)
        return _result(
            "ERROR",
            artifacts=list(artifacts),
            observations=observations,
            steps_executed=getattr(agent, "current_step", 0),
            termination="AGENT_ERROR",
        )

    steps = getattr(agent, "current_step", 0)
    if "Terminated: Reached max steps" in run_output:
        disposition = "ERROR"
        termination = "MAX_STEPS"
    else:
        disposition = "COMPLETED"
        termination = "COMPLETED"
    return _result(
        disposition,
        observed_post_state=_artifact_state(workspace_root, artifacts),
        artifacts=list(artifacts),
        observations=observations,
        steps_executed=steps,
        termination=termination,
    )


def main() -> int:
    raw = sys.stdin.read()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        value = None
    envelope, error = _validate_envelope(value)
    if error is not None or envelope is None:
        print(json.dumps(_result("REFUSED", termination="INVALID_ENVELOPE"), sort_keys=True))
        return 0

    with redirect_stdout(sys.stderr):
        result = asyncio.run(_run_openmanus(envelope))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
