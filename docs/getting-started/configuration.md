# Configuration

python-dependency-linter supports two config formats: YAML and TOML.

## YAML

Create `.python-dependency-linter.yaml` in your project root:

```yaml
rules:
  - name: domain-isolation
    modules: contexts.*.domain
    allow:
      standard_library: [dataclasses, typing]
      third_party: [pydantic]
      local: [contexts.*.domain]
```

## TOML (pyproject.toml)

```toml
[[tool.python-dependency-linter.rules]]
name = "domain-isolation"
modules = "contexts.*.domain"

[tool.python-dependency-linter.rules.allow]
standard_library = ["dataclasses", "typing"]
third_party = ["pydantic"]
local = ["contexts.*.domain"]
```

## Config Discovery

If no `--config` is given, the tool searches upward from the current directory for:

1. `.python-dependency-linter.yaml`
2. `pyproject.toml` (with `[tool.python-dependency-linter]` section)

The config file's parent directory is used as the project root.

If no config file is found, the tool exits with code `2`:

```
Error: Config file not found. Create .python-dependency-linter.yaml or configure [tool.python-dependency-linter] in pyproject.toml.
```

## Include / Exclude

Control which files are scanned:

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
