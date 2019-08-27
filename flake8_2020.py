import ast
from typing import Dict
from typing import Generator
from typing import List
from typing import Tuple
from typing import Type

import importlib_metadata

Flake8Error = Tuple[int, int, str, Type['Plugin']]

YTT101 = 'YTT101: `sys.version[:...]` referenced (python3.10), use `sys.version_info`'  # noqa: E501
YTT102 = 'YTT102: `sys.version[2]` referenced (python3.10), use `sys.version_info`'  # noqa: E501
YTT201 = 'YTT201: `sys.version_info[0] == 3` referenced (python4), use `>=`'
YTT202 = 'YTT202: `six.PY3` referenced (python4), use `not six.PY2`'
YTT301 = 'YTT301: `sys.version[0]` referenced (python10), use `sys.version_info`'  # noqa: E501


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: List[Tuple[int, int, str]] = []
        self._from_imports: Dict[str, str] = {}

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            if node.module is not None and not alias.asname:
                self._from_imports[alias.name] = node.module
        self.generic_visit(node)

    def _is_sys(self, attr: str, node: ast.AST) -> bool:
        return (
            # subscripting `sys.<thing>`
            isinstance(node, ast.Attribute) and
            isinstance(node.value, ast.Name) and
            node.value.id == 'sys' and
            node.attr == attr
        ) or (
            isinstance(node, ast.Name) and
            node.id == attr and
            self._from_imports.get(node.id) == 'sys'
        )

    def visit_Subscript(self, node: ast.Subscript) -> None:
        if (
                self._is_sys('version', node.value) and
                isinstance(node.slice, ast.Slice)
        ):
            self.errors.append((
                node.value.lineno, node.value.col_offset, YTT101,
            ))
        elif (
                self._is_sys('version', node.value) and
                isinstance(node.slice, ast.Index) and
                isinstance(node.slice.value, ast.Num) and
                node.slice.value.n == 2
        ):
            self.errors.append((
                node.value.lineno, node.value.col_offset, YTT102,
            ))
        elif (
                self._is_sys('version', node.value) and
                isinstance(node.slice, ast.Index) and
                isinstance(node.slice.value, ast.Num) and
                node.slice.value.n == 0
        ):
            self.errors.append((
                node.value.lineno, node.value.col_offset, YTT301,
            ))

        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        if (
                isinstance(node.left, ast.Subscript) and
                self._is_sys('version_info', node.left.value) and
                isinstance(node.left.slice, ast.Index) and
                isinstance(node.left.slice.value, ast.Num) and
                node.left.slice.value.n == 0 and
                len(node.ops) == 1 and
                isinstance(node.ops[0], ast.Eq) and
                isinstance(node.comparators[0], ast.Num) and
                node.comparators[0].n == 3
        ):
            self.errors.append((
                node.left.lineno, node.left.col_offset, YTT201,
            ))
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if (
                isinstance(node.value, ast.Name) and
                node.value.id == 'six' and
                node.attr == 'PY3'
        ):
            self.errors.append((node.lineno, node.col_offset, YTT202))
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id == 'PY3' and self._from_imports.get(node.id) == 'six':
            self.errors.append((node.lineno, node.col_offset, YTT202))
        self.generic_visit(node)


class Plugin:
    name = __name__
    version = importlib_metadata.version(__name__)

    def __init__(self, tree: ast.AST):
        self._tree = tree

    def run(self) -> Generator[Flake8Error, None, None]:
        visitor = Visitor()
        visitor.visit(self._tree)

        for line, col, msg in visitor.errors:
            yield line, col, msg, type(self)
