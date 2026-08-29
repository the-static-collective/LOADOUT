from __future__ import annotations

from datetime import datetime, timezone


def _parse(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        raise ValueError("timestamp must be offset-aware")
    return dt.astimezone(timezone.utc)


def decay_reasons(compile_record: dict, observed_at: str, signals: dict | None = None) -> list[str]:
    reasons: list[str] = []
    if _parse(observed_at) >= _parse(compile_record["expires_at"]):
        reasons.append("COMPILE_EXPIRED")
    mapping = [
        ("owner_ground_changed", "OWNER_GROUND_CHANGED"),
        ("repository_contract_changed", "REPOSITORY_CONTRACT_CHANGED"),
        ("head_changed", "HEAD_CHANGED"),
        ("contradictory_evidence", "CONTRADICTORY_EVIDENCE"),
    ]
    signals = signals or {}
    for key, code in mapping:
        if signals.get(key):
            reasons.append(code)
    return reasons
