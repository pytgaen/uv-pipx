#!/usr/bin/env python3

from __future__ import annotations

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.2.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"


import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import List, Union, Optional

from uvpipx import config
from uvpipx.internal_libs.misc import (
    cmd_prepare_env,
    cmd_run,
    find_executable,
    log_info,
    log_warm,
    shell_run,
    shell_run_elapse,
)


def install(
    package_name_ref: str,
    *,
    expose_bin_names: Optional[List[str]] = None,
    venv_name: Union[None, str] = None,
) -> None:
    package_name = re.search(r"([^=<>]+)(==|>)*", package_name_ref)[1]
    venv_name_ = venv_name or package_name
    expose_bin_names_ = expose_bin_names
    if expose_bin_names_ is None:
        expose_bin_names_ = ["*"]

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
    pck_venv = config.uvpipx_venvs / venv_name_
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
    print()

    log_info(" 🎯 Exposing program")
    if len(expose_bin_names_) == 1:
        if expose_bin_names_[0] == "*":
            exe = find_executable(pck_venv / ".venv" / "bin")
            expose_bin_names_ = [s.name for s in exe if not s.name.startswith("python")]
        elif expose_bin_names_[0] == "_":
            expose_bin_names_ = []

    uvpipx_dict["exposed_bins"] = []
    if expose_bin_names_:
        config.uvpipx_local_bin.mkdir(parents=True, exist_ok=True)
    for bin_name in expose_bin_names_:
        if ":" in bin_name:
            venv_bin_name, local_bin_name = bin_name.split(":")
        else:
            venv_bin_name = bin_name
            local_bin_name = bin_name

        link_dest = config.uvpipx_local_bin / local_bin_name
        uvpipx_dict["exposed_bins"].append(
            (pck_venv / ".venv" / "bin" / venv_bin_name, link_dest),
        )
        if (pck_venv / ".venv" / "bin" / venv_bin_name).exists():
            if not link_dest.exists():
                os.symlink(pck_venv / ".venv" / "bin" / venv_bin_name, link_dest)
                log_info(f"  📁 Exposing program {venv_bin_name} to {link_dest}")
            else:
                log_warm(f"  🟡 Link for {local_bin_name} already exist. Skipping !")
        else:
            msg = f" 🔴 Program {venv_bin_name} not exist in package {package_name_ref}"
            raise RuntimeError(
                msg,
            )

    with (pck_venv / "uvpipx.json").open("w") as outfile:
        json.dump(uvpipx_dict, outfile, indent=4, default=str)


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
        msg = "{pck_venv} not ready"
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


# TODO upgrade
# uv pip install --upgrade jc
# after upgrade check bin to link or unlink

# TODO upgrade-all

# def venv(package_name, cmdline, *, venv_name: Union[None, str] = None):
#     """venv is specific to uvpipx. it will replace inject, runpip, uninject

#     in fact runpip should be replace by uvpipx venv "truc" uv -- pip install me
#     """
#     venv_name_ = venv_name or package_name
#     pck_venv = config.uvpipx_venvs / venv_name_

#     if not (pck_venv / ".venv").exists():
#         raise RuntimeError("{pck_venv} not ready")

#     # VIRTUAL_ENV=pck_venv / ".venv"
#     # PATH="$VIRTUAL_ENV/bin:$PATH"
#     # unset PYTHONHOME

#     rc, stdo, stde = cmd_run(
#         pck_venv / ".venv" / "bin",
#         cmdline,
#     )
#     print(stdo)
#     print(stde, file=sys.stderr)
#     sys.exit(rc)


def uninstall(package_name: str, *, venv_name: Union[None, str] = None) -> None:
    venv_name_ = venv_name or package_name
    pck_venv = config.uvpipx_venvs / venv_name_

    with (pck_venv / "uvpipx.json").open() as outfile:
        uvpipx_dict = json.load(
            outfile,
        )

    exposed = {
        bin_local_bin: bin_venv
        for bin_venv, bin_local_bin in uvpipx_dict["exposed_bins"]
    }

    for bin_path in config.uvpipx_local_bin.iterdir():
        if bin_path.is_symlink() and str(bin_path) in exposed:
            official_uvpipx_target_path = exposed.get(str(bin_path))
            bin_target_path = bin_path.resolve()
            if str(bin_target_path) == official_uvpipx_target_path:
                log_info(f"Remove link {bin_path} -> {bin_target_path}")
                bin_path.unlink()
            else:
                log_warm(
                    f"Not is my {bin_path} -> {bin_target_path} ({official_uvpipx_target_path})",
                )

    log_info(f"Remove uvpipx venv {pck_venv}")
    shutil.rmtree(pck_venv)


# +info

# TODO roadmap
# +info ... --venv-name
# uninstall-all
# upgrade / -all
# reinstall / -all
# runpip (replace by venv)
# inject / uninject (replace by venv)
# environment
# completions (never)
