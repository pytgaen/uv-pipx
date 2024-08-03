from uvpipx.internal_libs.text_formatter import (
    max_string_length_per_column,
    wrap_text_in_table,
)


def test_wrap() -> None:
    infos = [
        ["toto", "Consectetur in do Lorem. Veniam incididunt cupidatat aliquip."],
        [
            "titi",
            "Et cillum ut veniam do nostrud esse mollit. Sit commodo id do et sit.",
        ],
    ]

    info_sizes_col = max_string_length_per_column(infos)
    assert info_sizes_col == [4, 69]

    size_cols = [10, 40]
    wrapped = wrap_text_in_table(infos, size_cols)

    assert wrapped == [
        [
            ["toto      ", "          "],
            [
                "Consectetur in do Lorem. Veniam         ",
                "incididunt cupidatat aliquip.           ",
            ],
        ],
        [
            ["titi      ", "          "],
            [
                "Et cillum ut veniam do nostrud esse     ",
                "mollit. Sit commodo id do et sit.       ",
            ],
        ],
    ]

    print()
    res = ""
    for row in wrapped:
        for ss in [list(sub_row) for sub_row in zip(*row)]:
            res += ((" | ".join(ss)).rstrip()) + "\n"

    print(res)
    assert (
        res
        == """toto       | Consectetur in do Lorem. Veniam
           | incididunt cupidatat aliquip.
titi       | Et cillum ut veniam do nostrud esse
           | mollit. Sit commodo id do et sit.
"""
    )
