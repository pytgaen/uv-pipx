from __future__ import annotations

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.2.0"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"

import textwrap
from typing import List


class NewLinePreservingWrapper(textwrap.TextWrapper):
    def wrap(self, text: str) -> List[str]:
        # Split the original text by new lines, process each part, then combine
        wrapped_lines = []
        for part in text.split("\n"):
            wrapped_lines.extend(super().wrap(part))
        return wrapped_lines

    def fill(self, text: str) -> str:
        # Use the wrap method and join the results with new lines
        return "\n".join(self.wrap(text))


def max_string_length_per_column(table: List[List[str]]) -> List[int]:
    """
    Calculates the maximum string length for each column in a 2D table.

    Args:
        table (list of list of str): A 2D list where each sublist represents a row of the table.

    Returns:
        list of int: A list containing the maximum string length found in each column.

    Raises:
        ValueError: If the table is empty or rows have inconsistent numbers of columns.
    """

    num_columns = len(table[0])

    # Initialize a list to store the maximum length found in each column.
    max_lengths = [0] * num_columns

    # Compute the maximum length for each column.
    for col_index in range(num_columns):
        # Using max() with a generator expression to find the max length in each column.
        max_lengths[col_index] = max(len(row[col_index]) for row in table)

    return max_lengths


def wrap_text_in_table(table: str, column_widths: int) -> List[str]:
    """
    Wraps text in each cell of a table to the specified widths for each column and ensures each line in a cell
    is padded with spaces to maintain the column width. Also ensures all cells in a row have the same number of lines.

    Parameters:
        table (list of list of str): The table to wrap text in, with each cell as a string.
        column_widths (list of int): The maximum width for each column.

    Returns:
        list of list of list of str: The table with text wrapped and aligned in each cell.
    """
    # Create a TextWrapper object for each column
    wrappers = [NewLinePreservingWrapper(width=width) for width in column_widths]

    # Process each row in the table
    wrapped_table = []
    for row in table:
        wrapped_row = []
        max_lines_per_row = 0

        # Wrap text in each cell and determine the max number of lines in this row
        for content, wrapper in zip(row, wrappers):
            wrapped_text = wrapper.wrap(text=content)
            # Pad each line to ensure it has the exact column width
            wrapped_text = [line.ljust(wrapper.width) for line in wrapped_text]
            max_lines_per_row = max(max_lines_per_row, len(wrapped_text))
            wrapped_row.append(wrapped_text)

        # Ensure all cells in this row have the same number of lines
        for i, cell in enumerate(wrapped_row):
            cell.extend(["".ljust(column_widths[i])] * (max_lines_per_row - len(cell)))

        wrapped_table.append(wrapped_row)

    return wrapped_table
