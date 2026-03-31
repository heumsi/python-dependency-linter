# CLI

## Usage

```bash
# Check with auto-discovered config (searches upward from cwd)
pdl check

# Specify config file (project root = config file's parent directory)
pdl check --config path/to/config.yaml
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0`  | No violations |
| `1`  | Violations found |
| `2`  | Config file not found |

## Config Discovery

If no `--config` is given, the tool searches upward from the current directory for `.python-dependency-linter.yaml` or `pyproject.toml` (with `[tool.python-dependency-linter]`). The config file's parent directory is used as the project root.

If no config file is found:

```
Error: Config file not found. Create .python-dependency-linter.yaml or configure [tool.python-dependency-linter] in pyproject.toml.
```
