# CLI

## `pdl check`

Run the linter against your project:

```bash
# Check with auto-discovered config (searches upward from cwd)
pdl check

# Specify config file (project root = config file's parent directory)
pdl check --config path/to/config.yaml
```

### Options

| Option | Description |
|--------|-------------|
| `--config` | Path to a config file. The config file's parent directory is used as the project root. |

### Config Auto-Discovery

If `--config` is not provided, `pdl check` searches upward from the current working directory for either:

- `.python-dependency-linter.yaml`
- `pyproject.toml` (with a `[tool.python-dependency-linter]` section)

The first matching file found is used, and its parent directory becomes the project root.

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | No violations found |
| `1` | One or more violations found |
| `2` | Config file not found |
