"""MADDcl0wnOUT / non-canonical: compare receipt axes without promotion.

This tiny probe answers only which declared axes changed between two JSON-like
receipts. It does not decide whether a change is meaningful, authorized, true,
or admissible.
"""
from __future__ import annotations

from typing import Any, Mapping, NamedTuple

AXES = ("payload", "provenance", "validation", "authority")


class AxisDelta(NamedTuple):
    """Immutable value receipt with no module-registration dependency."""

    axis: str
    changed: bool
    before_present: bool
    after_present: bool


def diff_receipt_axes(before: Mapping[str, Any], after: Mapping[str, Any]) -> tuple[AxisDelta, ...]:
    """Return deterministic, axis-local deltas; missing is distinct from null."""
    deltas = []
    for axis in AXES:
        before_present = axis in before
        after_present = axis in after
        changed = (before_present != after_present) or (
            before_present and after_present and before[axis] != after[axis]
        )
        deltas.append(AxisDelta(axis, changed, before_present, after_present))
    return tuple(deltas)


def changed_axes(before: Mapping[str, Any], after: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(delta.axis for delta in diff_receipt_axes(before, after) if delta.changed)
