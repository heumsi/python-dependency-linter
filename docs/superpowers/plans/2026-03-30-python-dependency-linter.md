# Python Dependency Linter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI tool (`pdl`) that checks module/package dependency rules and reports violations.

**Architecture:** Single-pass approach — scan Python files with AST, classify imports, match against declarative rules, report violations. Configuration via YAML or pyproject.toml.

**Tech Stack:** Python 3.10+, click (CLI), pyyaml (config), ast (import parsing), pytest (testing), ruff (linting)

---

## File Structure

```
python-dependency-linter/
├── pyproject.toml                          # packaging, dependencies, pdl entrypoint
├── .pre-commit-config.yaml                 # ruff pre-commit for this repo
├── .pre-commit-hooks.yaml                  # pre-commit hook definition for consumers
├── python_dependency_linter/
│   ├── __init__.py                         # version
│   ├── cli.py                              # click CLI entrypoint (pdl check)
│   ├── config.py                           # YAML / pyproject.toml config loading
│   ├── parser.py                           # AST-based import extraction
│   ├── resolver.py                         # import classification (std/third_party/local)
│   ├── matcher.py                          # wildcard matching, rule merging
│   ├── checker.py                          # rule violation checking
│   └── reporter.py                         # violation output formatting
├── tests/
│   ├── conftest.py                         # shared fixtures
│   ├── test_config.py
│   ├── test_parser.py
│   ├── test_resolver.py
│   ├── test_matcher.py
│   ├── test_checker.py
│   ├── test_reporter.py
│   ├── test_cli.py
│   └── fixtures/                           # test Python source files
│       ├── sample_project/
│       │   └── contexts/
│       │       ├── __init__.py
│       │       ├── boards/
│       │       │   ├── __init__.py
│       │       │   ├── domain/
│       │       │   │   ├── __init__.py
│       │       │   │   └── models.py
│       │       │   ├── application/
│       │       │   │   ├── __init__.py
│       │       │   │   └── service.py
│       │       │   └── adapters/
│       │       │       ├── __init__.py
│       │       │       └── repository.py
│       │       └── auth/
│       │           ├── __init__.py
│       │           ├── domain/
│       │           │   ├── __init__.py
│       │           │   └── models.py
│       │           └── application/
│       │               ├── __init__.py
│       │               └── service.py
│       ├── sample_config.yaml
│       └── sample_pyproject.toml
└── README.md
```

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `.pre-commit-config.yaml`
- Create: `python_dependency_linter/__init__.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "python-dependency-linter"
version = "0.1.0"
description = "A dependency linter for Python projects"
requires-python = ">=3.10"
dependencies = [
    "pyyaml>=6.0",
    "click>=8.0",
]

[project.scripts]
pdl = "python_dependency_linter.cli:main"

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.4",
    "pre-commit>=3.0",
]

[tool.ruff]
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create .pre-commit-config.yaml**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.8
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

- [ ] **Step 3: Create python_dependency_linter/__init__.py**

```python
__version__ = "0.1.0"
```

- [ ] **Step 4: Install project and pre-commit**

Run:
```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pre-commit install
```

Expected: project installs successfully, pre-commit hooks installed.

- [ ] **Step 5: Verify setup**

Run: `pdl --help`

Expected: click shows help (will fail with import error — that's fine, confirms entrypoint is wired)

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml .pre-commit-config.yaml python_dependency_linter/__init__.py
git commit -m "🔧 chore: Initialize project scaffolding"
```

---

### Task 2: Config Loading

**Files:**
- Create: `python_dependency_linter/config.py`
- Create: `tests/test_config.py`
- Create: `tests/fixtures/sample_config.yaml`
- Create: `tests/fixtures/sample_pyproject.toml`

- [ ] **Step 1: Create test fixtures**

`tests/fixtures/sample_config.yaml`:
```yaml
rules:
  - name: domain-isolation
    modules: contexts.*.domain
    allow:
      standard_library: [dataclasses, typing]
      third_party: [pydantic]
      local: [contexts.*.domain]

  - name: adapters-deny-boto
    modules: contexts.*.adapters
    deny:
      third_party: [boto3]
```

