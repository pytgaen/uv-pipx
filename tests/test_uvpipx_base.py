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


def test_help(env_setup: tuple[str, dict, str]) -> None:
    uvpipx_local_venvs, uvenvs, uvpipx_bin_dir = env_setup
    runenv = {**os.environ, **uvenvs}

    result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
        ["uvpipx", "--help"],  # noqa: S603, S607
        capture_output=True,
        text=True,
        env=runenv,
        check=False,
    )
    assert result.returncode == 0
    assert "Show the list of python package installed" in result.stdout


class TestBasicInsUninstall:
    def test_install_unins_jc(self, env_setup: tuple[str, dict, str]) -> None:
        uvpipx_local_venvs, uvenvs, uvpipx_bin_dir = env_setup
        runenv = {**os.environ, **uvenvs}

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
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

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
            ["uvpipx", "uninstall", "jc"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0

        assert not venv_jc_path.exists()
        assert not (Path(runenv["UVPIPX_BIN_DIR"]) / "jc").exists()

    def test_install_unins_jc_force(self, env_setup: tuple[str, dict, str]) -> None:
        uvpipx_local_venvs, uvenvs, uvpipx_bin_dir = env_setup
        runenv = {**os.environ, **uvenvs}

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
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

        (Path(runenv["UVPIPX_BIN_DIR"]) / "jc").unlink()  # destro the bin jc

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
            ["uvpipx", "install", "jc", "--force"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0

        assert venv_jc_path.exists()
        assert (Path(runenv["UVPIPX_BIN_DIR"]) / "jc").exists()
        assert venv_jc_path == (Path(runenv["UVPIPX_BIN_DIR"]) / "jc").resolve()

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
            ["uvpipx", "uninstall", "jc"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0

        assert not venv_jc_path.exists()
        assert not (Path(runenv["UVPIPX_BIN_DIR"]) / "jc").exists()


class TestBasicExpose:
    def test_install_unins_jc(self, env_setup: tuple[str, dict, str]) -> None:
        uvpipx_local_venvs, uvenvs, uvpipx_bin_dir = env_setup
        runenv = {**os.environ, **uvenvs}

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
            ["uvpipx", "install", "jc", "--expose", "jc"],  # noqa: S603, S607
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

        runenv = {**os.environ, **uvenvs}

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
            ["uvpipx", "uninstall", "jc"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0

        assert not venv_jc_path.exists()
        assert not (Path(runenv["UVPIPX_BIN_DIR"]) / "jc").exists()


class TestBasicExposeRename:
    def test_install_unins_jc(self, env_setup: tuple[str, dict, str]) -> None:
        uvpipx_local_venvs, uvenvs, uvpipx_bin_dir = env_setup
        runenv = {**os.environ, **uvenvs}

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
            ["uvpipx", "install", "jc", "--expose", "jc:myjc"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0
        venv_jc_path = Path(runenv["UVPIPX_LOCAL_VENVS"]) / "jc/.venv/bin/jc"

        assert venv_jc_path.exists()
        assert (Path(runenv["UVPIPX_BIN_DIR"]) / "myjc").exists()
        assert venv_jc_path == (Path(runenv["UVPIPX_BIN_DIR"]) / "myjc").resolve()

        # def test_uninstall_jc(self, env_setup):
        #
        #     uvpipx_local_venvs, uvenvs, uvpipx_bin_dir = env_setup

        runenv = {**os.environ, **uvenvs}

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
            ["uvpipx", "uninstall", "jc"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0

        assert not venv_jc_path.exists()
        assert not (Path(runenv["UVPIPX_BIN_DIR"]) / "myjc").exists()


class TestBasicRunLocalBin:
    def test_install_run_jc(self, env_setup: tuple[str, dict, str]) -> None:
        uvpipx_local_venvs, uvenvs, uvpipx_bin_dir = env_setup
        runenv = {**os.environ, **uvenvs}

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
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

        runenv = {
            **os.environ,
            **uvenvs,
            "PATH": os.environ["PATH"] + ":" + runenv["UVPIPX_BIN_DIR"],
        }

        fake_wc_ouput = "\t2\t30\t100"
        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
            ["jc", "--wc"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            input=fake_wc_ouput,
            env=runenv,
            check=False,
        )
        assert result.returncode == 0
        assert (
            result.stdout
            == '[{"filename":null,"lines":2,"words":30,"characters":100}]\n'
        )


class TestBasicInfo:
    def test_info(self, env_setup: tuple[str, dict, str]) -> None:
        uvpipx_local_venvs, uvenvs, uvpipx_bin_dir = env_setup
        runenv = {**os.environ, **uvenvs}

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
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

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
            ["uvpipx", "info", "jc"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0
        assert "📦 jc (jc==" in result.stdout
        assert "✅ jc" in result.stdout


class TestBasicList:
    def test_list(self, env_setup: tuple[str, dict, str]) -> None:
        uvpipx_local_venvs, uvenvs, uvpipx_bin_dir = env_setup
        runenv = {**os.environ, **uvenvs}

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
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

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
            ["uvpipx", "list"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0
        assert "📍 uvpipx venvs are in" in result.stdout
        assert "📦 jc (jc==" in result.stdout


class TestBasicInsAllUninstall:
    def test_install_unins_jc(self, env_setup: tuple[str, dict, str]) -> None:
        uvpipx_local_venvs, uvenvs, uvpipx_bin_dir = env_setup
        runenv = {**os.environ, **uvenvs}

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
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

        result = subprocess.run(  # nosec: B603, B607  # noqa: S603, S607
            ["uvpipx", "uninstall-all"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            env=runenv,
            check=False,
        )

        assert result.returncode == 0

        assert not venv_jc_path.exists()
        assert not (Path(runenv["UVPIPX_BIN_DIR"]) / "jc").exists()
