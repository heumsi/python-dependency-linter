# Layered Architecture

## Purpose

You have a layered architecture (`presentation → application → domain`) and want to enforce that dependencies only flow downward. The `domain` layer should have no outward dependencies.

## Configuration

```yaml
rules:
  - name: domain-isolation
    modules: my_app.domain
    description: Domain has no outward dependencies
    allow:
      standard_library: ["*"]
      third_party: []
      local: [my_app.domain]

  - name: application-layer
    modules: my_app.application
    description: Application depends on domain only, not on presentation
    allow:
      standard_library: ["*"]
      third_party: [pydantic]
      local:
        - my_app.application
        - my_app.domain

  - name: presentation-layer
    modules: my_app.presentation
    description: Presentation can depend on application and domain
    allow:
      standard_library: ["*"]
      third_party: [fastapi, pydantic]
      local:
        - my_app.presentation
        - my_app.application
        - my_app.domain
```

## Result

If `my_app.domain.models` imports `sqlalchemy`:

```text
my_app/domain/models.py:3
    [domain-isolation] Domain has no outward dependencies
    my_app.domain.models → sqlalchemy (third_party)

Found 1 violation(s).
```

If `my_app.application.service` imports `fastapi`:

```text
my_app/application/service.py:1
    [application-layer] Application depends on domain only, not on presentation
    my_app.application.service → fastapi (third_party)

Found 1 violation(s).
```
