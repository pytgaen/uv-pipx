from __future__ import annotations
import sys

from uvpipx.internal_libs.stylist import Painter
from uvpipx.version import show_version

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.6.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"

import uvpipx.cmd_launcher as cmd_launcher
from uvpipx.internal_libs.print import max_string_length_per_column, wrap_text_in_table
from uvpipx.uvpipx_args import arg_parser

cmd_map: dict[str, str] = {"list": "uvpipx_list"}


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

    print()


def main() -> None:
    """uv pipx

    like pipx but with uv ... intent to be miniamist, small and so fast !
    """

    if len(sys.argv) <= 1 or (len(sys.argv) == 2 and sys.argv[1] in ["-h", "--help"]):
        show_version()
        show_main_help()
        sys.exit(0)

    main_cmd = sys.argv[1]
    if main_cmd in arg_parser:
        main_cmd_map = main_cmd.replace("-", "_")
        cmd_function = getattr(cmd_launcher, cmd_map.get(main_cmd_map, main_cmd_map))
        cmd_function(arg_parser[sys.argv[1]])

    else:
        print(f"Unknow command {sys.argv[1]}, below the help")
        show_main_help()

        msg = f"Unknow command {sys.argv[1]}"
        raise RuntimeError(msg)


if __name__ == "__main__":
    main()
