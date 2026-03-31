# Inline Ignore

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
