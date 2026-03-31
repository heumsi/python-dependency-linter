# Hexagonal Architecture

## Problem

You want to isolate domain from infrastructure. Ports (interfaces) live in domain, adapters depend on domain but not vice versa. Each bounded context should only depend on its own domain.

## Configuration

Using [named captures](../guide/patterns.md#named-capture), you can enforce that each bounded context only depends on its own domain:

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

## Result

With `{context}`, `contexts.boards.domain` can only import from `contexts.boards.domain` and `shared.domain` — not from `contexts.auth.domain`:

```
contexts/boards/domain/service.py:2
    [domain-no-infra] contexts.boards.domain.service → contexts.auth.domain.models (local)

Found 1 violation(s).
```
