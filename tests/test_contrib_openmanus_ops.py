from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).parents[1] / "contrib" / "openmanus" / "bounded_ops.py"
spec = importlib.util.spec_from_file_location("bounded_ops", MODULE_PATH)
assert spec is not None and spec.loader is not None
bounded_ops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bounded_ops)


def test_read_and_write_are_confined_to_declared_workspace(tmp_path: Path) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    assert bounded_ops.write_text(root, "notes/a.txt", "hello") == "notes/a.txt"
    assert bounded_ops.read_text(root, "notes/a.txt") == "hello"
    with pytest.raises(ValueError, match="outside workspace"):
        bounded_ops.write_text(root, "../escape.txt", "no")
    with pytest.raises(ValueError, match="outside workspace"):
        bounded_ops.read_text(root, "/etc/passwd")


def test_bounded_arithmetic_accepts_numbers_and_basic_operators() -> None:
    assert bounded_ops.evaluate_arithmetic("(2 + 3) * 4") == 20
    assert bounded_ops.evaluate_arithmetic("7 / 2") == 3.5


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os').system('echo nope')",
        "open('x')",
        "[x for x in range(3)]",
        "2 ** 1000",
    ],
)
def test_bounded_arithmetic_rejects_code_and_unbounded_shapes(expression: str) -> None:
    with pytest.raises(ValueError):
        bounded_ops.evaluate_arithmetic(expression)
