from __future__ import annotations

import uvpipx

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2025 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.2.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"


import hashlib
import os
import platform
import shutil
import subprocess  # nosec: B404  # noqa: S404
import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeVar, get_args, get_origin

import uvpipx.platform
from uvpipx.exceptions import CommandExecutionError, PathValidationError
from uvpipx.internal_libs.Logger import Logger, get_logger


# Définir le chemin du répertoire à parcourir
def find_executable(dir_path: Path, allow_symlink: bool = False) -> list[Path]:
    if uvpipx.platform.sys_platform == "win":
        return [file for file in dir_path.iterdir() if file.is_file() and file.suffix.lower() == uvpipx.platform.bin_ext.lower()]

    return [file for file in dir_path.iterdir() if file.is_file() and os.access(file, os.X_OK) and (not file.is_symlink() or allow_symlink)]


@dataclass
class Elapser:
    """
    A context manager for measuring elapsed time.

    Explanation:
    This class can be used as a context manager to measure the elapsed time within the context block.

    Args:
        None

    Returns:
        None

    Examples:
        with Elapser() as elapser:
            # Code block to measure elapsed time
    """

    start: None | float = None
    end: None | float = None
    interval_seconds: float = -1
    elapsed_second: str = ""

    def __enter__(self) -> Elapser:
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args: list) -> bool | None:  # , *args
        self.end = time.perf_counter()
        if self.start is None or self.end is None:
            msg = "Missing start or end"
            raise RuntimeError(msg)

        self.interval_seconds = self.end - self.start
        self.elapsed_second = f"{self.interval_seconds:.3f} seconds"
        return None

    def ela_str(self, message: str) -> str:
        return f"{message}   ⏱️  {self.elapsed_second}"


def shell_run_safe(
    command: list[str],
    *,
    cwd: None | Path = None,
    env: None | dict[str, str] = None,
    raise_on_error: bool = True,
) -> tuple[int, str, str]:
    """
    Executes a shell command safely without shell injection risk.

    This function runs commands with shell=False, preventing command injection
    vulnerabilities. All arguments are passed as a list to subprocess.

    Security:
        - NO shell injection possible (shell=False)
        - Arguments properly escaped by subprocess
        - Safe for untrusted input

    Args:
        command: List of command and arguments (e.g., ["uv", "pip", "install", "package"])
        cwd: Working directory for command execution
        env: Environment variables to set
        raise_on_error: Raise RuntimeError if command fails

    Returns:
        Tuple of (return_code, stdout, stderr)

    Raises:
        RuntimeError: If command fails and raise_on_error=True

    Example:
        >>> shell_run_safe(["uv", "pip", "list"])
        (0, "package==1.0.0\\n", "")

        >>> shell_run_safe(["uv", "pip", "install", "ruff==0.8.1"])
        (0, "", "")
    """
    env_ = cmd_prepare_env(env)

    opt_args = {}
    if cwd is not None:
        opt_args["cwd"] = cwd

    with subprocess.Popen(  # noqa: S603  # nosec: B603
        command,  # List of args - safe from injection
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,  # SECURE: No shell interpretation
        text=True,
        env=env_,
        **opt_args,
    ) as proc:
        try:
            stdout, stderr = proc.communicate()
        except subprocess.SubprocessError as e:
            if raise_on_error:
                raise CommandExecutionError(command, -1, f"Subprocess error: {e}") from e
            stdout, stderr = "", str(e)

        rc = proc.returncode
        if rc != 0 and raise_on_error:
            raise CommandExecutionError(command, rc, stderr)

    return rc, stdout, stderr


