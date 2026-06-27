from __future__ import annotations

import re
from dataclasses import dataclass

from python_dependency_linter.core.config import AllowDeny, Rule
from python_dependency_linter.core.matcher import matches_pattern
from python_dependency_linter.core.parser import ImportInfo
from python_dependency_linter.core.resolver import ImportCategory

_CAPTURE_RE = re.compile(r"\{(\w+)\}")


def resolve_captures(pattern: str, captures: dict[str, str]) -> str:
    def _replace(m: re.Match) -> str:
        name = m.group(1)
        return captures.get(name, m.group(0))

    return _CAPTURE_RE.sub(_replace, pattern)


def _resolve_list(
    patterns: list[str] | None, captures: dict[str, str]
) -> list[str] | None:
    if patterns is None:
        return None
    return [resolve_captures(p, captures) for p in patterns]


def _resolve_allow_deny(
    allow_deny: AllowDeny | None, captures: dict[str, str]
) -> AllowDeny | None:
    if allow_deny is None:
        return None
    return AllowDeny(
        standard_library=_resolve_list(allow_deny.standard_library, captures),
        third_party=_resolve_list(allow_deny.third_party, captures),
        local=_resolve_list(allow_deny.local, captures),
    )


@dataclass
class Violation:
    rule_name: str
    source_module: str
    imported_module: str
    category: ImportCategory
    lineno: int
    rule_description: str | None = None


def _get_category_list(
    allow_deny: AllowDeny | None, category: ImportCategory
) -> list[str] | None:
    if allow_deny is None:
        return None
    match category:
        case ImportCategory.STANDARD_LIBRARY:
            return allow_deny.standard_library
        case ImportCategory.THIRD_PARTY:
            return allow_deny.third_party
        case ImportCategory.LOCAL:
            return allow_deny.local


def _matches_pattern_or_submodule(pattern: str, module: str) -> bool:
    """Return True if module matches pattern exactly or is a submodule of it."""
    if matches_pattern(pattern, module):
        return True
    # Check if module starts with a prefix that matches the pattern.
    # e.g. "contexts.*.domain" should match "contexts.boards.domain.models"
    module_parts = module.split(".")
    pattern_parts = pattern.split(".")
    if len(module_parts) > len(pattern_parts):
        prefix = ".".join(module_parts[: len(pattern_parts)])
        if matches_pattern(pattern, prefix):
            return True
    # Literal prefix match (no wildcards in pattern)
    if "*" not in pattern and module.startswith(pattern + "."):
        return True
    return False


def _is_in_list(module: str, patterns: list[str]) -> bool:
    if "*" in patterns:
        return True
    return any(_matches_pattern_or_submodule(p, module) for p in patterns)


def check_import(
    import_info: ImportInfo,
    category: ImportCategory,
    merged_rule: Rule | None,
    source_module: str,
    captures: dict[str, str] | None = None,
) -> Violation | None:
    if merged_rule is None:
        return None

    if captures:
        merged_rule = Rule(
            name=merged_rule.name,
            modules=merged_rule.modules,
            description=merged_rule.description,
            allow=_resolve_allow_deny(merged_rule.allow, captures),
            deny=_resolve_allow_deny(merged_rule.deny, captures),
        )

    module = import_info.module

    # Check deny first (deny takes priority over allow)
    deny_list = _get_category_list(merged_rule.deny, category)
    if deny_list is not None and _is_in_list(module, deny_list):
        return Violation(
            rule_name=merged_rule.name,
            source_module=source_module,
            imported_module=module,
            category=category,
            lineno=import_info.lineno,
            rule_description=merged_rule.description,
        )

    # Check allow
    allow_list = _get_category_list(merged_rule.allow, category)
    if allow_list is None:
        # No allow list for this category = allow all
        return None
    if _is_in_list(module, allow_list):
        return None

    return Violation(
        rule_name=merged_rule.name,
        source_module=source_module,
        imported_module=module,
        category=category,
        lineno=import_info.lineno,
        rule_description=merged_rule.description,
    )
