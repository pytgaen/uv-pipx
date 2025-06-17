#!/usr/bin/env python3

from __future__ import annotations

import uvpipx
from uvpipx import config
from uvpipx.exceptions import InstallationFailedError, VenvNotFoundError

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2025 Gaëtan Montury"
__license__ = "GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"
__version__ = "0.5.0"
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"

import shutil
from dataclasses import dataclass

import uvpipx.platform
from uvpipx.internal_libs.Logger import get_logger
from uvpipx.internal_libs.misc import Elapser
from uvpipx.req_spec import Requirement
from uvpipx.uvpipx_expose import ExposeApps
from uvpipx.uvpipx_venv_factory import path_link_from_model, uvpipx_venv_factory
from uvpipx.uvpipx_venv_load import uvpipx_load_venv
from uvpipx.UvPipxModels import (
    UvPipVenvNotReady,
    UvPipxExposedModel,
    UvPipxExposeInstallSets,
    UvPipxModel,
    UvPipxPackageModel,
)


@dataclass
class Installer:
    package_name_spec: str
    expose_rule_names: None | list[str] = None
    inject_pkgs_name_spec: None | list[str] = None
    name_override: None | str = None
    force_reinstall: bool = False

    def __post_init__(self) -> None:
        from uvpipx.uvpipx_core import UvPipxVenv
        from uvpipx.uvpipx_venv_factory import UvPipxVenvModel

        self.logger = get_logger("install")
        self.package_spec = Requirement.from_str(self.package_name_spec)
        self._inject_pkgs_name_spec = self.inject_pkgs_name_spec or []
        self.inject_pkgs_spec = [Requirement.from_str(pkg) for pkg in self._inject_pkgs_name_spec]
        self.all_pkgs_name_spec = [self.package_name_spec, *self._inject_pkgs_name_spec]
        self.all_pkgs_spec = [self.package_spec, *self._inject_pkgs_name_spec]
        self.package_name = self.package_spec.name
        self.prepare_expose_rule_names()
        self.uvpipx_cfg: UvPipxModel | None = None
        self.venv_model: UvPipxVenvModel | None = None
        self.venv: UvPipxVenv | None = None

    def prepare_expose_rule_names(self) -> None:
        self.expose_rule_names_def = self.expose_rule_names or ["__main__"]

    def check_existing_installation(self) -> tuple:
        try:
            uvpipx_prev, venv_prev = uvpipx_load_venv(
                self.package_name,
                self.name_override,
            )
            if self.force_reinstall:
                if uvpipx_prev.exposed and len(uvpipx_prev.exposed.install_sets) > 1:
                    self.logger.log_warn(
                        f"⚠️  {self.package_name} already installed but in multiple steps (install/inject). Manual uninstall/install/inject or just try an upgrade is needed",
                    )
                    return uvpipx_prev, venv_prev, False
            else:
                self.logger.log_warn(
                    f"⚠️  {self.package_name} already installed. Use --force to reinstall from scratch",
                )
                return uvpipx_prev, venv_prev, False
        except (UvPipVenvNotReady, VenvNotFoundError):
            return None, None, True

        return uvpipx_prev, venv_prev, True

    def create_virtual_env_if_needed(self) -> bool:
        assert self.venv is not None, "venv must be initialized before use"  # noqa: S101
        assert self.venv_model is not None, "venv_model must be initialized before use"  # noqa: S101
        created = False
        with Elapser() as ela:
            created = self.venv.create_venv_if_need()
        if created:
            self.logger.log_info(
                ela.ela_str(f" 📦 uv venv {self.venv_model.name()} created"),
            )
        return created

    def install_all_packages(self) -> None:
        assert self.venv is not None, "venv must be initialized before use"  # noqa: S101
        assert self.venv_model is not None, "venv_model must be initialized before use"  # noqa: S101
        with Elapser() as ela:
            self.venv.install(self.all_pkgs_name_spec)
        self.logger.log_info(
            ela.ela_str(
                f" 📥 uv pip install {self.all_pkgs_name_spec} in uvpipx venv {self.venv_model.name()}",
            ),
        )

    def save_pip_infos(self) -> None:
        assert self.venv is not None, "venv must be initialized before use"  # noqa: S101
        (self.venv.venv_path / "requirements.txt").write_text(self.venv.freeze())
        pip_metadata = self.venv.venv_path / "pip_metadata.json"
        uvpipx_console_scripts = config.uvpipx_self_dir / "uvpipx/uvpipx_console_scripts.py"
        python_venv_bin = self.venv.venv_bin_dir() / ("python" + uvpipx.platform.bin_ext)
        self.venv.run_in_venv(
            f"{python_venv_bin} {uvpipx_console_scripts} {self.venv.venv_path} {pip_metadata}",
        )

    def expose_binaries(
        self,
        prev_exposed: None | UvPipxExposedModel = None,
    ) -> None:
        assert self.venv is not None, "venv must be initialized before use"  # noqa: S101
        assert self.uvpipx_cfg is not None, "uvpipx_cfg must be initialized before use"  # noqa: S101
        expo_app = ExposeApps(self.venv, self.logger)
        expo_app.set_prev_exposed(prev_exposed)
        main_install_set = UvPipxExposeInstallSets(
            [self.package_name],
            self.expose_rule_names_def,
        )
        exposed_bins = expo_app.expose(
            self.package_name,
            self.expose_rule_names_def,
            main_install_set.package_name_sets,
        )
        install_sets = [main_install_set]
        self.uvpipx_cfg.exposed = UvPipxExposedModel(
            str(self.venv.venv_bin_dir()),
            install_sets,
            exposed_bins,
        )

    def install(self) -> None:
        uvpipx_prev, _, can_install = self.check_existing_installation()

        if not can_install:
            return

        uvpipx_injected_package = {
            k.name: UvPipxPackageModel(
                k.to_str(),
                k.name,
            )
            for k in self.inject_pkgs_spec
        }

        self.venv_model, self.venv = uvpipx_venv_factory(
            self.package_name,
            self.name_override,
        )
        self.uvpipx_cfg = UvPipxModel(
            venv=self.venv_model,
            main_package=UvPipxPackageModel(self.package_name_spec, self.package_name),
            injected_packages=uvpipx_injected_package,
            exposed=UvPipxExposedModel(str(self.venv.venv_bin_dir())),
        )

        created = self.create_virtual_env_if_needed()
        try:
            self.install_all_packages()

            self.save_pip_infos()
            self.logger.log_info("")
            self.expose_binaries(prev_exposed=uvpipx_prev.exposed if uvpipx_prev else None)
            self.uvpipx_cfg.save_json("uvpipx.json")

            self.logger.log_info(
                f" 🟢 uvpipx venv {self.venv_model.name()} with {self.package_name} ready",
            )
        except Exception as e:
            if created:
                shutil.rmtree(self.venv.venv_path)
                raise InstallationFailedError(
                    self.package_name,
                    f"Installation failed and venv was cleaned up: {e}",
                    self.venv.venv_path,
                ) from e

            raise


def install(
    package_name_spec: str,
    *,
    expose_rule_names: None | list[str] = None,
    inject_pkgs: None | list[str] = None,
    name_override: None | str = None,
    force_reinstall: bool = False,
) -> None:
    config = Installer(
        package_name_spec,
        expose_rule_names=expose_rule_names,
        inject_pkgs_name_spec=inject_pkgs,
        name_override=name_override,
        force_reinstall=force_reinstall,
    )
    config.install()


def uninstall(package_name: str, *, name_override: None | str = None) -> None:
    logger = get_logger("uninstall")
    uvpipx, venv = uvpipx_load_venv(package_name, name_override)
    logger.log_info(f"🪓 Uninstalling {package_name}\n")
    logger.log_info("🗑️  Remove exposed program")
    if uvpipx.exposed:
        for mpl in uvpipx.exposed.apps.values():
            pl = path_link_from_model(uvpipx.exposed, mpl)
            pl.unlink()
            logger.log_info(f" ❌ Remove Exposed program {pl.show_name_with_link()}")
    # TODO also delete injected exposed bin
    logger.log_info(f"\n🗑️  Remove uvpipx venv {venv.venv_path.name}")
    shutil.rmtree(venv.venv_path)
