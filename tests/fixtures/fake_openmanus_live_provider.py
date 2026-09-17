from __future__ import annotations

import json
from pathlib import Path
import sys


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "ok"
    envelope = json.loads(sys.stdin.read())
    if envelope.get("schema") != "loadout.openmanus-worker-envelope/v0":
        return 2
    if envelope.get("effect") != "LOCAL_MUTATE":
        return 3
    if envelope.get("target") != "workspace:specimen":
        return 4

    workspace = Path(envelope["workspace_root"])
    specimen = workspace / "specimen"

    if mode == "provider-refused":
        result = {
            "schema": "loadout.openmanus-worker-result/v0",
            "disposition": "REFUSED",
            "observed_post_state": None,
            "artifacts": [],
            "observations": [],
            "provider_receipt": {
                "steps_executed": 1,
                "termination": "FAKE_LIVE_REFUSED",
            },
        }
        print(json.dumps(result, sort_keys=True))
        return 0

    output = b"OPENMANUS-LIVE-001 OUTPUT" + bytes([10])
    if mode == "wrong-output":
        output = b"WRONG" + bytes([10])
    (specimen / "output.txt").write_bytes(output)
    if mode == "unexpected-delta":
        (specimen / "rogue.txt").write_text("rogue", encoding="utf-8")

    result = {
        "schema": "loadout.openmanus-worker-result/v0",
        "disposition": "COMPLETED",
        "observed_post_state": "fake-live:state:1",
        "artifacts": [{"path": "specimen/output.txt"}],
        "observations": [
            {
                "tool": "loadout_read_text",
                "relative_path": "specimen/input.txt",
                "content": "OPENMANUS-LIVE-001 INPUT",
            },
            {
                "tool": "loadout_write_text",
                "relative_path": "specimen/output.txt",
            },
        ],
        "provider_receipt": {
            "steps_executed": 2,
            "termination": "FAKE_LIVE_COMPLETE",
        },
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
