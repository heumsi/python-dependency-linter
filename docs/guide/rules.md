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
