from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path

_IGNORE_PATTERN = re.compile(r"#\s*pdl:\s*ignore(?:\[([^\]]*)\])?")


@dataclass(frozen=True)
class ImportInfo:
    module: str
    lineno: int
    ignore_rules: list[str] | None = field(default=None, compare=False)


def _parse_ignore_comment(line: str) -> list[str] | None:
    """Parse ``# pdl: ignore`` or ``# pdl: ignore[rule1, rule2]`` from a source line.

    Returns ``None`` if no ignore comment is found, an empty list for
    blanket ignore, or a list of rule names for selective ignore.
    """
    m = _IGNORE_PATTERN.search(line)
    if m is None:
        return None
    if m.group(1) is None:
        return []
    return [r.strip() for r in m.group(1).split(",") if r.strip()]


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
    source_lines = source.splitlines()

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            ignore = _parse_ignore_comment(source_lines[node.lineno - 1])
            for alias in node.names:
                imports.append(
                    ImportInfo(
                        module=alias.name, lineno=node.lineno, ignore_rules=ignore
                    )
                )
        elif isinstance(node, ast.ImportFrom):
            ignore = _parse_ignore_comment(source_lines[node.lineno - 1])
            if node.level and node.level > 0:
                resolved = _resolve_relative_import(
                    file_path, project_root, node.level, node.module
                )
                if resolved is not None:
                    imports.append(
                        ImportInfo(
                            module=resolved, lineno=node.lineno, ignore_rules=ignore
                        )
                    )
            elif node.module is not None:
                imports.append(
                    ImportInfo(
                        module=node.module, lineno=node.lineno, ignore_rules=ignore
                    )
                )

    return imports
