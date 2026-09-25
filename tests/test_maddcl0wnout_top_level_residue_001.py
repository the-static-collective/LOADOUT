import importlib.util
from pathlib import Path

PATH = Path(__file__).parents[1] / "experimental" / "maddcl0wnout" / "top_level_residue_001.py"
SPEC = importlib.util.spec_from_file_location("top_level_residue_001", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
changed_keys = MODULE.changed_keys


def test_exact_replay_has_no_residue():
    assert changed_keys({"payload": 1}, {"payload": 1}) == ()


def test_unknown_key_remains_visible():
    assert changed_keys({"payload": 1}, {"payload": 1, "custody": "A"}) == ("custody",)


def test_missing_is_not_null():
    assert changed_keys({}, {"custody": None}) == ("custody",)


def test_order_is_not_change():
    assert changed_keys({"b": 2, "a": 1}, {"a": 1, "b": 2}) == ()
