from python_dependency_linter.core.resolver import ImportCategory
from python_dependency_linter.domain.checker import Violation
from python_dependency_linter.io.reporter import format_violations


def test_format_violations_without_description():
    violations = [
        Violation(
            rule_name="domain-isolation",
            source_module="contexts.boards.domain",
            imported_module="contexts.boards.application.service",
            category=ImportCategory.LOCAL,
            lineno=6,
        ),
    ]
    file_path = "contexts/boards/domain/models.py"
    output = format_violations(file_path, violations)

    assert "contexts/boards/domain/models.py:6" in output
    assert "[domain-isolation]" in output
    assert (
        "contexts.boards.domain \u2192 contexts.boards.application.service (local)"
        in output
    )


def test_format_violations_with_description():
    violations = [
        Violation(
            rule_name="domain-isolation",
            source_module="contexts.boards.domain",
            imported_module="contexts.boards.application.service",
            category=ImportCategory.LOCAL,
            lineno=6,
            rule_description="Domain layer must remain pure",
        ),
    ]
    file_path = "contexts/boards/domain/models.py"
    output = format_violations(file_path, violations)

    assert "contexts/boards/domain/models.py:6" in output
    assert "[domain-isolation] Domain layer must remain pure" in output
    assert (
        "contexts.boards.domain \u2192 contexts.boards.application.service (local)"
        in output
    )


def test_format_violations_arrow_always_on_separate_line():
    """Arrow line should always be on its own line, regardless of description."""
    violations = [
        Violation(
            rule_name="r1",
            source_module="a.b",
            imported_module="c.d",
            category=ImportCategory.LOCAL,
            lineno=1,
        ),
    ]
    output = format_violations("a/b.py", violations)
    lines = output.strip().split("\n")
    assert lines[0] == "a/b.py:1"
    assert lines[1] == "    [r1]"
    assert lines[2] == "    a.b \u2192 c.d (local)"


def test_format_violations_multiple():
    violations = [
        Violation(
            rule_name="r1",
            source_module="a.b",
            imported_module="c.d",
            category=ImportCategory.LOCAL,
            lineno=1,
        ),
        Violation(
            rule_name="r2",
            source_module="a.b",
            imported_module="sqlalchemy",
            category=ImportCategory.THIRD_PARTY,
            lineno=5,
        ),
    ]
    output = format_violations("a/b.py", violations)
    assert "[r1]" in output
    assert "[r2]" in output


def test_format_violations_empty():
    output = format_violations("a/b.py", [])
    assert output == ""
