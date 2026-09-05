from __future__ import annotations

import ast
import operator
from pathlib import Path
from typing import Callable

_MAX_EXPRESSION_LENGTH = 256
_MAX_ABS_RESULT = 1_000_000_000_000

_BINARY_OPERATORS: dict[type[ast.operator], Callable[[int | float, int | float], int | float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}
_UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[int | float], int | float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def resolve_workspace_path(workspace_root: Path, relative_path: str) -> Path:
    root = workspace_root.resolve()
    if not root.is_dir():
        raise ValueError("workspace root must exist")
    if not isinstance(relative_path, str) or not relative_path or "\x00" in relative_path:
        raise ValueError("path outside workspace")
    candidate = Path(relative_path)
    if candidate.is_absolute():
        raise ValueError("path outside workspace")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ValueError("path outside workspace") from error
    return resolved


def read_text(workspace_root: Path, relative_path: str) -> str:
    path = resolve_workspace_path(workspace_root, relative_path)
    return path.read_text(encoding="utf-8")


def write_text(workspace_root: Path, relative_path: str, content: str) -> str:
    if not isinstance(content, str):
        raise ValueError("content must be text")
    path = resolve_workspace_path(workspace_root, relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path.relative_to(workspace_root.resolve()).as_posix()


def _bounded_number(value: object) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("expression must produce a finite bounded number")
    if not (-_MAX_ABS_RESULT <= value <= _MAX_ABS_RESULT):
        raise ValueError("arithmetic result exceeds bound")
    return value


def _evaluate(node: ast.AST) -> int | float:
    if isinstance(node, ast.Constant):
        return _bounded_number(node.value)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        operand = _evaluate(node.operand)
        return _bounded_number(_UNARY_OPERATORS[type(node.op)](operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate(node.left)
        right = _evaluate(node.right)
        try:
            result = _BINARY_OPERATORS[type(node.op)](left, right)
        except (ArithmeticError, OverflowError) as error:
            raise ValueError("invalid arithmetic operation") from error
        return _bounded_number(result)
    raise ValueError("unsupported arithmetic expression")


def evaluate_arithmetic(expression: str) -> int | float:
    if not isinstance(expression, str) or not expression or len(expression) > _MAX_EXPRESSION_LENGTH:
        raise ValueError("invalid arithmetic expression")
    try:
        parsed = ast.parse(expression, mode="eval")
    except (SyntaxError, ValueError) as error:
        raise ValueError("invalid arithmetic expression") from error
    return _evaluate(parsed.body)


__all__ = [
    "evaluate_arithmetic",
    "read_text",
    "resolve_workspace_path",
    "write_text",
]
