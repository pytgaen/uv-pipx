#!/usr/bin/env python3

from __future__ import annotations

from uvpipx.internal_libs.Logger import get_logger
from uvpipx.req_spec import Requirement
from uvpipx.uvpipx_expose import ExposeApps
from uvpipx.uvpipx_venv_factory import (
    path_link_from_model,
    uvpipx_venv_factory,
)
from uvpipx.uvpipx_venv_load import uvpipx_load_venv
from uvpipx.UvPipxEnv import UvPipVenvNotReady
from uvpipx.UvPipxModels import (
    UvPipxExposedModel,
    UvPipxExposeInstallSets,
    UvPipxModel,
    UvPipxPackageModel,
)

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.6.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"


import shutil
from typing import List, Optional, Union

from uvpipx.internal_libs.misc import (
    Elapser,
)


def install(
    package_name_spec: str,
    *,
    expose_rule_names: Optional[List[str]] = None,
    name_override: Union[None, str] = None,
    force_reinstall: bool = False,
) -> None:
    logger = get_logger("install")

    package_spec = Requirement.from_str(package_name_spec)
    package_name = package_spec.name
    expose_rule_names_ = expose_rule_names or ["*"]
    venv_model, venv = uvpipx_venv_factory(package_name, name_override)

    uvpipx_prev = None
    venv_prev = None
    try:
        uvpipx_prev, venv_prev = uvpipx_load_venv(package_name, name_override)
        if force_reinstall:
            if len(uvpipx_prev.exposed.install_sets) > 1:
                logger.log_warn(
                    f"⚠️  {package_name_spec} already installed but in with many step (install/inject). need to manually uninstall/install/inject or just try an upgrade",
                )
                return
        else:
            if len(uvpipx_prev.exposed.install_sets) > 1:
                logger.log_warn(
                    f"⚠️  {package_name_spec} already installed but in with many step (install/inject). need to manually uninstall/install/inject or just try an upgrade",
                )
            else:
                logger.log_warn(
                    f"⚠️  {package_name_spec} already installed. need to use option --force to reinstall from scratch",
                )
            return
    except UvPipVenvNotReady:
        pass

    uvpipx_cfg = UvPipxModel(
        venv=venv_model,
        main_package=UvPipxPackageModel(
            package_name_spec,
            package_name,
        ),
        injected_packages={},
        exposed=UvPipxExposedModel(str(venv.venv_bin)),
    )

    with Elapser() as ela:
        created = venv.create_venv_if_need()
    if created:
        logger.log_info(ela.ela_str(f" 📦 uv venv {venv_model.name()} created"))

    with Elapser() as ela:
        venv.install(package_name_spec)
    logger.log_info(
        ela.ela_str(
            f" 📥 uv pip install {package_name_spec} in uvpipx venv {venv_model.name()}",
        ),
    )

    logger.log_info(f" 🟢 uvpipx venv {venv_model.name()} with {package_name} ready")

    (venv.venv_path / "requirements.txt").write_text(venv.freeze())
    logger.log_info("")

    expo_app = ExposeApps(venv, logger)
    main_install_set = UvPipxExposeInstallSets([package_name], expose_rule_names_)
    exposed_bins = expo_app.expose(
        expose_rule_names_, main_install_set.package_name_sets,
    )
    install_sets = [main_install_set]

    uvpipx_cfg.exposed = UvPipxExposedModel(
        venv.venv_path / ".venv/bin", install_sets, exposed_bins,
    )

    uvpipx_cfg.save_json("uvpipx.json")


# def reinstall(
#     package_name_spec: str,
#     *,
#     expose_bin_names: Optional[List[str]] = None,
#     venv_name: Union[None, str] = None,
# ) -> None:
#     return install(
#         package_name_spec,
#         expose_bin_names=expose_bin_names,
#         venv_name=venv_name,
#         force_reinstall=True,
#     )


def uninstall(package_name: str, *, name_override: Union[None, str] = None) -> None:
    logger = get_logger("uninstall")

    uvpipx, venv = uvpipx_load_venv(package_name, name_override)

    logger.log_info(f"🪓 Uninstalling {package_name}\n")

    logger.log_info("🗑️  Remove exposed program")
    for mpl in uvpipx.exposed.apps.values():
        pl = path_link_from_model(uvpipx.exposed, mpl)
        pl.unlink()
        logger.log_info(f" ❌ Remove Exposed program {pl.show_name_with_link()}")

    # TODO also delete injected exposed bin

    logger.log_info(f"\n🗑️  Remove uvpipx venv {venv.venv_path.name}")
    shutil.rmtree(venv.venv_path)
