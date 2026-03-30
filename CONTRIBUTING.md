# Contributing

## Commit Convention

Commit messages must follow [Conventional Commits](https://www.conventionalcommits.org/) with [gitmoji](https://gitmoji.dev/) prefix.

### Format

```
<gitmoji> <type>: <description>
```

- The first letter after the colon must be **capitalized**.
- The description must be in **English**.

### Types

| Gitmoji | Type       | Description              |
|---------|------------|--------------------------|
| ✨      | `feat`     | New feature              |
| 🐛      | `fix`      | Bug fix                  |
| ♻️      | `refactor` | Code refactoring         |
| 📝      | `docs`     | Documentation            |
| ✅      | `test`     | Adding or updating tests |
| 🔧      | `chore`    | Maintenance tasks        |
| 👷      | `ci`       | CI/CD changes            |
| ⚡      | `perf`     | Performance improvement  |

### Examples

```
✨ feat: Add support for relative imports
🐛 fix: Use exit code 2 for config file not found
♻️ refactor: Simplify module resolver logic
```

## Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) with [ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

All commits must pass the pre-commit hooks before being accepted.
