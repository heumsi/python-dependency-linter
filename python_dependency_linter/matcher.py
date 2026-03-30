from __future__ import annotations

import re

from python_dependency_linter.config import AllowDeny, Rule

_CAPTURE_RE = re.compile(r"^\{(\w+)\}$")


def matches_pattern(pattern: str, module: str) -> bool:
    return match_pattern_with_captures(pattern, module) is not None


def match_pattern_with_captures(pattern: str, module: str) -> dict[str, str] | None:
    pattern_parts = pattern.split(".")
    module_parts = module.split(".")
    captures: dict[str, str] = {}
    if _match_with_captures(pattern_parts, module_parts, captures):
        return captures
    return None


def _match_with_captures(
    pattern_parts: list[str],
    module_parts: list[str],
    captures: dict[str, str],
) -> bool:
    if not pattern_parts and not module_parts:
        return True
    if not pattern_parts:
        return False

    if pattern_parts[0] == "**":
        for i in range(1, len(module_parts) + 1):
            snapshot = dict(captures)
            if _match_with_captures(pattern_parts[1:], module_parts[i:], captures):
                return True
            captures.clear()
            captures.update(snapshot)
        return False

    if not module_parts:
        return False

    m = _CAPTURE_RE.match(pattern_parts[0])
    if m:
        name = m.group(1)
        value = module_parts[0]
        if name in captures:
            if captures[name] != value:
                return False
        else:
            captures[name] = value
        return _match_with_captures(pattern_parts[1:], module_parts[1:], captures)

    if pattern_parts[0] == "*" or pattern_parts[0] == module_parts[0]:
        return _match_with_captures(pattern_parts[1:], module_parts[1:], captures)

    return False


def find_matching_rules(
    module: str, rules: list[Rule]
) -> list[tuple[Rule, dict[str, str]]]:
    result = []
    for r in rules:
        captures = match_pattern_with_captures(r.modules, module)
        if captures is not None:
            result.append((r, captures))
    return result


def _merge_allow_deny(
    base: AllowDeny | None, override: AllowDeny | None
) -> AllowDeny | None:
    if base is None and override is None:
        return None
    if base is None:
        return override
    if override is None:
        return base

    def _merge_lists(a: list[str] | None, b: list[str] | None) -> list[str] | None:
        if a is None and b is None:
            return None
        if a is None:
            return b
        if b is None:
            return a
        return list(set(a + b))

    return AllowDeny(
        standard_library=_merge_lists(base.standard_library, override.standard_library),
        third_party=_merge_lists(base.third_party, override.third_party),
        local=_merge_lists(base.local, override.local),
    )


def merge_rules(rules: list[Rule]) -> Rule:
    merged = rules[0]
    for rule in rules[1:]:
        merged = Rule(
            name=merged.name,
            modules=merged.modules,
            allow=_merge_allow_deny(merged.allow, rule.allow),
            deny=_merge_allow_deny(merged.deny, rule.deny),
        )
    return merged
