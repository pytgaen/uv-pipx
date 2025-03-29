from uvpipx.internal_libs.args import Arg, ArgParser, ArgParserMode


def test_general(capsys) -> None:
    """test general usage case"""
    argp = ArgParser(
        [
            Arg("cmd", help="the command"),
            Arg("pkg"),
            Arg("--expose", mode="array"),
            Arg("--verbose", mode="count", help="verbose"),
            Arg("--dry-run", mode="bool/true"),
            Arg("--uv", mode="bool/true"),
        ],
    )
    argp.parse(
        [
            "install",
            "-e",
            "e1",
            "--expose",
            "e2",
            "--verbose",
            "--verbose",
            "--uv",
            "ruff",
            "--",
            "some",
            "-tricky",
            "stuff",
        ],
    )
    assert argp.args["cmd"].value == "install"
    assert argp.args["pkg"].value == "ruff"
    assert argp.args["--expose"].value == ["e1", "e2"]
    assert argp.args["--verbose"].value == 2
    assert argp.args["--dry-run"].value is None
    assert argp.args["--dry-run"].defaulted_value() is False
    assert argp.args["--uv"].value is True
    assert argp.extra_args == ["some", "-tricky", "stuff"]

    argp.print_help()
    captured = capsys.readouterr()
    assert (
        """  cmd                  | the command

  pkg                  |

  --expose, -e "value" |

  --verbose, -v        | verbose

  --dry-run, -d        |

  --uv, -u             |

"""
        in captured.out
    )


def test_auto_extra() -> None:
    """test general usage case"""
    argp = ArgParser(
        [
            Arg("cmd"),
        ],
        mode=ArgParserMode.AUTO_EXTRA_ARGS,
    )
    argp.parse(
        [
            "install",
            "some",
            "stuff",
        ],
    )
    assert argp.args["cmd"].value == "install"
    assert argp.extra_args == ["some", "stuff"]

    pass
