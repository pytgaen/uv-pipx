from __future__ import annotations

from uvpipx.internal_libs.Logger import get_logger
from uvpipx.uvpipx_install import uninstall
from uvpipx.uvpipx_upgrade import upgrade

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.6.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"


from uvpipx import config


def upgrade_all() -> None:
    logger = get_logger("upgrade_all")

    infos = ""

    nb = 0
    if config.uvpipx_venvs.exists():
        for pck_venv in config.uvpipx_venvs.iterdir():
            if nb > 0:
                logger.log_info("")
            upgrade(pck_venv.name)  # This is a tricky way to get the name
            logger.log_info(" ----------------")
            nb += 1

    if nb == 0:
        infos += "⭕ Nothing is installed !"

    if infos:
        logger.log_info(infos)


def uninstall_all() -> None:
    logger = get_logger("uninstall_all")

    infos = ""

    nb = 0
    if config.uvpipx_venvs.exists():
        for pck_venv in config.uvpipx_venvs.iterdir():
            if nb > 0:
                logger.log_info("")
            uninstall(pck_venv.name)  # This is a tricky way to get the name
            logger.log_info(" ----------------")
            nb += 1

    if nb == 0:
        infos += "⭕ Nothing is installed !"

    if infos:
        logger.log_info(infos)
