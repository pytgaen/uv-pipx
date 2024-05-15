import sys

from uvpipx.internal_libs.colors import Painter

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.2.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"

from uvpipx.cmd_launcher import ensurepath, info, install, uninstall, uvpipx_list, venv
from uvpipx.internal_libs.print import max_string_length_per_column, wrap_text_in_table
from uvpipx.uvpipx_args import arg_parser


def show_main_help() -> None:
    print(
        Painter.parse_color_tags("<ST_UNDERLINE>uvpipx general help</ST_UNDERLINE>\n"),
    )

    print("uvpipx cmd [--help] ... parameters ...\n\ncmd can be:")
    help_ = [[f"{k}", f"{v.help}"] for k, v in arg_parser.items()]
    size_col = max_string_length_per_column(help_)

    wrapped = wrap_text_in_table(help_, [size_col[0], 100 - size_col[0]])
    for row in wrapped:
        for ss in [list(sub_row) for sub_row in zip(*row)]:
            print("  " + (" | ".join(ss)).rstrip())
        # print()

    print()


def main() -> None:
    """uv pipx

    like pipx but with uv ... intent to be miniamist, small and so fast !
    """
    print(
        Painter.parse_color_tags(
            f"<BRIGHT_WHITE>uvpipx</BRIGHT_WHITE> version <CYAN>{__version__}</CYAN>\n",
        ),
    )
    if len(sys.argv) <= 1 or (len(sys.argv) == 2 and sys.argv[1] in ["-h", "--help"]):
        show_main_help()
        sys.exit(0)

    if sys.argv[1] == "install":
        install(arg_parser["install"])

    elif sys.argv[1] == "uninstall":
        uninstall(arg_parser["uninstall"])

    elif sys.argv[1] == "venv":
        venv(arg_parser["venv"])

    elif sys.argv[1] == "ensurepath":
        ensurepath(arg_parser["ensurepath"])

    elif sys.argv[1] == "list":
        uvpipx_list(arg_parser["list"])

    elif sys.argv[1] == "info":
        info(arg_parser["info"])

    else:
        print(f"Unkonw command {sys.argv[1]}, below the help")
        show_main_help()

        msg = f"Unkonw command {sys.argv[1]}"
        raise RuntimeError(msg)


if __name__ == "__main__":
    main()
