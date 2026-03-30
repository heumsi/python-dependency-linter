from python_dependency_linter.config import AllowDeny, Rule
from python_dependency_linter.matcher import (
    find_matching_rules,
    matches_pattern,
    merge_rules,
)


def test_matches_pattern_exact():
    assert matches_pattern("contexts.boards.domain", "contexts.boards.domain") is True
    assert matches_pattern("contexts.boards.domain", "contexts.auth.domain") is False


def test_matches_pattern_wildcard():
    assert matches_pattern("contexts.*.domain", "contexts.boards.domain") is True
    assert matches_pattern("contexts.*.domain", "contexts.auth.domain") is True
    assert matches_pattern("contexts.*.domain", "contexts.boards.application") is False


def test_matches_pattern_wildcard_in_allow():
    assert matches_pattern("contexts.*.domain", "contexts.boards.domain") is True


def test_find_matching_rules():
    rules = [
        Rule(
            name="r1",
            modules="contexts.*.domain",
            allow=AllowDeny(third_party=["pydantic"]),
        ),
        Rule(
            name="r2",
            modules="contexts.boards.domain",
            allow=AllowDeny(third_party=["attrs"]),
        ),
        Rule(
            name="r3",
            modules="contexts.*.adapters",
            deny=AllowDeny(third_party=["boto3"]),
        ),
    ]
    matched = find_matching_rules("contexts.boards.domain", rules)
    assert len(matched) == 2
    assert matched[0].name == "r1"
    assert matched[1].name == "r2"


def test_merge_rules_merges_allow():
    wildcard_rule = Rule(
        name="r1",
        modules="contexts.*.domain",
        allow=AllowDeny(third_party=["pydantic"], standard_library=["typing"]),
    )
    specific_rule = Rule(
        name="r2",
        modules="contexts.boards.domain",
        allow=AllowDeny(third_party=["attrs"]),
    )
    merged = merge_rules([wildcard_rule, specific_rule])

    assert sorted(merged.allow.third_party) == ["attrs", "pydantic"]
    assert merged.allow.standard_library == ["typing"]
    assert merged.deny is None


def test_merge_rules_single():
    rule = Rule(
        name="r1",
        modules="contexts.*.domain",
        allow=AllowDeny(third_party=["pydantic"]),
    )
    merged = merge_rules([rule])
    assert merged.allow.third_party == ["pydantic"]


def test_merge_rules_merges_deny():
    rule1 = Rule(
        name="r1", modules="contexts.*.adapters", deny=AllowDeny(third_party=["boto3"])
    )
    rule2 = Rule(
        name="r2",
        modules="contexts.boards.adapters",
        deny=AllowDeny(third_party=["requests"]),
    )
    merged = merge_rules([rule1, rule2])

    assert sorted(merged.deny.third_party) == ["boto3", "requests"]