`tests/fixtures/sample_pyproject.toml`:
```toml
[tool.python-dependency-linter]

[[tool.python-dependency-linter.rules]]
name = "domain-isolation"
modules = "contexts.*.domain"

[tool.python-dependency-linter.rules.allow]
standard_library = ["dataclasses", "typing"]
third_party = ["pydantic"]
local = ["contexts.*.domain"]
```

- [ ] **Step 2: Write failing tests**

`tests/test_config.py`:
```python
from pathlib import Path

from python_dependency_linter.config import load_config, Rule, AllowDeny

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_yaml_config():
    config = load_config(FIXTURES / "sample_config.yaml")
    assert len(config.rules) == 2

    rule = config.rules[0]
    assert rule.name == "domain-isolation"
    assert rule.modules == "contexts.*.domain"
    assert rule.allow.standard_library == ["dataclasses", "typing"]
    assert rule.allow.third_party == ["pydantic"]
    assert rule.allow.local == ["contexts.*.domain"]
    assert rule.deny is None


def test_load_yaml_config_deny():
    config = load_config(FIXTURES / "sample_config.yaml")
    rule = config.rules[1]
    assert rule.name == "adapters-deny-boto"
    assert rule.deny.third_party == ["boto3"]
    assert rule.allow is None


def test_load_pyproject_toml():
    config = load_config(FIXTURES / "sample_pyproject.toml")
    assert len(config.rules) == 1

    rule = config.rules[0]
    assert rule.name == "domain-isolation"
    assert rule.modules == "contexts.*.domain"
    assert rule.allow.standard_library == ["dataclasses", "typing"]


def test_load_config_file_not_found():
    import pytest

    with pytest.raises(FileNotFoundError):
        load_config(Path("nonexistent.yaml"))
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `pytest tests/test_config.py -v`

Expected: FAIL with `ImportError: cannot import name 'load_config'`

- [ ] **Step 4: Implement config.py**

`python_dependency_linter/config.py`:
```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class AllowDeny:
    standard_library: list[str] | None = None
    third_party: list[str] | None = None
    local: list[str] | None = None


@dataclass
class Rule:
    name: str
    modules: str
    allow: AllowDeny | None = None
    deny: AllowDeny | None = None


@dataclass
class Config:
    rules: list[Rule]


def _parse_allow_deny(data: dict | None) -> AllowDeny | None:
    if data is None:
        return None
    return AllowDeny(
        standard_library=data.get("standard_library"),
        third_party=data.get("third_party"),
        local=data.get("local"),
    )


def _parse_rules(rules_data: list[dict]) -> list[Rule]:
    rules = []
    for r in rules_data:
        rules.append(
            Rule(
                name=r["name"],
                modules=r["modules"],
                allow=_parse_allow_deny(r.get("allow")),
                deny=_parse_allow_deny(r.get("deny")),
            )
        )
    return rules


def _load_yaml(path: Path) -> Config:
    with open(path) as f:
        data = yaml.safe_load(f)
    return Config(rules=_parse_rules(data["rules"]))


def _load_pyproject_toml(path: Path) -> Config:
    import tomllib

    with open(path, "rb") as f:
        data = tomllib.load(f)
    tool_config = data["tool"]["python-dependency-linter"]
    return Config(rules=_parse_rules(tool_config["rules"]))


def load_config(path: Path) -> Config:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    if path.suffix == ".toml":
        return _load_pyproject_toml(path)
    return _load_yaml(path)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_config.py -v`

Expected: all 4 tests PASS

- [ ] **Step 6: Commit**

```bash
git add python_dependency_linter/config.py tests/test_config.py tests/fixtures/sample_config.yaml tests/fixtures/sample_pyproject.toml
git commit -m "✨ feat: Add config loading for YAML and pyproject.toml"
```

---

### Task 3: AST Import Parser

**Files:**
- Create: `python_dependency_linter/parser.py`
- Create: `tests/test_parser.py`
- Create: `tests/fixtures/sample_project/` (directory structure with test files)

- [ ] **Step 1: Create fixture files**

`tests/fixtures/sample_project/contexts/__init__.py`: empty file
`tests/fixtures/sample_project/contexts/boards/__init__.py`: empty file
`tests/fixtures/sample_project/contexts/boards/domain/__init__.py`: empty file

`tests/fixtures/sample_project/contexts/boards/domain/models.py`:
```python
import dataclasses
from typing import Optional

