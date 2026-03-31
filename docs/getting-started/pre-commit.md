# Pre-commit

Add to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/heumsi/python-dependency-linter
  rev: ''  # Use the tag you want to point at (e.g., v0.5.0)
  hooks:
    - id: python-dependency-linter
```

To pass custom options (e.g., a different config file):

```yaml
- repo: https://github.com/heumsi/python-dependency-linter
  rev: ''
  hooks:
    - id: python-dependency-linter
      args: [--config, custom-config.yaml]
```
