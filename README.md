# python-dependency-linter

A dependency linter for Python projects. Define rules for which modules can depend on what, and catch violations.

## What It Does

- Define dependency rules between modules using a simple YAML or TOML config
- Detect imports that violate your rules with a single CLI command
- Integrate into CI or pre-commit to keep your architecture consistent

For Python developers who care about module boundaries and dependency direction — whether you're applying Layered, Hexagonal, Clean Architecture, or your own conventions.

## Installation

```bash
pip install python-dependency-linter
```

Or with uv:

```bash
uv add python-dependency-linter
```

## Quick Start

Create `.python-dependency-linter.yaml` in your project root:

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
```

Run:

```bash
pdl check
```

Output:

```
contexts/boards/domain/models.py:6
    [domain-isolation] contexts.boards.domain.models → contexts.boards.application.service (local)

contexts/boards/domain/models.py:9
    [domain-isolation] contexts.boards.domain.models → sqlalchemy (third_party)

Found 2 violation(s).
```

## Examples

### Layered Architecture

Enforce dependency direction: `presentation → application → domain`, where `domain` has no outward dependencies.

```yaml
rules:
  - name: domain-isolation
    modules: my_app.domain
    allow:
      standard_library: ["*"]
      third_party: []
      local: [my_app.domain]

  - name: application-layer
    modules: my_app.application
    allow:
      standard_library: ["*"]
      third_party: [pydantic]
      local:
        - my_app.application
        - my_app.domain

  - name: presentation-layer
    modules: my_app.presentation
    allow:
      standard_library: ["*"]
      third_party: [fastapi, pydantic]
      local:
        - my_app.presentation
        - my_app.application
        - my_app.domain
```

### Hexagonal Architecture

Isolate domain from infrastructure. Ports (interfaces) live in domain, adapters depend on domain but not vice versa.

```yaml
rules:
  - name: domain-no-infra
    modules: contexts.*.domain
    allow:
      standard_library: [dataclasses, typing, abc]
      third_party: []
      local: [contexts.*.domain]

  - name: adapters-depend-on-domain
    modules: contexts.*.adapters
    allow:
      standard_library: ["*"]
      third_party: ["*"]
      local:
        - contexts.*.adapters
        - contexts.*.domain
```

## Configuration

### Rule Structure

Each rule has:

- `name` — Rule identifier, shown in violation output
- `modules` — Module pattern to apply the rule to (supports `*` wildcard)
- `allow` — Whitelist: only listed dependencies are allowed
- `deny` — Blacklist: listed dependencies are denied

```yaml
rules:
  - name: rule-name
    modules: my_package.*.domain
    allow:
      standard_library: [dataclasses]
      third_party: [pydantic]
      local: [my_package.*.domain]
    deny:
      third_party: [boto3]
```

### Import Categories

Dependencies are classified into three categories (per PEP 8):

- `standard_library` — Python built-in modules (`os`, `sys`, `typing`, ...)
- `third_party` — Installed packages (`pydantic`, `sqlalchemy`, ...)
- `local` — Modules in your project

Both absolute imports (`from contexts.boards.domain import models`) and relative imports (`from ..domain import models`) are analyzed. Relative imports are resolved to absolute module names based on the file's location.

### Behavior

- **No rule** — Everything is allowed
- **`allow` only** — Whitelist mode. Only listed dependencies are allowed
- **`deny` only** — Blacklist mode. Listed dependencies are denied, rest allowed
- **`allow` + `deny`** — Allow first, then deny removes exceptions
- If `allow` exists but a category is omitted, that category allows all. For example:

```yaml
rules:
  - name: domain-isolation
    modules: contexts.*.domain
    allow:
      third_party: [pydantic]
      local: [contexts.*.domain]
      # standard_library is omitted → all standard library imports are allowed
```

Use `"*"` to allow all within a category:

```yaml
allow:
  standard_library: ["*"]  # allow all standard library imports
```

### Wildcard

`*` matches a single level in dotted module paths:

```yaml
modules: contexts.*.domain  # matches contexts.boards.domain, contexts.auth.domain, ...
```

`**` matches one or more levels in dotted module paths:

```yaml
modules: contexts.**.domain  # matches contexts.boards.domain, contexts.boards.sub.domain, ...
```

### Submodule Matching

When a pattern is used in `allow` or `deny`, it also matches submodules of the matched module. For example:

```yaml
allow:
  local: [contexts.*.domain]
```

This allows imports of `contexts.boards.domain` as well as its submodules like `contexts.boards.domain.models` or `contexts.boards.domain.entities.metric`.

### Rule Merging

When multiple rules match a module, they are merged. Specific rules override wildcard rules per field:

```yaml
rules:
  - name: base
    modules: contexts.*.domain
    allow:
      third_party: [pydantic]

  - name: boards-extra
    modules: contexts.boards.domain
    allow:
      third_party: [attrs]  # merged: [pydantic, attrs]
```

### pyproject.toml

You can also configure in `pyproject.toml`:

```toml
[[tool.python-dependency-linter.rules]]
name = "domain-isolation"
modules = "contexts.*.domain"

[tool.python-dependency-linter.rules.allow]
standard_library = ["dataclasses", "typing"]
third_party = ["pydantic"]
local = ["contexts.*.domain"]

[[tool.python-dependency-linter.rules]]
name = "application-dependency"
modules = "contexts.*.application"

[tool.python-dependency-linter.rules.allow]
standard_library = ["*"]
third_party = ["pydantic"]
local = ["contexts.*.application", "contexts.*.domain"]

[[tool.python-dependency-linter.rules]]
name = "no-boto-in-domain"
modules = "contexts.*.domain"

[tool.python-dependency-linter.rules.deny]
third_party = ["boto3"]
```

## CLI

```bash
# Check with default config (.python-dependency-linter.yaml)
pdl check

# Specify config file
pdl check --config path/to/config.yaml

# Specify project root
pdl check --project-root path/to/project
```

Exit codes:

- `0` — No violations
- `1` — Violations found

## Pre-commit

Add to `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/heumsi/python-dependency-linter
  rev: v0.1.0
  hooks:
    - id: python-dependency-linter
```

To pass custom options (e.g., a different config file or project root):

```yaml
- repo: https://github.com/heumsi/python-dependency-linter
  rev: v0.1.0
  hooks:
    - id: python-dependency-linter
      args: [--config, custom-config.yaml, --project-root, src]
```

## License

MIT
