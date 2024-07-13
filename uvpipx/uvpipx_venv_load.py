from __future__ import annotations

import json
from typing import Tuple, Union

from uvpipx.uvpipx_core import UvPipxVenv
from uvpipx.uvpipx_venv_factory import uvpipx_venv_factory
from uvpipx.UvPipxModels import UvPipVenvNotReady, UvPipxModel
from uvpipx.UvPipxModelsUpgrader import check_and_upgrade


def uvpipx_load_venv(
    package_name: str,
    name_override: Union[str, None] = None,
) -> Tuple[UvPipxModel, UvPipxVenv]:
    venv_m, venv = uvpipx_venv_factory(package_name, name_override)

    if not venv.exists():
        msg = f"🔴 {package_name} not exist (path {venv.venv_path})"
        raise UvPipVenvNotReady(msg)

    if not (venv.venv_path / "uvpipx.json").exists():
        msg = f"🔴 {package_name} not exist (path {venv.venv_path})"
        raise UvPipVenvNotReady(msg)

    with (venv.venv_path / "uvpipx.json").open("r") as infile:
        file_dict = json.load(
            infile,
        )

    current_vers_dict, upgraded = check_and_upgrade(file_dict)
    if current_vers_dict is None:
        msg = "Bad venv, please unistall and install"
        raise UvPipVenvNotReady(msg)

    uvpipx_cfg = UvPipxModel.from_dict(current_vers_dict)

    if upgraded:
        uvpipx_cfg.save_json("uvpipx.json")

    return uvpipx_cfg, venv