def shell_run(
    command: str,
    *,
    cwd: None | Path = None,
    env: None | dict[str, str] = None,
    raise_on_error: bool = True,
) -> tuple[int, str, str]:
    """
    DEPRECATED: Use shell_run_safe() instead for security.

    This function uses shell=True which is vulnerable to command injection.
    Will be removed in v1.0.0.

    Args:
        command: Shell command string (UNSAFE - can be injected)
        raise_on_error: Flag to raise an error if the command execution fails

    Returns:
        Tuple[int, str, str]: A tuple containing the return code, standard output, and standard error.

    Security Warning:
        This function is vulnerable to shell injection attacks.
        Migrate to shell_run_safe() immediately.
    """
    import warnings

    warnings.warn(
        "shell_run() with shell=True is deprecated and insecure. Use shell_run_safe() with list of arguments instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    env_ = cmd_prepare_env(env)
    # encoding = cmd_prepare_encoding()

    opt_args = {}
    if cwd is not None:
        opt_args["cwd"] = cwd

    stdout = ""
    stderr = ""
    rc = 0
    with subprocess.Popen(  # nosec: B602 # noqa: S602
        command,  # type: ignore[arg-type, call-overload]
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,  # nosec: B602 # noqa: S602 # nosemgrep: python.lang.security.audit.subprocess-shell-true.subprocess-shell-true
        text=True,
        env=env_,
        **opt_args,
    ) as proc:  # nosec: B602
        try:
            stdout, stderr = proc.communicate()
        except subprocess.SubprocessError:
            if raise_on_error:
                raise

        rc = proc.returncode
        # stdout = stdout.decode(encoding)
        # stderr = stderr.decode(encoding)
        if rc != 0 and raise_on_error:
            short_msg = f"{stderr:2000}".rstrip()
            msg = f"🔴 Command failed with return code {rc} {short_msg}..."
            raise RuntimeError(
                msg,
            )

    return rc, stdout, stderr


def cmd_run(
    cwd: Path | str,
    command: str | list[str],
    *,
    env: None | dict[str, str] = None,
    raise_on_error: bool = True,
    raw_pipe: bool = False,
) -> tuple[int | Any, None | str, None | str]:
    """
    Executes a shell command and returns the result.

    Explanation:
    This function runs a shell command and captures the standard output, standard error, and return code.

    Args:
        command (List[str]): The shell command to be executed.
        raise_on_error (bool): Flag to raise an error if the command execution fails. Default is False.

    Returns:
        Tuple[int, str, str]: A tuple containing the return code, standard output, and standard error.
    """
    env_ = cmd_prepare_env(env)
    # encoding = cmd_prepare_encoding()
    pipe_type = None if raw_pipe else subprocess.PIPE

    stdout: str | None = ""
    stderr: str | None = ""
    rc = 0
    with subprocess.Popen(  # nosec: B602 # noqa: S602
        command,
        stdout=pipe_type,
        stderr=pipe_type,
        cwd=cwd,
        shell=True,  # nosec: B602 # noqa: S602 # nosemgrep: python.lang.security.audit.subprocess-shell-true.subprocess-shell-true
        text=True,
        env=env_,
    ) as proc:
        try:
            if raw_pipe:
                stdout, stderr = (None, None)
                proc.wait()
            else:
                stdout, stderr = proc.communicate()
                # stdout = stdout.decode(encoding)
                # stderr = stderr.decode(encoding)
        except subprocess.SubprocessError:
            if raise_on_error:
                raise

    rc = proc.returncode
    if rc != 0 and raise_on_error:
        short_msg = f"{stderr:2000}".rstrip() if stderr else ""
        msg = f"🔴 Command failed with return code {rc} {short_msg}..."
        raise RuntimeError(msg)

    return rc, stdout, stderr


def cmd_prepare_env(env: None | dict[str, str]) -> dict[str, str]:
    env_ = env
    if env_ is None:
        env_ = os.environ.copy()
        k_to_del = [k for k in env_ if "VIRTUAL_ENV" in k]
        for k in k_to_del:
            del env_[k]
    return env_


def cmd_prepare_encoding() -> str:
    os_type = platform.system()
    encoding = "utf-8"
    if os_type == "Windows":
        encoding = "utf-16"
    #     if "powershell" in command[0]:
    #         # command = ["powershell", "-Command"] + command
    #         encoding = 'utf-16'
    #     else:
    #         # command = ["cmd", "/c"] + command
    #         encoding = 'oem'
    return encoding


def shell_run_elapse(
    command: str,
    message: str,
    *,
    raise_on_error: bool = True,
    logger: None | Logger = None,
) -> None:
    logger_ = logger or get_logger("shell_run_elapse")
    with Elapser() as ela:
        _ = shell_run(command, raise_on_error=raise_on_error)  # rc, std_o, std_e unused

    logger_.log_info(f"{message}   ⏱️  {ela.elapsed_second}")


def validate_venv_path(venv_path: Path, base_dir: Path) -> Path:
    """
    Validate venv path to prevent directory traversal attacks.

    Security:
        - Prevents path traversal (../../../etc/passwd)
        - Ensures path is within allowed base directory
        - Rejects hidden directory components
        - Resolves symlinks for validation

    Args:
        venv_path: Path to validate
        base_dir: Base directory that must contain venv_path

    Returns:
        Resolved absolute path if valid

    Raises:
        ValueError: If path is invalid or outside base_dir

    Example:
        >>> validate_venv_path(Path("ruff"), Path("/home/user/.local/uv-pipx/venvs"))
        Path('/home/user/.local/uv-pipx/venvs/ruff')

        >>> validate_venv_path(Path("../../etc"), Path("/home/user/.local/uv-pipx/venvs"))
        ValueError: Path traversal detected
    """
    try:
        # Resolve to absolute path (follows symlinks)
        resolved = venv_path.resolve()
        base_resolved = base_dir.resolve()

        # Check if path is within base_dir
        try:
            relative_path = resolved.relative_to(base_resolved)
        except ValueError as e:
            raise PathValidationError(venv_path, f"Path traversal detected: path is outside {base_dir}") from e

        # Check for hidden directory components in the relative path only (security risk)
        for part in relative_path.parts:
            if part.startswith(".") and part not in (".", ".."):
                raise PathValidationError(venv_path, f"Hidden directory component not allowed: {part}")

        return resolved

    except (RuntimeError, OSError) as e:
        raise PathValidationError(venv_path, f"Invalid path: {e}") from e


def command_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None


class InvalidTypeError(Exception):
    def __init__(self, expected_types: Sequence[type], actual_type: type) -> None:
        self.expected_types = expected_types
        self.actual_type = actual_type
        super().__init__(self.__str__())

    def __str__(self) -> str:
        expected = ", ".join([t.__name__ for t in self.expected_types])
        return f"Invalid type: expected one of ({expected}), got {self.actual_type.__name__}"


# def check_type(value: Any, expected_types: List[Union[Type, None]]) -> None:
#     if not any(isinstance(value, t) for t in expected_types):
#         raise InvalidTypeError(expected_types, type(value))

T = TypeVar("T")


def check_type(value: Any, expected_types: type[T] | Sequence[type[T]]) -> T:  # noqa: ANN401
    expected_types_ = (
        list(expected_types) if isinstance(expected_types, Sequence) and not isinstance(expected_types, type) else [expected_types]
    )
    if value is None:
        raise InvalidTypeError(expected_types_, type(value))

    for expected_type in expected_types_:
        origin = get_origin(expected_type)
        if origin:
            args = get_args(expected_type)
            if isinstance(value, origin) and all(isinstance(elem, args[0]) for elem in value):
                return value

        if isinstance(value, expected_type):
            return value

    raise InvalidTypeError(expected_types_, type(value))


def check_type_n_None(
    value: Any,  # noqa: ANN401
    expected_types: type[T] | Sequence[type[T]],
) -> T | None:
    expected_types_ = (
        list(expected_types) if isinstance(expected_types, Sequence) and not isinstance(expected_types, type) else [expected_types]
    )
    if value is None:
        return value

    try:
        for expected_type in expected_types_:
            origin = get_origin(expected_type)
            if origin:
                args = get_args(expected_type)
                if isinstance(value, origin) and all(isinstance(elem, args[0]) for elem in value):
                    return value

            if isinstance(value, expected_type):
                return value
    except Exception as e:
        raise InvalidTypeError(expected_types_, type(value)) from e

    raise InvalidTypeError(expected_types_, type(value))


def file_md5(file_path) -> str:
    md5_hash = hashlib.md5(usedforsecurity=False)
    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    with file_path.open(mode="rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()
