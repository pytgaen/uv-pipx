from __future__ import annotations

from uvpipx.internal_libs.Logger import Logger, get_logger

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.2.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"


import os
import platform
import shutil
import subprocess  # nosec: B404
import time
from pathlib import Path
from typing import Dict, List, Tuple, Union


# Définir le chemin du répertoire à parcourir
def find_executable(dir_path: Path, allow_symlink: bool = False) -> List[Path]:
    return [
        file
        for file in dir_path.iterdir()
        if file.is_file()
        and os.access(file, os.X_OK)
        and (not file.is_symlink() or allow_symlink)
    ]


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

    def __init__(self) -> None:
        self.start = None
        self.end = None
        self.interval_seconds = None
        self.elapsed_second = None

    def __enter__(self) -> Elapser:
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args: list) -> Union[bool, None]:  # , *args
        self.end = time.perf_counter()
        self.interval_seconds = self.end - self.start
        self.elapsed_second = f"{self.interval_seconds:.3f} seconds"

    def ela_str(self, message: str) -> str:
        return f"{message}   ⏱️  {self.elapsed_second}"


def shell_run(
    command: str,
    *,
    cwd: Union[None, Path] = None,
    env: Union[None, Dict[str, str]] = None,
    raise_on_error: bool = True,
) -> Tuple[int, Union[bytes, str], Union[bytes, str]]:
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
    encoding = cmd_prepare_encoding()  # noqa: F841

    opt_args = {}
    if cwd is not None:
        opt_args["cwd"] = cwd

    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,  # noqa: S602
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
    cwd: str,
    command: str,
    *,
    env: Union[None, Dict[str, str]] = None,
    raise_on_error: bool = True,
    raw_pipe: bool = False,
) -> Tuple[int, Union[bytes, str], Union[bytes, str]]:
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
    encoding = cmd_prepare_encoding()  # noqa: F841
    pipe_type = None if raw_pipe else subprocess.PIPE

    with subprocess.Popen(   
        command,
        stdout=pipe_type,
        stderr=pipe_type,
        cwd=cwd,
        shell=True,   # noqa: S602  # nosec: B602
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
        short_msg = f"{stderr:2000}".rstrip()
        msg = f"🔴 Command failed with return code {rc} {short_msg}..."
        raise RuntimeError(msg)

    return rc, stdout, stderr


def cmd_prepare_env(env: Dict[str, str]) -> Dict[str, str]:
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
    logger: Union[None, Logger] = None,
) -> None:
    logger_ = logger or get_logger("shell_run_elapse")
    with Elapser() as ela:
        rc, std_o, std_e = shell_run(command, raise_on_error=raise_on_error)

    logger_.log_info(f"{message}   ⏱️  {ela.elapsed_second}")


def command_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None
