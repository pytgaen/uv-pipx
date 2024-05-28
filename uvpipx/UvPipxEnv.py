from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Union

from uvpipx import config
from uvpipx.internal_libs.misc import find_executable

# cat /home/gaetan/.local/uv-pipx/venvs/jc/uvpipx.json


@dataclass
class ExposeBin:
    venv_path: Path
    venv_bin_name: str
    local_bin_path: Union[None, Path] = None

    def venv_bin_path(self) -> Path:
        return self.venv_path / ".venv/bin" / self.venv_bin_name

    def exists(self) -> bool:
        return self.venv_bin_path().exists()

    def link_exists(self) -> bool:
        if self.local_bin_path is None:
            msg = "Link not defined"
            raise RuntimeError(msg)

        return self.local_bin_path.exists()

    def valid(self) -> bool:
        if self.local_bin_path.exists():
            return self.local_bin_path.is_symlink() and (
                self.venv_bin_path() == self.local_bin_path.resolve()
            )

        return False

    @classmethod
    def build_local_bin_path(
        cls,
        venv_path: Path,
        venv_bin_name: str,
        alias_bin_name: Union[None, str] = None,
    ) -> Path:
        bin_name = alias_bin_name or venv_bin_name
        return cls(venv_path, venv_bin_name, Path(config.uvpipx_local_bin) / bin_name)

    def link(self) -> None:
        os.symlink(self.venv_bin_path(), self.local_bin_path)

    def unlink(self, if_valid: bool = True) -> None:
        if (if_valid and self.valid()) or (not if_valid and self.exists()):
            self.local_bin_path.unlink()


@dataclass
class UvPipx:
    package_name: str
    venv_name: Union[None, str]
    exposed_bins: Union[List[ExposeBin]] = None

    def __post_init__(self):
        self.venv_name_ = self.venv_name or self.package_name
        self.pck_venv = config.uvpipx_venvs / self.venv_name_
        if self.exists():
            self.load()

    def exists(self) -> bool:
        return self.pck_venv.exists()

    def saved_bin_exposed(self) -> List[ExposeBin]:
        return [
            ExposeBin(
                venv_path=self.pck_venv,
                venv_bin_name=Path(exposed_bin[0]).name,
                local_bin_path=Path(exposed_bin[1]),
            )
            for exposed_bin in self.uvpipx_dict.get("exposed_bins", [])
        ]

    def load(self) -> None:
        # expose_bin_names_ = expose_bin_names or ["*"]

        with (self.pck_venv / "uvpipx.json").open() as outfile:
            self.uvpipx_dict = json.load(outfile)

    def save(self, uvpipx_dict: dict[str, Any]) -> None:
        with (self.pck_venv / "uvpipx.json").open("w") as outfile:
            json.dump(uvpipx_dict, outfile, indent=4, default=str)

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
            venv_bin_name, local_bin_name = (
                bin_name.split(":") if ":" in bin_name else (bin_name, bin_name)
            )
            prep_expose_bins.append(
                ExposeBin.build_local_bin_path(
                    self.pck_venv, venv_bin_name, local_bin_name
                )
            )

        return prep_expose_bins
        # self.exposed_bins = prep_expose_bins
