# Clean Architecture

## Purpose

You follow Clean Architecture with concentric layers: `entities → use_cases → interface_adapters → frameworks`. Inner layers must not depend on outer layers.

## Configuration

```yaml
rules:
  - name: entities-isolation
    modules: my_app.entities
    allow:
      standard_library: [dataclasses, typing, abc, enum]
      third_party: []
      local: [my_app.entities]

  - name: use-cases
    modules: my_app.use_cases
    allow:
      standard_library: ["*"]
      third_party: []
      local:
        - my_app.use_cases
        - my_app.entities

  - name: interface-adapters
    modules: my_app.interface_adapters
    allow:
      standard_library: ["*"]
      third_party: [pydantic, sqlalchemy]
      local:
        - my_app.interface_adapters
        - my_app.use_cases
        - my_app.entities

  - name: frameworks
    modules: my_app.frameworks
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
    [entities-isolation] my_app.entities.user → pydantic (third_party)

Found 1 violation(s).
```

If `my_app.use_cases.create_user` imports from `my_app.interface_adapters`:

```
my_app/use_cases/create_user.py:3
    [use-cases] my_app.use_cases.create_user → my_app.interface_adapters.repo (local)

Found 1 violation(s).
```
