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

Using named captures (`{context}`), you can enforce that each bounded context only depends on its own domain — not other contexts' domains:

```yaml
rules:
  - name: domain-no-infra
    modules: contexts.{context}.domain
    allow:
      standard_library: [dataclasses, typing, abc]
      third_party: []
      local: [contexts.{context}.domain, shared.domain]

  - name: adapters-depend-on-domain
    modules: contexts.{context}.adapters
    allow:
      standard_library: ["*"]
      third_party: ["*"]
      local:
        - contexts.{context}.adapters
        - contexts.{context}.domain
        - shared
```

With `{context}`, `contexts.boards.domain` can only import from `contexts.boards.domain` and `shared.domain` — not from `contexts.auth.domain`. See [Named Capture](#named-capture) for details.

## Configuration

### Include / Exclude

Control which files are scanned using `include` and `exclude`:

```yaml
include:
  - src
exclude:
  - src/generated/**

rules:
  - name: ...
```

- **No `include` or `exclude`** — All `.py` files under the project root are scanned
- **`include` only** — Only files matching the given paths are scanned
- **`exclude` only** — All files except those matching the given paths are scanned
- **Both** — `include` is applied first, then `exclude` filters within that result

Bare directory names (e.g., `src`) and trailing-slash forms (e.g., `src/`) are treated the same as `src/**`.

In `pyproject.toml`:

```toml
[tool.python-dependency-linter]
include = ["src"]
exclude = ["src/generated/**"]
```

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

### Named Capture

`{name}` captures a single level (like `*`) and allows back-referencing the captured value in `allow` and `deny`:

```yaml
rules:
  - name: domain-isolation
    modules: contexts.{context}.domain
    allow:
      local: [contexts.{context}.domain, shared.domain]
```

When this rule matches `contexts.boards.domain`, `{context}` captures `"boards"`. The `allow` pattern `contexts.{context}.domain` resolves to `contexts.boards.domain`, so only the same context's domain is allowed.

You can use multiple captures in a single rule:

```yaml
rules:
  - name: bounded-context-layers
    modules: contexts.{context}.{layer}
    allow:
      local:
        - contexts.{context}.{layer}
        - contexts.{context}.domain
        - shared
```

Named captures coexist with `*` and `**` wildcards. `{name}` always matches exactly one level.

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
# Check with auto-discovered config (searches upward from cwd)
pdl check

# Specify config file (project root = config file's parent directory)
pdl check --config path/to/config.yaml
```

Exit codes:

- `0` — No violations
- `1` — Violations found
- `2` — Config file not found

If no `--config` is given, the tool searches upward from the current directory for `.python-dependency-linter.yaml` or `pyproject.toml` (with `[tool.python-dependency-linter]`). The config file's parent directory is used as the project root. If no config file is found, the tool prints an error and exits with code `2`:

```
Error: Config file not found. Create .python-dependency-linter.yaml or configure [tool.python-dependency-linter] in pyproject.toml.
```

## Pre-commit

Add to `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/heumsi/python-dependency-linter
  rev: v0.1.0
  hooks:
    - id: python-dependency-linter
```

To pass custom options (e.g., a different config file):

```yaml
- repo: https://github.com/heumsi/python-dependency-linter
  rev: v0.1.0
  hooks:
    - id: python-dependency-linter
      args: [--config, custom-config.yaml]
```

## License

MIT
