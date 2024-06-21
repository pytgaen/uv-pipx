from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Union

from uvpipx import config
from uvpipx.internal_libs.misc import find_executable

# cat /home/gaetan/.local/uv-pipx/venvs/jc/uvpipx.json


class UvPipVenvNotReady(Exception):
    def __init__(self, message: str, error_code: Union[None, int] = None) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


@dataclass
class ExposeBin:  # TODO remove
    venv_path: Path
    bin_name: str
    local_bin_name: Union[None, Path] = None

    def venv_bin_name(self) -> Path:
        return self.venv_path / ".venv/bin" / self.bin_name

    def exists(self) -> bool:
        return self.venv_bin_name().exists()

    def link_exists(self) -> bool:
        if self.local_bin_name is None:
            msg = "Link not defined"
            raise RuntimeError(msg)

        return self.local_bin_name.exists()

    def valid(self) -> bool:
        if self.local_bin_name.exists():
            return self.local_bin_name.is_symlink() and (
                self.venv_bin_name() == self.local_bin_name.resolve()
            )

        return False

    @classmethod
    def build_local_bin_name(
        cls,  # noqa: ANN102
        venv_path: Path,
        bin_name: str,
        alias_bin_name: Union[None, str] = None,
    ) -> Path:
        bin_name = alias_bin_name or bin_name
        return cls(venv_path, bin_name, Path(config.uvpipx_local_bin) / bin_name)

    def link(self) -> None:
        os.symlink(self.venv_bin_name(), self.local_bin_name)

    def unlink(self, if_valid: bool = True) -> None:
        if (if_valid and self.valid()) or (not if_valid and self.exists()):
            self.local_bin_name.unlink()


@dataclass
class UvPipxTransi:  # TODO remove
    """transitionnal class to manage save config"""

    package_name: str
    name_override: Union[None, str]
    exposed_bins: Union[List[ExposeBin]] = None

    def __post_init__(self) -> None:
        self.venv_name_ = self.name_override or self.package_name
        self.pck_venv = config.uvpipx_venvs / self.venv_name_
        if self.exists():
            self.load()

    def dir_bins_to_expose(self, expose_bin_names: list[str]) -> list[ExposeBin]:
        expose_bin_names_ = expose_bin_names
        if len(expose_bin_names_) == 1:
            if expose_bin_names_[0] == "*":
                exe = find_executable(self.pck_venv / ".venv" / "bin")
                expose_bin_names_ = [
                    s.name for s in exe if not s.name.startswith("python")
                ]
            elif expose_bin_names_[0] == "_":
                expose_bin_names_ = []

        prep_expose_bins: list[ExposeBin] = []
        for bin_name in expose_bin_names_:
            bin_name_, local_bin_name = (
                bin_name.split(":") if ":" in bin_name else (bin_name, bin_name)
            )
            prep_expose_bins.append(
                ExposeBin.build_local_bin_name(self.pck_venv, bin_name_, local_bin_name),
            )

        return prep_expose_bins
        # self.exposed_bins = prep_expose_bins
