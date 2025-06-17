from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import uvpipx
import uvpipx.platform
from uvpipx import config
from uvpipx.internal_libs.Logger import Logger, get_logger
from uvpipx.uvpipx_core import UvPipxVenv
from uvpipx.uvpipx_venv_factory import path_link_factory
from uvpipx.uvpipx_venv_load import uvpipx_load_venv
from uvpipx.UvPipxModels import UvPipxExposedModel, UvPipxVenvExposeAppModel


@dataclass
class ExposeApps:
    venv: UvPipxVenv
    logger: None | Logger = None
    prev_exposed: None | UvPipxExposedModel = None

    def __post_init__(self) -> None:
        self.logger_ = self.logger or get_logger()

    def set_prev_exposed(self, prev_exposed: None | UvPipxExposedModel) -> None:
        self.prev_exposed = prev_exposed

    def _get_eponym_apps(self, main_package_name: str) -> tuple[list[Path] | None, str | None]:
        """Get eponym app (app with same name as package)."""
        if self.venv.venv_bin(main_package_name).exists():
            return [self.venv.venv_bin(main_package_name)], None

        self.logger_.log_warn(
            f" ⚠️  no find eponym app {self.venv.venv_bin(main_package_name)}. will fallback to app of main package",
        )
        return None, "__main__"

    def _get_main_package_apps(self, main_package_name: str) -> tuple[list[Path] | None, str | None]:
        """Get apps from main package metadata."""
        self.venv.update_metadata()

        with (self.venv.venv_path / "pip_metadata.json").open("r") as infile:
            metadata_dict = json.load(infile)

        console_scripts = metadata_dict["console_scripts"].get(main_package_name, [])
        if console_scripts:
            apps = [self.venv.venv_bin(main_bin) for main_bin in console_scripts if not re.match(r"^(python|pip)(\d+(\.\d+)?)?$", main_bin)]
            return apps, None

        self.logger_.log_warn(" ⚠️  cannot find metadata of package. fallback to eponym app")
        return None, "__eponym__"

    def _get_all_apps(self) -> list[Path]:
        """Get all apps in venv (excluding python/pip)."""
        if uvpipx.platform.sys_platform == "win":
            return self.venv.venv_bins(regex_to_exclude=[r"^(python|pythonw|pip)(\d+(\.\d+)?)?(\.exe)?$"])
        return self.venv.venv_bins(regex_to_exclude=[r"^(python|pip)(\d+(\.\d+)?)?$"])

    def get_apps_list(
        self,
        expose_app_rules: list[str],
        main_package_name: str,
    ) -> tuple[list[Path], dict[str, str]]:
        """Get list of apps to expose based on exposure rules."""
        if not expose_app_rules:
            return [], {}

        expose_apps_list = None
        expose_fallback = None
        renamed_apps = {}

        # Handle __eponym__ rule
        if expose_app_rules == ["__eponym__"]:
            expose_apps_list, expose_fallback = self._get_eponym_apps(main_package_name)

        # Handle __main__ rule or fallback
        if expose_app_rules == ["__main__"] or expose_fallback == "__main__":
            expose_apps_list, expose_fallback = self._get_main_package_apps(main_package_name)

        # Handle __eponym__ fallback
        if expose_fallback == "__eponym__":
            if self.venv.venv_bin(main_package_name, fail_if_notexist=False).exists():
                self.logger_.log_info(" 🔰 fallback to eponym app is OK ")
                expose_apps_list = [self.venv.venv_bin(main_package_name)]
                expose_fallback = None
            else:
                self.logger_.log_warn(
                    f" ⚠️  fallback also failed: unable to find eponym app {main_package_name}. will fallback to all app in venv",
                )
                expose_fallback = "__all__"

        # Handle __all__ rule or fallback
        if expose_app_rules == ["__all__"] or expose_fallback == "__all__":
            expose_apps_list = self._get_all_apps()
        elif not expose_apps_list:
            # Handle custom app list with optional renaming
            renamed_apps = {key: value for item in expose_app_rules if ":" in item for key, value in [item.split(":", 1)]}
            expose_apps_list = [self.venv.venv_bin(item.split(":", 1)[0]) for item in expose_app_rules]

        return expose_apps_list, renamed_apps

    def get_apps_to_remove(
        self,
        future_exposed_apps: dict[str, UvPipxVenvExposeAppModel],
    ) -> dict[str, Path]:
        if self.prev_exposed is None:
            return {}

        prev_exposed_apps = {k: Path(app.exposed_app_path) for k, app in self.prev_exposed.apps.items()}
        # remove pre_exposed_apps that are not in future_exposed_apps
        return {k: v for k, v in prev_exposed_apps.items() if k not in future_exposed_apps}

    def add_exposing(
        self,
        exposing_apps: list[Path],
        renamed_apps: dict[str, str],
        pkgs_sets: list[str],
    ) -> dict[str, UvPipxVenvExposeAppModel]:
        config.uvpipx_local_bin.mkdir(parents=True, exist_ok=True)
        exposed_apps = {}

        for app_bin in exposing_apps:
            pl = path_link_factory(
                app_bin,
                config.uvpipx_local_bin,
                rename_local_bin=renamed_apps.get(app_bin.name),
            )
            if not pl.link_exists():
                self.logger_.log_info(
                    f" 🎯 Exposing program {pl.show_name_with_link()}",
                )
                pl.link()
                exposed_apps[app_bin.name] = UvPipxVenvExposeAppModel(
                    app_bin.name,
                    str(pl.link_path),
                    pkgs_sets,
                )
            elif pl.is_valid():
                self.logger_.log_info(
                    f" 🔵 Already exposed to current uvpipx venv program {pl.show_name_with_link()}",
                )
                exposed_apps[app_bin.name] = UvPipxVenvExposeAppModel(
                    app_bin.name,
                    str(pl.link_path),
                    pkgs_sets,
                )
            else:
                if pl.link_path:
                    self.logger_.log_warn(
                        f" ❌ Not exposing program {app_bin.name}; {pl.link_path} already exist to {pl.link_path.resolve()}!",
                    )
                else:
                    msg = "link_path is None"
                    raise ValueError(msg)

        return exposed_apps

    def remove_exposing(
        self,
        remove_apps: dict[str, Path],
    ) -> None:
        for app_bin, link_path in remove_apps.items():
            if link_path.exists():
                self.logger_.log_info(
                    f" 🗑️  Removing exposing {link_path} -> {app_bin} ",
                )
                link_path.unlink()

    def expose(
        self,
        main_package_name: str,
        expose_app_rules: list[str],
        pkgs_sets: list[str],
    ) -> dict[str, UvPipxVenvExposeAppModel]:
        exposing_apps, renamed_apps = self.get_apps_list(
            expose_app_rules,
            main_package_name,
        )

        exposed_apps = self.add_exposing(exposing_apps, renamed_apps, pkgs_sets)
        remove_apps = self.get_apps_to_remove(exposed_apps)
        self.remove_exposing(remove_apps)

        return exposed_apps

    # TODO add function to clean old link in local bin


