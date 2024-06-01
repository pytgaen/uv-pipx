#!/usr/bin/env python3

from __future__ import annotations
import difflib

from uvpipx.uvpipx_bins import relink_bins

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.4.1"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"


import json
import re
from typing import Union

from uvpipx import config
from uvpipx.internal_libs.misc import (
    log_info,
    shell_run,
    shell_run_elapse,
)


def upgrade(
    package_name_ref: str,
    *,
    venv_name: Union[None, str] = None,
) -> None:
    package_name = re.search(r"([^=<>]+)(==|>)*", package_name_ref)[1]
    venv_name_ = venv_name or package_name
    pck_venv = config.uvpipx_venvs / venv_name_

    if not (pck_venv / ".venv").exists():
        msg = "{pck_venv} not exist or ready"
        raise RuntimeError(msg)

    with (pck_venv / "uvpipx.json").open() as outfile:
        uvpipx_dict = json.load(
            outfile,
        )
    expose_bin_names_ = uvpipx_dict["bin_names"]
    package_name_ref_ = uvpipx_dict["package_name_ref"]

    rc, stdout, stderr = shell_run(f"cd {pck_venv}; uv pip freeze")
    old_vers = sorted(line for line in stdout.split("\n"))

    shell_run_elapse(
        f"cd {pck_venv}; uv pip install --upgrade {package_name_ref_}",
        f" 📥 uv pip install {package_name_ref_} in uvpipx venv {venv_name_}",
    )
    log_info(f" 🟢 uvpipx venv {venv_name_} with {package_name} ready")
    shell_run(f"cd {pck_venv}; uv pip freeze > requirements.txt")
    rc, stdout, stderr = shell_run(f"cd {pck_venv}; uv pip freeze")
    new_vers = sorted(line for line in stdout.split("\n"))

    diff_vers = [
        n
        for n in difflib.ndiff(old_vers, new_vers)
        if n[:2] in ["+ ", "- "]
    ]

    if diff_vers:
        log_info("\n 🏗️  changes")
        log_info("\n".join(f"   {n}" for n in diff_vers))
    else:
        log_info("\n ⭕ no change")

    log_info("")

    with (pck_venv / "uvpipx.json").open("w") as outfile:
        json.dump(uvpipx_dict, outfile, indent=4, default=str)

    # log_info(" 🎯 Re-Exposing program change")
    # relink_bins(package_name, expose_bin_names=expose_bin_names_, venv_name=venv_name)
