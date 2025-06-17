#!/usr/bin/env sh

>&2 printf "%b" "[\\e[1;94mINFO\\e[0m] Python version...\n"
python -V

>&2 printf "%b" "[\\e[1;94mINFO\\e[0m] Install uv...\n"
pip install uv

>&2 printf "%b" "[\\e[1;94mINFO\\e[0m] Install requirements with uv...\n"

uv sync --all-groups

ln -s "$PWD/.venv/bin/mkdocs" /usr/local/bin/mkdocs
mkdocs --version

>&2 printf "%b" "[\\e[1;94mINFO\\e[0m] ------------------------------------\n"
