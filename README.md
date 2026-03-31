# python-dependency-linter

A dependency linter for Python projects. Define rules for which modules can depend on what, and catch violations.

## Installation

```bash
pip install python-dependency-linter
```

Or with uv:

```bash
uv add python-dependency-linter
```

## Quick Start

Create `.python-dependency-linter.yaml` in your project root:

```yaml
rules:
  - name: domain-isolation
    modules: contexts.*.domain
    allow:
      standard_library: [dataclasses, typing]
      third_party: [pydantic]
      local: [contexts.*.domain]
```

Run:

```bash
pdl check
```

## Documentation

For full documentation, visit [heumsi.github.io/python-dependency-linter](https://heumsi.github.io/python-dependency-linter/).

## License

MIT
