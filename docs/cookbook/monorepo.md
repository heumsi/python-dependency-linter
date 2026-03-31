# Monorepo

## Purpose

Your project has multiple packages in a monorepo and you want to lint each package's dependencies separately, or enforce boundaries between packages.

## Configuration

### Per-package config

Each package has its own `.python-dependency-linter.yaml`:

```text
monorepo/
├── packages/
│   ├── auth/
│   │   ├── .python-dependency-linter.yaml
│   │   └── auth/
│   ├── billing/
│   │   ├── .python-dependency-linter.yaml
│   │   └── billing/
```

Run per package:

```bash
cd packages/auth && pdl check
cd packages/billing && pdl check
```

### Shared config with include

Use a single config at the repo root with `include` to scope each rule:

```yaml
include:
  - packages

rules:
  - name: auth-isolation
    modules: auth
    description: Auth package can only depend on itself and shared
    allow:
      standard_library: ["*"]
      third_party: ["*"]
      local: [auth, shared]

  - name: billing-isolation
    modules: billing
    description: Billing package can only depend on itself and shared
    allow:
      standard_library: ["*"]
      third_party: ["*"]
      local: [billing, shared]
```

## Result

If `billing.service` imports `auth.models`:

```text
packages/billing/billing/service.py:1
    [billing-isolation] Billing package can only depend on itself and shared
    billing.service → auth.models (local)

Found 1 violation(s).
```
