# Gradual Adoption

## Purpose

You want to introduce dependency linting to an existing project without fixing all violations at once.

## Strategy 1: Start with deny rules

Instead of a strict allowlist, start by denying only the most problematic dependencies:

```yaml
rules:
  - name: no-orm-in-domain
    modules: my_app.domain
    description: Domain must not use ORM frameworks directly
    deny:
      third_party: [sqlalchemy, django]
```

This catches new violations without flagging existing ones that don't match the deny list.

## Strategy 2: Scope with include

Lint only new or well-structured parts of your codebase:

```yaml
include:
  - my_app/new_module

rules:
  - name: new-module-rules
    modules: my_app.new_module
    description: New module follows strict dependency rules
    allow:
      standard_library: ["*"]
      third_party: [pydantic]
      local: [my_app.new_module, my_app.shared]
```

Expand the `include` list as you clean up more modules.

## Strategy 3: Use inline ignore for known violations

Add `# pdl: ignore` to existing violations you plan to fix later, so the linter passes in CI:

```python
import sqlalchemy  # pdl: ignore[no-orm-in-domain]
```

Then remove the ignore comments as you refactor.

## Strategy 4: One rule at a time

Start with the most important boundary (usually domain isolation) and add rules incrementally:

```yaml
# Week 1: Just domain isolation
rules:
  - name: domain-isolation
    modules: my_app.domain
    description: Domain has no outward dependencies
    allow:
      standard_library: ["*"]
      third_party: []
      local: [my_app.domain]
```

```yaml
# Week 2: Add application layer
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
    description: Application depends on domain only
    allow:
      standard_library: ["*"]
      third_party: [pydantic]
      local: [my_app.application, my_app.domain]
```

## Result

With Strategy 1, only the specific denied imports are flagged:

```
my_app/domain/repo.py:1
    [no-orm-in-domain] Domain must not use ORM frameworks directly
    my_app.domain.repo → sqlalchemy (third_party)

Found 1 violation(s).
```

Other third-party imports in domain are still allowed until you switch to a stricter allowlist.
