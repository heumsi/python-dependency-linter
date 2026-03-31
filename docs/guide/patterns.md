# Patterns

## Wildcard

`*` matches a single level in dotted module paths:

```yaml
modules: contexts.*.domain  # matches contexts.boards.domain, contexts.auth.domain, ...
```

`**` matches one or more levels in dotted module paths:

```yaml
modules: contexts.**.domain  # matches contexts.boards.domain, contexts.boards.sub.domain, ...
```

## Named Capture

`{name}` captures a single level (like `*`) and allows back-referencing the captured value in `allow` and `deny`:

```yaml
rules:
  - name: domain-isolation
    modules: contexts.{context}.domain
    allow:
      local: [contexts.{context}.domain, shared.domain]
```

When this rule matches `contexts.boards.domain`, `{context}` captures `"boards"`. The `allow` pattern `contexts.{context}.domain` resolves to `contexts.boards.domain`, so only the same context's domain is allowed.

You can use multiple captures in a single rule:

```yaml
rules:
  - name: bounded-context-layers
    modules: contexts.{context}.{layer}
    allow:
      local:
        - contexts.{context}.{layer}
        - contexts.{context}.domain
        - shared
```

Named captures coexist with `*` and `**` wildcards. `{name}` always matches exactly one level.

## Submodule Matching

When a pattern is used in `modules`, `allow`, or `deny`, it also matches submodules of the matched module.

For example, the following rule applies to `contexts.boards.domain` as well as its submodules like `contexts.boards.domain.models` or `contexts.boards.domain.entities.metric`:

```yaml
rules:
  - name: domain-layer
    modules: contexts.*.domain
    allow:
      local: [contexts.*.domain]
```

> **Note:** `contexts.*.domain` matches the module itself (`__init__.py`) **and** all submodules beneath it, while `contexts.*.domain.**` matches submodules only.
