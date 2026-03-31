# Rules

## Rule Structure

Each rule has:

- `name` — Rule identifier, shown in violation output
- `modules` — Module pattern to apply the rule to (supports `*` wildcard)
- `allow` — Whitelist: only listed dependencies are allowed
- `deny` — Blacklist: listed dependencies are denied

```yaml
rules:
  - name: rule-name
    modules: my_package.*.domain
    allow:
      standard_library: [dataclasses]
      third_party: [pydantic]
      local: [my_package.*.domain]
    deny:
      third_party: [boto3]
```

## Import Categories

Dependencies are classified into three categories (per PEP 8):

- `standard_library` — Python built-in modules (`os`, `sys`, `typing`, ...)
- `third_party` — Installed packages (`pydantic`, `sqlalchemy`, ...)
- `local` — Modules in your project

Both absolute imports (`from contexts.boards.domain import models`) and relative imports (`from ..domain import models`) are analyzed. Relative imports are resolved to absolute module names based on the file's location.

## Behavior

- **No rule** — Everything is allowed
- **`allow` only** — Whitelist mode. Only listed dependencies are allowed
- **`deny` only** — Blacklist mode. Listed dependencies are denied, rest allowed
- **`allow` + `deny`** — Allow first, then deny removes exceptions
- If `allow` exists but a category is omitted, that category allows all. For example:

```yaml
rules:
  - name: domain-isolation
    modules: contexts.*.domain
    allow:
      third_party: [pydantic]
      local: [contexts.*.domain]
      # standard_library is omitted → all standard library imports are allowed
```

Use `"*"` to allow all within a category:

```yaml
allow:
  standard_library: ["*"]  # allow all standard library imports
```

## Patterns

### Wildcard

`*` matches a single level in dotted module paths:

```yaml
modules: contexts.*.domain  # matches contexts.boards.domain, contexts.auth.domain, ...
```

`**` matches one or more levels in dotted module paths:

```yaml
modules: contexts.**.domain  # matches contexts.boards.domain, contexts.boards.sub.domain, ...
```

### Named Capture

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

### Submodule Matching

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

## Rule Merging

When multiple rules match a module, they are merged. Specific rules override wildcard rules per field:

```yaml
rules:
  - name: base
    modules: contexts.*.domain
    allow:
      third_party: [pydantic]

  - name: boards-extra
    modules: contexts.boards.domain
    allow:
      third_party: [attrs]  # merged: [pydantic, attrs]
```

In this example, `contexts.boards.domain` matches both rules. The `allow.third_party` lists are merged, so both `pydantic` and `attrs` are allowed.

## Inline Ignore

Suppress violations on specific import lines using `# pdl: ignore` comments:

```python
import boto3  # pdl: ignore
```

To suppress only specific rules, specify rule names in brackets:

```python
import boto3  # pdl: ignore[no-boto-in-domain]
```

Multiple rules can be listed with commas:

```python
import boto3  # pdl: ignore[no-boto-in-domain, other-rule]
```
