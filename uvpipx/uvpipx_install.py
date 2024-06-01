#!/usr/bin/env python3

from __future__ import annotations

from uvpipx.uvpipx_bins import relink_bins

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.4.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"


import json
import re
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Union

from uvpipx import config
from uvpipx.internal_libs.misc import (
    cmd_prepare_env,
    cmd_run,
    log_info,
    shell_run,
    shell_run_elapse,
)


def install(
    package_name_ref: str,
    *,
    expose_bin_names: Optional[List[str]] = None,
    venv_name: Union[None, str] = None,
    force_reinstall: bool = False,
) -> None:
    package_name = re.search(r"([^=<>]+)(==|>)*", package_name_ref)[1]
    venv_name_ = venv_name or package_name
    expose_bin_names_ = expose_bin_names

    pck_venv = config.uvpipx_venvs / venv_name_

    if expose_bin_names_ is None:
        expose_bin_names_ = ["*"]

    if not force_reinstall and (pck_venv / "uvpipx.json").exists():
        log_info(
            f"⚠️  {package_name_ref} already installed. need to use option --force to reinstall"
        )
        return

    uvpipx_dict = {
        "package_name_ref": package_name_ref,
        "package_name": package_name,
        "venv_name": venv_name,
        "bin_names": expose_bin_names_,
    }

    # if not command_exists("uv"):
    #     log_info("Install uv")
    #     shell_run_elapse("pip install uv", "uv installed")

    (config.uvpipx_venvs / venv_name_).mkdir(exist_ok=True, parents=True)
    uvpipx_dict["uvpipx_package_path"] = pck_venv

    if not (pck_venv / ".venv").exists():
        shell_run_elapse(
            f"uv venv {pck_venv / '.venv'}",
            f" 📦 uv venv {pck_venv} created",
        )

    shell_run_elapse(
        f"cd {pck_venv}; uv pip install {package_name_ref}",
        f" 📥 uv pip install {package_name_ref} in uvpipx venv {venv_name_}",
    )
    log_info(f" 🟢 uvpipx venv {venv_name_} with {package_name} ready")
    shell_run(f"cd {pck_venv}; uv pip freeze > requirements.txt")
    log_info("")

    with (pck_venv / "uvpipx.json").open("w") as outfile:
        json.dump(uvpipx_dict, outfile, indent=4, default=str)

    log_info(" 🎯 Exposing program")
    relink_bins(package_name, expose_bin_names=expose_bin_names_, venv_name=venv_name)


# def reinstall(
#     package_name_ref: str,
#     *,
#     expose_bin_names: Optional[List[str]] = None,
#     venv_name: Union[None, str] = None,
# ) -> None:
#     return install(
#         package_name_ref,
#         expose_bin_names=expose_bin_names,
#         venv_name=venv_name,
#         force_reinstall=True,
#     )


def run_venv_bin(
    package_name: str,
    cmdline: str,
    *,
    venv_name: Union[None, str] = None,
) -> None:
    """venv is specific to uvpipx. it can replace inject, runpip (oups runuv), uninject

    in fact runpip should be replace by uvpipx venv "truc" uv -- pip install me
    """
    venv_name_ = venv_name or package_name
    pck_venv = config.uvpipx_venvs / venv_name_

    if not (pck_venv / ".venv").exists():
        msg = "{pck_venv} not exist or ready"
        raise RuntimeError(msg)

    env = cmd_prepare_env(None)
    env["VIRTUAL_ENV"] = str(pck_venv / ".venv")
    env["PATH"] = str(pck_venv / ".venv" / "bin") + ":" + env["PATH"]
    if "PYTHONHOME" in env:
        del env["PYTHONHOME"]

    rc, stdo, stde = cmd_run(
        # pck_venv / ".venv" / "bin",
        Path.cwd(),
        cmdline,
        env=env,
        raw_pipe=True,
    )
    # print(stdo)
    # print(stde, file=sys.stderr)
    sys.exit(rc)


def uninstall(package_name: str, *, venv_name: Union[None, str] = None) -> None:
    venv_name_ = venv_name or package_name
    pck_venv = config.uvpipx_venvs / venv_name_

    if not (pck_venv / ".venv").exists():
        msg = f"🔴 {package_name} not exist (path {pck_venv})"
        raise RuntimeError(msg)

    with (pck_venv / "uvpipx.json").open() as outfile:
        uvpipx_dict = json.load(
            outfile,
        )

    log_info(f"🗑️  Remove exposed program")
    relink_bins(package_name, expose_bin_names=["_"], venv_name=venv_name)

    log_info(f"  🗑️  Remove uvpipx venv {pck_venv}")
    shutil.rmtree(pck_venv)
