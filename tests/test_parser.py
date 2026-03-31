from pathlib import Path

from python_dependency_linter.parser import (
    ImportInfo,
    _parse_ignore_comment,
    parse_imports,
)

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


# --- _parse_ignore_comment tests ---


def test_parse_ignore_comment_no_comment():
    assert _parse_ignore_comment("import os") is None


def test_parse_ignore_comment_blanket():
    assert _parse_ignore_comment("import os  # pdl: ignore") == []


def test_parse_ignore_comment_single_rule():
    assert _parse_ignore_comment("import os  # pdl: ignore[domain-isolation]") == [
        "domain-isolation"
    ]


def test_parse_ignore_comment_multiple_rules():
    assert _parse_ignore_comment(
        "import os  # pdl: ignore[domain-isolation, adapters-deny]"
    ) == ["domain-isolation", "adapters-deny"]


def test_parse_ignore_comment_whitespace_variants():
    assert _parse_ignore_comment("import os  #pdl:ignore") == []
    assert _parse_ignore_comment("import os  #  pdl:  ignore[rule1]") == ["rule1"]


# --- parse_imports with ignore comment ---


def test_parse_imports_with_ignore_comment(tmp_path):
    source = """\
import os  # pdl: ignore
from typing import Optional
import sys  # pdl: ignore[domain-isolation, adapters-deny]
"""
    file_path = tmp_path / "test.py"
    file_path.write_text(source)
    imports = parse_imports(file_path, project_root=tmp_path)

    os_imp = next(i for i in imports if i.module == "os")
    assert os_imp.ignore_rules == []

    typing_imp = next(i for i in imports if i.module == "typing")
    assert typing_imp.ignore_rules is None

    sys_imp = next(i for i in imports if i.module == "sys")
    assert sys_imp.ignore_rules == ["domain-isolation", "adapters-deny"]
