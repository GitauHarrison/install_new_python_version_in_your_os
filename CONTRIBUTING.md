# Contributing to the Python Version & pyenv Helper

Thank you for your interest in improving this helper for installing and managing new Python versions with `pyenv` (and optionally `pyenv-virtualenv`).

This repository is focused on making it easier to:

- Install a new Python version alongside the system default.
- Configure `pyenv` and (optionally) `pyenv-virtualenv` correctly.
- Provide a repeatable, documented process for setting up Python on macOS/Linux.

## Scope of this repository

This repo is about:

- Scripts, configuration, and documentation that help set up Python via `pyenv` and related tools.
- Example commands and usage patterns for working with multiple Python versions and virtual environments.

It is **not** a general-purpose Python tutorial. Issues and PRs should be about the helper itself and the workflows it documents.

## Ways to contribute

- Report bugs or unclear steps in the installation or configuration process.
- Improve documentation (clarify wording, add missing steps, update examples for new OS versions or shells).
- Suggest safer defaults or more robust checks.
- Add small helper scripts that make `pyenv`/virtualenv workflows less error-prone (with clear documentation).

## Getting started

1. Read the README and any existing guides in this repo.
2. Try running through the documented setup flow on a test machine or a fresh user account to see what works and what is confusing.
3. Take notes on where you got stuck or where output was surprising, and turn those into issues or improvements.

## Guidelines for changes

- Keep changes focused and incremental.
- When altering shell instructions, be explicit about which shell(s) they apply to (e.g. `bash`, `zsh`, etc.).
- Prefer commands and patterns that are safe to re-run (idempotent or at least non-destructive by default).
- Be careful when suggesting edits to dotfiles like `~/.zshrc` or `~/.bashrc`; clearly explain what will be added and why.

## Testing your changes

Before opening a pull request:

- Run through the modified steps on at least one environment (e.g. macOS with `zsh`).
- Verify that the resulting Python version and `pyenv` configuration behave as described.
- If you change or add scripts, run them with `set -x` or similar to verify each step behaves as expected.

By contributing improvements here, you help make Python environment setup less error-prone and easier to automate for others.
