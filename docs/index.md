# python-dependency-linter

A dependency linter for Python projects. Define rules for which modules can depend on what, and catch violations.

## What It Does

- Define dependency rules between modules using a simple YAML or TOML config
- Detect imports that violate your rules with a single CLI command
- Integrate into CI or pre-commit to keep your architecture consistent

For Python developers who care about module boundaries and dependency direction — whether you're applying Layered, Hexagonal, Clean Architecture, or your own conventions.

## Key Features

| Feature | Description |
|---------|-------------|
| **Allow / Deny Rules** | Whitelist or blacklist dependencies per module |
| **Import Categories** | Separate rules for standard library, third-party, and local imports |
| **Wildcard Patterns** | Target modules with `*` and `**` glob-style patterns |
| **Named Captures** | Use `{name}` to enforce same-context boundaries without repeating rules |
| **Rule Merging** | Combine base rules with specific overrides |
| **Inline Ignore** | Suppress violations on specific lines with `# pdl: ignore` |
| **Pre-commit** | Drop-in integration with pre-commit hooks |

## Quick Start

**Install:**

```bash
pip install python-dependency-linter
```

**Create `.python-dependency-linter.yaml` in your project root:**

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

**Run:**

```bash
pdl check
```

**Output:**

```text
contexts/boards/domain/models.py:6
    [domain-isolation] contexts.boards.domain.models → contexts.boards.application.service (local)

contexts/boards/domain/models.py:9
    [domain-isolation] contexts.boards.domain.models → sqlalchemy (third_party)

Found 2 violation(s).
```

## More Examples

### Hexagonal Architecture — Bounded Context Isolation

Using named captures to enforce that each context only depends on its own domain:

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

This prevents `contexts.boards.domain` from importing `contexts.auth.domain`.

### Deny Rules — Block Specific Dependencies

Use deny rules to block specific dependencies without a full allowlist:

```yaml
rules:
  - name: no-orm-in-domain
    modules: my_app.domain
    deny:
      third_party: [sqlalchemy, django]
```

