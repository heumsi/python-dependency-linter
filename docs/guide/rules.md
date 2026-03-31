# Rules

Rules are the core building blocks of `pdl`. Each rule targets a set of modules and enforces which dependencies are allowed or denied.

## Structure

Every rule has two required fields and two optional ones:

```yaml
rules:
  - name: my-rule                          # Unique identifier for this rule
    modules: my_app.domain                 # Which modules this rule applies to
    description: Keep domain layer pure    # (optional) Human-readable description
    allow: { ... }                         # (optional) Whitelist of allowed dependencies
    deny: { ... }                          # (optional) Blacklist of denied dependencies
```

The `name` is used in violation output and in `# pdl: ignore` comments. The optional `description` is also shown in violation output to explain why the rule exists.

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier. Must match `[a-zA-Z0-9_-]+`. Shown in violation output and referenced in `# pdl: ignore` comments |
| `modules` | Yes | Module pattern to apply the rule to. Supports `*`, `**`, and `{name}` captures (see [Patterns](#patterns)) |
| `description` | No | Human-readable description shown in violation output |
| `allow` | No | Whitelist of allowed dependencies (see [Allow / Deny](#allow-deny)) |
| `deny` | No | Blacklist of denied dependencies (see [Allow / Deny](#allow-deny)) |

---

## Import Categories

Dependencies are classified into three categories (per PEP 8):

| Category | What it covers | Examples |
|----------|---------------|----------|
| `standard_library` | Python built-in modules | `os`, `sys`, `typing`, `dataclasses` |
| `third_party` | Installed packages | `pydantic`, `sqlalchemy`, `fastapi` |
| `local` | Modules in your project | `my_app.domain`, `contexts.boards` |

Both absolute imports (`from contexts.boards.domain import models`) and relative imports (`from ..domain import models`) are analyzed. Relative imports are resolved to absolute module names based on the file's location.

---

## Allow / Deny

Each category can be configured independently in the `allow` and `deny` blocks:

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

### Behavior Modes

| Mode | When | Effect |
|------|------|--------|
| No rule | Module has no matching rule | Everything is allowed |
| `allow` only | Only `allow` is set | Whitelist mode — only listed dependencies are allowed |
| `deny` only | Only `deny` is set | Blacklist mode — listed dependencies are denied, rest allowed |
| `allow` + `deny` | Both are set | Allow first, then deny removes exceptions |

**Example — allow only (whitelist mode):**

```yaml
rules:
  - name: domain-isolation
    modules: my_app.domain
    description: Domain layer must not depend on application or infrastructure
    allow:
      standard_library: [dataclasses, typing]
      third_party: [pydantic]
      local: [my_app.domain]
```

| Import in `my_app.domain` | Result |
|---------------------------|--------|
| `import dataclasses` | Pass — in allow list |
| `import typing` | Pass — in allow list |
| `import pydantic` | Pass — in allow list |
| `from my_app.domain import models` | Pass — in allow list |
| `import sqlalchemy` | **Violation** — not in allow list |
| `from my_app.application import service` | **Violation** — not in allow list |

**Example — deny only (blacklist mode):**

```yaml
rules:
  - name: no-orm-in-domain
    modules: my_app.domain
    description: Domain must not use ORM frameworks directly
    deny:
      third_party: [sqlalchemy, django]
```

| Import in `my_app.domain` | Result |
|---------------------------|--------|
| `import pydantic` | Pass — not in deny list |
| `import os` | Pass — not in deny list |
| `import sqlalchemy` | **Violation** — in deny list |
| `import django` | **Violation** — in deny list |

### Omitted Categories

If `allow` exists but a category is omitted, that category allows all:

```yaml
rules:
  - name: domain-isolation
    modules: contexts.*.domain
    allow:
      third_party: [pydantic]
      local: [contexts.*.domain]
      # standard_library is omitted → all standard library imports are allowed
```

| Import | Result |
|--------|--------|
| `import os` | Pass — `standard_library` omitted, so all allowed |
| `import typing` | Pass — `standard_library` omitted, so all allowed |
| `import pydantic` | Pass — in `third_party` allow list |
| `import sqlalchemy` | **Violation** — not in `third_party` allow list |

### Wildcard Allow

Use `"*"` to allow all within a category:

```yaml
allow:
  standard_library: ["*"]
  third_party: [pydantic]
  local: [my_app.domain]
```

| Import | Result |
|--------|--------|
| `import os` | Pass — `"*"` allows all standard library |
| `import collections` | Pass — `"*"` allows all standard library |
| `import pydantic` | Pass — in allow list |
| `import sqlalchemy` | **Violation** — not in `third_party` allow list |

---

## Patterns

### Wildcard

`*` matches exactly one level in dotted module paths:

```yaml
modules: contexts.*.domain
```

| Module | Match? |
|--------|--------|
| `contexts.boards.domain` | Yes — `*` matches `boards` |
| `contexts.auth.domain` | Yes — `*` matches `auth` |
| `contexts.domain` | No — nothing to match `*` |
| `contexts.boards.sub.domain` | No — `*` matches only one level |

`**` matches one or more levels in dotted module paths:

```yaml
modules: contexts.**.domain
```

| Module | Match? |
|--------|--------|
| `contexts.boards.domain` | Yes — `**` matches `boards` |
| `contexts.boards.sub.domain` | Yes — `**` matches `boards.sub` |
| `contexts.domain` | No — `**` requires at least one level |

---

### Named Capture

`{name}` captures a single level (like `*`) and allows back-referencing the captured value in `allow` and `deny`:

```yaml
rules:
  - name: domain-isolation
    modules: contexts.{context}.domain
    description: Each context's domain can only depend on its own domain and shared
    allow:
      local: [contexts.{context}.domain, shared.domain]
```

When this rule matches `contexts.boards.domain`, `{context}` captures `"boards"`. The `allow` pattern `contexts.{context}.domain` resolves to `contexts.boards.domain`, so only the same context's domain is allowed.

| Import in `contexts.boards.domain` | Result |
|------------------------------------|--------|
| `from contexts.boards.domain import models` | Pass — same context's domain |
| `from shared.domain import base` | Pass — in allow list |
| `from contexts.auth.domain import user` | **Violation** — different context's domain |

You can use multiple captures in a single rule:

```yaml
rules:
  - name: bounded-context-layers
    modules: contexts.{context}.{layer}
    description: Each layer can only depend on itself, its domain, and shared
    allow:
      local:
        - contexts.{context}.{layer}
        - contexts.{context}.domain
        - shared
```

Named captures coexist with `*` and `**` wildcards. `{name}` always matches exactly one level.

---

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

| Module | Matched by `contexts.*.domain`? |
|--------|-------------------------------|
| `contexts.boards.domain` | Yes — exact match |
| `contexts.boards.domain.models` | Yes — submodule of match |
| `contexts.boards.domain.entities.metric` | Yes — nested submodule of match |
| `contexts.boards.application` | No — different path |

> **Note:** `contexts.*.domain` matches the module itself (`__init__.py`) **and** all submodules beneath it, while `contexts.*.domain.**` matches submodules only.

---

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
      third_party: [attrs]
```

In this example, `contexts.boards.domain` matches both rules. The `allow.third_party` lists are merged:

| Import in `contexts.boards.domain` | Result |
|------------------------------------|--------|
| `import pydantic` | Pass — from `base` rule |
| `import attrs` | Pass — from `boards-extra` rule |
| `import sqlalchemy` | **Violation** — not in either rule |

| Import in `contexts.auth.domain` | Result |
|----------------------------------|--------|
| `import pydantic` | Pass — from `base` rule |
| `import attrs` | **Violation** — `boards-extra` doesn't match `auth` |

---

## Inline Ignore

Suppress violations on specific import lines using `# pdl: ignore` comments.

### Ignore All Rules on a Line

Add `# pdl: ignore` at the end of a line to suppress all `pdl` violations reported for that line:

```python
import boto3  # pdl: ignore
```

Any rule that would have flagged the import on this line is silenced.

### Ignore a Specific Rule on a Line

To suppress only one rule, specify the rule name in brackets:

```python
import boto3  # pdl: ignore[no-boto-in-domain]
```

Only the `no-boto-in-domain` rule is suppressed on this line. Any other rules that match this line will still report violations.

### Ignore Multiple Specific Rules on a Line

To suppress more than one rule on the same line, list rule names separated by commas:

```python
import boto3  # pdl: ignore[no-boto-in-domain, other-rule]
```

### Practical Examples

**Suppressing a legacy import that you plan to refactor later:**

```python
from contexts.auth.domain import user  # pdl: ignore[domain-isolation]
```

**Suppressing a necessary cross-context dependency:**

```python
from contexts.shared.utils import helper  # pdl: ignore
```

### Summary

| Topic | Detail |
|---|---|
| Scope | Comments apply only to the line they appear on; other lines are unaffected. |
| Case sensitivity | Rule names are case-sensitive and must match exactly. |
| Unknown rule names | If a rule name does not exist in your config, the comment is silently ignored — no error is raised. |
| Prefer targeted suppression | Use `# pdl: ignore[rule-name]` over `# pdl: ignore` so that future rules are not accidentally silenced. |

---

## Summary

### Rule fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier, shown in output and referenced in `# pdl: ignore` |
| `modules` | Yes | Module pattern to apply the rule to |
| `description` | No | Human-readable description shown in violation output |
| `allow` | No | Whitelist of allowed dependencies |
| `deny` | No | Blacklist of denied dependencies |

### Import categories

| Category | What it covers |
|----------|---------------|
| `standard_library` | Python built-in modules |
| `third_party` | Installed packages |
| `local` | Modules in your project |

### Behavior modes

| Mode | Effect |
|------|--------|
| No rule | Everything is allowed |
| `allow` only | Whitelist — only listed dependencies allowed |
| `deny` only | Blacklist — listed dependencies denied, rest allowed |
| `allow` + `deny` | Allow first, then deny removes exceptions |

### Pattern types

| Pattern | Matches | Example |
|---------|---------|---------|
| `*` | Exactly one level | `contexts.*.domain` matches `contexts.boards.domain` |
| `**` | One or more levels | `contexts.**.domain` matches `contexts.boards.sub.domain` |
| `{name}` | One level with back-reference | `contexts.{ctx}.domain` captures and reuses in allow/deny |
| `"*"` (in allow/deny) | All modules in a category | `standard_library: ["*"]` allows all stdlib imports |
