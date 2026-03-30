from pathlib import Path

from python_dependency_linter.parser import ImportInfo, parse_imports

FIXTURES = Path(__file__).parent / "fixtures" / "sample_project"


def test_parse_imports_from_file():
    file_path = FIXTURES / "contexts" / "boards" / "domain" / "models.py"
    imports = parse_imports(file_path, project_root=FIXTURES)

    assert ImportInfo(module="dataclasses", lineno=1) in imports
    assert ImportInfo(module="typing", lineno=2) in imports
    assert ImportInfo(module="pydantic", lineno=4) in imports
    assert ImportInfo(module="contexts.boards.application.service", lineno=6) in imports
    assert ImportInfo(module="contexts.auth.domain.models", lineno=7) in imports


def test_parse_imports_plain_import():
    file_path = FIXTURES / "contexts" / "boards" / "application" / "service.py"
    imports = parse_imports(file_path, project_root=FIXTURES)

    assert ImportInfo(module="os", lineno=1) in imports
    assert ImportInfo(module="contexts.boards.domain.models", lineno=2) in imports


def test_parse_imports_empty_file():
    file_path = FIXTURES / "contexts" / "__init__.py"
    imports = parse_imports(file_path, project_root=FIXTURES)
    assert imports == []


def test_parse_relative_import_level1_with_module():
    """from .repository_utils import helper -> contexts.boards.adapters.repository_utils"""  # noqa: E501
    file_path = FIXTURES / "contexts" / "boards" / "adapters" / "repository.py"
    imports = parse_imports(file_path, project_root=FIXTURES)

    assert (
        ImportInfo(module="contexts.boards.adapters.repository_utils", lineno=4)
        in imports
    )


def test_parse_relative_import_level1_no_module():
    """from . import __init__ -> contexts.boards.adapters"""
    file_path = FIXTURES / "contexts" / "boards" / "adapters" / "repository.py"
    imports = parse_imports(file_path, project_root=FIXTURES)

    assert ImportInfo(module="contexts.boards.adapters", lineno=5) in imports


def test_parse_relative_import_level2_with_module():
    """from ..domain import models -> contexts.boards.domain"""
    file_path = FIXTURES / "contexts" / "boards" / "adapters" / "repository.py"
    imports = parse_imports(file_path, project_root=FIXTURES)

    assert ImportInfo(module="contexts.boards.domain", lineno=6) in imports


def test_parse_relative_import_over_level_skipped():
    """from ....outside import something -> level exceeds root, should be skipped"""
    file_path = FIXTURES / "contexts" / "boards" / "adapters" / "repository.py"
    imports = parse_imports(file_path, project_root=FIXTURES)

    modules = [imp.module for imp in imports]
    assert not any("outside" in m for m in modules)


def test_parse_relative_import_from_init():
    """from .domain import models in __init__.py -> contexts.boards.domain"""
    file_path = FIXTURES / "contexts" / "boards" / "__init__.py"
    imports = parse_imports(file_path, project_root=FIXTURES)

    assert ImportInfo(module="contexts.boards.domain", lineno=1) in imports
