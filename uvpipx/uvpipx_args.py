from __future__ import annotations

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2025 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.8.1"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"


from uvpipx.internal_libs.args import Arg, ArgParser, ArgParserMode

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
            default=["__main__"],
            help="""By default, all executable program in bin will be exposed to `uvpipx_local_bin`\nYou can use --expose jc to expose only this program. you can use many --expose\n--expose _ tell to expose nothing""",
        ),
        Arg(
            "--inject",
            mode="array",
            default=[],
            help="""Inject a package in the venv like main package""",
        ),
        Arg(
            "--force",
            mode="bool/true",
            help="""Allow to force reinstall""",
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

arg_parser["uninstall-all"] = ArgParser(
    [
        verbose_arg,
        help_arg,
    ],
    help="Uninstall all python packages",
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
    help="Show the list of python packages installed",
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
    help="Show information about a python package",
)

arg_parser["upgrade"] = ArgParser(
    [
        Arg(
            "python_pkg",
            help="""The python package name to upgrade (for example "jc")\nBut you can also give version using "jc==1.25.2" """,
        ),
        verbose_arg,
        help_arg,
    ],
    help="Upgrade a python package",
)

arg_parser["upgrade-all"] = ArgParser(
    [
        verbose_arg,
        help_arg,
    ],
    help="Upgrade all python packages",
)

arg_parser["inject"] = ArgParser(
    [
        Arg(
            "python_pkg",
            help="""The python main package name (for example "jc")\nBut you can also give version using "jc==1.25.2" """,
        ),
        Arg(
            "inject_python_pkg",
            help="""The python package name to inject (for example "jc")\nBut you can also give version using "jc==1.25.2" """,
        ),
        verbose_arg,
        help_arg,
    ],
    mode=ArgParserMode.AUTO_EXTRA_ARGS,
    help="Inject one or many python package(s) in main python package",
)

arg_parser["uninject"] = ArgParser(
    [
        Arg(
            "python_pkg",
            help="""The python main package name (for example "jc")\nBut you can also give version using "jc==1.25.2" """,
        ),
        Arg(
            "uninject_python_pkg",
            help="""The python package name to uninject (for example "jc")\nBut you can also give version using "jc==1.25.2" """,
        ),
        verbose_arg,
        help_arg,
    ],
    mode=ArgParserMode.AUTO_EXTRA_ARGS,
    help="Uninject one or many python package(s) in main python package",
)

arg_parser["expose"] = ArgParser(
    [
        Arg(
            "python_pkg",
            help="""The python package name to expose (for example "jc")""",
        ),
        Arg(
            "expose_rule_names",
            help="""Expose only scripts from main package""",
        ),
        verbose_arg,
        help_arg,
    ],
    help="Expose a python package",
)

arg_parser["expose-all"] = ArgParser(
    [
        Arg(
            "expose_rule_names",
            help="""Expose only scripts from main package""",
        ),
        # Arg(
        #     "--main-package-scripts",
        #     help="""Expose only scripts from main package""",
        #     mode="bool/true",
        # ),
        verbose_arg,
        help_arg,
    ],
    help="Expose all python packages",
)

arg_parser["environnement"] = ArgParser(
    [
        verbose_arg,
        help_arg,
    ],
    help="Show config of uvpipx (deprecated use environment)",
)

arg_parser["environment"] = ArgParser(
    [
        verbose_arg,
        help_arg,
    ],
    help="Show config of uvpipx",
)