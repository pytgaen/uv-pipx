from __future__ import annotations

import os
import subprocess  # nosec: B404 # noqa: S404
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator, Tuple

import pytest


@pytest.fixture(scope="class")
def env_setup() -> Generator[Tuple[str, Dict, str], Any, None]:
    # Créer des répertoires temporaires
    with tempfile.TemporaryDirectory(
        prefix="uvpipxbindir-",
    ) as uvpipx_bin_dir, tempfile.TemporaryDirectory(
        prefix="uvpipxvenvs-",
    ) as uvpipx_local_venvs:
        # Configurer les variables d'environnement
        uvenvs = {}
        uvenvs["UVPIPX_LOCAL_VENVS"] = uvpipx_local_venvs
        uvenvs["UVPIPX_BIN_DIR"] = uvpipx_bin_dir
        # uvpipx.config.uvpipx_home = Path(str(uvpipx_home))
        # uvpipx.config.uvpipx_local_venvs = Path(str(uvpipx_local_venvs))

        # Vous pouvez ajouter ici la logique pour initialiser les répertoires si nécessaire

        # Cette partie rend les chemins disponibles pour les tests
        yield uvpipx_local_venvs, uvenvs, uvpipx_bin_dir


class TestInject:
    def test_inject_jc(self, env_setup: tuple[str, dict, str]) -> None:
        uvpipx_local_venvs, uvenvs, uvpipx_bin_dir = env_setup
        runenv = {**os.environ, **uvenvs}

        result = subprocess.run(  # nosec: B603, B607
            ["uvpipx", "install", "jc"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0
        venv_jc_path = Path(runenv["UVPIPX_LOCAL_VENVS"]) / "jc/.venv/bin/jc"

        assert venv_jc_path.exists()
        assert (Path(runenv["UVPIPX_BIN_DIR"]) / "jc").exists()
        assert venv_jc_path == (Path(runenv["UVPIPX_BIN_DIR"]) / "jc").resolve()

        result = subprocess.run(  # nosec: B603, B607
            ["uvpipx", "inject", "jc", "art"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0

        result = subprocess.run(  # nosec: B603, B607
            ["uvpipx", "info", "jc", "-g"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0
        venv_pass = result.stdout.rstrip()
        assert Path(f"{venv_pass}/bin/art").exists()

        runenv = {
            **os.environ,
            **uvenvs,
            "PATH": os.environ["PATH"] + ":" + venv_pass + "/bin",
        }

        result = subprocess.run(  # nosec: B603, B607
            ["art", "text", "toto"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )
        assert result.returncode == 0
        assert (
            """ _           _          
| |_   ___  | |_   ___  
| __| / _ \\ | __| / _ \\ 
| |_ | (_) || |_ | (_) |
 \\__| \\___/  \\__| \\___/"""
            in result.stdout
        )

        runenv = {**os.environ, **uvenvs}

        result = subprocess.run(  # nosec: B603, B607
            ["uvpipx", "uninject", "jc", "art"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0

        assert not Path(f"{venv_pass}/bin/art").exists()
