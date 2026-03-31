# Config Schema

Complete reference for all configuration fields.

## Top-level Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `rules` | list of [Rule](#rule) | Yes | — | List of dependency rules |
| `include` | list of str | No | `null` (scan all) | File paths to include in scanning |
| `exclude` | list of str | No | `null` (no exclusions) | File paths to exclude from scanning |

## Rule

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | str | Yes | — | Rule identifier, shown in violation output. Must match `[a-zA-Z0-9_.-]+` |
| `modules` | str | Yes | — | Module pattern to apply the rule to. Supports `*`, `**`, and `{name}` captures |
| `description` | str | No | `null` | Human-readable description shown in violation output |
| `allow` | [DependencyFilter](#dependencyfilter) | No | `null` | Whitelist of allowed dependencies |
| `deny` | [DependencyFilter](#dependencyfilter) | No | `null` | Blacklist of denied dependencies |

## DependencyFilter

Used in both `allow` and `deny` fields.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `standard_library` | list of str | `null` (allow all if in `allow`, deny none if in `deny`) | Standard library module patterns |
| `third_party` | list of str | `null` (allow all if in `allow`, deny none if in `deny`) | Third-party package patterns |
| `local` | list of str | `null` (allow all if in `allow`, deny none if in `deny`) | Local module patterns |

Each list entry can be:
- An exact module name: `pydantic`
- A wildcard pattern: `contexts.*.domain`
- A named capture reference: `contexts.{context}.domain`
- `"*"` to match all modules in the category
