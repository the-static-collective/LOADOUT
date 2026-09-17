from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

from loadout.dev.openmanus_live import run_live_specimen


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKER = REPO_ROOT / "contrib" / "openmanus" / "worker.py"


def _absolute_path(parser: argparse.ArgumentParser, label: str, raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        parser.error(f"{label} must be absolute")
    return path


def _is_within(parent: Path, child: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run one bounded OPENMANUS-LIVE-001 provider occurrence."
    )
    parser.add_argument("--provider-checkout", required=True)
    parser.add_argument("--provider-python", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model-config-class", required=True)
    parser.add_argument("--forward-env", action="append", default=[])
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--max-steps", type=int, default=20)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    provider_checkout = _absolute_path(
        parser, "provider-checkout", args.provider_checkout
    )
    provider_python = _absolute_path(parser, "provider-python", args.provider_python)
    workspace = _absolute_path(parser, "workspace", args.workspace)
    output = _absolute_path(parser, "output", args.output)

    if not args.model_config_class.strip():
        parser.error("model-config-class must be non-empty")
    if args.timeout_seconds <= 0:
        parser.error("timeout-seconds must be positive")
    if args.max_steps < 1:
        parser.error("max-steps must be at least 1")
    if _is_within(workspace, output):
        parser.error("output must be outside workspace")
    if not WORKER.is_file():
        parser.error("OPENMANUS-LIVE-001 worker is unavailable")

    try:
        bundle_path = run_live_specimen(
            provider_checkout=provider_checkout,
            provider_command=(str(provider_python), str(WORKER)),
            workspace_root=workspace,
            output_dir=output,
            model_config_class=args.model_config_class,
            forwarded_env_names=tuple(args.forward_env),
            source_env=os.environ,
            timeout_seconds=args.timeout_seconds,
            max_steps=args.max_steps,
        )
    except ValueError as error:
        parser.error(str(error))

    print(bundle_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
