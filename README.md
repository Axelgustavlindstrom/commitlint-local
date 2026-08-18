# commitlint-local

A lightweight, repo-local commit message linter for Git. Enforce Conventional Commits rules for one repository without affecting others, with configurable scopes and quick CI feedback.

Repository: https://github.com/Axelgustavlindstrom/commitlint-local

## About / description
`commitlint-local` inspects staged commit messages from a local repo and applies Conventional Commits heuristics. It ships as a Python CLI and a pre-commit hook. Unlike broad tooling, it targets one repository, reads a local `.commitlintrc`, and prints actionable fixes.

## Features
- Enforce Conventional Commits: `<type>[optional scope]: <description>`
- Configured via `.commitlintrc` in the repo root
- Pre-commit hook installer: `.git/hooks/commit-msg`
- Quiet mode and verbose mode for CI or interactive use
- Exits non-zero for invalid commits without blocking valid ones
- Repo-local: configuration is discovered from the repo being committed into

## Installation
```bash
python3 -m pip install .
```

## Usage
```bash
commitlint validate "feat(repo): add help output"
commitlint validate --config .commitlintrc_ci "fix: edge case"
commitlint install-hook
```

## Project structure
```
commitlint-local/
├── README.md
├── pyproject.toml
├── .gitignore
├── LICENSE
├── commitlint_local/
│   ├── __init__.py
│   ├── __main__.py
│   └── cli.py
└── tests/
    └── test_cli.py
```

## Tags / keywords
commitlint, conventional commits, git hook, local, ci, cli
