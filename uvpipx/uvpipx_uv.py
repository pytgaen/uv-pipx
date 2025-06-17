from __future__ import annotations

from uvpipx.internal_libs.misc import shell_run_safe


def uv_get_version() -> str:
    _, stdout, _ = shell_run_safe(["uv", "--version"])  # rc, stderr unused
    return stdout.strip().removeprefix("uv").strip()
