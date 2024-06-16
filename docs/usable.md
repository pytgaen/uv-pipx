# Usable and Non-Usable Apps with uvpipx

uvpipx is designed to install and run Python applications in isolated environments. However, not all Python tools are suitable for this kind of isolation. This page provides guidance on which tools work well with uvpipx and which ones may face challenges.

## Usable Apps

The following tools are well-suited for installation and use with uvpipx. They typically work as standalone applications and don't require access to your project's specific dependencies:

- [Poetry](https://python-poetry.org) - Dependency management and packaging made easy
- [ruff](https://astral.sh/ruff) - An extremely fast Python linter
- [pre-commit](https://pre-commit.com) - A framework for managing and maintaining multi-language pre-commit hooks
- [black](https://github.com/psf/black) - The uncompromising Python code formatter
- [isort](https://pycqa.github.io/isort/) - A Python utility / library to sort imports
- [Bandit](https://bandit.readthedocs.io/en/latest/) - A tool designed to find common security issues in Python code

These tools can be installed using uvpipx, for example:

```bash
uvpipx install poetry
uvpipx install ruff
```

## Non-Usable Apps

Some tools are not ideal for use with uvpipx, primarily because they need access to the packages used in your specific project. These include:

- [Pytest](https://docs.pytest.org) - A framework for writing and running tests in Python
- [deptry](https://deptry.com) - A command line utility to check for unused, missing, and transitive dependencies in a Python project
- [mypy](https://mypy-lang.org) - An optional static type checker for Python

These tools typically need to be installed within your project's environment (e.g., using `pip install` or as part of your project's dependencies in |`poetry pyproject.toml`) rather than isolated with uvpipx.

## Why the Difference?

The key distinction lies in how these tools interact with your project:

1. **Usable apps** are generally standalone tools that operate on your code or environment without needing to import your project's specific packages. They can work effectively from an isolated environment.

2. **Non-usable apps** often need to directly interact with or analyze your project's code and its dependencies. They may need to import modules from your project, which isn't possible from an isolated environment created by uvpipx.

## Best Practices

- Use uvpipx for global tools that you use across multiple projects (like formatters, linters, and build tools).
- Install project-specific tools (like testing frameworks and type checkers) directly in your project's virtual environment.
- Always check a tool's documentation for recommended installation methods.

Remember, while this list provides general guidance, your specific use case may vary. Always test to ensure the tool works as expected in your workflow when using uvpipx.

Next page [Troubleshooting](troubleshooting.md)