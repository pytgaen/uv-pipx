from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Union

from uvpipx.internal_libs.misc import find_executable, shell_run
from uvpipx.req_spec import Requirement


@dataclass
class UvPipxVenv:
    venv_path: Path

    def exists(self) -> bool:
        return (self.venv_path / ".venv").exists()

    def create_venv_if_need(self) -> bool:
        self.venv_path.mkdir(exist_ok=True, parents=True)

        if not self.exists():
            rc, std_o, std_e = shell_run(
                f"uv venv {self.venv_path / '.venv'}", raise_on_error=True,
            )
            return True
        return False

    def freeze(self) -> str:
        rc, stdout, stderr = shell_run("uv pip freeze", cwd=self.venv_path)
        return stdout if isinstance(stdout, str) else stdout.decode("utf-8")

    def installed_package(self) -> list[Requirement]:
        return self.freeze().rstrip().split("\n")

    def installed_package_as_req(self) -> list[Requirement]:
        req = self.freeze().rstrip().split("\n")
        req_tuple = [Requirement.from_str(r) for r in req]

        return req_tuple

    def install(self, package_name_spec: str, allow_upgrade: bool = False) -> str:
        opt = " --upgrade" if allow_upgrade else ""
        rc, stdout, stderr = shell_run(
            f"uv pip install{opt} {package_name_spec}", cwd=self.venv_path,
        )
        return stdout if isinstance(stdout, str) else stdout.decode("utf-8")

    def uninstall(self, package_name_spec: str) -> str:
        rc, stdout, stderr = shell_run(
            f"uv pip uninstall {package_name_spec}", cwd=self.venv_path,
        )
        return stdout if isinstance(stdout, str) else stdout.decode("utf-8")

    def venv_bins(self, regex_to_exclude: list[str]) -> list[Path]:
        re_comp_to_exclude = [re.compile(r) for r in regex_to_exclude]
        all_bins = find_executable(self.venv_path / ".venv/bin")
        return [
            s for s in all_bins if not any(r.search(s.name) for r in re_comp_to_exclude)
        ]

    def venv_bin(self, name: str, fail_if_notexist: bool = True) -> Path:
        path_ = self.venv_path / ".venv/bin" / name

        if fail_if_notexist and not path_.exists():
            msg = f"🔴 {name} not exist (path {path_})"
            raise RuntimeError(msg)

        return path_


@dataclass
class PathLink:
    local_path: Path
    link_path: Union[Path, None] = None

    def exists(self) -> bool:
        return self.local_path.exists()

    def link_exists(self) -> bool:
        if self.link_path is None:
            msg = "Link not defined"
            raise RuntimeError(msg)

        return self.link_path.exists()

    def is_valid(self) -> bool:
        if self.link_path.exists():
            return self.link_path.is_symlink() and (
                self.local_path == self.link_path.resolve()
            )

        return False

    def link(self) -> None:
        os.symlink(self.local_path, self.link_path)

    def unlink(self, if_valid: bool = True) -> None:
        if (if_valid and self.is_valid()) or (not if_valid and self.exists()):
            self.link_path.unlink()

    def show_name_with_link(self) -> str:
        return (
            self.link_path.name
            if self.link_path.name == self.local_path.name
            else f" {self.local_path.name} -> {self.link_path.name}"
        )
