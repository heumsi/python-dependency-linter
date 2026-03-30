from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImportInfo:
    module: str
    lineno: int


def _resolve_relative_import(
    file_path: Path,
    project_root: Path,
    level: int,
    module: str | None,
) -> str | None:
    """Resolve a relative import to an absolute module name.

    Returns ``None`` when *level* exceeds the package depth (i.e. the
    import would escape *project_root*).
    """
    relative = file_path.relative_to(project_root)
    parts = list(relative.with_suffix("").parts)
    parts = parts[:-1]

    # level=1 means current package, level=2 means parent package, etc.
    go_up = level - 1
    if go_up >= len(parts):
        return None

    base_parts = parts[: len(parts) - go_up]
    resolved = ".".join(base_parts)
    if module:
        resolved = f"{resolved}.{module}" if resolved else module
    return resolved or None


def parse_imports(file_path: Path, project_root: Path) -> list[ImportInfo]:
    source = file_path.read_text()
    tree = ast.parse(source, filename=str(file_path))

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(ImportInfo(module=alias.name, lineno=node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                resolved = _resolve_relative_import(
                    file_path, project_root, node.level, node.module
                )
                if resolved is not None:
                    imports.append(ImportInfo(module=resolved, lineno=node.lineno))
            elif node.module is not None:
                imports.append(ImportInfo(module=node.module, lineno=node.lineno))

    return imports
