from __future__ import annotations

from uvpipx.uvpipx_upgrade import upgrade

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.4.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"


from uvpipx import config
from uvpipx.internal_libs.misc import log_info


def upgrade_all() -> None:
    infos = ""

    nb = 0
    if config.uvpipx_venvs.exists():
        for pck_venv in config.uvpipx_venvs.iterdir():
            if nb > 0:
                print("")
            upgrade(pck_venv.name)
            print(" ----------------")
            nb += 1

    if nb == 0:
        infos += "⭕ Nothing is installed !"

    if infos:
        log_info(infos)
