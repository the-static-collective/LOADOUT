import importlib.util
from pathlib import Path

MODULE = Path(__file__).parents[1] / "experiments" / "maddcl0wnout" / "unknown_axis_diff.py"
spec = importlib.util.spec_from_file_location("unknown_axis_diff", MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def test_declared_axis_change_stays_declared():
    out = mod.receipt_axis_diff({"payload": "a"}, {"payload": "b"})
    assert out == {
        "changed_declared_axes": ["payload"],
        "unknown_changed_fields": [],
        "classification_complete": True,
    }


def test_undeclared_change_is_residue_not_authority():
    out = mod.receipt_axis_diff(
        {"payload": "a", "custody": "left"},
        {"payload": "a", "custody": "right"},
    )
    assert out["changed_declared_axes"] == []
    assert out["unknown_changed_fields"] == ["custody"]
    assert out["classification_complete"] is False


def test_missing_is_not_null_even_for_unknown_field():
    out = mod.receipt_axis_diff({}, {"mystery": None})
    assert out["unknown_changed_fields"] == ["mystery"]
    assert out["classification_complete"] is False


def test_exact_replay_has_no_residue():
    receipt = {"payload": "a", "provenance": "p", "extra": {"x": 1}}
    out = mod.receipt_axis_diff(receipt, dict(receipt))
    assert out["changed_declared_axes"] == []
    assert out["unknown_changed_fields"] == []
    assert out["classification_complete"] is True
