from python_dependency_linter.core.config import AllowDeny, Rule
from python_dependency_linter.core.parser import ImportInfo
from python_dependency_linter.core.resolver import ImportCategory
from python_dependency_linter.domain.checker import (
    Violation,
    check_import,
    resolve_captures,
)


def test_allow_all_when_no_rules():
    result = check_import(
        import_info=ImportInfo(module="sqlalchemy", lineno=1),
        category=ImportCategory.THIRD_PARTY,
        merged_rule=None,
        source_module="contexts.boards.adapters",
    )
    assert result is None


def test_allow_whitelist_pass():
    rule = Rule(
        name="domain-isolation",
        modules="contexts.*.domain",
        allow=AllowDeny(third_party=["pydantic"]),
    )
    result = check_import(
        import_info=ImportInfo(module="pydantic", lineno=1),
        category=ImportCategory.THIRD_PARTY,
        merged_rule=rule,
        source_module="contexts.boards.domain",
    )
    assert result is None


def test_allow_whitelist_violation():
    rule = Rule(
        name="domain-isolation",
        modules="contexts.*.domain",
        allow=AllowDeny(third_party=["pydantic"]),
    )
    result = check_import(
        import_info=ImportInfo(module="sqlalchemy", lineno=5),
        category=ImportCategory.THIRD_PARTY,
        merged_rule=rule,
        source_module="contexts.boards.domain",
    )
    assert isinstance(result, Violation)
    assert result.rule_name == "domain-isolation"
    assert result.source_module == "contexts.boards.domain"
    assert result.imported_module == "sqlalchemy"
    assert result.category == ImportCategory.THIRD_PARTY
    assert result.lineno == 5
    assert result.rule_description is None


def test_deny_blacklist_violation():
    rule = Rule(
        name="adapters-deny",
        modules="contexts.*.adapters",
        deny=AllowDeny(third_party=["boto3"]),
    )
    result = check_import(
        import_info=ImportInfo(module="boto3", lineno=3),
        category=ImportCategory.THIRD_PARTY,
        merged_rule=rule,
        source_module="contexts.boards.adapters",
    )
    assert isinstance(result, Violation)
    assert result.rule_name == "adapters-deny"


def test_deny_blacklist_pass():
    rule = Rule(
        name="adapters-deny",
        modules="contexts.*.adapters",
        deny=AllowDeny(third_party=["boto3"]),
    )
    result = check_import(
        import_info=ImportInfo(module="sqlalchemy", lineno=1),
        category=ImportCategory.THIRD_PARTY,
        merged_rule=rule,
        source_module="contexts.boards.adapters",
    )
    assert result is None


def test_allow_and_deny_combined():
    rule = Rule(
        name="combined",
        modules="contexts.*.adapters",
        allow=AllowDeny(third_party=["*"]),
        deny=AllowDeny(third_party=["boto3"]),
    )
    # allowed by wildcard, but denied explicitly
    result = check_import(
        import_info=ImportInfo(module="boto3", lineno=1),
        category=ImportCategory.THIRD_PARTY,
        merged_rule=rule,
        source_module="contexts.boards.adapters",
    )
    assert isinstance(result, Violation)

    # allowed by wildcard, not denied
    result = check_import(
        import_info=ImportInfo(module="sqlalchemy", lineno=2),
        category=ImportCategory.THIRD_PARTY,
        merged_rule=rule,
        source_module="contexts.boards.adapters",
    )
    assert result is None


def test_allow_local_with_wildcard():
    rule = Rule(
        name="domain-isolation",
        modules="contexts.*.domain",
        allow=AllowDeny(local=["contexts.*.domain"]),
    )
    result = check_import(
        import_info=ImportInfo(module="contexts.boards.domain.models", lineno=1),
        category=ImportCategory.LOCAL,
        merged_rule=rule,
        source_module="contexts.boards.domain",
    )
    assert result is None


def test_allow_local_violation():
    rule = Rule(
        name="domain-isolation",
        modules="contexts.*.domain",
        allow=AllowDeny(local=["contexts.*.domain"]),
    )
    result = check_import(
        import_info=ImportInfo(module="contexts.boards.application.service", lineno=6),
        category=ImportCategory.LOCAL,
        merged_rule=rule,
        source_module="contexts.boards.domain",
    )
    assert isinstance(result, Violation)


