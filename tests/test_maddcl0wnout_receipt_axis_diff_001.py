import importlib.util
from pathlib import Path

MODULE = Path(__file__).parents[1] / "experiments" / "maddcl0wnout_receipt_axis_diff_001.py"
spec = importlib.util.spec_from_file_location("receipt_axis_diff", MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def test_provenance_only_delta_does_not_become_payload_delta():
    before = {"payload": {"digest": "p"}, "provenance": ["a"], "authority": "none"}
    after = {"payload": {"digest": "p"}, "provenance": ["a", "b"], "authority": "none"}
    assert mod.changed_axes(before, after) == ("provenance",)


def test_payload_only_delta_does_not_become_provenance_delta():
    before = {"payload": {"digest": "p1"}, "provenance": ["a"], "authority": "none"}
    after = {"payload": {"digest": "p2"}, "provenance": ["a"], "authority": "none"}
    assert mod.changed_axes(before, after) == ("payload",)


def test_validation_only_delta_does_not_become_payload_or_authority_delta():
    before = {"payload": "same", "validation": {"status": "pending"}, "authority": "none"}
    after = {"payload": "same", "validation": {"status": "passed"}, "authority": "none"}
    assert mod.changed_axes(before, after) == ("validation",)


def test_missing_is_not_null():
    before = {"payload": None, "authority": "none"}
    after = {"authority": "none"}
    deltas = {d.axis: d for d in mod.diff_receipt_axes(before, after)}
    assert deltas["payload"].changed is True
    assert deltas["payload"].before_present is True
    assert deltas["payload"].after_present is False


def test_authority_change_stays_its_own_axis():
    before = {"payload": "same", "provenance": ["same"], "authority": "none"}
    after = {"payload": "same", "provenance": ["same"], "authority": "delegated:fixture-only"}
    assert mod.changed_axes(before, after) == ("authority",)


def test_exact_replay_has_no_axis_delta():
    receipt = {
        "payload": {"digest": "p"},
        "provenance": ["a"],
        "validation": {"status": "passed"},
        "authority": "none",
    }
    assert mod.changed_axes(receipt, dict(receipt)) == ()


def test_untracked_fields_do_not_expand_the_contract():
    before = {"payload": "same", "debug": 1}
    after = {"payload": "same", "debug": 2}
    assert mod.changed_axes(before, after) == ()
