from __future__ import annotations

from uvpipx.internal_libs.misc import shell_run


def uv_get_version() -> str:
    rc, stdout, stderr = shell_run("uv --version")
    return stdout.strip().removeprefix("uv").strip()
