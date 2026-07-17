---
name: release
description: Create a new release by calculating the next version from conventional commits, updating the changelog, and pushing a git tag
---

Create a new release following the project's release process defined in [CONTRIBUTING.md](../../../CONTRIBUTING.md).

The release workflow is defined in [.github/workflows/publish.yaml](../../../.github/workflows/publish.yaml).

## Steps

1. Read `CONTRIBUTING.md` to check the release process.
2. Follow the steps described in the Release section.
3. Ask the user to confirm the version before writing the changelog, since the version is
   baked into it. Do not tag or push anything before that confirmation.
