#!/usr/bin/env python3

from __future__ import annotations

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


def inject(
    package_main_name: str,
    lst_package_name_ref: list[str],
    *,
    # expose_bin_names: Optional[List[str]] = None,
    venv_name: Union[None, str] = None,
) -> None:
    package_name = package_main_name
    # re.search(r"([^=<>]+)(==|>)*", lst_package_name_ref)[1]
    venv_name_ = venv_name or package_main_name
    pck_venv = config.uvpipx_venvs / venv_name_

    # expose_bin_names_ = expose_bin_names
    # if expose_bin_names_ is None:
    #     expose_bin_names_ = ["*"]

    if not (pck_venv / ".venv").exists():
        msg = "{pck_venv} not exist or ready"
        raise RuntimeError(msg)

    with (pck_venv / "uvpipx.json").open() as outfile:
        uvpipx_dict = json.load(
            outfile,
        )

    injected_package = {
        re.search(r"([^=<>]+)(==|>)*", pck_name)[1]: pck_name
        for pck_name in lst_package_name_ref
    }
    pre_injected_package = uvpipx_dict.get("injected_package", {})

    for pck_name in injected_package:
        if pck_name in pre_injected_package:
            msg = f"🔴 {pck_name} already injected"
            raise RuntimeError(msg)

    pip_packages_spec = " ".join(lst_package_name_ref)
    shell_run_elapse(
        f"cd {pck_venv}; uv pip install --upgrade {pip_packages_spec}",
        f" 📥 uv pip install {pip_packages_spec} in uvpipx venv {venv_name_}",
    )
    log_info(f" 🟢 injected {lst_package_name_ref}")
    shell_run(f"cd {pck_venv}; uv pip freeze > requirements.txt")
    log_info("")

    tmp_dict = {**pre_injected_package, **injected_package}
    uvpipx_dict["injected_package"] = {k: tmp_dict[k] for k in sorted(tmp_dict)}
    with (pck_venv / "uvpipx.json").open("w") as outfile:
        json.dump(uvpipx_dict, outfile, indent=4, default=str)

    # log_info(" 🎯 Re-Exposing program change")
    # relink_bins(package_name, expose_bin_names=expose_bin_names_, venv_name=venv_name)


def uninject(
    package_main_name: str,
    lst_package_name_ref: list[str],
    *,
    venv_name: Union[None, str] = None,
) -> None:
    venv_name_ = venv_name or package_main_name
    pck_venv = config.uvpipx_venvs / venv_name_

    if not (pck_venv / ".venv").exists():
        msg = "{pck_venv} not exist or ready"
        raise RuntimeError(msg)

    with (pck_venv / "uvpipx.json").open() as outfile:
        uvpipx_dict = json.load(
            outfile,
        )

    pre_injected_package = uvpipx_dict.get("injected_package", {})

    uninjected_package = {
        re.search(r"([^=<>]+)(==|>)*", pck_name)[1]: pck_name
        for pck_name in lst_package_name_ref
    }

    for pck_name in uninjected_package:
        if pck_name not in pre_injected_package:
            msg = f"🔴 {pck_name} is not injected"
            raise RuntimeError(msg)

    futur_injected_package = {
        pck_name: pck_ref
        for pck_name, pck_ref in pre_injected_package.items()
        if pck_name not in uninjected_package
    }

    pip_packages_spec = " ".join(uninjected_package.keys())
    shell_run_elapse(
        f"cd {pck_venv}; uv pip uninstall {pip_packages_spec}",
        f" 📥 uv pip iunnstall {pip_packages_spec} in uvpipx venv {venv_name_}",
    )
    log_info(f" 🟢 iunnjected {lst_package_name_ref}")
    shell_run(f"cd {pck_venv}; uv pip freeze > requirements.txt")
    log_info("")

    uvpipx_dict["injected_package"] = sorted(futur_injected_package)

    with (pck_venv / "uvpipx.json").open("w") as outfile:
        json.dump(uvpipx_dict, outfile, indent=4, default=str)

    # log_info(" 🎯 Re-Exposing program change")
    # relink_bins(package_name, expose_bin_names=expose_bin_names_, venv_name=venv_name)
