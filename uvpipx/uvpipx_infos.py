from __future__ import annotations

from uvpipx.version import show_version

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.4.0"  # to bump
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
    if str(config.uvpipx_local_bin) + "x" in path_set:
        log_info("🟢 Configuration of PATH already OK")
        return

    profile_path = Path(os.environ["HOME"]) / ".profile"

    profile_content = Path(profile_path).read_text()
    if "# Added by uvpipx" in profile_content:
        log_info(f"""⚠️  Configuration already in {profile_path}

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

    log_info(f"""Configuration added to {profile_path}

⚠️  To use without restart the shell, launch 
export PATH=$PATH:{config.uvpipx_local_bin}
""")


def _info(pck_venv: Path) -> str:
    def get_version(pck_name, stdout_line):
        vers = next(
            (line for line in stdout_line if pck_name in line),
            None,
        )
        if vers is None:
            vers = f"{pck_name} Unknow version"

        return vers

    uvpipx_dict = {}
    with (pck_venv / "uvpipx.json").open() as intfile:
        uvpipx_dict = json.load(
            intfile,
        )
    rc, stdout, stderr = shell_run(f"cd {pck_venv}; uv pip freeze")
    stdout_line =[line for line in stdout.split("\n")]
    main_vers = get_version(uvpipx_dict["package_name"], stdout_line)
        # vers = "unable to retreive package information"

    injected_vers=[]
    for pkg_injected in uvpipx_dict.get("injected_package",[]):
        injected_vers.append(get_version(pkg_injected, stdout_line))
    injected_vers = sorted(injected_vers)

    bins = "\n".join(
        f"   ✅ {bin_.split('/')[-1]}" for _, bin_ in uvpipx_dict["exposed_bins"]
    )
    if not bins:
        bins = "   ❌ Nothing exposed"

    output = f""" 📦 {uvpipx_dict['package_name']} ({main_vers}) in venv {uvpipx_dict['uvpipx_package_path']}"""
    if injected_vers:
        output_inject = "\n".join(f"""   📦 {pkg_ver}""" for pkg_ver in injected_vers)
        output += f"""

 🎯 Injected packages
{output_inject}"""
        
    output += f"""

 🎯 Exposed program
{bins}\n"""
    
    return output



def info(
    package_name: str,
    *,
    venv_name: Union[None, str] = None,
    get_venv: bool = False,
) -> None:
    venv_name_ = venv_name or package_name
    pck_venv = config.uvpipx_venvs / venv_name_

    info = str(pck_venv / ".venv") if get_venv else _info(pck_venv)

    log_info(info)


def uvpipx_list() -> None:
    infos = f"""📍 uvpipx venvs are in {config.uvpipx_venvs}
💻 apps are exposed at {config.uvpipx_local_bin} 

"""
    show_version()

    nb = 0
    if config.uvpipx_venvs.exists():
        for pck_venv in config.uvpipx_venvs.iterdir():
            infos += _info(pck_venv)
            infos += "\n\n"
            nb += 1

    if nb == 0:
        infos += "⭕ Nothing is installed !"

    log_info(infos)
