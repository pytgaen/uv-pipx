#!/usr/bin/env python3

from __future__ import annotations

import difflib

from uvpipx.internal_libs.Logger import get_logger
from uvpipx.uvpipx_venv_load import uvpipx_load_venv

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

# TODO review code at this point


def upgrade(
    package_name: str,
    *,
    name_override: Union[None, str] = None,
) -> None:
    logger = get_logger("upgrade")

    venv_model, venv = uvpipx_load_venv(package_name, name_override)

    old_vers = sorted(venv.installed_package())
    package_name_spec = venv_model.main_package.package_name_spec

    with Elapser() as ela:
        venv.install(package_name_spec, allow_upgrade=True)
    logger.log_info(
        ela.ela_str(
            f" 📥 uv pip install {package_name_spec} in uvpipx venv {venv_model.venv.name()}",
        ),
    )

    logger.log_info(
        f" 🟢 uvpipx venv {venv.venv_path.name} with {venv_model.main_package.package_name} ready",
    )

    new_vers = sorted(venv.installed_package())

    diff_vers = [n for n in difflib.ndiff(old_vers, new_vers) if n[:2] in ["+ ", "- "]]

    if diff_vers:
        logger.log_info("\n 🏗️  changes")
        logger.log_info("\n".join(f"   {n}" for n in diff_vers))
    else:
        logger.log_info("\n ⭕ no change")

    logger.log_info("")

    # with (pck_venv / "uvpipx.json").open("w") as outfile:
    #     json.dump(uvpipx_dict, outfile, indent=4, default=str)

    # logger.log_info(" 🎯 Re-Exposing program change")
    # relink_bins(package_name, expose_bin_names=expose_bin_names_, venv_name=venv_name)