from pydantic import BaseModel

from contexts.boards.application.service import BoardService
from contexts.auth.domain.models import User
```

`tests/fixtures/sample_project/contexts/boards/application/__init__.py`: empty file

`tests/fixtures/sample_project/contexts/boards/application/service.py`:
```python
import os
from contexts.boards.domain.models import Board
```

`tests/fixtures/sample_project/contexts/boards/adapters/__init__.py`: empty file

`tests/fixtures/sample_project/contexts/boards/adapters/repository.py`:
```python
from sqlalchemy import Column
from contexts.boards.domain.models import Board
from contexts.boards.application.service import BoardService
```

`tests/fixtures/sample_project/contexts/auth/__init__.py`: empty file
`tests/fixtures/sample_project/contexts/auth/domain/__init__.py`: empty file

`tests/fixtures/sample_project/contexts/auth/domain/models.py`:
```python
from pydantic import BaseModel
```

`tests/fixtures/sample_project/contexts/auth/application/__init__.py`: empty file

`tests/fixtures/sample_project/contexts/auth/application/service.py`:
```python
from contexts.auth.domain.models import User
```

- [ ] **Step 2: Write failing tests**

`tests/test_parser.py`:
```python
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
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `pytest tests/test_parser.py -v`

Expected: FAIL with `ImportError: cannot import name 'parse_imports'`

- [ ] **Step 4: Implement parser.py**

`python_dependency_linter/parser.py`:
```python
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImportInfo:
    module: str
    lineno: int


def parse_imports(file_path: Path) -> list[ImportInfo]:
    source = file_path.read_text()
    tree = ast.parse(source, filename=str(file_path))

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(ImportInfo(module=alias.name, lineno=node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                imports.append(ImportInfo(module=node.module, lineno=node.lineno))

    return imports
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_parser.py -v`

Expected: all 3 tests PASS

- [ ] **Step 6: Commit**

```bash
git add python_dependency_linter/parser.py tests/test_parser.py tests/fixtures/sample_project/
git commit -m "✨ feat: Add AST-based import parser"
```

---

### Task 4: Import Resolver

**Files:**
- Create: `python_dependency_linter/resolver.py`
- Create: `tests/test_resolver.py`

- [ ] **Step 1: Write failing tests**

`tests/test_resolver.py`:
```python
from pathlib import Path

from python_dependency_linter.resolver import ImportCategory, resolve_import

FIXTURES = Path(__file__).parent / "fixtures" / "sample_project"


def test_resolve_standard_library():
    assert resolve_import("os", FIXTURES) == ImportCategory.STANDARD_LIBRARY
    assert resolve_import("sys", FIXTURES) == ImportCategory.STANDARD_LIBRARY
    assert resolve_import("dataclasses", FIXTURES) == ImportCategory.STANDARD_LIBRARY
    assert resolve_import("typing", FIXTURES) == ImportCategory.STANDARD_LIBRARY


def test_resolve_local():
    assert resolve_import("contexts.boards.domain.models", FIXTURES) == ImportCategory.LOCAL
    assert resolve_import("contexts.auth.domain.models", FIXTURES) == ImportCategory.LOCAL


def test_resolve_third_party():
    assert resolve_import("pydantic", FIXTURES) == ImportCategory.THIRD_PARTY
    assert resolve_import("sqlalchemy", FIXTURES) == ImportCategory.THIRD_PARTY
    assert resolve_import("click", FIXTURES) == ImportCategory.THIRD_PARTY
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_resolver.py -v`

Expected: FAIL with `ImportError: cannot import name 'resolve_import'`

- [ ] **Step 3: Implement resolver.py**

