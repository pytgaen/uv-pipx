from __future__ import annotations

from uvpipx.internal_libs.Logger import get_logger
from uvpipx.uvpipx_core import UvPipxVenv
from uvpipx.uvpipx_venv_factory import path_link_from_model
from uvpipx.uvpipx_venv_load import uvpipx_load_venv
from uvpipx.UvPipxModels import UvPipxModel
from uvpipx.version import show_version

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.6.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"


import os
from pathlib import Path
from typing import List, Union

from uvpipx import config
from uvpipx.internal_libs.misc import shell_run


def ensurepath() -> None:
    logger = get_logger("uninstall")

    path_set = os.environ["PATH"].split(":")
    if str(config.uvpipx_local_bin) + "x" in path_set:
        logger.log_info("🟢 Configuration of PATH already OK")
        return

    profile_path = Path(os.environ["HOME"]) / ".profile"

    profile_content = Path(profile_path).read_text()
    if "# Added by uvpipx" in profile_content:
        logger.log_info(f"""⚠️  Configuration already in {profile_path}

⚠️  To use without restart the shell, launch 
export PATH=$PATH:{config.uvpipx_local_bin}
""")
        return

    line_to_add = ""
    if Path(profile_path).read_text()[-1] != "\n":
        line_to_add = "\n"

    line_to_add += f"""# Added by uvpipx
export PATH=$PATH:{config.uvpipx_local_bin}\n"""

    with profile_path.open("a") as file:
        file.write(line_to_add)

    logger.log_info(f"""Configuration added to {profile_path}

⚠️  To use without restart the shell, launch 
export PATH=$PATH:{config.uvpipx_local_bin}
""")


def _info(uvpipx: UvPipxModel, venv: UvPipxVenv) -> str:
    def get_version(pck_name: str, stdout_line: List[str]) -> str:
        vers = next(
            (line for line in stdout_line if pck_name in line),
            None,
        )
        if vers is None:
            vers = f"{pck_name} Unknow version"

        return vers

    rc, stdout, stderr = shell_run("uv pip freeze", cwd=venv.venv_path)
    stdout_line = stdout.split("\n")
    main_vers = get_version(uvpipx.main_package.package_name, stdout_line)

    injected_vers = []
    for pkg_injected in list(uvpipx.injected_packages.keys()):
        injected_vers.append(get_version(pkg_injected, stdout_line))
    injected_vers = sorted(injected_vers)

    path_links = [
        path_link_from_model(uvpipx.exposed, m) for m in uvpipx.exposed.apps.values()
    ]
    bins = "\n".join(f"   ✅ {app_bin.show_name_with_link()}" for app_bin in path_links)

    # TODO add show info about install set in advanced view

    if not bins:
        bins = "   ❌ Nothing exposed"

    output = f""" 📦 {uvpipx.main_package.package_name} ({main_vers}) in venv {uvpipx.venv.uvpipx_dir}"""
    if injected_vers:
        output_inject = "\n".join(f"""   📦 {pkg_ver}""" for pkg_ver in injected_vers)
        output += f"""

 🎯 Injected packages
{output_inject}"""

    output += f"""

 🎯 Exposed program
{bins}\n"""

    return output


def _info_pkg(
    package_name: str,
    *,
    name_override: Union[None, str] = None,
    get_venv: bool = False,
) -> str:
    uvpipx, venv = uvpipx_load_venv(package_name, name_override)

    return str(venv.venv_path / ".venv") if get_venv else _info(uvpipx, venv)


def info(
    package_name: str,
    *,
    name_override: Union[None, str] = None,
    get_venv: bool = False,
) -> None:
    logger = get_logger("info")

    info = _info_pkg(package_name, name_override=name_override, get_venv=get_venv)
    logger.log_info(info)


def uvpipx_list() -> None:
    infos = f"""📍 uvpipx venvs are in {config.uvpipx_venvs}
💻 apps are exposed at {config.uvpipx_local_bin} 

"""
    logger = get_logger("uvpipx_list")

    show_version()

    nb = 0
    if config.uvpipx_venvs.exists():
        for pck_venv in config.uvpipx_venvs.iterdir():
            infos += _info_pkg(pck_venv)  # this is a tricky way to get the name
            infos += "\n\n"
            nb += 1

    if nb == 0:
        infos += "⭕ Nothing is installed !"

    logger.log_info(infos)