def test_no_allow_for_category_means_allow_all():
    rule = Rule(
        name="domain-isolation",
        modules="contexts.*.domain",
        allow=AllowDeny(third_party=["pydantic"]),
        # standard_library is not specified in allow -> allow all
    )
    result = check_import(
        import_info=ImportInfo(module="os", lineno=1),
        category=ImportCategory.STANDARD_LIBRARY,
        merged_rule=rule,
        source_module="contexts.boards.domain",
    )
    assert result is None


def test_resolve_captures_single():
    result = resolve_captures("src.contexts.{context}.domain", {"context": "analytics"})
    assert result == "src.contexts.analytics.domain"


def test_resolve_captures_multiple():
    result = resolve_captures(
        "src.{ctx}.adapters.{dir}", {"ctx": "auth", "dir": "inbound"}
    )
    assert result == "src.auth.adapters.inbound"


def test_resolve_captures_no_placeholders():
    result = resolve_captures("src.shared.domain", {"context": "analytics"})
    assert result == "src.shared.domain"


def test_resolve_captures_unresolved_placeholder():
    result = resolve_captures("src.{unknown}.domain", {"context": "analytics"})
    assert result == "src.{unknown}.domain"


def test_cross_context_isolation_allowed():
    """Same context's domain import should be allowed."""
    rule = Rule(
        name="domain-layer",
        modules="contexts.{context}.domain",
        allow=AllowDeny(local=["contexts.{context}.domain", "shared.domain"]),
    )
    result = check_import(
        import_info=ImportInfo(module="contexts.boards.domain.models", lineno=1),
        category=ImportCategory.LOCAL,
        merged_rule=rule,
        source_module="contexts.boards.domain",
        captures={"context": "boards"},
    )
    assert result is None


def test_cross_context_isolation_violation():
    """Different context's domain import should be denied."""
    rule = Rule(
        name="domain-layer",
        modules="contexts.{context}.domain",
        allow=AllowDeny(local=["contexts.{context}.domain", "shared.domain"]),
    )
    result = check_import(
        import_info=ImportInfo(module="contexts.auth.domain.models", lineno=5),
        category=ImportCategory.LOCAL,
        merged_rule=rule,
        source_module="contexts.boards.domain",
        captures={"context": "boards"},
    )
    assert isinstance(result, Violation)
    assert result.imported_module == "contexts.auth.domain.models"


def test_check_import_no_captures_backward_compat():
    """Existing behavior works when no captures provided."""
    rule = Rule(
        name="domain-isolation",
        modules="contexts.*.domain",
        allow=AllowDeny(third_party=["pydantic"]),
    )
    result = check_import(
        import_info=ImportInfo(module="pydantic", lineno=1),
        category=ImportCategory.THIRD_PARTY,
        merged_rule=rule,
        source_module="contexts.boards.domain",
    )
    assert result is None


def test_violation_includes_description():
    """Violation should carry rule description when present."""
    rule = Rule(
        name="domain-isolation",
        modules="contexts.*.domain",
        description="Domain layer must remain pure",
        allow=AllowDeny(third_party=["pydantic"]),
    )
    result = check_import(
        import_info=ImportInfo(module="sqlalchemy", lineno=5),
        category=ImportCategory.THIRD_PARTY,
        merged_rule=rule,
        source_module="contexts.boards.domain",
    )
    assert isinstance(result, Violation)
    assert result.rule_description == "Domain layer must remain pure"


def test_deny_violation_includes_description():
    """Deny violation should also carry rule description."""
    rule = Rule(
        name="adapters-deny",
        modules="contexts.*.adapters",
        description="Adapters must not use boto3 directly",
        deny=AllowDeny(third_party=["boto3"]),
    )
    result = check_import(
        import_info=ImportInfo(module="boto3", lineno=3),
        category=ImportCategory.THIRD_PARTY,
        merged_rule=rule,
        source_module="contexts.boards.adapters",
    )
    assert isinstance(result, Violation)
    assert result.rule_description == "Adapters must not use boto3 directly"
