from pathlib import Path

from python_dependency_linter.parser import ImportInfo, parse_imports

FIXTURES = Path(__file__).parent / "fixtures" / "sample_project"


def test_parse_imports_from_file():
    file_path = FIXTURES / "contexts" / "boards" / "domain" / "models.py"
    imports = parse_imports(file_path)

    assert ImportInfo(module="dataclasses", lineno=1) in imports
    assert ImportInfo(module="typing", lineno=2) in imports
    assert ImportInfo(module="pydantic", lineno=4) in imports
    assert ImportInfo(module="contexts.boards.application.service", lineno=6) in imports
    assert ImportInfo(module="contexts.auth.domain.models", lineno=7) in imports


def test_parse_imports_plain_import():
    file_path = FIXTURES / "contexts" / "boards" / "application" / "service.py"
    imports = parse_imports(file_path)

    assert ImportInfo(module="os", lineno=1) in imports
    assert ImportInfo(module="contexts.boards.domain.models", lineno=2) in imports


def test_parse_imports_empty_file():
    file_path = FIXTURES / "contexts" / "__init__.py"
    imports = parse_imports(file_path)
    assert imports == []
