from __future__ import annotations

from pathlib import Path
from typing import Union

from uvpipx import config
from uvpipx.uvpipx_core import PathLink, UvPipxVenv
from uvpipx.UvPipxModels import (
    UvPipxExposedModel,
    UvPipxVenvExposeAppModel,
    UvPipxVenvModel,
)


def uvpipx_venv_factory(
    package_name: str, name_override: Union[str, None] = None,
) -> tuple[UvPipxVenvModel, UvPipxVenv]:
    name = name_override or package_name

    venv_m = UvPipxVenvModel(str(Path(config.uvpipx_venvs) / name), name_override)
    venv = UvPipxVenv(venv_path=venv_m.uvpipx_path())

    return venv_m, venv


def path_link_factory(
    app_bin: Path, local_app_bin_dir: Path, rename_local_bin: Union[None, str] = None,
) -> PathLink:
    expose_local_bin_name = local_app_bin_dir / (rename_local_bin or app_bin.name)
    p_link = PathLink(app_bin, expose_local_bin_name)

    return p_link


def path_link_from_model(
    exposed: UvPipxExposedModel, app_bin_model: UvPipxVenvExposeAppModel,
) -> PathLink:
    p_link = PathLink(
        Path(exposed.venv_bin_dir) / app_bin_model.bin_app_name,
        Path(app_bin_model.exposed_app_path),
    )

    return p_link
