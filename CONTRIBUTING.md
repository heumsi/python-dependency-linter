# Contributing

## Commit Convention

Commit messages must follow [Conventional Commits](https://www.conventionalcommits.org/) with [gitmoji](https://gitmoji.dev/) prefix.

### Format

```text
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

```text
✨ feat: Add support for relative imports
🐛 fix: Use exit code 2 for config file not found
♻️ refactor: Simplify module resolver logic
```

## Pull Request Convention

- PRs are always **squash merged**, so the PR title becomes the final commit message.
- PR titles must follow the same format as commit messages (`<gitmoji> <type>: <description>`).
- PR descriptions must be written in **English**.

## Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) for linting, formatting, and type checking.

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

All commits must pass the pre-commit hooks before being accepted.

## Release

Update the changelog and tag the commit that contains it, then push both. The rest is
automated via GitHub Actions.

### Steps

1. Calculate the next version based on conventional commits:
   ```bash
   uvx git-cliff --bumped-version
   ```
2. Review the commits since the last tag:
   ```bash
   git log $(git describe --tags --abbrev=0)..HEAD --oneline
   ```
3. Update `CHANGELOG.md` for the new version:
   ```bash
   uvx git-cliff --tag <version> -o CHANGELOG.md
   ```
   Passing the version explicitly keeps the changelog, the commit message and the tag from
   drifting apart. `uvx git-cliff --bump -o CHANGELOG.md` works too, and picks the version
   itself.
4. Commit the changelog:
   ```bash
   git commit -m "📝 docs: Update CHANGELOG for <version>" CHANGELOG.md
   ```
5. Tag that commit:
   ```bash
   git tag <version>
   ```
6. Push the commit and the tag:
   ```bash
   git push origin main
   git push origin <version>
   ```

The GitHub Actions workflows will then automatically:
- Create a GitHub Release with release notes, and publish the package to PyPI (from the tag)
- Deploy the documentation site (from the `CHANGELOG.md` change on `main`)

The changelog is written before tagging on purpose. A workflow could generate it after the
tag instead, but it would have to commit the result back to `main`, and pushes made with the
built-in `GITHUB_TOKEN` do not trigger other workflows — so the docs site would never
redeploy. Writing it first keeps the tag, the changelog, and the docs in sync.
