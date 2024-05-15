from __future__ import annotations

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.2.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"


from uvpipx.internal_libs.args import Arg, ArgParser

arg_parser: dict[str, ArgParser] = {}

verbose_arg = Arg(
    "--verbose",
    mode="count",
    help="""Define the output verbosity, you can use --verbose up to three time to increase the verbosity""",
)

help_arg = Arg(
    "--help",
    mode="bool/true/stopper",
    help="""Show help""",
)

arg_parser["install"] = ArgParser(
    [
        Arg(
            "python_pkg",
            help="""The python package name to install (for example "jc")\nBut you can also give version using "jc==1.25.2" """,
        ),
        Arg(
            "--expose",
            mode="array",
            default=["*"],
            help="""By default, all executable program in bin will be expose to `uvpipx_local_bin`\nYou can use --expose jc to expose only this program. you can use many --expose\n--expose _ tell to expose nothing""",
        ),
        verbose_arg,
        help_arg,
    ],
    help="Install a python package",
)

arg_parser["uninstall"] = ArgParser(
    [
        Arg(
            "python_pkg",
            help="""The python package name to uninstall (for example "jc")""",
        ),
        verbose_arg,
        help_arg,
    ],
    help="Uninstall a python package",
)

arg_parser["venv"] = ArgParser(
    [
        Arg(
            "python_pkg",
            help="""The python package name of the venv you want to use (for example "jc")""",
        ),
        verbose_arg,
        help_arg,
    ],
    help="Run a command in the venv of the python package",
)

arg_parser["ensurepath"] = ArgParser(
    [
        verbose_arg,
        help_arg,
    ],
    help="Configure PATH for uvpipx",
)
arg_parser["list"] = ArgParser(
    [
        verbose_arg,
        help_arg,
    ],
    help="Show the list of python package installed",
)
arg_parser["info"] = ArgParser(
    [
        Arg(
            "python_pkg",
            help="""The python package name to get information (for example "jc")""",
        ),
        verbose_arg,
        help_arg,
        Arg("--get-venv", mode="bool/true"),
    ],
    help="Show information of the python package",
)
# arg_parser['...'] = None
