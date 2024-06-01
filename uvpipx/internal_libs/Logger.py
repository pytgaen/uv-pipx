from __future__ import annotations

import datetime
import os
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Dict

from uvpipx.internal_libs.stylist import Color, Painter


class LogMode(Enum):
    PRINT = "print"
    BUFFER = "buffer"


class LogLevel(IntEnum):
    DEBUG = 0
    INFO = 50
    NOTICE = 100
    WARN = 200
    ERROR = 300


@dataclass
class LogEntry:
    level: LogLevel
    ts: datetime.datetime
    message: str


@dataclass
class Logger:
    log_mode: LogMode = LogMode.PRINT
    show_level: LogLevel = LogLevel.INFO
    show_log_mode_prefix: bool = os.getenv("UVPIPX_SHOW_LOG_PREFIX", "0").lower() in [
        "1",
        "true",
    ]

    def __post_init__(self) -> None:
        self.__buffer = []

    def render(self, messages: LogEntry) -> None:
        for message in messages:
            if message.level >= self.show_level:
                if self.log_mode == LogMode.PRINT:
                    self.screen_log_entry(message)
                elif self.log_mode == LogMode.BUFFER:
                    self.__buffer.append(messages)

    def render_level_prefix(self, level: LogLevel) -> None:
        text_info = ""
        if level == level.INFO:
            text_info = Painter.color_str("INFO", Color.BRIGHT_CYAN, Color.ST_BOLD)
        elif level == level.WARN:
            text_info = Painter.color_str("WARN", Color.BRIGHT_YELLOW, Color.ST_BOLD)
        elif level == level.ERROR:
            text_info = Painter.color_str("ERR ", Color.BRIGHT_RED, Color.ST_BOLD)
        elif level == level.DEBUG:
            text_info = Painter.color_str("DEBG", Color.BLUE)

        return f"[{text_info}] " if self.show_log_mode_prefix else ""

    def screen_log_entry(self, entry: list[LogEntry]) -> None:
        print(f"{self.render_level_prefix(entry.level)}{entry.message}")

    def log_at_level(self, level: LogLevel, messages: str) -> None:
        ts = datetime.datetime.now().astimezone()
        log_messages = [
            LogEntry(level, ts, message) for message in messages.split("\n")
        ]
        self.render(log_messages)

    def log_debug(self, messages: str) -> None:
        """
        Logs a message with an optional verbosity level.

        Args:
            message (str): The message to be logged.
            level (int, optional): The verbosity level of the message. Defaults to 1.

        Returns:
            None
        """

        self.log_at_level(LogLevel.DEBUG, messages)

    def log_info(self, messages: str) -> None:
        """
        Logs an informational message.

        Explanation:
        This function prints an informational message with a specific format to the render.

        Args:
            message (str): The message to be logged.

        Returns:
            None
        """

        self.log_at_level(LogLevel.INFO, messages)

    def log_notice(self, messages: str) -> None:
        """
        Logs an notice message.

        Explanation:
        This function prints an notice message with a specific format to the render.

        Args:
            message (str): The message to be logged.

        Returns:
            None
        """

        self.log_at_level(LogLevel.INFO, messages)

    def log_warn(self, messages: str) -> None:
        """
        Logs a warm message.

        Args:
            message (str): The warm message to be logged.

        Returns:
            None
        """

        self.log_at_level(LogLevel.WARN, messages)

    def log_error(self, messages: str) -> None:
        """
        Logs a error message.

        Args:
            message (str): The error message to be logged.

        Returns:
            None
        """

        self.log_at_level(LogLevel.ERROR, messages)


LOGGER: Dict[str, Logger] = {}


def get_logger(name: str = "default") -> Logger:
    if name not in LOGGER:
        LOGGER[name] = Logger()
    return LOGGER[name]
