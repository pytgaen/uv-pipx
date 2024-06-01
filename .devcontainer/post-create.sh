#!/bin/bash

# task --help 2>/dev/null
uvpipx install ruff
uvpipx install bandit
poetry install --no-interaction --no-ansi --no-root --with dev
