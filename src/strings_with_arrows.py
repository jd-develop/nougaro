#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

def string_with_arrows(text: str, pos_start, pos_end) -> str:
    """
        In this example, text will be 'var 1a = 123'
        If you execute this line with nougaro, it crashes with an :
            InvalidSyntaxError : expected identifier, but got INT.

        It generates this view of the line with arrows (^) under line :
            var 1a = 123
                ^

        The pos_start is the 1 token pos_start, same for pos end.

    :param text: base text
    :param pos_start: position start
    :param pos_end: position end
    :return: str as defined above
    """
    result = ''

    # Calculate indices
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

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0:
            idx_end = len(text)

    return result.replace('\t', '').replace('\n', '\n\t')
