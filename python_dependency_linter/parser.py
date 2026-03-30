from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImportInfo:
    module: str
    lineno: int


def parse_imports(file_path: Path) -> list[ImportInfo]:
    source = file_path.read_text()
    tree = ast.parse(source, filename=str(file_path))

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(ImportInfo(module=alias.name, lineno=node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                imports.append(ImportInfo(module=node.module, lineno=node.lineno))

    return imports
