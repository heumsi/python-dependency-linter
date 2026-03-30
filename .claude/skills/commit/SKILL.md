---
name: commit
description: Create a git commit following the project's commit convention
---

Create a git commit following the project's commit convention defined in [CONTRIBUTING.md](../../../CONTRIBUTING.md).

## Steps

1. Read `CONTRIBUTING.md` to check the commit convention.
2. Run `git status` and `git diff` to review all changes.
3. Draft a commit message following the convention.
4. Stage only relevant files (do NOT use `git add -A`). Exclude secrets and unrelated files.
5. Commit using a HEREDOC for proper formatting:
   ```bash
   git commit -m "$(cat <<'EOF'
   <commit message here>

   Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
   EOF
   )"
   ```
6. Run `git status` to verify success.
7. If pre-commit hook fails, fix the issue and create a **new** commit (never amend).
