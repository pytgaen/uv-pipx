import os

from uvpipx.internal_libs.stylist import Color, Emoji, Painter


def test_general() -> None:
    """test general usage case"""
    msg_1 = (
        "no_color "
        + Painter.color_str("test_cyan", Color.ST_UNDERLINE, Color.CYAN)
        + " "
        + Painter.color_str("test_dim", Color.CYAN, Color.ST_DIM)
        + ".\n"
    )
    print(msg_1)
    assert msg_1 == "no_color \x1b[4m\x1b[36mtest_cyan\x1b[0m \x1b[36m\x1b[2mtest_dim\x1b[0m.\n"

    os.environ["NO_COLOR"] = "1"
    msg_1 = (
        "no_color "
        + Painter.color_str("test_cyan", Color.ST_UNDERLINE, Color.CYAN)
        + " "
        + Painter.color_str("test_dim", Color.CYAN, Color.ST_DIM)
        + ".\n"
    )
    print(msg_1)
    assert msg_1 == "no_color test_cyan test_dim.\n"

    os.environ["NO_COLOR"] = ""
    test_tag_msg2 = "no_color <RED><ST_UNDERLINE>red_underline</ST_UNDERLINE> red only</RED>.\n"
    msg_2 = Painter.parse_color_tags(test_tag_msg2)
    print(msg_2)
    assert msg_2 == "no_color \x1b[31m\x1b[4mred_underline\x1b[0m\x1b[31m red only\x1b[0m.\n"

    os.environ["NO_COLOR"] = "1"
    msg_2 = Painter.parse_color_tags(test_tag_msg2)
    print(msg_2)
    assert msg_2 == "no_color red_underline red only.\n"
    os.environ["NO_COLOR"] = ""


def test_rgb_color() -> None:
    os.environ["NO_COLOR"] = ""
    msg_1 = Painter.hex_color("#FF0000") + "toto " + Painter.hex_color("#00FF00") + "titi\n" + Painter.reset()
    print(msg_1)
    assert msg_1 == "\x1b[38;2;255;0;0mtoto \x1b[38;2;0;255;0mtiti\n\x1b[0m"

    os.environ["NO_COLOR"] = "1"
    msg_1 = Painter.hex_color("#FF0000") + "toto " + Painter.hex_color("#00FF00") + "titi\n" + Painter.reset()
    print(msg_1)
    assert msg_1 == "toto titi\n"


def test_emoji() -> None:
    os.environ["NO_EMOJI"] = ""
    msg_1 = Emoji().m("test 👍")
    print(msg_1)
    assert msg_1 == "test 👍"

    os.environ["NO_EMOJI"] = "1"
    msg_1 = Emoji().m("test 👍")
    print(msg_1)
    assert msg_1 == "test "

    os.environ["NO_EMOJI"] = ""
    assert Emoji().r("👍") == "👍"

    os.environ["NO_EMOJI"] = "1"
    assert Emoji().r("👍") == ""
