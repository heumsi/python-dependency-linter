from python_dependency_linter.checker import Violation
from python_dependency_linter.reporter import format_violations
from python_dependency_linter.resolver import ImportCategory


def test_format_violations():
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
        "contexts.boards.domain → contexts.boards.application.service (local)" in output
    )


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
