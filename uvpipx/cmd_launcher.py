__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.2.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"

import os
import sys

from uvpipx import uvpipx, uvpipx_infos
from uvpipx.internal_libs.args import ArgParser
from uvpipx.internal_libs.misc import Elapser, log_debug, log_info


def common_args(argp: ArgParser) -> None:
    argp.parse(sys.argv[2:])
    os.environ["UVPIPX_SHOW_DEBUG_LEVEL"] = str(
        argp.args["--verbose"].defaulted_value(),
    )
    log_debug(f"Received args {sys.argv}")

    if argp.args["--help"].defaulted_value():
        argp.print_help()
        sys.exit(0)


def install(argp: ArgParser) -> None:
    """install package locally in their own venv"""

    common_args(argp)

    with Elapser() as ela:
        uvpipx.install(
            argp.args["python_pkg"].value,
            expose_bin_names=argp.args["--expose"].defaulted_value(),
        )

    log_info(f"\n 🏁 Finish install  ⏱️  {ela.elapsed_second}")


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

    common_args(argp)

    uvpipx.uninstall(
        argp.args["python_pkg"].value,
    )


def venv(argp: ArgParser) -> None:
    """run command of a package without installing it"""
    common_args(argp)

    uvpipx.run_venv_bin(argp.args["python_pkg"].value, argp.extra_args)
