from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loadout.canonical import canonical_json


EVIDENCE_SCHEMA = "loadout.merge-formation-evidence/v0"
RECEIPT_SCHEMA = "loadout.merge-formation-receipt/v0"
CHECK_STATES = {"pass", "fail", "not-run", "unknown"}
RESOLUTIONS = {"main", "feature", "combined", "manual", None}

_COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_FILE_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass
class MergeFormationInputError(ValueError):
    reason_code: str
    residual: str

    def __str__(self) -> str:
        return self.residual


def _refuse(reason_code: str, residual: str) -> None:
    raise MergeFormationInputError(reason_code, residual)


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _refuse("INVALID_DIGEST_STATE", f"{label} must be an object")
    return value


def _valid_commit_sha(value: Any) -> bool:
    return isinstance(value, str) and _COMMIT_SHA.fullmatch(value) is not None


def _require_identity(value: Any, label: str) -> str:
    if not _valid_commit_sha(value):
        _refuse("MISSING_IDENTITY", f"{label} must be a 40-character lowercase commit identity")
    return value


def _require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        _refuse("INVALID_DIGEST_STATE", f"{label} must be boolean")
    return value


def _require_digest_or_none(value: Any, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or _FILE_DIGEST.fullmatch(value) is None:
        _refuse("INVALID_DIGEST_STATE", f"{label} must be sha256:<64 lowercase hex> or null")
    return value


def _normalize_surface(raw_surface: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_surface, list):
        _refuse("INVALID_DIGEST_STATE", "surface must be an array")

    seen_paths: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, raw_record in enumerate(raw_surface):
        record = _require_mapping(raw_record, f"surface[{index}]")
        path = record.get("path")
        if not isinstance(path, str) or not path:
            _refuse("INVALID_DIGEST_STATE", f"surface[{index}].path must be a non-empty string")
        if path in seen_paths:
            _refuse("DUPLICATE_PATH", f"surface contains duplicate path {path!r}")
        seen_paths.add(path)

        base_digest = _require_digest_or_none(record.get("base_digest"), f"{path}.base_digest")
        main_digest = _require_digest_or_none(record.get("main_digest"), f"{path}.main_digest")
        feature_digest = _require_digest_or_none(record.get("feature_digest"), f"{path}.feature_digest")
        candidate_digest = _require_digest_or_none(
            record.get("candidate_digest"), f"{path}.candidate_digest"
        )

        main_changed = _require_bool(record.get("main_changed"), f"{path}.main_changed")
        feature_changed = _require_bool(record.get("feature_changed"), f"{path}.feature_changed")
        if main_changed != (main_digest != base_digest):
            _refuse(
                "DECLARED_CHANGE_MISMATCH",
                f"{path}.main_changed disagrees with base/main digests",
            )
        if feature_changed != (feature_digest != base_digest):
            _refuse(
                "DECLARED_CHANGE_MISMATCH",
                f"{path}.feature_changed disagrees with base/feature digests",
            )

        resolution = record.get("resolution")
        if resolution not in RESOLUTIONS:
            _refuse("INVALID_DIGEST_STATE", f"{path}.resolution is not declared")
        sentinel = record.get("sentinel", False)
        if not isinstance(sentinel, bool):
            _refuse("INVALID_DIGEST_STATE", f"{path}.sentinel must be boolean")

        normalized.append(
            {
                "path": path,
                "base_digest": base_digest,
                "main_digest": main_digest,
                "feature_digest": feature_digest,
                "candidate_digest": candidate_digest,
                "main_changed": main_changed,
                "feature_changed": feature_changed,
                "resolution": resolution,
                "sentinel": sentinel,
            }
        )

    return sorted(normalized, key=lambda item: item["path"])


def _normalize_parent_shas(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        _refuse("MISSING_IDENTITY", "candidate_parent_shas must be an array")
    parents: list[str] = []
    for index, parent in enumerate(value):
        parents.append(_require_identity(parent, f"candidate_parent_shas[{index}]"))
    return parents


def _normalize_evidence(evidence: Any) -> dict[str, Any]:
    packet = _require_mapping(evidence, "evidence")
    if packet.get("schema") != EVIDENCE_SCHEMA:
        _refuse("WRONG_SCHEMA", f"schema must equal {EVIDENCE_SCHEMA}")

    base_sha = _require_identity(packet.get("base_sha"), "base_sha")
    main_sha = _require_identity(packet.get("main_sha"), "main_sha")
    feature_sha = _require_identity(packet.get("feature_sha"), "feature_sha")
    candidate_complete = _require_bool(packet.get("candidate_complete"), "candidate_complete")
    candidate_sha = packet.get("candidate_sha")
    if candidate_complete:
        if not _valid_commit_sha(candidate_sha):
            _refuse(
                "CANDIDATE_IDENTITY_REQUIRED",
                "candidate_sha is required when candidate_complete is true",
            )
    elif candidate_sha is not None and not _valid_commit_sha(candidate_sha):
        _refuse("MISSING_IDENTITY", "candidate_sha must be null or a valid commit identity")

    behind_main = _require_bool(packet.get("behind_main"), "behind_main")
    surface_complete = _require_bool(packet.get("surface_complete"), "surface_complete")
    check_state = packet.get("combined_verification")
    if check_state not in CHECK_STATES:
        _refuse("INVALID_CHECK_STATE", "combined_verification is not a declared check state")

    return {
        "base_sha": base_sha,
        "main_sha": main_sha,
        "feature_sha": feature_sha,
        "candidate_sha": candidate_sha,
        "behind_main": behind_main,
        "surface_complete": surface_complete,
        "candidate_complete": candidate_complete,
        "combined_verification": check_state,
        "candidate_parent_shas": _normalize_parent_shas(packet.get("candidate_parent_shas", [])),
        "surface": _normalize_surface(packet.get("surface")),
    }


def _classify_paths(packet: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    main_preserved: list[str] = []
    feature_preserved: list[str] = []
    overlap: list[str] = []
    lost: list[dict[str, str]] = []
    incomplete: list[str] = []

    candidate_complete = packet["candidate_complete"]
    for record in packet["surface"]:
        path = record["path"]
        main_changed = record["main_changed"]
        feature_changed = record["feature_changed"]

        if not candidate_complete:
            if main_changed or feature_changed or record["sentinel"]:
                incomplete.append(path)
            continue

        if main_changed and feature_changed:
            overlap.append(path)
            continue

        if main_changed:
            if record["candidate_digest"] == record["main_digest"]:
                main_preserved.append(path)
            else:
                lost.append({"path": path, "side": "main"})
            continue

        if feature_changed:
            if record["candidate_digest"] == record["feature_digest"]:
                feature_preserved.append(path)
            else:
                lost.append({"path": path, "side": "feature"})
            continue

        if record["sentinel"] and record["candidate_digest"] != record["base_digest"]:
            lost.append({"path": path, "side": "sentinel"})

    paths = {
        "feature_preserved": sorted(feature_preserved),
        "main_preserved": sorted(main_preserved),
        "overlap": sorted(overlap),
        "lost": sorted(lost, key=lambda item: (item["path"], item["side"])),
        "incomplete": sorted(incomplete),
    }
    return paths, bool(lost)


def analyze_merge_formation(evidence: dict[str, object]) -> dict[str, object]:
    """Analyze frozen merge evidence without mutating or consulting any source system."""

    packet = _normalize_evidence(evidence)
    paths, content_loss = _classify_paths(packet)

    if content_loss:
        classification = "LOSS_DETECTED"
    elif not packet["surface_complete"] or not packet["candidate_complete"]:
        classification = "INCOMPLETE_EVIDENCE"
    elif paths["overlap"]:
        classification = "OVERLAP_REVIEW_REQUIRED"
    else:
        classification = "SAFE_CONTENT_COMPOSITION"

    parents = list(packet["candidate_parent_shas"])
    histories_diverged = packet["main_sha"] != packet["feature_sha"]
    multiple_parents = len(parents) > 1

    return {
        "schema": RECEIPT_SCHEMA,
        "classification": classification,
        "content_loss": content_loss,
        "behind_main": packet["behind_main"],
        "surface_complete": packet["surface_complete"],
        "candidate_complete": packet["candidate_complete"],
        "identity": {
            "base_sha": packet["base_sha"],
            "main_sha": packet["main_sha"],
            "feature_sha": packet["feature_sha"],
            "candidate_sha": packet["candidate_sha"],
        },
        "paths": paths,
        "checks": {"combined_verification": packet["combined_verification"]},
        "formation": {
            "histories_diverged": histories_diverged,
            "candidate_has_multiple_parents": multiple_parents,
            "formation_data_available": histories_diverged or multiple_parents,
            "candidate_parent_shas": parents,
        },
        "authority": "none",
    }


def render_merge_formation_receipt(receipt: dict[str, object]) -> str:
    """Render one deterministic receipt line."""

    return canonical_json(receipt) + "\n"


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze frozen merge-formation evidence")
    parser.add_argument("evidence", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        raw = args.evidence.read_text(encoding="utf-8")
        evidence = json.loads(raw)
        receipt = analyze_merge_formation(evidence)
    except OSError as error:
        sys.stderr.write(f"IO_ERROR: {error}\n")
        return 2
    except json.JSONDecodeError as error:
        sys.stderr.write(f"INVALID_JSON: {error.msg}\n")
        return 2
    except MergeFormationInputError as error:
        sys.stderr.write(f"{error.reason_code}: {error.residual}\n")
        return 2

    sys.stdout.write(render_merge_formation_receipt(receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "MergeFormationInputError",
    "analyze_merge_formation",
    "render_merge_formation_receipt",
]
