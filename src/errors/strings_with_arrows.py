#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from src.lexer.position import Position


def string_with_arrows(text: str, pos_start, pos_end) -> str:
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
    assert isinstance(pos_start, Position), f"pos_start is not a Position object. {text=}. Please report this bug."
    assert isinstance(pos_end, Position), f"pos_end is not a Position object. {text=}. Please report this bug."
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

        # Append to result
        result += line + '\n'
        result += ' ' * col_start + '^' * (col_end - col_start)

        # Re-calculate indexes
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0:
            idx_end = len(text)

    return result.replace('\t', '').replace('\n', '\n\t')
