from __future__ import annotations

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2025 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.2.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"


import os
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


class Color(Enum):
    # Foreground colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    BG_BRIGHT_RED = "\033[101m"
    BG_BRIGHT_GREEN = "\033[102m"
    BG_BRIGHT_YELLOW = "\033[103m"
    BG_BRIGHT_BLUE = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN = "\033[106m"
    BG_BRIGHT_WHITE = "\033[107m"

    # Reset and text styles
    ST_RESET = "\033[0m"
    ST_BOLD = "\033[1m"
    ST_DIM = "\033[2m"
    ST_ITALIC = "\033[3m"
    ST_UNDERLINE = "\033[4m"
    ST_BLINK = "\033[5m"
    ST_REVERSE = "\033[7m"
    ST_HIDDEN = "\033[8m"

    @staticmethod
    def rgb_color(r: int, g: int, b: int, background: bool = False) -> str:
        """Generates an ANSI escape sequence for a given RGB color."""
        if background:
            return f"\033[48;2;{r};{g};{b}m"  # ANSI escape for background color

        return f"\033[38;2;{r};{g};{b}m"  # ANSI escape for foreground color


class Painter:
    @staticmethod
    def hex_color(hexcode: str, background: bool = False) -> str:
        """Generates an ANSI escape sequence from a hex color code."""
        if os.getenv("NO_COLOR", "") != "":
            return ""

        hexcode = hexcode.strip("#")
        r, g, b = int(hexcode[:2], 16), int(hexcode[2:4], 16), int(hexcode[4:6], 16)
        return Color.rgb_color(r, g, b, background)

    @staticmethod
    def reset() -> str:
        if os.getenv("NO_COLOR", "") != "":
            return ""

        return f"{Color.ST_RESET.value}"

    @staticmethod
    def color_str(message: str, *styles: Color) -> str:
        if os.getenv("NO_COLOR", "") != "":
            return message

        style_codes = "".join(style.value for style in styles)
        return f"{style_codes}{message}{Color.ST_RESET.value}"

    @staticmethod
    def parse_color_tags(message: str) -> str:
        pattern = re.compile(r"</?([A-Z_]+)>")
        styles_set = set()
        message_ = message

        # Function to process each match
        def replace_tag(tag: str) -> str:
            if os.getenv("NO_COLOR", "") != "":
                return ""

            tag_ = tag[1:-1]
            if not tag_.startswith("/"):
                styles_set.add(tag_)
                return Color[tag_].value

            styles_set.remove(tag_[1:])
            ansi_style = Color["ST_RESET"].value
            for style in styles_set:
                ansi_style += Color[style].value

            return ansi_style

        match_tag = pattern.search(message_)
        while match_tag:
            m = match_tag[0]
            message_ = message_.replace(m, replace_tag(m), 1)
            match_tag = pattern.search(message_)

        return message_


class RenderEmoji(Enum):
    EMOJI = "emoji"
    STR = "str"
    REMOVE = "remove"


@dataclass
class Emoji:
    render_emoji: RenderEmoji = RenderEmoji.EMOJI
    emoji_to_str: Dict[str, str] = field(init=False)

    def __post_init(self) -> None:
        self.emoji_to_str = {
            "🔴": "",
            "🟢": "",
            "🎯": "",
            "⚠️": "",
            "📥": "",
            "🗑️": "",
            "🏗️": "",
            "⭕": "",
            "✅": "",
            "❌": "",
            "📦": "",
        }

    @staticmethod
    def use_emoji() -> bool:
        return not (
            os.getenv("NO_EMOJI", "") != ""
            # or "--no-emoji" in sys.argv
            or sys.stdout.encoding.lower() != "utf-8"
        )

    @staticmethod
    def is_emoji(char) -> bool:
        return unicodedata.category(char) in ("So", "Sk", "Sm")

    @staticmethod
    def get_emoji_name(char: str) -> str:
        return unicodedata.name(char, "EMOJI")

    @staticmethod
    def remove_emoji(text: str) -> str:
        return "".join("" if Emoji.is_emoji(char) else char for char in text)

    def replace_emoji(self, text: str) -> str:
        return "".join(self.emoji_to_str.get(char, "") if Emoji.is_emoji(char) else char for char in text)

    def m(self, text: str) -> str:
        """handle message with render_emoji mode or NO_EMOJI"""
        if Emoji.use_emoji() and self.render_emoji == RenderEmoji.EMOJI:
            return text

        if self.render_emoji == RenderEmoji.STR:
            return self.replace_emoji(text)

        return self.remove_emoji(text)

    def r(self, emoji: str) -> str:
        """handle emoji with render_emoji mode or NO_EMOJI"""
        if Emoji.use_emoji() and self.render_emoji == RenderEmoji.EMOJI:
            return emoji
        if self.render_emoji == RenderEmoji.STR:
            return self.emoji_to_str.get(emoji, "")

        #  RenderEmoji.REMOVE:
        return ""
