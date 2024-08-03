from __future__ import annotations

import sys

from uvpipx.internal_libs.Logger import Logger, LogMode, get_logger
from uvpipx.platform.win import get_env_variable, set_env_variable
from uvpipx.uvpipx_core import UvPipxVenv
from uvpipx.uvpipx_uv import uv_get_version
from uvpipx.uvpipx_venv_factory import path_link_from_model
from uvpipx.uvpipx_venv_load import uvpipx_load_venv
from uvpipx.UvPipxModels import UvPipxModel
from uvpipx.version import show_version

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.7.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"


import os
from pathlib import Path
from typing import List, Union

import uvpipx.platform
from uvpipx import config
from uvpipx.internal_libs.misc import shell_run


def ensurepath(just_check: bool = False) -> str:
    if uvpipx.platform.sys_platform == "win":
        return ensurepath_win(just_check)

    return ensurepath_unix(just_check)


def ensurepath_unix(just_check: bool = False) -> str:
    logger = Logger(log_mode=LogMode.BUFFER) if just_check else get_logger("ensurepath")

    logger.log_info(f"Search {config.uvpipx_local_bin} in PATH\n")

    path_os_setted = os.environ["PATH"].split(":")
    if str(config.uvpipx_local_bin) in path_os_setted:
        logger.log_info("🟢 Configuration of PATH already OK")
        return "OK"

    profile_path = Path(os.environ["HOME"]) / ".profile"

    profile_content = Path(profile_path).read_text()
    if "# Added by uvpipx" in profile_content:
        logger.log_info(f"""🟣  Configuration already in {profile_path}

⚠️  To use without restart the shell, launch 
export PATH=$PATH:{config.uvpipx_local_bin}
""")
        return "OK/RESTART_NEED"

    if just_check:
        return "KO"

    line_to_add = "\n" if Path(profile_path).read_text()[-1] != "\n" else ""
    line_to_add += f"""# Added by uvpipx
export PATH=$PATH:{config.uvpipx_local_bin}\n"""

    with profile_path.open("a") as file:
        file.write(line_to_add)

    logger.log_info(f"""⚙️  Configuration added to {profile_path}

⚠️  To use without restart the shell, launch 
export PATH=$PATH:{config.uvpipx_local_bin}
""")

    return "OK/RESTART_NEED"


def ensurepath_win(just_check: bool = False) -> str:
    logger = Logger(log_mode=LogMode.BUFFER) if just_check else get_logger("ensurepath")

    logger.log_info(f"Search {config.uvpipx_local_bin} in PATH\n")

    path_os_setted = os.environ["PATH"].split(";")
    if str(config.uvpipx_local_bin) in path_os_setted:
        logger.log_info("🟢 Configuration of PATH already OK")
        return "OK"

    path_reg_level = None
    path_reg_user = get_env_variable("PATH")
    if str(config.uvpipx_local_bin) in path_reg_user.split(";"):
        path_reg_level = "user"

    if path_reg_level is None:
        path_reg_system = get_env_variable("PATH", system=True)
        if str(config.uvpipx_local_bin) in path_reg_system.split(";"):
            path_reg_level = "system"

    if path_reg_level:
        logger.log_info(f"""🟣  Configuration of PATH already in registry {path_reg_level} but not in shell.
                        
⚠️ you should restart the shell to use the new configuration.""")
        return "OK/RESTART_NEED"

    set_env_variable("PATH", f"{config.uvpipx_local_bin};{path_reg_user}")
    logger.log_info("""⚙️  Configuration added to PATH in user environnement vars.

⚠️ you should restart the shell to use the new configuration.""")

    return "OK/RESTART_NEED"


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

    path_links = (
        [path_link_from_model(uvpipx.exposed, m) for m in uvpipx.exposed.apps.values()]
        if uvpipx.exposed and uvpipx.exposed.apps
        else []
    )
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
            infos += _info_pkg(pck_venv.name)  # this is a tricky way to get the name
            infos += "\n\n"
            nb += 1

    if nb == 0:
        infos += "⭕ No uvpipx package installed !"

    logger.log_info(infos)


def uvpipx_show_config() -> None:
    logger = get_logger("uvpipx_show_config")

    show_version()

    uv_version = uv_get_version()
    py_version = f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}"

    logger.log_info("🔍 Uvpipx configuration:")

    logger.log_info(f"💻 platform = {uvpipx.platform.sys_platform}")
    logger.log_info(f"💻 python version = {py_version}")
    logger.log_info(f"💻 uv version = {uv_version}")
    logger.log_info(f"🏠 user home = {config.home}")

    logger.log_info(f"\n🌳 uvpipx home = {config.uvpipx_home}")
    logger.log_info("    Path to the main directory of uvpipx.")
    if uvpipx.platform.sys_platform == "win":
        logger.log_info(
            "    🎚️  Defined by the UVPIPX_HOME environment variable or defaults to $HOME/.local/uv-pipx",
        )
    else:
        logger.log_info(
            "    🎚️  Defined by the UVPIPX_HOME environment variable or defaults to ~/.local/uv-pipx",
        )

    logger.log_info(f"\n🌿 uvpipx venvs = {config.uvpipx_venvs}")
    logger.log_info("    Path to the directory of uvpipx virtual environments.")
    logger.log_info(
        "    🎚️  Defined by the UVPIPX_LOCAL_VENVS environment variable or defaults to $UVPIPX_HOME/venvs",
    )

    logger.log_info(f"\n📁 exposing bin directory = {config.uvpipx_local_bin}")
    logger.log_info("    Default path for exposed executables.")
    if uvpipx.platform.sys_platform == "win":
        logger.log_info(
            """    Default to %HOME%/.local/bin""",
        )
    else:
        logger.log_info(
            """    Default:
            ~/.local/bin for normal users or
            /usr/local/bin for root.""",
        )
    logger.log_info(
        "    🎚️  Can be defined by the UVPIPX_BIN_DIR environment variable",
    )
    # logger.log_info(
    #     "    Note: The value for Windows is not defined in the provided code.",
    # )
