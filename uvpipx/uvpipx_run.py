from __future__ import annotations

import sys
from pathlib import Path
from typing import Union

from uvpipx.internal_libs.misc import cmd_prepare_env, cmd_run
from uvpipx.uvpipx_venv_load import uvpipx_load_venv


def run_venv_bin(
    package_name: str,
    cmdline: str,
    *,
    name_override: Union[None, str] = None,
) -> None:
    """venv is specific to uvpipx. it can replace inject, runpip (oups runuv), uninject

    in fact runpip could be replace by uvpipx venv "truc" uv -- pip install me
    """
    venv_model, venv = uvpipx_load_venv(package_name, name_override)

    env = cmd_prepare_env(None)
    env["VIRTUAL_ENV"] = str(venv.venv_path)
    env["PATH"] = str(venv.venv_path / ".venv/bin") + ":" + env["PATH"]
    if "PYTHONHOME" in env:
        del env["PYTHONHOME"]

    rc, stdo, stde = cmd_run(
        Path.cwd(),
        cmdline,
        env=env,
        raw_pipe=True,
    )

    # print(stdo)
    # print(stde, file=sys.stderr)

    sys.exit(rc)
