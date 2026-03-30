from python_dependency_linter.config import AllowDeny, Rule
from python_dependency_linter.matcher import (
    find_matching_rules,
    match_pattern_with_captures,
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


def test_matches_pattern_double_star():
    # matches one level
    assert matches_pattern("contexts.**.domain", "contexts.analytics.domain") is True
    # matches multiple levels
    assert (
        matches_pattern("contexts.**.domain", "contexts.analytics.sub.domain") is True
    )
    # does not match zero levels (** requires one or more)
    assert matches_pattern("contexts.**.domain", "contexts.domain") is False
    # does not match wrong suffix
    assert (
        matches_pattern("contexts.**.domain", "contexts.analytics.application") is False
    )


def test_matches_pattern_double_star_at_end():
    assert (
        matches_pattern("contexts.**.domain.**", "contexts.a.domain.entities") is True
    )
    assert (
        matches_pattern("contexts.**.domain.**", "contexts.a.domain.entities.metric")
        is True
    )
    assert matches_pattern("contexts.**.domain.**", "contexts.a.domain") is False


def test_matches_pattern_double_star_alone():
    # ** alone matches any module with one or more parts
    assert matches_pattern("**", "anything") is True
    assert matches_pattern("**", "a.b.c") is True


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
    assert matched[0][0].name == "r1"
    assert matched[1][0].name == "r2"


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


def test_capture_single():
    result = match_pattern_with_captures(
        "src.contexts.{context}.domain", "src.contexts.analytics.domain"
    )
    assert result == {"context": "analytics"}


def test_capture_multiple():
    result = match_pattern_with_captures(
        "src.contexts.{ctx}.adapters.{dir}", "src.contexts.auth.adapters.inbound"
    )
    assert result == {"ctx": "auth", "dir": "inbound"}


def test_capture_duplicate_name_consistent():
    result = match_pattern_with_captures("src.{a}.middle.{a}", "src.foo.middle.foo")
    assert result == {"a": "foo"}


def test_capture_duplicate_name_inconsistent():
    result = match_pattern_with_captures("src.{a}.middle.{a}", "src.foo.middle.bar")
    assert result is None


def test_capture_no_match():
    result = match_pattern_with_captures(
        "src.contexts.{context}.domain", "src.utils.helpers"
    )
    assert result is None


def test_capture_no_captures_with_star():
    result = match_pattern_with_captures("src.*.domain", "src.analytics.domain")
    assert result == {}


def test_capture_coexist_with_star():
    result = match_pattern_with_captures(
        "src.{ctx}.*.domain", "src.auth.adapters.domain"
    )
    assert result == {"ctx": "auth"}


def test_capture_coexist_with_double_star():
    result = match_pattern_with_captures(
        "src.{ctx}.**.domain", "src.auth.deep.nested.domain"
    )
    assert result == {"ctx": "auth"}


def test_capture_exact_no_wildcards():
    result = match_pattern_with_captures(
        "src.contexts.analytics.domain", "src.contexts.analytics.domain"
    )
    assert result == {}


def test_capture_exact_no_wildcards_no_match():
    result = match_pattern_with_captures(
        "src.contexts.analytics.domain", "src.contexts.auth.domain"
    )
    assert result is None


def test_find_matching_rules_with_captures():
    rules = [
        Rule(
            name="domain-layer",
            modules="contexts.{context}.domain",
            allow=AllowDeny(local=["contexts.{context}.domain"]),
        ),
        Rule(
            name="adapters",
            modules="contexts.*.adapters",
            deny=AllowDeny(third_party=["boto3"]),
        ),
    ]
    matched = find_matching_rules("contexts.boards.domain", rules)
    assert len(matched) == 1
    rule, captures = matched[0]
    assert rule.name == "domain-layer"
    assert captures == {"context": "boards"}


def test_capture_after_double_star():
    result = match_pattern_with_captures(
        "src.**.{layer}.models", "src.deep.nested.domain.models"
    )
    assert result == {"layer": "domain"}


def test_capture_after_double_star_backtrack():
    result = match_pattern_with_captures("**.{x}.end", "a.b.c.end")
    assert result == {"x": "c"}
