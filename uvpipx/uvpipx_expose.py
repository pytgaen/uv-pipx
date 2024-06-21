from __future__ import annotations

from dataclasses import dataclass
from typing import List, Union

from uvpipx import config
from uvpipx.internal_libs.Logger import Logger, get_logger
from uvpipx.uvpipx_core import UvPipxVenv
from uvpipx.uvpipx_venv_factory import path_link_factory
from uvpipx.UvPipxModels import UvPipxExposedModel, UvPipxVenvExposeAppModel


@dataclass
class ExposeApps:
    venv: UvPipxVenv
    logger: Union[Logger, None] = None

    def __post_init__(self) -> None:
        if not self.logger:
            self.logger = get_logger()

    def get_apps_list(self, expose_app_rules: List[str]):  # noqa: ANN201
        expose_apps_list = expose_app_rules
        renamed_apps = {}

        if not expose_app_rules:
            return []

        if expose_app_rules == ["*"]:
            expose_apps_list = self.venv.venv_bins(
                regex_to_exclude=[r"^(python|pip)(\d+(\.\d+)?)?$"],
            )
        else:
            renamed_apps = {
                key: value
                for item in expose_app_rules
                if ":" in item
                for key, value in [item.split(":", 1)]
            }
            expose_apps_list = [
                self.venv.venv_bin(item.split(":", 1)[0]) for item in expose_app_rules
            ]

        return expose_apps_list, renamed_apps

    def expose(
        self, expose_app_rules: List[str], pkgs_sets,  # noqa: ANN001
    ) -> List[UvPipxExposedModel]:
        exposing_apps, renamed_apps = self.get_apps_list(expose_app_rules)

        config.uvpipx_local_bin.mkdir(parents=True, exist_ok=True)
        exposed_apps = {}
        for app_bin in exposing_apps:
            pl = path_link_factory(
                app_bin,
                config.uvpipx_local_bin,
                rename_local_bin=renamed_apps.get(app_bin.name),
            )
            if not pl.link_exists():
                self.logger.log_info(f" 🎯 Exposing program {pl.show_name_with_link()}")
                pl.link()
                exposed_apps[app_bin.name] = UvPipxVenvExposeAppModel(
                    app_bin.name, pl.link_path, pkgs_sets,
                )
            elif pl.is_valid():
                self.logger.log_info(
                    f" 🎯 Already exposed to current uvpipx venv program {pl.show_name_with_link()}",
                )
                exposed_apps[app_bin.name] = UvPipxVenvExposeAppModel(
                    app_bin.name, pl.link_path, pkgs_sets,
                )
            else:
                self.logger.log_warn(
                    f" ❌ Not exposing program {app_bin.name}; {pl.link_path} already exist to {pl.link_path.resolve()}!",
                )

        return exposed_apps

    # TODO add function to clean old link in local bin
