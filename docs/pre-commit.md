# Pre-commit

`pdl` can be used as a [pre-commit](https://pre-commit.com/) hook to enforce dependency rules before every commit.

## Setup

Add the following to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/heumsi/python-dependency-linter
  rev: ''  # Use the tag you want to point at (e.g., v0.5.0)
  hooks:
    - id: python-dependency-linter
```

## Custom Options

To pass custom options (e.g., a specific config file path), use `args`:

```yaml
- repo: https://github.com/heumsi/python-dependency-linter
  rev: ''
  hooks:
    - id: python-dependency-linter
      args: [--config, custom-config.yaml]
```
