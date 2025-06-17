"""
Business exceptions for uvpipx.

This module defines a hierarchy of domain-specific exceptions that provide
better error context and handling than generic RuntimeError.
"""

from __future__ import annotations

from pathlib import Path


class UvPipxError(Exception):
    """Base exception for all uvpipx errors."""

    pass


class BinaryNotFoundError(UvPipxError):
    """Raised when a required binary is not found in the venv."""

    def __init__(self, binary_name: str, venv_path: Path, available: list[str] | None = None) -> None:
        self.binary_name = binary_name
        self.venv_path = venv_path
        self.available = available or []

        avail_str = f"\nAvailable binaries: {', '.join(self.available)}" if self.available else ""
        super().__init__(
            f"Binary '{binary_name}' not found in {venv_path}{avail_str}\n\n"
            f"This usually means the package doesn't provide this executable.\n"
            f"Try: uvpipx info {venv_path.name} to see available binaries."
        )


class PackageAlreadyInjectedError(UvPipxError):
    """Raised when attempting to inject an already injected package."""

    def __init__(self, package_name: str, venv_name: str) -> None:
        self.package_name = package_name
        self.venv_name = venv_name
        super().__init__(
            f"Package '{package_name}' is already injected in venv '{venv_name}'.\n\n"
            f"To upgrade: uvpipx upgrade {venv_name}\n"
            f"To force reinstall: uvpipx uninstall {venv_name} && uvpipx install {venv_name} --inject {package_name}"
        )


class InstallationFailedError(UvPipxError):
    """Raised when package installation fails."""

    def __init__(self, package_name: str, reason: str, venv_path: Path | None = None) -> None:
        self.package_name = package_name
        self.reason = reason
        self.venv_path = venv_path

        venv_str = f"\nVenv path: {venv_path}" if venv_path else ""
        super().__init__(
            f"Failed to install '{package_name}': {reason}{venv_str}\n\n"
            f"Common causes:\n"
            f"  - Package doesn't exist on PyPI\n"
            f"  - Network connectivity issues\n"
            f"  - Dependency conflicts\n\n"
            f"Try: uv pip install {package_name} --dry-run to diagnose"
        )


class VenvNotFoundError(UvPipxError):
    """Raised when a venv doesn't exist."""

    def __init__(self, venv_name: str, venv_path: Path) -> None:
        self.venv_name = venv_name
        self.venv_path = venv_path
        super().__init__(
            f"Virtual environment '{venv_name}' not found at {venv_path}\n\n"
            f"Available venvs: uvpipx list\n"
            f"Install with: uvpipx install {venv_name}"
        )


class InvalidExposeRuleError(UvPipxError):
    """Raised when an invalid exposure rule is provided."""

    def __init__(self, rule: str, package_name: str, available_binaries: list[str] | None = None) -> None:
        self.rule = rule
        self.package_name = package_name
        self.available_binaries = available_binaries or []

        avail_str = ""
        if self.available_binaries:
            avail_str = f"\n\nAvailable binaries in {package_name}:\n  " + "\n  ".join(self.available_binaries)

        super().__init__(
            f"Invalid expose rule: '{rule}'\n\n"
            f"Valid expose rules:\n"
            f"  __main__     - Expose programs from main package (default)\n"
            f"  __eponym__   - Expose only program with same name as package\n"
            f"  __all__      - Expose all programs in venv\n"
            f"  custom,list  - Expose specific programs: jc,othertool{avail_str}\n\n"
            f"Example:\n"
            f"  uvpipx expose {package_name} __main__\n"
            f"  uvpipx expose {package_name} jc,jc-cli"
        )


class PathValidationError(UvPipxError):
    """Raised when path validation fails (security)."""

    def __init__(self, path: Path, reason: str) -> None:
        self.path = path
        self.reason = reason
        super().__init__(
            f"Path validation failed: {path}\nReason: {reason}\n\nThis is a security measure to prevent path traversal attacks."
        )


class VenvNotReadyError(UvPipxError):
    """Raised when trying to use a venv that isn't fully initialized."""

    def __init__(self, venv_path: Path, missing: str) -> None:
        self.venv_path = venv_path
        self.missing = missing
        super().__init__(
            f"Virtual environment at {venv_path} is not ready.\n"
            f"Missing: {missing}\n\n"
            f"Try reinstalling: uvpipx uninstall {venv_path.name} && uvpipx install {venv_path.name}"
        )


class CommandExecutionError(UvPipxError):
    """Raised when a command execution fails."""

    def __init__(self, command: list[str] | str, return_code: int, stderr: str) -> None:
        self.command = command
        self.return_code = return_code
        self.stderr = stderr

        cmd_str = " ".join(command) if isinstance(command, list) else command
        stderr_short = stderr[:500] if stderr else "(no error output)"

        super().__init__(f"Command failed with return code {return_code}\nCommand: {cmd_str}\nError: {stderr_short}")
