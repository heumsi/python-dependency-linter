# Configuration

`pdl` supports two config file formats: a standalone YAML file or an inline section inside `pyproject.toml`.

## Config File Discovery

When you run `pdl check` without `--config`, the tool searches **upward from the current working directory** for one of:

- `.python-dependency-linter.yaml`
- `pyproject.toml` (containing a `[tool.python-dependency-linter]` section)

The first matching file is used, and its parent directory becomes the project root.

To use a specific config file, pass it explicitly:

```bash
pdl check --config path/to/config.yaml
```

## YAML Format

Create `.python-dependency-linter.yaml` in your project root:

```yaml
rules:
  - name: domain-isolation
    modules: contexts.*.domain
    description: Domain layer must not depend on external services
    allow:
      standard_library: [dataclasses, typing]
      third_party: [pydantic]
      local: [contexts.*.domain]
```

## pyproject.toml Format

You can embed the same configuration inside `pyproject.toml` using the `[tool.python-dependency-linter]` namespace:

```toml
[[tool.python-dependency-linter.rules]]
name = "domain-isolation"
modules = "contexts.*.domain"
description = "Domain layer must not depend on external services"

[tool.python-dependency-linter.rules.allow]
standard_library = ["dataclasses", "typing"]
third_party = ["pydantic"]
local = ["contexts.*.domain"]
```

Both formats are equivalent — use whichever fits your project's conventions.

## Top-Level Keys

| Key | Description |
|-----|-------------|
| `rules` | List of dependency rule definitions |
| `include` | Paths to include when scanning (optional) |
| `exclude` | Paths to exclude when scanning (optional) |

### include / exclude

Control which files are scanned:

```yaml
include:
  - src
exclude:
  - src/generated/**
```

Behavior:

- **Neither** — all `.py` files under the project root are scanned.
- **`include` only** — only files matching the given paths are scanned.
- **`exclude` only** — all files except those matching the given paths are scanned.
- **Both** — `include` is applied first, then `exclude` filters within that result.

Bare directory names (e.g., `src`) and trailing-slash forms (e.g., `src/`) are treated the same as `src/**`.

In `pyproject.toml`:

```toml
[tool.python-dependency-linter]
include = ["src"]
exclude = ["src/generated/**"]
```
