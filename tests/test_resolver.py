from pathlib import Path

from python_dependency_linter.core.resolver import ImportCategory, resolve_import

FIXTURES = Path(__file__).parent / "fixtures" / "sample_project"


def test_resolve_standard_library():
    assert resolve_import("os", FIXTURES) == ImportCategory.STANDARD_LIBRARY
    assert resolve_import("sys", FIXTURES) == ImportCategory.STANDARD_LIBRARY
    assert resolve_import("dataclasses", FIXTURES) == ImportCategory.STANDARD_LIBRARY
    assert resolve_import("typing", FIXTURES) == ImportCategory.STANDARD_LIBRARY


def test_resolve_local():
    assert (
        resolve_import("contexts.boards.domain.models", FIXTURES)
        == ImportCategory.LOCAL
    )
    assert (
        resolve_import("contexts.auth.domain.models", FIXTURES) == ImportCategory.LOCAL
    )


def test_resolve_third_party():
    assert resolve_import("pydantic", FIXTURES) == ImportCategory.THIRD_PARTY
    assert resolve_import("sqlalchemy", FIXTURES) == ImportCategory.THIRD_PARTY
    assert resolve_import("click", FIXTURES) == ImportCategory.THIRD_PARTY
