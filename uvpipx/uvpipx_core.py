from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import uvpipx.platform
from uvpipx import config
from uvpipx.exceptions import BinaryNotFoundError
from uvpipx.internal_libs.misc import (
    file_md5,
    find_executable,
    shell_run,
    shell_run_safe,
    validate_venv_path,
)
from uvpipx.req_spec import Requirement


@dataclass
class UvPipxVenv:
    venv_path: Path

    def __post_init__(self) -> None:
        """
        Validate venv_path on initialization to prevent path traversal.

        Security:
            Ensures venv_path is within UVPIPX_LOCAL_VENVS directory.
            Prevents directory traversal attacks.

        Raises:
            ValueError: If venv_path is invalid or outside allowed directory
        """
        # Validate path is within allowed venvs directory
        self.venv_path = validate_venv_path(self.venv_path, config.uvpipx_venvs)

    def exists(self) -> bool:
        return (self.venv_path / ".venv").exists()

    def create_venv_if_need(self) -> bool:
        self.venv_path.mkdir(exist_ok=True, parents=True)

        if not self.exists():
            venv_path_str = str(self.venv_path / ".venv")
            _ = shell_run_safe(  # rc, stdout, stderr unused
                ["uv", "venv", venv_path_str],
                raise_on_error=True,
            )
            return True
        return False

    def freeze(self) -> str:
        _, stdout, _ = shell_run_safe(["uv", "pip", "freeze"], cwd=self.venv_path)  # rc, stderr unused
        return stdout  # if isinstance(stdout, str) else stdout.decode("utf-8")

    def installed_package(self) -> list[str]:
        return self.freeze().rstrip().split("\n")

    def installed_package_as_req(self) -> list[Requirement]:
        req = self.freeze().rstrip().split("\n")
        req_tuple = [Requirement.from_str(r) for r in req]

        return req_tuple

    def install(
        self,
        packages_name_spec: list[str],
        allow_upgrade: bool = False,
    ) -> str:
        cmd = ["uv", "pip", "install"]
        if allow_upgrade:
            cmd.append("--upgrade")
        cmd.extend(packages_name_spec)
        _, stdout, _ = shell_run_safe(  # rc, stderr unused
            cmd,
            cwd=self.venv_path,
        )
        return stdout  # if isinstance(stdout, str) else stdout.decode("utf-8")

    def uninstall(self, package_name_spec: str) -> str:
        _, stdout, _ = shell_run_safe(  # rc, stderr unused
            ["uv", "pip", "uninstall", package_name_spec],
            cwd=self.venv_path,
        )
        return stdout  # if isinstance(stdout, str) else stdout.decode("utf-8")

    def venv_bin_dir(self) -> Path:
        return self.venv_path / ".venv" / uvpipx.platform.venv_bin_dir

    def venv_bins(self, regex_to_exclude: list[str]) -> list[Path]:
        re_comp_to_exclude = [re.compile(r) for r in regex_to_exclude]
        all_bins = find_executable(self.venv_bin_dir())
        return [s for s in all_bins if not any(r.search(s.name) for r in re_comp_to_exclude)]

    def venv_bin(self, name: str, fail_if_notexist: bool = True) -> Path:
        path_ = self.venv_bin_dir() / (name + uvpipx.platform.bin_ext)

        if fail_if_notexist and not path_.exists():
            # Get available binaries for helpful error message
            available = [p.stem for p in find_executable(self.venv_bin_dir())]
            raise BinaryNotFoundError(name, self.venv_path, available)

        return path_

    def run_in_venv(
        self,
        cmdline: str,
        *,
        cwd: None | Path = None,
        env: None | dict[str, str] = None,
    ) -> tuple[int, str, str]:
        """
        Run a command in the venv context.

        WARNING: This uses shell=True for user-provided commands (uvpipx venv pkg -- cmd).
        This is intentional to allow shell features, but means the cmdline must be trusted.

        Args:
            cmdline: Shell command to execute (USER INPUT - must be trusted)
            cwd: Working directory
            env: Environment variables

        Returns:
            Tuple of (return_code, stdout, stderr)

        Security Note:
            Only use with trusted input (direct user commands).
            Never pass package names or untrusted data here.
        """
        rc, stdout, stderr = shell_run(cmdline, cwd=cwd, env=env)
        if rc != 0:
            msg = f"🔴 Command failed with return code {rc} {stdout} {stderr}"
            raise RuntimeError(msg)

        return rc, stdout, stderr

    def update_metadata(self, if_not_exist: bool = True) -> None:
        pip_metadata = self.venv_path / "pip_metadata.json"
        if pip_metadata.exists() and if_not_exist:
            return

        uvpipx_console_scripts = config.uvpipx_self_dir / "uvpipx/uvpipx_console_scripts.py"
        python_venv_bin = self.venv_bin_dir() / "python"
        self.run_in_venv(
            f"{python_venv_bin} {uvpipx_console_scripts} {self.venv_path} {pip_metadata}",
        )


@dataclass
class PathLink:
    local_path: Path
    link_path: Path | None = None

    def exists(self) -> bool:
        return self.local_path.exists()

    def link_exists(self) -> bool:
        if self.link_path is None:
            msg = "Link not defined"
            raise RuntimeError(msg)

        return self.link_path.exists()

    def is_valid(self) -> bool:
        if self.link_path is None:
            msg = "link_path is None"
            raise ValueError(msg)

        if uvpipx.platform.sys_platform == "win":
            return self.link_path.exists() and file_md5(self.link_path) == file_md5(
                self.local_path,
            )

        if self.link_path.exists():
            return self.link_path.is_symlink() and (self.local_path == self.link_path.resolve())

        return False

    def link(self) -> None:
        if self.link_path is None:
            msg = "link_path is None"
            raise ValueError(msg)

        if uvpipx.platform.sys_platform == "win":
            shutil.copy2(self.local_path, self.link_path)
        else:
            os.symlink(self.local_path, self.link_path)

    def unlink(self, if_valid: bool = True) -> None:
        if self.link_path is None:
            msg = "link_path is None"
            raise ValueError(msg)

        if (if_valid and self.is_valid()) or (not if_valid and self.exists()):
            self.link_path.unlink()
        # TODO maybe is not valid we shoud explain this

    def show_name_with_link(self) -> str:
        if self.link_path is None:
            msg = "link_path is None"
            raise ValueError(msg)

        return self.link_path.name if self.link_path.name == self.local_path.name else f" {self.local_path.name} -> {self.link_path.name}"
