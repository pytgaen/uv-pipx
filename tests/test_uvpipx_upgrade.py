from __future__ import annotations

import json
import os
import subprocess  # nosec: B404  # noqa: S404
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


class TestUpgrade:
    def test_upgrade_jc(self, env_setup: tuple[str, dict, str]) -> None:
        uvpipx_local_venvs, uvenvs, uvpipx_bin_dir = env_setup
        runenv = {**os.environ, **uvenvs}

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
            ["uvpipx", "install", "jc==1.24.0"],  # noqa: S603, S607
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

        # result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
        #     ["uvpipx", "install", "jc", "--force"],
        #     capture_output=True,
        #     text=True,
        #     env=runenv,
        #     check=False,
        # )

        # assert result.returncode == 0

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
            ["uvpipx", "info", "jc"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0
        assert "jc==1.24.0" in result.stdout

        # patch file to allow upgrade
        with (Path(runenv["UVPIPX_LOCAL_VENVS"]) / "jc/uvpipx.json").open(
            "r",
        ) as infile:
            d_dict = json.load(infile)
        d_dict["main_package"]["package_name_spec"] = "jc"
        with (Path(runenv["UVPIPX_LOCAL_VENVS"]) / "jc/uvpipx.json").open(
            "w",
        ) as outfile:
            json.dump(d_dict, outfile)

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
            ["uvpipx", "upgrade", "jc"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0
        assert "- jc==1.24.0" in result.stdout
        assert "+ jc==" in result.stdout

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
            ["uvpipx", "info", "jc"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0
        assert "jc==1.24.0" not in result.stdout


class TestUpgradeAll:
    def test_upgrade_all(self, env_setup: tuple[str, dict, str]) -> None:
        uvpipx_local_venvs, uvenvs, uvpipx_bin_dir = env_setup
        runenv = {**os.environ, **uvenvs}

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
            ["uvpipx", "install", "jc==1.24.0"],  # noqa: S603, S607
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

        # result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
        #     ["uvpipx", "install", "jc", "--force"],
        #     capture_output=True,
        #     text=True,
        #     env=runenv,
        #     check=False,
        # )

        # assert result.returncode == 0

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
            ["uvpipx", "info", "jc"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0
        assert "jc==1.24.0" in result.stdout

        # patch file to allow upgrade
        with (Path(runenv["UVPIPX_LOCAL_VENVS"]) / "jc/uvpipx.json").open(
            "r",
        ) as infile:
            d_dict = json.load(infile)
        d_dict["main_package"]["package_name_spec"] = "jc"
        with (Path(runenv["UVPIPX_LOCAL_VENVS"]) / "jc/uvpipx.json").open(
            "w",
        ) as outfile:
            json.dump(d_dict, outfile)

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607  # noqa: S603, S607
            ["uvpipx", "upgrade-all"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607   # noqa: S603, S607
            ["uvpipx", "info", "jc"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0
        assert "jc==1.24.0" not in result.stdout
