from __future__ import annotations


def record_delta(left: dict, right: dict) -> list[dict]:
    paths = sorted(set(left) | set(right))
    delta: list[dict] = []
    for path in paths:
        before = left.get(path)
        after = right.get(path)
        if before != after:
            delta.append({"path": path, "before": before, "after": after})
    return delta
