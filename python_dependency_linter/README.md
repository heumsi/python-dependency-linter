# Internal Architecture

This is the developer-facing map of the `pdl` source tree. For installation and
usage, see the [project README](../README.md) and the
[documentation](https://heumsi.github.io/python-dependency-linter/).

`pdl` is organized into explicit dependency layers, and it lints its own layering
with [`.python-dependency-linter.yaml`](../.python-dependency-linter.yaml) — so the
rules below are enforced in CI and pre-commit, not just documented here.

## Layers

```text
cli.py        entry point — orchestrates a `pdl check` run        (may use all)
  │
  ▼
io/           reporter                                            (→ domain, core)
  │
  ▼
domain/       checker                                             (→ core)
  │
  ▼
core/         config, parser, resolver, matcher                   (→ core only)
```

Intra-project dependencies only point **downward**:

| Layer | Module(s) | May depend on |
|-------|-----------|---------------|
| `cli` | `cli.py` | everything |
| `io` | `reporter` | `domain`, `core` |
| `domain` | `checker` | `core` |
| `core` | `config`, `parser`, `resolver`, `matcher` | `core` only |

Within `core` the only internal edge is `matcher → config`; `config`, `parser`,
and `resolver` have no intra-project dependencies. The self-lint config also keeps
third-party packages out of the inner layers — e.g. `click` lives only in `cli`,
and `domain`/`io` pull in no third-party packages at all.

## Modules

| Module | Layer | Responsibility |
|--------|-------|----------------|
| `cli` | cli | CLI entry point (`pdl check`); discovers files and drives the pipeline |
| `config` | core | Loads YAML / `pyproject.toml` config; defines `Config`, `Rule`, `AllowDeny` |
| `parser` | core | Extracts imports via AST; resolves relative imports; parses `# pdl: ignore` |
| `resolver` | core | Classifies an import as `standard_library`, `third_party`, or `local` |
| `matcher` | core | Matches modules against rule patterns (`*`, `**`, `{name}`); merges rules |
| `checker` | domain | Applies `allow` / `deny` to produce a `Violation` |
| `reporter` | io | Formats violations for terminal output |

## How a `check` run flows

```text
config.load_config          read rules + include / exclude
        │
   discover *.py             cli._find_python_files
        │
   for each file:
        ├─ matcher.find_matching_rules / merge_rules    which rules apply
        ├─ parser.parse_imports                         imports + ignore hints
        └─ for each import:
               ├─ resolver.resolve_import   → stdlib / third_party / local
               └─ checker.check_import      → Violation | None
        │
   reporter.format_violations               print results; exit 1 if any
```
