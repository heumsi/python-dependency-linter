# Clean Architecture

## Purpose

You follow Clean Architecture with concentric layers: `entities → use_cases → interface_adapters → frameworks`. Inner layers must not depend on outer layers.

## Configuration

```yaml
rules:
  - name: entities-isolation
    modules: my_app.entities
    description: Entities are pure domain objects with no external dependencies
    allow:
      standard_library: [dataclasses, typing, abc, enum]
      third_party: []
      local: [my_app.entities]

  - name: use-cases
    modules: my_app.use_cases
    description: Use cases depend only on entities, not on adapters or frameworks
    allow:
      standard_library: ["*"]
      third_party: []
      local:
        - my_app.use_cases
        - my_app.entities

  - name: interface-adapters
    modules: my_app.interface_adapters
    description: Adapters bridge use cases and frameworks
    allow:
      standard_library: ["*"]
      third_party: [pydantic, sqlalchemy]
      local:
        - my_app.interface_adapters
        - my_app.use_cases
        - my_app.entities

  - name: frameworks
    modules: my_app.frameworks
    description: Frameworks layer can depend on all inner layers
    allow:
      standard_library: ["*"]
      third_party: ["*"]
      local:
        - my_app.frameworks
        - my_app.interface_adapters
        - my_app.use_cases
        - my_app.entities
```

## Result

If `my_app.entities.user` imports `pydantic`:

```
my_app/entities/user.py:1
    [entities-isolation] Entities are pure domain objects with no external dependencies
    my_app.entities.user → pydantic (third_party)

Found 1 violation(s).
```

If `my_app.use_cases.create_user` imports from `my_app.interface_adapters`:

```
my_app/use_cases/create_user.py:3
    [use-cases] Use cases depend only on entities, not on adapters or frameworks
    my_app.use_cases.create_user → my_app.interface_adapters.repo (local)

Found 1 violation(s).
```
