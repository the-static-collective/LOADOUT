from __future__ import annotations

import argparse
from pathlib import Path
import sys

from loadout.dev.openmanus_live import verify_live_bundle


def _absolute_path(parser: argparse.ArgumentParser, label: str, raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        parser.error(f"{label} must be absolute")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Independently verify one retained OPENMANUS-LIVE-001 bundle."
    )
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--bundle", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    workspace = _absolute_path(parser, "workspace", args.workspace)
    bundle = _absolute_path(parser, "bundle", args.bundle)

    try:
        verified, reasons = verify_live_bundle(bundle, workspace)
    except ValueError as error:
        print(f"OPENMANUS-LIVE-001 HOLD: {error}", file=sys.stderr)
        return 1

    if verified:
        print("OPENMANUS-LIVE-001 VERIFIED")
        return 0

    reason_text = ", ".join(reasons) if reasons else "UNSPECIFIED"
    print(f"OPENMANUS-LIVE-001 HOLD: {reason_text}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
