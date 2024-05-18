#!/usr/bin/env sh

>&2 printf "%b" "[\\e[1;94mINFO\\e[0m] Python version...\n"
python -V

>&2 printf "%b" "[\\e[1;94mINFO\\e[0m] Install poetry...\n"
pip install poetry==1.8.*
poetry config virtualenvs.create false

>&2 printf "%b" "[\\e[1;94mINFO\\e[0m] Install requirements with poetry...\n"
poetry install --all-extras

>&2 printf "%b" "[\\e[1;94mINFO\\e[0m] ------------------------------------\n"
