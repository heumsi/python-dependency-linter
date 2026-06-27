from __future__ import annotations

from python_dependency_linter.domain.checker import Violation


def format_violations(file_path: str, violations: list[Violation]) -> str:
    if not violations:
        return ""

    lines = []
    for v in violations:
        lines.append(f"{file_path}:{v.lineno}")
        if v.rule_description:
            lines.append(f"    [{v.rule_name}] {v.rule_description}")
        else:
            lines.append(f"    [{v.rule_name}]")
        arrow = f"{v.source_module} \u2192 {v.imported_module}"
        lines.append(f"    {arrow} ({v.category.value})")
        lines.append("")

    return "\n".join(lines)
