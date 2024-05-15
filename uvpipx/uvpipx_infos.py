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
from pathlib import Path
from typing import Union

from uvpipx import config
from uvpipx.internal_libs.misc import log_info, shell_run


def ensurepath() -> None:
    path_set = os.environ["PATH"].split(":")
    if str(config.uvpipx_local_bin) in path_set:
        log_info("Configuration of PATH already OK")
        return

    profile_path = Path(os.environ["HOME"]) / ".profile"

    line_to_add = ""
    if Path(profile_path).read_text()[-1] != "\n":
        line_to_add = "\n"

    line_to_add += f"""# Adder by uvpipx
export PATH=$PATH:{config.uvpipx_local_bin}\n"""

    with profile_path.open("a") as file:
        file.write(line_to_add)

    log_info(f"""Configuration adder to {profile_path}

To use without restart the shell, launch 
export PATH=$PATH:{config.uvpipx_local_bin}
""")


def _info(pck_venv: Path) -> str:
    uvpipx_dict = {}
    with (pck_venv / "uvpipx.json").open() as intfile:
        uvpipx_dict = json.load(
            intfile,
        )
    rc, stdout, stderr = shell_run(f"cd {pck_venv}; uv pip freeze")
    vers = next(
        (line for line in stdout.split("\n") if uvpipx_dict["package_name"] in line),
        None,
    )
    if vers is None:
        vers = "unknow ?"
        # vers = "unable to retreive package information"

    bins = "\n".join(
        f"  - {bin_.split('/')[-1]}" for _, bin_ in uvpipx_dict["exposed_bins"]
    )
    if not bins:
        bins = "  * Nothing exposed"

    return f"""{uvpipx_dict['package_name']} ({vers}) in venv {uvpipx_dict['uvpipx_package_path']}
{bins}\n"""


def info(
    package_name: str,
    *,
    venv_name: Union[None, str] = None,
    get_venv: bool = False,
) -> None:
    venv_name_ = venv_name or package_name
    pck_venv = config.uvpipx_venvs / venv_name_

    info = str(pck_venv / ".venv") if get_venv else _info(pck_venv)

    print(info)


def uvpipx_list() -> None:
    infos = f"""uvpipx venvs are in {config.uvpipx_venvs}
apps are exposed at {config.uvpipx_local_bin} 

"""
    nb = 0
    if config.uvpipx_venvs.exists():
        for pck_venv in config.uvpipx_venvs.iterdir():
            infos += _info(pck_venv)
            infos += "\n"
            nb += 1

    if nb == 0:
        infos += "Nothing is installed !"

    print(infos)
