# python-dependency-linter

A dependency linter for Python projects. Define rules for which modules can depend on what, and catch violations.

## What It Does

- Define dependency rules between modules using a simple YAML or TOML config
- Detect imports that violate your rules with a single CLI command
- Integrate into CI or pre-commit to keep your architecture consistent

For Python developers who care about module boundaries and dependency direction — whether you're applying Layered, Hexagonal, Clean Architecture, or your own conventions.

## Quick Example

```yaml
rules:
  - name: domain-isolation
    modules: contexts.*.domain
    allow:
      standard_library: [dataclasses, typing]
      third_party: [pydantic]
      local: [contexts.*.domain]
```

```bash
$ pdl check
contexts/boards/domain/models.py:6
    [domain-isolation] contexts.boards.domain.models → contexts.boards.application.service (local)

Found 1 violation(s).
```

## Next Steps

- [Installation](getting-started/installation.md) — Install the package
- [Quick Start](getting-started/quick-start.md) — Set up your first config and run the linter
- [Cookbook](cookbook/layered-architecture.md) — See examples for common architecture patterns
