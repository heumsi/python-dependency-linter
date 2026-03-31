# Changelog

All notable changes to this project will be documented in this file.

## [0.7.1] - 2026-03-31

### Bug Fixes

- Allow dot (.) in rule names (#28)

### Documentation

- Add description field example to README quick start
## [0.7.0] - 2026-03-31

### Documentation

- Add documentation site with mkdocs-shadcn (#23)
- Add manual docs deployment workflow
- Add description examples to all rule configs (#25)
- Remove redundant Next Steps section from docs landing page

### Features

- Add optional description field to rules (#24)
## [0.6.0] - 2026-03-31

### CI/CD

- Add ty type checker to dev toolchain

### Documentation

- Update pre-commit description in CONTRIBUTING.md

### Features

- Add rule name validation (#21)
- Add inline ignore comment support (#22)

### Miscellaneous

- Rename pre-commit hook ids and names for clarity
## [0.5.1] - 2026-03-30

### Bug Fixes

- Match submodules in modules pattern consistent with allow/deny (#19)

### Documentation

- Replace hardcoded pre-commit rev with placeholder
- Update submodule matching section to include modules pattern
## [0.5.0] - 2026-03-30

### Features

- Add named capture in module patterns for back-referencing in allow/deny (#17)
## [0.4.0] - 2026-03-30

### Bug Fixes

- Use fnmatch for include/exclude pattern matching (#15)

### Features

- Remove --project-root, auto-detect from config file location (#14)
## [0.3.0] - 2026-03-30

### Bug Fixes

- Use exit code 2 for config file not found (#11)

### Documentation

- Add CONTRIBUTING.md and CLAUDE.md
- Add PR title convention to template and CONTRIBUTING.md
- Add release process to CONTRIBUTING.md and /release skill

### Features

- Resolve relative imports to absolute module names (#10)
- Add include/exclude file filtering options (#12)

### Miscellaneous

- Add /commit skill for Claude Code
- Add uv.lock for reproducible builds
## [0.2.0] - 2026-03-30

### Documentation

- Remove design spec and implementation plan docs
- Add GitHub issue and PR templates
- Add example for omitted category behavior in allow rules
- Add architecture examples to README
- Add pre-commit hook custom options example
- Expand pyproject.toml examples with multiple rules and deny
- Add "What It Does" section to README

### Features

- Support `**` glob pattern for matching nested submodules (#6)
- Add undocumented features to README

### Miscellaneous

- Use hatch-vcs for dynamic versioning from git tags
- Add gitmoji preprocessor to git-cliff config
- Move git-cliff config from cliff.toml to pyproject.toml
- Skip CHANGELOG update commits in git-cliff output

### Testing

- Limit CI to source and test file changes

### Build

- Bump actions/checkout from 4 to 6 (#3)
- Bump actions/setup-python from 5 to 6 (#2)
## [0.1.0] - 2026-03-30

### Bug Fixes

- Add isort config and fix plan typo
- Add tomli fallback for Python 3.10 compatibility
- Add import content to fixture files

### CI/CD

- Add GitHub Actions for CI, PyPI publish, and Dependabot
- Add git-cliff changelog generation on release
- Add GitHub Release creation on tag

### Documentation

- Add design spec for python-dependency-linter
- Add implementation plan
- Add README
- Add MIT LICENSE

### Features

- Add config loading for YAML and pyproject.toml
- Add AST-based import parser
- Add import resolver for classification
- Add wildcard matcher and rule merging
- Add dependency checker with allow/deny logic
- Add violation reporter
- Add CLI with check command
- Add pre-commit hook definition

### Miscellaneous

- Initialize project scaffolding
- Add license, readme, and classifiers to pyproject.toml
- Add .gitignore