def expose(package_name: str, expose_rule_names: list[str]) -> None:
    logger = get_logger("expose")

    logger.log_info(f"🔭  Exposing apps of {package_name}\n")

    expose_rule_names_ = expose_rule_names

    uvpipx_model, venv = uvpipx_load_venv(
        package_name,
    )
    assert uvpipx_model is not None, "uvpipx_model should never be None"  # noqa: S101
    assert uvpipx_model.exposed is not None, "uvpipx_model.exposed should never be None"  # noqa: S101
    expo_app = ExposeApps(venv, logger)
    expo_app.set_prev_exposed(uvpipx_model.exposed)
    package_name = uvpipx_model.main_package.package_name

    uvpipx_model.exposed.apps = expo_app.expose(
        package_name,
        expose_rule_names_,
        [package_name],
    )
    uvpipx_model.save_json("uvpipx.json")

    logger.log_info(
        f" 🟢 uvpipx venv {uvpipx_model.venv.name()} with {package_name} ready",
    )


def expose_all(expose_rule_names: list[str]) -> None:
    logger = get_logger("expose_all")

    infos = ""

    nb = 0
    if config.uvpipx_venvs.exists():
        for pck_venv in config.uvpipx_venvs.iterdir():
            if nb > 0:
                logger.log_info("")
            expose(
                pck_venv.name,
                expose_rule_names,
            )  # This is a tricky way to get the name
            logger.log_info(" ----------------")
            nb += 1

    if nb == 0:
        infos += "⭕ No uvpipx package installed!"

    if infos:
        logger.log_info(infos)
