from __future__ import annotations

import sys

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.6.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"


import os
from pathlib import Path
from typing import Union

# $XDG_CACHE_HOME = $HOME/.cache
# PIPX_HOME= so default to /home/gaetan/.local/pipx
# PIPX_LOCAL_VENVS=/home/gaetan/.local/pipx/venvs
# PIPX_VENV_CACHEDIR=/home/gaetan/.local/pipx/.cache
# PIPX_DEFAULT_PYTHON=/usr/bin/python3
# USE_EMOJI=true


def env_to_path(env_name: str, default: Union[str, None] = None) -> Path:
    return Path(os.path.expandvars(os.environ.get(env_name, default)))


ci_project_dir = env_to_path("CI_PROJECT_DIR", ".")
home = Path(
    os.path.expanduser("~"),  # noqa: PTH111
)  # remark Path.expanduser("~") not work
uvpipx_home = env_to_path("UVPIPX_HOME", home / ".local/uv-pipx")
uvpipx_venvs = env_to_path("UVPIPX_LOCAL_VENVS", uvpipx_home / "venvs")

default_local_bin = home / ".local/bin"
if home == Path("/root"):
    default_local_bin = "/usr/local/bin"

uvpipx_local_bin = env_to_path("UVPIPX_BIN_DIR", default_local_bin)

platform = "win" if sys.platform.startswith("win") else sys.platform


# TODO on windows .venv/bin is .venv/Scripts so need to change expose

