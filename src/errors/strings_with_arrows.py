#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from src.lexer.position import Position


def string_with_arrows(text: str, pos_start: Position, pos_end: Position) -> str:
    """Generate a string with arrows under it.
        In this example, text will be 'var 1a = 123'
        If you execute this line with nougaro, it crashes with an :
            InvalidSyntaxError : expected identifier, but got int.

        It generates this preview of the line with arrows (^) under the problematic characters :
            var 1a = 123
                ^

        Here, pos_start is the '1' token pos_start, same for pos end.

    :param text: base text
    :param pos_start: position start
    :param pos_end: position end
    :return: str as defined above
    """
    assert isinstance(pos_start, Position), f"pos_start is not a Position object, but of type {type(pos_start)}. " \
                                            f"{text=}. Please report this bug at " \
                                            f"https://jd-develop.github.io/nougaro/bugreport."
    assert isinstance(pos_end, Position), f"pos_end is not a Position object, but of type {type(pos_end)}. " \
                                          f"{text=}. Please report this bug at " \
                                          f"https://jd-develop.github.io/nougaro/bugreport."
    result = ''

    # Calculate indexes
    idx_start = max(text.rfind('\n', 0, pos_start.index), 0)
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0:
        idx_end = len(text)

    # Generate each line
    line_count = pos_end.line_number - pos_start.line_number + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[idx_start:idx_end]
        col_start = pos_start.colon if i == 0 else 0
        col_end = pos_end.colon if i == line_count - 1 else len(line) - 1

        # the following code cleans up the tabs
        new_line = ""
        new_col_start = 0
        new_col_end = 0
        for j in range(0, col_start):
            if line[j] == "\t":
                new_line += "    "
                new_col_start += 4
                new_col_end += 4
            else:
                new_line += line[j]
                new_col_start += 1
                new_col_end += 1
        for j in range(col_start, col_end):
            if j == len(line):
                new_col_end += 1
                continue
            if line[j] == "\t":
                new_line += "    "
                new_col_end += 4
            else:
                new_line += line[j]
                new_col_end += 1
        for j in range(col_end, len(line)):
            new_line += line[j]

        # Append to result
        result += new_line + '\n'
        result += ' ' * new_col_start + '^' * (new_col_end - new_col_start)

        # Re-calculate indexes
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0:
            idx_end = len(text)

    return result.replace('\t', '    ')  # .replace('\n', '\n    ')
