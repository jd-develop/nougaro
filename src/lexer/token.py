#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.lexer.position import Position

"""File for Token class. For token types list, please refer to ./token_types.py"""


# ##########
# TOKENS
# ##########
class Token:
    """Token class.
    A token have a type (keyboard, int, str, statement, ...) and sometimes a value ("foo", 123, break)"""
    def __init__(self, type_: str, value: str | int | float | None = None, pos_start: Position | None = None, pos_end: Position | None = None):
        self.type = type_  # type
        self.value = value  # value
        self.pos_start = self.pos_end = None

        if pos_start is not None:  # if there is a pos start given
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()  # the pos end is pos_start + 1
        if pos_end is not None:
            self.pos_end = pos_end.copy()

    def __repr__(self) -> str:
        if self.value is not None:
            if isinstance(self.value, str):
                return f'{self.type}:"{self.value}"'
            return f'{self.type}:{self.value}'
        return f'{self.type}'

    def __str__(self):
        return repr(self)

    def matches(self, type_: str, value: str):
        """Check if the token have the given type and the given value"""
        return self.type == type_ and self.value == value

    def copy(self):
        """Returns a copy of self"""
        return Token(self.type, self.value, self.pos_start, self.pos_end)

    def set_value(self, value: str):
        self.value: str | int | float | None = value
        return self
