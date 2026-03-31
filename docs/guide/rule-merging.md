# Rule Merging

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
