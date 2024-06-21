__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.6.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"

import os
import sys

import uvpipx.uvpipx_run
from uvpipx import (
    uvpipx_all,
    uvpipx_infos,
    uvpipx_inject,
    uvpipx_install,
    uvpipx_upgrade,
)
from uvpipx.internal_libs.args import ArgParser
from uvpipx.internal_libs.Logger import get_logger
from uvpipx.internal_libs.misc import Elapser


def common_args(argp: ArgParser) -> None:
    logger = get_logger()
    argp.parse(sys.argv[2:])
    os.environ["UVPIPX_SHOW_DEBUG_LEVEL"] = str(
        argp.args["--verbose"].defaulted_value(),
    )
    logger.log_debug(f"Received args {sys.argv}")

    if argp.args["--help"].defaulted_value():
        argp.print_help()
        sys.exit(0)


def install(argp: ArgParser) -> None:
    """install package locally in their own venv"""
    logger = get_logger("install")

    common_args(argp)

    with Elapser() as ela:
        uvpipx_install.install(
            argp.args["python_pkg"].value,
            expose_rule_names=argp.args["--expose"].defaulted_value(),
            force_reinstall=argp.args["--force"].defaulted_value(),
        )

    logger.log_info(f"\n 🏁 Finish install  ⏱️  {ela.elapsed_second}")


def ensurepath(argp: ArgParser) -> None:
    """help to define PATH"""

    common_args(argp)

    uvpipx_infos.ensurepath()


def uvpipx_list(argp: ArgParser) -> None:
    """show the list of uvpipx venv"""

    common_args(argp)

    uvpipx_infos.uvpipx_list()


def info(
    argp: ArgParser,
) -> None:
    """show the list of uvpipx venv"""

    common_args(argp)

    uvpipx_infos.info(
        argp.args["python_pkg"].value,
        get_venv=argp.args["--get-venv"].defaulted_value(),
    )


def uninstall(argp: ArgParser) -> None:
    """uninstall package and their venv"""
    logger = get_logger("uninstall")

    common_args(argp)

    with Elapser() as ela:
        uvpipx_install.uninstall(
            argp.args["python_pkg"].value,
        )

    logger.log_info(f"\n 🏁 Finish uninstall  ⏱️  {ela.elapsed_second}")


def uninstall_all(argp: ArgParser) -> None:
    """upgrade all package locally in their own venv"""
    logger = get_logger("upgrade")

    common_args(argp)

    with Elapser() as ela:
        uvpipx_all.uninstall_all()

    logger.log_info(f"\n 🏁 Finish uninstall  ⏱️  {ela.elapsed_second}")


def venv(argp: ArgParser) -> None:
    """run command of a package without installing it"""
    common_args(argp)

    uvpipx.uvpipx_run.run_venv_bin(argp.args["python_pkg"].value, argp.extra_args)


def upgrade(argp: ArgParser) -> None:
    """upgrade package locally in their own venv"""
    logger = get_logger("upgrade")

    common_args(argp)

    with Elapser() as ela:
        uvpipx_upgrade.upgrade(
            argp.args["python_pkg"].value,
        )

    logger.log_info(f"\n 🏁 Finish upgrade  ⏱️  {ela.elapsed_second}")


def upgrade_all(argp: ArgParser) -> None:
    """upgrade all package locally in their own venv"""
    logger = get_logger("upgrade")

    common_args(argp)

    with Elapser() as ela:
        uvpipx_all.upgrade_all()

    logger.log_info(f"\n 🏁 Finish upgrade  ⏱️  {ela.elapsed_second}")


def inject(argp: ArgParser) -> None:
    """inject package locally in venv"""
    logger = get_logger("inject")

    common_args(argp)

    with Elapser() as ela:
        inject_pkg = [argp.args["inject_python_pkg"].value, *argp.extra_args]
        uvpipx_inject.inject(argp.args["python_pkg"].value, inject_pkg)

    logger.log_info(f"\n 🏁 Finish install  ⏱️  {ela.elapsed_second}")


def uninject(argp: ArgParser) -> None:
    """inject package locally in venv"""
    logger = get_logger("uninject")

    common_args(argp)

    with Elapser() as ela:
        inject_pkg = [argp.args["uninject_python_pkg"].value, *argp.extra_args]
        uvpipx_inject.uninject(argp.args["python_pkg"].value, inject_pkg)

    logger.log_info(f"\n 🏁 Finish install  ⏱️  {ela.elapsed_second}")
