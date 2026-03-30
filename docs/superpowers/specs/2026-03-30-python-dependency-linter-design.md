# Python Dependency Linter - Design Spec

## Overview

Python 프로젝트에서 모듈/패키지 간 의존성 규칙을 선언적으로 정의하고, 위반을 검사하는 린터.

import-linter에서 영감을 받았으나, 써드파티 화이트리스트 기능과 더 간결한 인터페이스를 목표로 한다.

## Core Concepts

### 의존성 규칙

- **기본 동작**: allow-all (규칙에 아무것도 안 쓰면 모든 의존 허용)
- **allow**: 화이트리스트 모드 (명시된 것만 허용)
- **deny**: 블랙리스트 모드 (명시된 것만 거부)
- **allow + deny**: allow 범위 내에서 deny로 예외 제거

### Import 분류 (PEP8 기준)

- **standard_library**: `sys.stdlib_module_names` (3.10+)로 판별
- **third_party**: standard_library도 local도 아닌 것
- **local**: 프로젝트 루트 기준으로 파일시스템에 존재하는 모듈/패키지

### 와일드카드

- `*`: 단일 레벨 매칭 (dot 기준 세그먼트 하나)
- 예: `contexts.*.domain` → `contexts.boards.domain`, `contexts.auth.domain`

### 규칙 병합

- 와일드카드 규칙과 구체적 규칙이 동시에 매칭될 때, 구체적 규칙에서 명시한 필드만 머지
- 명시되지 않은 필드는 와일드카드 규칙 그대로 유지

## Configuration

### YAML (.python-dependency-linter.yaml)

```yaml
rules:
  - name: domain-isolation
    modules: contexts.*.domain
    allow:
      standard_library: [dataclasses, typing]
      third_party: [pydantic]
      local: [contexts.*.domain]

  - name: application-dependency
    modules: contexts.*.application
    allow:
      standard_library: ["*"]
      third_party: [pydantic]
      local:
        - contexts.*.application
        - contexts.*.domain

  - name: adapters-dependency
    modules: contexts.*.adapters
    deny:
      third_party: [boto3]

  - name: auth-isolation
    modules: contexts.auth
    deny:
      local: [contexts.boards, contexts.billing]
```

### pyproject.toml

```toml
[[tool.python-dependency-linter.rules]]
name = "domain-isolation"
modules = "contexts.*.domain"

[tool.python-dependency-linter.rules.allow]
standard_library = ["dataclasses", "typing"]
third_party = ["pydantic"]
local = ["contexts.*.domain"]
```

## Architecture

### Project Structure

```
python-dependency-linter/
├── pyproject.toml
├── python_dependency_linter/
│   ├── __init__.py
│   ├── cli.py              # CLI entry point (pdl check)
│   ├── config.py           # config loading (YAML, pyproject.toml)
│   ├── parser.py           # AST-based import extraction
│   ├── resolver.py         # import classification (std/third_party/local)
│   ├── matcher.py          # wildcard matching, rule merging
│   ├── checker.py          # rule violation checking
│   └── reporter.py         # violation output formatting
├── tests/
│   ├── test_config.py
│   ├── test_parser.py
│   ├── test_resolver.py
│   ├── test_matcher.py
│   ├── test_checker.py
│   ├── test_reporter.py
│   ├── test_cli.py
│   └── fixtures/
└── .pre-commit-hooks.yaml
```

### Processing Flow

1. `config.py` — 설정 파일 로딩 및 파싱
2. `parser.py` — 대상 Python 파일들의 import 구문 추출 (AST)
3. `resolver.py` — 각 import를 standard_library / third_party / local로 분류
4. `matcher.py` — 파일이 어떤 규칙에 매칭되는지 판별, 와일드카드 처리, 규칙 병합
5. `checker.py` — 매칭된 규칙에 따라 위반 여부 판정
6. `reporter.py` — 위반 결과 포맷팅 및 출력
7. `cli.py` — 위 흐름을 조합하여 실행

## CLI Interface

```bash
# basic usage (auto-detect config in current directory)
pdl check

# specify config file
pdl check --config .python-dependency-linter.yaml
```

### Exit Codes

- `0` — no violations
- `1` — violations found

## Output Format

### Violations Found

```
contexts/boards/domain/models.py:3
    [domain-isolation] contexts.boards.domain → contexts.boards.application (local)
    from contexts.boards.application.service import BoardService

contexts/boards/domain/models.py:5
    [domain-isolation] contexts.boards.domain → sqlalchemy (third_party)
    from sqlalchemy import Column

Found 2 violations.
```

### No Violations

```
No violations found.
```

## Pre-commit Hook

### .pre-commit-hooks.yaml (in this repo)

```yaml
- id: python-dependency-linter
  name: Python Dependency Linter
  entry: pdl check
  language: python
  types: [python]
```

### Usage (in user's project)

```yaml
- repo: https://github.com/heumsi/python-dependency-linter
  rev: v0.1.0
  hooks:
    - id: python-dependency-linter
```

## Packaging

```toml
[project]
name = "python-dependency-linter"
requires-python = ">=3.10"
dependencies = [
    "pyyaml",
    "click",
]

[project.scripts]
pdl = "python_dependency_linter.cli:main"
```

- PyPI에 `python-dependency-linter`로 배포
- `pip install python-dependency-linter` / `uv add python-dependency-linter`

## Testing Strategy

### Unit Tests

- `test_config.py` — config loading/parsing
- `test_parser.py` — import extraction
- `test_resolver.py` — import classification
- `test_matcher.py` — wildcard matching, rule merging
- `test_checker.py` — violation detection
- `test_reporter.py` — output formatting
- `test_cli.py` — CLI integration tests
- `fixtures/` — test Python files

### Key Test Cases

- allowed import → no violation
- disallowed import → violation detected
- wildcard matching accuracy
- rule merge behavior
- allow + deny combination
- missing/invalid config error handling

## Development Conventions

### Commit Rules

- Always in English, first letter after colon capitalized
- Conventional Commits format with gitmoji prefix:
  - `✨ feat: Add config parser`
  - `🐛 fix: Fix wildcard matching`
  - `♻️ refactor: Extract matcher logic`
  - `📝 docs: Add design spec`
  - `✅ test: Add resolver tests`
  - `🔧 chore: Update dependencies`
  - `👷 ci: Add GitHub Actions`
  - `⚡ perf: Optimize file scanning`
- Semantic versioning

### Pre-commit

- ruff must pass before every commit
- Configured via `.pre-commit-config.yaml`