`python_dependency_linter/resolver.py`:
```python
from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path


class ImportCategory(Enum):
    STANDARD_LIBRARY = "standard_library"
    THIRD_PARTY = "third_party"
    LOCAL = "local"


def resolve_import(module: str, project_root: Path) -> ImportCategory:
    top_level = module.split(".")[0]

    if top_level in sys.stdlib_module_names:
        return ImportCategory.STANDARD_LIBRARY

    # Check if it exists as a local module/package
    if (project_root / top_level).is_dir() or (project_root / f"{top_level}.py").is_file():
        return ImportCategory.LOCAL

    return ImportCategory.THIRD_PARTY
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_resolver.py -v`

Expected: all 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add python_dependency_linter/resolver.py tests/test_resolver.py
git commit -m "✨ feat: Add import resolver for classification"
```

---

### Task 5: Wildcard Matcher

**Files:**
- Create: `python_dependency_linter/matcher.py`
- Create: `tests/test_matcher.py`

- [ ] **Step 1: Write failing tests**

`tests/test_matcher.py`:
```python
from python_dependency_linter.config import AllowDeny, Rule
from python_dependency_linter.matcher import matches_pattern, find_matching_rules, merge_rules


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
        Rule(name="r1", modules="contexts.*.domain", allow=AllowDeny(third_party=["pydantic"])),
        Rule(name="r2", modules="contexts.boards.domain", allow=AllowDeny(third_party=["attrs"])),
        Rule(name="r3", modules="contexts.*.adapters", deny=AllowDeny(third_party=["boto3"])),
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
    rule1 = Rule(name="r1", modules="contexts.*.adapters", deny=AllowDeny(third_party=["boto3"]))
    rule2 = Rule(name="r2", modules="contexts.boards.adapters", deny=AllowDeny(third_party=["requests"]))
    merged = merge_rules([rule1, rule2])

    assert sorted(merged.deny.third_party) == ["boto3", "requests"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_matcher.py -v`

Expected: FAIL with `ImportError: cannot import name 'matches_pattern'`

- [ ] **Step 3: Implement matcher.py**

`python_dependency_linter/matcher.py`:
```python
from __future__ import annotations

from python_dependency_linter.config import AllowDeny, Rule


def matches_pattern(pattern: str, module: str) -> bool:
    pattern_parts = pattern.split(".")
    module_parts = module.split(".")

    if len(pattern_parts) != len(module_parts):
        return False

    for p, m in zip(pattern_parts, module_parts):
        if p == "*":
            continue
        if p != m:
            return False

    return True


def find_matching_rules(module: str, rules: list[Rule]) -> list[Rule]:
    return [r for r in rules if matches_pattern(r.modules, module)]


def _merge_allow_deny(base: AllowDeny | None, override: AllowDeny | None) -> AllowDeny | None:
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_matcher.py -v`

Expected: all 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add python_dependency_linter/matcher.py tests/test_matcher.py
git commit -m "✨ feat: Add wildcard matcher and rule merging"
```

---

### Task 6: Checker

**Files:**
- Create: `python_dependency_linter/checker.py`
- Create: `tests/test_checker.py`

- [ ] **Step 1: Write failing tests**

`tests/test_checker.py`:
```python
from python_dependency_linter.checker import check_import, Violation
from python_dependency_linter.config import AllowDeny, Rule
from python_dependency_linter.parser import ImportInfo
from python_dependency_linter.resolver import ImportCategory


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_checker.py -v`

Expected: FAIL with `ImportError: cannot import name 'check_import'`

- [ ] **Step 3: Implement checker.py**

`python_dependency_linter/checker.py`:
```python
from __future__ import annotations

from dataclasses import dataclass

from python_dependency_linter.config import AllowDeny, Rule
from python_dependency_linter.matcher import matches_pattern
from python_dependency_linter.parser import ImportInfo
from python_dependency_linter.resolver import ImportCategory


@dataclass
class Violation:
    rule_name: str
    source_module: str
    imported_module: str
    category: ImportCategory
    lineno: int


def _get_category_list(allow_deny: AllowDeny | None, category: ImportCategory) -> list[str] | None:
    if allow_deny is None:
        return None
    match category:
        case ImportCategory.STANDARD_LIBRARY:
            return allow_deny.standard_library
        case ImportCategory.THIRD_PARTY:
            return allow_deny.third_party
        case ImportCategory.LOCAL:
            return allow_deny.local


def _is_in_list(module: str, patterns: list[str]) -> bool:
    if "*" in patterns:
        return True
    return any(matches_pattern(p, module) or module.startswith(p + ".") for p in patterns)


def check_import(
    import_info: ImportInfo,
    category: ImportCategory,
    merged_rule: Rule | None,
    source_module: str,
) -> Violation | None:
    if merged_rule is None:
        return None

    module = import_info.module

    # Check deny first (deny takes priority over allow)
    deny_list = _get_category_list(merged_rule.deny, category)
    if deny_list is not None and _is_in_list(module, deny_list):
        return Violation(
            rule_name=merged_rule.name,
            source_module=source_module,
            imported_module=module,
            category=category,
            lineno=import_info.lineno,
        )

    # Check allow
    allow_list = _get_category_list(merged_rule.allow, category)
    if allow_list is None:
        # No allow list for this category = allow all
        return None
    if _is_in_list(module, allow_list):
        return None

    return Violation(
        rule_name=merged_rule.name,
        source_module=source_module,
        imported_module=module,
        category=category,
        lineno=import_info.lineno,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_checker.py -v`

Expected: all 9 tests PASS

- [ ] **Step 5: Commit**

```bash
git add python_dependency_linter/checker.py tests/test_checker.py
git commit -m "✨ feat: Add dependency checker with allow/deny logic"
```

---

### Task 7: Reporter

**Files:**
- Create: `python_dependency_linter/reporter.py`
- Create: `tests/test_reporter.py`

- [ ] **Step 1: Write failing tests**

`tests/test_reporter.py`:
```python
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
    assert "contexts.boards.domain → contexts.boards.application.service (local)" in output


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_reporter.py -v`

Expected: FAIL with `ImportError: cannot import name 'format_violations'`

- [ ] **Step 3: Implement reporter.py**

`python_dependency_linter/reporter.py`:
```python
from __future__ import annotations

from python_dependency_linter.checker import Violation


def format_violations(file_path: str, violations: list[Violation]) -> str:
    if not violations:
        return ""

    lines = []
    for v in violations:
        lines.append(f"{file_path}:{v.lineno}")
        lines.append(f"    [{v.rule_name}] {v.source_module} → {v.imported_module} ({v.category.value})")
        lines.append("")

    return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_reporter.py -v`

Expected: all 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add python_dependency_linter/reporter.py tests/test_reporter.py
git commit -m "✨ feat: Add violation reporter"
```

---

### Task 8: CLI Integration

**Files:**
- Create: `python_dependency_linter/cli.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests**

`tests/test_cli.py`:
```python
from pathlib import Path

from click.testing import CliRunner

from python_dependency_linter.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


def test_cli_check_with_violations(tmp_path):
    config_content = """\
rules:
  - name: domain-isolation
    modules: contexts.*.domain
    allow:
      standard_library: [dataclasses, typing]
      third_party: [pydantic]
      local: [contexts.*.domain]
"""
    config_file = tmp_path / ".python-dependency-linter.yaml"
    config_file.write_text(config_content)

    # Copy sample project to tmp_path
    import shutil
    src = FIXTURES / "sample_project" / "contexts"
    dst = tmp_path / "contexts"
    shutil.copytree(src, dst)

    runner = CliRunner()
    result = runner.invoke(main, ["check", "--config", str(config_file), "--project-root", str(tmp_path)])
    assert result.exit_code == 1
    assert "[domain-isolation]" in result.output
    assert "Found" in result.output


def test_cli_check_no_violations(tmp_path):
    config_content = """\
rules:
  - name: allow-all
    modules: contexts.*.domain
    allow:
      standard_library: ["*"]
      third_party: ["*"]
      local: ["*"]
"""
    config_file = tmp_path / ".python-dependency-linter.yaml"
    config_file.write_text(config_content)

    import shutil
    src = FIXTURES / "sample_project" / "contexts"
    dst = tmp_path / "contexts"
    shutil.copytree(src, dst)

    runner = CliRunner()
    result = runner.invoke(main, ["check", "--config", str(config_file), "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    assert "No violations found." in result.output


def test_cli_check_config_not_found():
    runner = CliRunner()
    result = runner.invoke(main, ["check", "--config", "nonexistent.yaml"])
    assert result.exit_code != 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_cli.py -v`

Expected: FAIL with `ImportError: cannot import name 'main'`

- [ ] **Step 3: Implement cli.py**

`python_dependency_linter/cli.py`:
```python
from __future__ import annotations

from pathlib import Path

import click

from python_dependency_linter.checker import check_import
from python_dependency_linter.config import load_config
from python_dependency_linter.matcher import find_matching_rules, merge_rules
from python_dependency_linter.parser import parse_imports
from python_dependency_linter.reporter import format_violations
from python_dependency_linter.resolver import resolve_import


def _file_to_module(file_path: Path, project_root: Path) -> str:
    relative = file_path.relative_to(project_root)
    parts = relative.with_suffix("").parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _find_python_files(project_root: Path) -> list[Path]:
    return sorted(project_root.rglob("*.py"))


@click.group()
def main():
    pass


@main.command()
@click.option("--config", "config_path", default=".python-dependency-linter.yaml", help="Path to config file.")
@click.option("--project-root", default=".", help="Project root directory.")
def check(config_path: str, project_root: str):
    root = Path(project_root).resolve()
    config_file = Path(config_path)

    try:
        config = load_config(config_file)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    all_violations = []
    python_files = _find_python_files(root)

    for file_path in python_files:
        module = _file_to_module(file_path, root)
        matching_rules = find_matching_rules(module, config.rules)
        if not matching_rules:
            continue

        merged_rule = merge_rules(matching_rules)
        imports = parse_imports(file_path)

        file_violations = []
        for imp in imports:
            category = resolve_import(imp.module, root)
            violation = check_import(imp, category, merged_rule, module)
            if violation is not None:
                file_violations.append(violation)

        if file_violations:
            rel_path = str(file_path.relative_to(root))
            output = format_violations(rel_path, file_violations)
            click.echo(output)
            all_violations.extend(file_violations)

    if all_violations:
        click.echo(f"Found {len(all_violations)} violation(s).")
        raise SystemExit(1)
    else:
        click.echo("No violations found.")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_cli.py -v`

Expected: all 3 tests PASS

- [ ] **Step 5: Run all tests**

Run: `pytest -v`

Expected: all tests PASS

- [ ] **Step 6: Commit**

```bash
git add python_dependency_linter/cli.py tests/test_cli.py
git commit -m "✨ feat: Add CLI with check command"
```

---

### Task 9: Pre-commit Hook Definition

**Files:**
- Create: `.pre-commit-hooks.yaml`

- [ ] **Step 1: Create .pre-commit-hooks.yaml**

`.pre-commit-hooks.yaml`:
```yaml
- id: python-dependency-linter
  name: Python Dependency Linter
  entry: pdl check
  language: python
  types: [python]
  pass_filenames: false
```

- [ ] **Step 2: Commit**

```bash
git add .pre-commit-hooks.yaml
git commit -m "✨ feat: Add pre-commit hook definition"
```

---

### Task 10: End-to-End Verification

- [ ] **Step 1: Run full test suite with ruff**

Run:
```bash
ruff check .
ruff format --check .
pytest -v
```

Expected: all checks pass

- [ ] **Step 2: Test CLI manually against fixtures**

Run:
```bash
pdl check --config tests/fixtures/sample_config.yaml --project-root tests/fixtures/sample_project
```

Expected: violations reported for domain files importing from application layer

- [ ] **Step 3: Final commit if any fixes needed**

```bash
git add -A
git commit -m "🔧 chore: Fix lint and formatting issues"
```
