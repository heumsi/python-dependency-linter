# Named Capture Recipes

## Problem

You have multiple bounded contexts or feature modules and want to enforce that each module only depends on its own internals, without writing a separate rule for each module.

## Recipe 1: Isolate bounded contexts

Each context can only import from its own domain:

```yaml
rules:
  - name: context-boundary
    modules: contexts.{context}.{layer}
    allow:
      standard_library: ["*"]
      third_party: ["*"]
      local:
        - contexts.{context}
        - shared
```

This prevents `contexts.orders` from importing `contexts.users` internals. Cross-context communication must go through `shared`.

## Recipe 2: Layer enforcement within each context

Combine context isolation with layer direction:

```yaml
rules:
  - name: domain-isolation
    modules: contexts.{context}.domain
    allow:
      standard_library: ["*"]
      third_party: []
      local:
        - contexts.{context}.domain
        - shared.domain

  - name: application-layer
    modules: contexts.{context}.application
    allow:
      standard_library: ["*"]
      third_party: ["*"]
      local:
        - contexts.{context}.application
        - contexts.{context}.domain
        - shared
```

## Recipe 3: Feature-scoped modules

For a flat feature structure like `features.{feature}.api`, `features.{feature}.service`, `features.{feature}.repo`:

```yaml
rules:
  - name: feature-boundary
    modules: features.{feature}
    allow:
      standard_library: ["*"]
      third_party: ["*"]
      local:
        - features.{feature}
        - core
```

Each feature is isolated — `features.billing` cannot import from `features.auth`.

## Result

With Recipe 1, if `contexts.orders.service` imports `contexts.users.models`:

```
contexts/orders/service.py:2
    [context-boundary] contexts.orders.service → contexts.users.models (local)

Found 1 violation(s).
```
