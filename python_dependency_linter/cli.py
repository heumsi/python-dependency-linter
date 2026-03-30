from __future__ import annotations

from pathlib import Path

import click

from python_dependency_linter.checker import check_import
from python_dependency_linter.config import load_config
from python_dependency_linter.matcher import find_matching_rules, merge_rules
from python_dependency_linter.parser import parse_imports
from python_dependency_linter.reporter import format_violations
from python_dependency_linter.resolver import resolve_import


def _file_to_module(file_path: Path, project_root: Path) -> str:
    relative = file_path.relative_to(project_root)
    parts = relative.with_suffix("").parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _package_module(file_path: Path, project_root: Path) -> str:
    """Return the package (directory) module path for a file.

    For ``contexts/boards/domain/models.py`` this returns
    ``contexts.boards.domain``, which is the module name to use when
    matching against rule patterns like ``contexts.*.domain``.
    """
    relative = file_path.relative_to(project_root)
    parts = relative.with_suffix("").parts
    if parts[-1] != "__init__":
        parts = parts[:-1]
    else:
        parts = parts[:-1]
    return ".".join(parts)


def _normalize_pattern(pattern: str, project_root: Path) -> str:
    """Normalize a pattern so that bare directory names match all files within."""
    clean = pattern.rstrip("/")
    candidate = project_root / clean
    if candidate.is_dir() or not any(c in clean for c in ("*", "?")):
        clean = f"{clean}/**"
    return clean


def _matches_any(path: Path, patterns: list[str]) -> bool:
    return any(path.match(p) for p in patterns)


def _find_python_files(
    project_root: Path,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> list[Path]:
    all_files = sorted(project_root.rglob("*.py"))

    if include is not None:
        normalized = [_normalize_pattern(p, project_root) for p in include]
        all_files = [
            f
            for f in all_files
            if _matches_any(f.relative_to(project_root), normalized)
        ]

    if exclude is not None:
        normalized = [_normalize_pattern(p, project_root) for p in exclude]
        all_files = [
            f
            for f in all_files
            if not _matches_any(f.relative_to(project_root), normalized)
        ]

    return all_files


@click.group()
def main():
    pass


@main.command()
@click.option(
    "--config",
    "config_path",
    default=None,
    help="Path to config file.",
)
def check(config_path: str | None):
    if config_path is not None:
        config_file = Path(config_path)
        if not config_file.exists():
            click.echo(f"Error: Config file not found: {config_file}", err=True)
            raise SystemExit(2)
        root = config_file.resolve().parent
    else:
        from python_dependency_linter.config import find_config

        config_file = find_config()
        if config_file is None:
            click.echo(
                "Error: Config file not found. "
                "Create .python-dependency-linter.yaml or configure "
                "[tool.python-dependency-linter] in pyproject.toml.",
                err=True,
            )
            raise SystemExit(2)
        root = config_file.parent

    try:
        config = load_config(config_file)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(2)

    all_violations = []
    python_files = _find_python_files(root, config.include, config.exclude)

    for file_path in python_files:
        module = _file_to_module(file_path, root)
        package = _package_module(file_path, root)
        matching_rules = find_matching_rules(package, config.rules)
        if not matching_rules:
            continue

        merged_rule = merge_rules(matching_rules)
        imports = parse_imports(file_path, root)

        file_violations = []
        for imp in imports:
            category = resolve_import(imp.module, root)
            violation = check_import(imp, category, merged_rule, module)
            if violation is not None:
                file_violations.append(violation)

        if file_violations:
            rel_path = str(file_path.relative_to(root))
            output = format_violations(rel_path, file_violations)
            click.echo(output)
            all_violations.extend(file_violations)

    if all_violations:
        click.echo(f"Found {len(all_violations)} violation(s).")
        raise SystemExit(1)
    else:
        click.echo("No violations found.")
