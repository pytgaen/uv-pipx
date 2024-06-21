#!/usr/bin/env python3

from __future__ import annotations

from uvpipx.internal_libs.Logger import get_logger
from uvpipx.req_spec import Requirement
from uvpipx.uvpipx_venv_load import uvpipx_load_venv
from uvpipx.UvPipxModels import UvPipxExposeInstallSets, UvPipxPackageModel

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.6.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"


from typing import Union

from uvpipx.internal_libs.misc import (
    Elapser,
)


def inject(
    package_main_name: str,
    lst_package_name_spec: list[str],
    *,
    # expose_bin_names: Optional[List[str]] = None,
    name_override: Union[None, str] = None,
) -> None:
    logger = get_logger("inject")

    uvpipx_cfg, venv = uvpipx_load_venv(package_main_name, name_override)

    injecting_package = {
        r.name: r for rl in lst_package_name_spec for r in [Requirement.from_str(rl)]
    }

    for pck_name in injecting_package:  # TODO allow upgrade
        if pck_name in uvpipx_cfg.injected_packages:
            msg = f"🔴 {pck_name} already injected"
            raise RuntimeError(msg)

    pip_packages_spec = " ".join(lst_package_name_spec)
    with Elapser() as ela:
        venv.install(pip_packages_spec, allow_upgrade=False)
    logger.log_info(
        ela.ela_str(
            f" 📥 uv pip install {pip_packages_spec} in uvpipx venv {uvpipx_cfg.venv.name()}",
        ),
    )

    logger.log_info(f" 🟢 injected {lst_package_name_spec}")
    (venv.venv_path / "requirements.txt").write_text(venv.freeze())
    logger.log_info("")

    injected_package = {
        k: UvPipxPackageModel(
            injecting_package[k].to_str(),
            k,
        )
        for k in injecting_package
    }
    tmp_dict = {**uvpipx_cfg.injected_packages, **injected_package}
    uvpipx_cfg.injected_packages = {k: tmp_dict[k] for k in sorted(tmp_dict)}
    uvpipx_cfg.exposed.install_sets.append(
        UvPipxExposeInstallSets(list(injected_package.keys()), []),
    )

    uvpipx_cfg.save_json("uvpipx.json")

    # TODO add exposing


def uninject(
    package_main_name: str,
    lst_package_name_spec: list[str],
    *,
    name_override: Union[None, str] = None,
) -> None:
    logger = get_logger("uninject")

    uvpipx_cfg, venv = uvpipx_load_venv(package_main_name, name_override)

    uninjected_package = {
        r.name: r for rl in lst_package_name_spec for r in [Requirement.from_str(rl)]
    }

    for pck_name in uninjected_package:
        if pck_name not in uvpipx_cfg.injected_packages:
            msg = f"🔴 {pck_name} is not injected"
            raise RuntimeError(msg)

    pip_packages_spec = " ".join(uninjected_package.keys())
    with Elapser() as ela:
        venv.uninstall(pip_packages_spec)
    logger.log_info(
        ela.ela_str(
            f" 🗑️  uv pip uninstall {pip_packages_spec} in uvpipx venv {uvpipx_cfg.venv.name()}",
        ),
    )

    logger.log_info(f" 🗑️  uninjected {lst_package_name_spec}")
    (venv.venv_path / "requirements.txt").write_text(venv.freeze())
    logger.log_info("")

    stay_injected_package = {
        pck_name: pck_ref
        for pck_name, pck_ref in uvpipx_cfg.injected_packages.items()
        if pck_name not in uninjected_package
    }

    uvpipx_cfg.injected_packages = {
        k: stay_injected_package[k] for k in sorted(stay_injected_package)
    }

    uvpipx_cfg.save_json("uvpipx.json")

    # TODO change exposing
