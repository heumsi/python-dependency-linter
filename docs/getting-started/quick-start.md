# Quick Start

## 1. Create a config file

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

You can also use `pyproject.toml`. See [Configuration](./configuration.md) for details.

## 2. Run the linter

```bash
pdl check
```

## 3. Review violations

```
contexts/boards/domain/models.py:6
    [domain-isolation] contexts.boards.domain.models → contexts.boards.application.service (local)

contexts/boards/domain/models.py:9
    [domain-isolation] contexts.boards.domain.models → sqlalchemy (third_party)

Found 2 violation(s).
```

Exit codes:

- `0` — No violations
- `1` — Violations found
- `2` — Config file not found
