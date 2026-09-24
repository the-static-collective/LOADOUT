"""MADDcl0wnOUT experiment: declared-axis diff with explicit unknown residue.

Non-canonical. No LOADOUT runtime/schema/authority promotion.
"""
from __future__ import annotations

from typing import Any

DECLARED_AXES = ("payload", "provenance", "validation", "authority")
_MISSING = object()


def receipt_axis_diff(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Separate declared-axis deltas from undeclared residue without interpreting it."""
    changed = [
        axis
        for axis in DECLARED_AXES
        if left.get(axis, _MISSING) != right.get(axis, _MISSING)
    ]
    unknown = sorted(
        key
        for key in (set(left) | set(right)) - set(DECLARED_AXES)
        if left.get(key, _MISSING) != right.get(key, _MISSING)
    )
    return {
        "changed_declared_axes": changed,
        "unknown_changed_fields": unknown,
        "classification_complete": not unknown,
    }
