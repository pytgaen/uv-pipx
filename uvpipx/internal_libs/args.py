"""intend to be independent(internal one file) args parser ... be cool enougth"""

from __future__ import annotations

from uvpipx.internal_libs.stylist import Painter

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.2.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"


from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Tuple, Union

from uvpipx.internal_libs.print import max_string_length_per_column, wrap_text_in_table


@dataclass
class Arg:
    name: str
    mode: Union[None, str] = None
    type_: Any = str
    default: Any = None
    help: str = ""
    alternate_name: Union[List[str], None] = field(init=False, default_factory=list)
    arg_pos: int = field(init=False, default=-1)
    value: Any = field(init=False, default=None)

    def defaulted_value(self) -> Union[str, None, bool, int]:
        default_ = self.default
        if self.mode and self.mode.startswith("bool/"):
            default_ = False if self.mode.startswith("bool/true") else False

        if self.mode and self.mode.startswith("count"):
            default_ = 0

        return self.value if self.value is not None else default_


class ArgParserMode(Enum):
    STRICT = "STRICT"
    ALLOW_MISSING_POSITIONAL = "ALLOW_MISSING_POSITIONAL"
    AUTO_EXTRA_ARGS = "AUTO_EXTRA_ARGS"


@dataclass
class ArgParser:
    args_def: List[Arg]
    mode: ArgParserMode = ArgParserMode.STRICT
    args_pos_def: Dict[str, Arg] = field(init=False, default_factory=dict)
    args: Dict[str, Arg] = field(init=False, default_factory=dict)
    args_pos: Dict[str, Arg] = field(init=False, default_factory=dict)
    extra_args: List[str] = field(init=False, default_factory=list)
    help: Union[str, None] = None
    _nb_expected_args: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        for arg_def in self.args_def:
            self._process_arg_definition(arg_def)

    def _process_arg_definition(self, arg_def: List[Arg]) -> None:
        self.args[arg_def.name] = arg_def
        if arg_def.name.startswith("--"):
            if not arg_def.alternate_name and arg_def.name[1:3] not in self.args:
                arg_def.alternate_name = [arg_def.name[1:3]]
                self.args[arg_def.alternate_name[0]] = arg_def
            # TODO manage provider alternate_name
        else:
            arg_def.arg_pos = len(self.args_pos_def)
            self.args_pos_def[arg_def.name] = arg_def
            self._nb_expected_args += 1

    def parse(self, received_args: List[str]) -> None:
        i_token = 0

        # print("received_args",received_args)
        stopper = None

        while i_token < len(received_args):
            try:
                nb_consumed_element, arg = self._parse_arg(i_token, received_args)
                if nb_consumed_element == -1:
                    if arg is None:
                        break
                    else:
                        stopper = arg
                        break

                i_token += nb_consumed_element
                if (
                    self.mode == ArgParserMode.AUTO_EXTRA_ARGS
                    and len(self.args_pos) == self._nb_expected_args
                ):
                    break
            except IndexError as e:
                msg = f"Unable to parse arg {received_args[i_token]}"
                raise RuntimeError(
                    msg,
                ) from e

        # if nb_consumed_element == -1 and self.mode in [ArgParserMode.ALLOW_MISSING_POSITIONAL, ArgParserMode.STRICT]:
        if (
            self.mode == ArgParserMode.STRICT
            and stopper is None
            and len(self.args_pos) != self._nb_expected_args
        ):
            msg = "Missing some parameter"
            raise RuntimeError(
                msg,
            )  # TODO better message indicating the missing list

        if self.mode != ArgParserMode.AUTO_EXTRA_ARGS:
            # if we are here this is because there -- to allow extra extra so we skip one to bypass --
            i_token += 1
        self.extra_args = received_args[i_token:]

        # print("extra_args", self.extra_args)

    def _parse_arg(
        self,
        i_token: int,
        received_args: List[str],
    ) -> Union[Tuple[int, Dict[str, Arg]], Tuple[int, None]]:
        val_arg = received_args[i_token]
        if val_arg == "--":
            return -1, None

        if val_arg.startswith("-"):
            return self._parse_flag(i_token, received_args)
        else:
            return self._parse_positional_argument(val_arg)

    def _parse_flag(
        self,
        i_token: int,
        received_args: List[str],
    ) -> Tuple[int, Dict[str, Arg]]:
        val_arg = received_args[i_token]

        if self.args[val_arg].mode == "count":
            self._parse_count_flag(val_arg)
            return 1, self.args[val_arg]
        if self.args[val_arg].mode == "bool/true/stopper":
            self.args[val_arg].value = True
            return -1, self.args[val_arg]
        if self.args[val_arg].mode == "bool/true":
            self.args[val_arg].value = True
            return 1, self.args[val_arg]
        if self.args[val_arg].mode == "bool/false":
            self.args[val_arg].value = False
            return 1, self.args[val_arg]

        try:
            next_val_arg = received_args[i_token + 1]
        except IndexError as e:
            msg = "Need value for optional arg {val_arg.name}"
            raise RuntimeError(msg) from e

        if self.args[val_arg].mode == "array":
            self._parse_array_flag(val_arg, next_val_arg)
        else:
            self.args[val_arg].value = next_val_arg

        return 2, self.args[val_arg]

    def _parse_array_flag(self, val_arg: Arg, next_val_arg: Arg) -> None:
        if self.args[val_arg].value is None:  # not hasattr(self.args[val_arg], "value")
            self.args[val_arg].value = [next_val_arg]
        else:
            self.args[val_arg].value.append(next_val_arg)

    def _parse_count_flag(self, val_arg: Arg) -> None:
        if self.args[val_arg].value is None:
            self.args[val_arg].value = 1
        else:
            self.args[val_arg].value += 1

    def _parse_positional_argument(self, val_arg: Arg) -> Tuple[int, Dict[str, Arg]]:
        i_pos_name = list(self.args_pos_def.keys())[len(self.args_pos.keys())]
        self.args[i_pos_name].value = val_arg
        self.args_pos[i_pos_name] = self.args[i_pos_name]

        return 1, self.args[i_pos_name]

        # TODO finish check
        # all positional have a value

    def print_help(self) -> None:
        if self.help:
            print(
                Painter.parse_color_tags(f"<ST_UNDERLINE>{self.help}</ST_UNDERLINE>\n"),
            )

        # TODO show command line argument

        info_not_option = []
        info_option = []
        for arg in self.args_def:
            if arg.name.startswith("-"):
                opt = ", ".join([arg.name, *arg.alternate_name])
                next_value = (
                    ""
                    if arg.mode == "count" or arg.mode.startswith("bool/")
                    else ' "value"'
                )
                info_option.append([f"""{opt}{next_value}""", arg.help])
            else:
                info_not_option.append([arg.name, arg.help])

        infos = info_not_option + info_option

        size_col = max_string_length_per_column(infos)

        wrapped = wrap_text_in_table(infos, [size_col[0], 100 - size_col[0]])
        for row in wrapped:
            for ss in [list(sub_row) for sub_row in zip(*row)]:
                print("  " + (" | ".join(ss)).rstrip())
            print()
