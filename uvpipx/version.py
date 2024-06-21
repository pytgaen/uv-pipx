from uvpipx.internal_libs.stylist import Painter

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.6.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"


def show_version() -> None:
    print(
        Painter.parse_color_tags(
            f"<BRIGHT_WHITE>uvpipx</BRIGHT_WHITE> version <CYAN>{__version__}</CYAN>\n",
        ),
    )
