from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from loadout.dev.merge_formation import (
    MergeFormationInputError,
    analyze_merge_formation,
    render_merge_formation_receipt,
)


FIXTURES = Path(__file__).parent / "fixtures" / "merge_formation"


def load_fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def digest(char: str) -> str:
    return f"sha256:{char * 64}"


def valid_packet() -> dict[str, object]:
    return load_fixture("safe-disjoint.json")


def assert_reason(packet: dict[str, object], reason: str) -> None:
    with pytest.raises(MergeFormationInputError) as caught:
        analyze_merge_formation(packet)
    assert caught.value.reason_code == reason


def test_refuses_wrong_schema() -> None:
    packet = valid_packet()
    packet["schema"] = "wrong"
    assert_reason(packet, "WRONG_SCHEMA")


def test_refuses_missing_identity() -> None:
    packet = valid_packet()
    packet["main_sha"] = ""
    assert_reason(packet, "MISSING_IDENTITY")


def test_refuses_duplicate_path() -> None:
    packet = valid_packet()
    packet["surface"].append(copy.deepcopy(packet["surface"][0]))
    assert_reason(packet, "DUPLICATE_PATH")


def test_refuses_invalid_digest_state() -> None:
    packet = valid_packet()
    packet["surface"][0]["main_digest"] = "sha256:not-a-digest"
    assert_reason(packet, "INVALID_DIGEST_STATE")


def test_refuses_declared_change_mismatch() -> None:
    packet = valid_packet()
    record = next(item for item in packet["surface"] if item["path"] == "a.txt")
    record["main_changed"] = False
    assert_reason(packet, "DECLARED_CHANGE_MISMATCH")


def test_refuses_missing_candidate_identity_when_candidate_is_complete() -> None:
    packet = valid_packet()
    packet["candidate_sha"] = None
    assert_reason(packet, "CANDIDATE_IDENTITY_REQUIRED")


def test_refuses_invalid_check_state() -> None:
    packet = valid_packet()
    packet["combined_verification"] = "green-ish"
    assert_reason(packet, "INVALID_CHECK_STATE")


def test_safe_disjoint_content_is_composed_even_when_behind_main() -> None:
    receipt = analyze_merge_formation(load_fixture("safe-disjoint.json"))
    assert receipt["classification"] == "SAFE_CONTENT_COMPOSITION"
    assert receipt["behind_main"] is True
    assert receipt["content_loss"] is False
    assert receipt["paths"]["main_preserved"] == ["a.txt"]
    assert receipt["paths"]["feature_preserved"] == ["b.txt"]
    assert receipt["paths"]["overlap"] == []
    assert receipt["paths"]["lost"] == []


def test_feature_loss_and_main_loss_are_detected() -> None:
    feature = analyze_merge_formation(load_fixture("loss-feature.json"))
    main = analyze_merge_formation(load_fixture("loss-main.json"))
    assert feature["classification"] == "LOSS_DETECTED"
    assert main["classification"] == "LOSS_DETECTED"
    assert feature["paths"]["lost"] == [{"path": "b.txt", "side": "feature"}]
    assert main["paths"]["lost"] == [{"path": "a.txt", "side": "main"}]


def test_unchanged_sentinel_drift_is_loss_class_finding() -> None:
    packet = valid_packet()
    sentinel = next(item for item in packet["surface"] if item["path"] == "sentinel.txt")
    sentinel["candidate_digest"] = digest("9")
    receipt = analyze_merge_formation(packet)
    assert receipt["classification"] == "LOSS_DETECTED"
    assert receipt["paths"]["lost"] == [{"path": "sentinel.txt", "side": "sentinel"}]


@pytest.mark.parametrize("name", ["overlap-feature.json", "overlap-combined.json"])
def test_overlap_never_auto_promotes_to_safe(name: str) -> None:
    receipt = analyze_merge_formation(load_fixture(name))
    assert receipt["classification"] == "OVERLAP_REVIEW_REQUIRED"
    assert receipt["paths"]["overlap"] == ["same.txt"]
    assert receipt["content_loss"] is False


def test_incomplete_candidate_is_not_misreported_as_loss() -> None:
    receipt = analyze_merge_formation(load_fixture("incomplete.json"))
    assert receipt["classification"] == "INCOMPLETE_EVIDENCE"
    assert receipt["content_loss"] is False
    assert receipt["paths"]["incomplete"] == ["a.txt", "b.txt"]


def test_green_checks_never_override_content_loss() -> None:
    receipt = analyze_merge_formation(load_fixture("loss-feature.json"))
    assert receipt["checks"]["combined_verification"] == "pass"
    assert receipt["classification"] == "LOSS_DETECTED"


def test_failed_checks_do_not_rewrite_mechanical_content_classification() -> None:
    packet = valid_packet()
    packet["combined_verification"] = "fail"
    receipt = analyze_merge_formation(packet)
    assert receipt["classification"] == "SAFE_CONTENT_COMPOSITION"
    assert receipt["checks"]["combined_verification"] == "fail"


def test_formation_topology_is_orthogonal_to_content() -> None:
    one_parent = valid_packet()
    one_parent["candidate_parent_shas"] = [one_parent["main_sha"]]
    two_parent = valid_packet()
    two_parent["candidate_parent_shas"] = [two_parent["main_sha"], two_parent["feature_sha"]]

    left = analyze_merge_formation(one_parent)
    right = analyze_merge_formation(two_parent)
    assert left["classification"] == right["classification"] == "SAFE_CONTENT_COMPOSITION"
    assert left["formation"]["candidate_has_multiple_parents"] is False
    assert right["formation"]["candidate_has_multiple_parents"] is True
    assert right["formation"]["histories_diverged"] is True
    assert right["formation"]["formation_data_available"] is True
    assert right["formation"]["candidate_parent_shas"] == [two_parent["main_sha"], two_parent["feature_sha"]]


def test_reordered_surface_renders_byte_identically_but_parent_order_is_preserved() -> None:
    packet = valid_packet()
    before = render_merge_formation_receipt(analyze_merge_formation(packet))
    packet["surface"].reverse()
    after = render_merge_formation_receipt(analyze_merge_formation(packet))
    assert before == after
    assert before.endswith("\n")


def test_receipt_is_neutral_and_non_authoritative() -> None:
    receipt = analyze_merge_formation(valid_packet())
    assert receipt["schema"] == "loadout.merge-formation-receipt/v0"
    assert receipt["authority"] == "none"
    assert "humanentropy" not in render_merge_formation_receipt(receipt).lower()
