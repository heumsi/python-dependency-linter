# Quick Start

Get `pdl` running in your project in three steps.

## Step 1: Create a Config File

Create `.python-dependency-linter.yaml` in your project root and define your dependency rules:

```yaml
rules:
  - name: domain-isolation
    modules: contexts.*.domain
    description: Domain layer must not depend on application or infrastructure
    allow:
      standard_library: [dataclasses, typing]
      third_party: [pydantic]
      local: [contexts.*.domain]

  - name: application-dependency
    modules: contexts.*.application
    description: Application layer can depend on domain but not on infrastructure
    allow:
      standard_library: ["*"]
      third_party: [pydantic]
      local:
        - contexts.*.application
        - contexts.*.domain
```

This config defines two rules:

- `domain-isolation` — modules under `contexts.*.domain` can only import `dataclasses`, `typing`, `pydantic`, and other domain modules.
- `application-dependency` — modules under `contexts.*.application` can import any standard library, `pydantic`, and application or domain modules.

You can also use `pyproject.toml`. See [Configuration](./configuration.md) for details.

## Step 2: Run the Linter

From your project root, run:

```bash
pdl check
```

`pdl` automatically discovers the config file by searching upward from the current working directory.

## Step 3: Review the Output

Violations are reported with the file path, line number, rule name, and the dependency direction:

```
contexts/boards/domain/models.py:6
    [domain-isolation] Domain layer must not depend on application or infrastructure
    contexts.boards.domain.models → contexts.boards.application.service (local)

contexts/boards/domain/models.py:9
    [domain-isolation] Domain layer must not depend on application or infrastructure
    contexts.boards.domain.models → sqlalchemy (third_party)

Found 2 violation(s).
```

Fix the reported imports and re-run `pdl check` until no violations remain.

## Next Steps

- Learn all available config options in [Configuration](./configuration.md).
- See rule details and pattern options in the [Guide](../guide/rules.md).
