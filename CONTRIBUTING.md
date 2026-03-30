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

## Pull Request Convention

- PRs are always **squash merged**, so the PR title becomes the final commit message.
- PR titles must follow the same format as commit messages (`<gitmoji> <type>: <description>`).
- PR descriptions must be written in **English**.

## Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) with [ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

All commits must pass the pre-commit hooks before being accepted.

## Release

Releases are automated via GitHub Actions. You only need to create and push a version tag.

### Steps

1. Calculate the next version based on conventional commits:
   ```bash
   uvx git-cliff --bumped-version
   ```
2. Review the commits since the last tag:
   ```bash
   git log $(git describe --tags --abbrev=0)..HEAD --oneline
   ```
3. Push the latest commits to `main`:
   ```bash
   git push origin main
   ```
4. Create and push the tag:
   ```bash
   git tag <version>
   git push origin <version>
   ```

The GitHub Actions workflow will then automatically:
- Generate `CHANGELOG.md` and commit it to `main`
- Create a GitHub Release with release notes
- Publish the package to PyPI
