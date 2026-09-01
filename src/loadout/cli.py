from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from loadout.adapters.alex import to_alex_envelope
from loadout.adapters.project0 import parse_project0_handoff
from loadout.bind import evaluate_binding
from loadout.compile import compile_loadout
from loadout.decay import decay_reasons
from loadout.delta import record_delta
from loadout.dev.live_git import resolve_current_organ_from_git
from loadout.dev.local_git import LocalGitReadAdapter
from loadout.live_surface import resolve_current_organ
from loadout.pressure.ablate import ablate_binding, task_reachable
from loadout.reconstitution import evaluate_reconstitution_threshold, reconstitute_world
from loadout.trace import trace_binding


def _read(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _emit(value) -> None:
    print(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="loadout", description="Deterministic bounded-world compiler kernel")
    commands = parser.add_subparsers(dest="command", required=True)

    bind = commands.add_parser("bind", help="Evaluate one capability against an effect fence")
    bind.add_argument("capability")
    bind.add_argument("--fence", required=True)

    compile_cmd = commands.add_parser("compile", help="Compile a bounded LOADOUT spec")
    compile_cmd.add_argument("spec")

    alex = commands.add_parser("envelope-alex", help="Lower a compile into alex.run-envelope/v0")
    alex.add_argument("compile")
    alex.add_argument("request")

    delta = commands.add_parser("delta", help="Compare two bounded records")
    delta.add_argument("left")
    delta.add_argument("right")

    reach = commands.add_parser("reach", help="Evaluate required capability reachability")
    reach.add_argument("compile")

    ablate = commands.add_parser("ablate", help="Remove one capability binding counterfactually")
    ablate.add_argument("compile")
    ablate.add_argument("capability")
    ablate.add_argument("new_compile_id")

    trace = commands.add_parser("trace", help="Render a binding decision trace")
    trace.add_argument("receipt")

    decay = commands.add_parser("decay", help="Evaluate compile decay reasons")
    decay.add_argument("compile")
    decay.add_argument("observed_at")
    decay.add_argument("--signal", action="append", default=[])

    reconstitute = commands.add_parser(
        "reconstitute",
        help="Evaluate and locally constitute one PHASELIFT crossing",
    )
    reconstitute.add_argument("project0_fixture")
    reconstitute.add_argument("project0_provenance")
    reconstitute.add_argument("request")
    reconstitute.add_argument("compile_spec")
    reconstitute.add_argument("--world-id", required=True)
    reconstitute.add_argument("--occurred-at", required=True)
    reconstitute.add_argument("--resolved-bodies", required=True)

    resolve_live = commands.add_parser(
        "resolve-live",
        help="Resolve host-supplied current-organ evidence at one exact commit SHA",
    )
    resolve_live.add_argument("manifest")
    resolve_live.add_argument("evidence")
    resolve_live.add_argument("--path", action="append", default=[])

    resolve_live_git = commands.add_parser(
        "resolve-live-git",
        help="Resolve one current-organ occurrence from a local Git repository through the read-only adapter",
    )
    resolve_live_git.add_argument("repo_root")
    resolve_live_git.add_argument("--body-time-id", required=True)
    resolve_live_git.add_argument("--ref", default="HEAD")
    resolve_live_git.add_argument("--path", action="append", default=[])

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "bind":
        _emit(evaluate_binding(_read(args.capability), _read(args.fence)))
    elif args.command == "compile":
        _emit(compile_loadout(_read(args.spec)))
    elif args.command == "envelope-alex":
        _emit(to_alex_envelope(_read(args.compile), _read(args.request)))
    elif args.command == "delta":
        _emit(record_delta(_read(args.left), _read(args.right)))
    elif args.command == "reach":
        _emit(task_reachable(_read(args.compile)))
    elif args.command == "ablate":
        _emit(ablate_binding(_read(args.compile), args.capability, args.new_compile_id))
    elif args.command == "trace":
        _emit(trace_binding(_read(args.receipt)))
    elif args.command == "decay":
        signals = {signal: True for signal in args.signal}
        _emit(decay_reasons(_read(args.compile), args.observed_at, signals))
    elif args.command == "reconstitute":
        handoff = parse_project0_handoff(
            _read(args.project0_fixture),
            _read(args.project0_provenance),
        )
        threshold = evaluate_reconstitution_threshold(handoff, _read(args.request))
        output = {"threshold": threshold}
        if threshold["disposition"] in {"LIFT", "DEGRADED"}:
            output.update(
                reconstitute_world(
                    handoff,
                    threshold,
                    _read(args.compile_spec),
                    world_id=args.world_id,
                    occurred_at=args.occurred_at,
                    resolved_bodies=_read(args.resolved_bodies),
                )
            )
        _emit(output)
    elif args.command == "resolve-live":
        result = resolve_current_organ(
            _read(args.manifest),
            _read(args.evidence),
            requested_paths=args.path,
        )
        _emit(result)
        return 0 if result["status"] == "RESOLVED" else 2
    elif args.command == "resolve-live-git":
        adapter = LocalGitReadAdapter(
            args.repo_root,
            body_time_id=args.body_time_id,
        )
        result = resolve_current_organ_from_git(
            adapter,
            ref=args.ref,
            requested_paths=args.path,
        )
        _emit(result)
        return 0 if result["status"] == "RESOLVED" else 2
    else:
        raise AssertionError(f"unhandled command: {args.command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
