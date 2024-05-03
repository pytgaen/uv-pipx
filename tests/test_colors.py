from uvpipx.internal_libs.colors import Color, Painter


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
    assert (
        msg_1
        == "no_color \x1b[4m\x1b[36mtest_cyan\x1b[0m \x1b[36m\x1b[2mtest_dim\x1b[0m.\n"
    )

    test_tag_msg2 = (
        "no_color <RED><ST_UNDERLINE>red_underline</ST_UNDERLINE> red only</RED>.\n"
    )
    msg_2 = Painter.parse_color_tags(test_tag_msg2)
    print(msg_2)
    assert (
        msg_2
        == "no_color \x1b[31m\x1b[4mred_underline\x1b[0m\x1b[31m red only\x1b[0m.\n"
    )
