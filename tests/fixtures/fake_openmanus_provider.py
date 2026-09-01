from __future__ import annotations

import json
import os
import sys
import time


envelope = json.loads(sys.stdin.read())
mode = envelope.get("parameters", {}).get("fixture_mode", "ok")

if mode == "timeout":
    time.sleep(5)
elif mode == "malformed":
    sys.stdout.write("not-json")
elif mode == "multi":
    sys.stdout.write("{}\n{}\n")
elif mode == "wrong-schema":
    print(json.dumps({"schema": "wrong/v0", "disposition": "COMPLETED"}))
else:
    observations = [
        {
            "allowed_env": os.environ.get("LOADOUT_ALLOWED"),
            "secret_env": os.environ.get("LOADOUT_SECRET"),
            "effect": envelope["effect"],
        }
    ]
    print(
        json.dumps(
            {
                "schema": "loadout.openmanus-worker-result/v0",
                "disposition": "REFUSED" if mode == "refused" else "COMPLETED",
                "observed_post_state": None if mode == "refused" else "state:1",
                "artifacts": [{"path": "artifact.txt"}],
                "observations": observations,
                "provider_receipt": {
                    "steps_executed": 3,
                    "termination": mode,
                },
            }
        )
    )
    print("provider diagnostic", file=sys.stderr)
