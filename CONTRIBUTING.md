# Contributing to commitlint-local

Thank you for your interest in contributing to commitlint-local! This document
provides guidelines for submitting issues and pull requests.

## Getting Started

1. Fork the repository on GitHub.
2. Clone your fork locally: `git clone https://github.com/<your-username>/commitlint-local.git`
3. Create a virtual environment and install the package in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
```

## Running Tests

```bash
python3 -m pytest tests -q
```

All pull requests should pass the existing test suite. Please add tests for new
behavior or bug fixes.

## Code Style

- Follow PEP 8 for Python code.
- Use type annotations for public functions.
- Keep commit messages conventional: `type(scope): description`.

## Submitting Changes

1. Create a feature branch from `main`.
2. Make your changes and ensure tests pass.
3. Open a pull request describing the motivation and what the change does.

## Reporting Issues

- Include the commit message that triggered the failure.
- Share your `.commitlintrc` configuration if relevant.
- Note the Python version and operating system.
