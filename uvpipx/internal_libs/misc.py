from __future__ import annotations

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
import subprocess  # nosec: B404  # noqa: S404
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple, Type, TypeVar, Union, get_args, get_origin

from uvpipx.internal_libs.Logger import Logger, get_logger


# Définir le chemin du répertoire à parcourir
def find_executable(dir_path: Path, allow_symlink: bool = False) -> List[Path]:
    return [
        file
        for file in dir_path.iterdir()
        if file.is_file()
        and os.access(file, os.X_OK)
        and (not file.is_symlink() or allow_symlink)
    ]


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

    start: Union[None, float] = None
    end: Union[None, float] = None
    interval_seconds: float = -1
    elapsed_second: str = ""

    def __enter__(self) -> Elapser:
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args: list) -> Union[bool, None]:  # , *args
        self.end = time.perf_counter()
        if self.start is None or self.end is None:
            msg = "Missing start or end"
            raise RuntimeError(msg)

        self.interval_seconds = self.end - self.start
        self.elapsed_second = f"{self.interval_seconds:.3f} seconds"
        return None

    def ela_str(self, message: str) -> str:
        return f"{message}   ⏱️  {self.elapsed_second}"


def shell_run(
    command: str,
    *,
    cwd: Union[None, Path] = None,
    env: Union[None, Dict[str, str]] = None,
    raise_on_error: bool = True,
) -> Tuple[int, Union[str], Union[str]]:
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

    opt_args = {}
    if cwd is not None:
        opt_args["cwd"] = cwd

    with subprocess.Popen(
        command,  # type: ignore[arg-type, call-overload]
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
    cwd: Union[Path, str],
    command: Union[str, List[str]],
    *,
    env: Union[None, Dict[str, str]] = None,
    raise_on_error: bool = True,
    raw_pipe: bool = False,
) -> Tuple[Union[int, Any], Union[None, str], Union[None, str]]:
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

    with subprocess.Popen(
        command,
        stdout=pipe_type,
        stderr=pipe_type,
        cwd=cwd,
        shell=True,  # nosec: B602 # noqa: S602
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
        short_msg = f"{stderr:2000}".rstrip()
        msg = f"🔴 Command failed with return code {rc} {short_msg}..."
        raise RuntimeError(msg)

    return rc, stdout, stderr


def cmd_prepare_env(env: Union[None, Dict[str, str]]) -> Dict[str, str]:
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


class InvalidTypeError(Exception):
    def __init__(self, expected_types: List[Type], actual_type: Type) -> None:
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


def check_type(value: Any, expected_types: Union[Type[T], List[Type[T]]]) -> T:  # noqa: ANN401
    expected_types_ = (
        expected_types if isinstance(expected_types, list) else [expected_types]
    )
    if value is None:
        raise InvalidTypeError(expected_types_, type(value))

    for expected_type in expected_types_:
        origin = get_origin(expected_type)
        if origin:
            args = get_args(expected_type)
            if isinstance(value, origin) and all(
                isinstance(elem, args[0]) for elem in value
            ):
                return value

        if isinstance(value, expected_type):
            return value

    raise InvalidTypeError(expected_types_, type(value))


def check_type_n_None(
    value: Any,  # noqa: ANN401
    expected_types: Union[Type[T], List[Type[T]]],
) -> Union[T, None]:
    expected_types_ = (
        expected_types if isinstance(expected_types, list) else [expected_types]
    )
    if value is None:
        return value

    try:
        for expected_type in expected_types_:
            origin = get_origin(expected_type)
            if origin:
                args = get_args(expected_type)
                if isinstance(value, origin) and all(
                    isinstance(elem, args[0]) for elem in value
                ):
                    return value

            if isinstance(value, expected_type):
                return value
    except Exception as e:
        raise InvalidTypeError(expected_types_, type(value)) from e

    raise InvalidTypeError(expected_types_, type(value))
