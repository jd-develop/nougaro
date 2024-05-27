#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.lexer.position import Position

"""File for Token class. For token types list, please refer to src.lexer.token_types.py"""


# ##########
# TOKENS
# ##########
class Token:
    """The token class.
    A token have a type (keyword, int, str, identifier...) and sometimes a value ("foo", 123, break)
    Types are listed in src.lexer.token_types
    """
    def __init__(self, type_: str, pos_start: Position, pos_end: Position | None = None, value: str | int | float | None = None):
        self.type = type_  # type
        self.value = value  # value

        self.pos_start: Position = pos_start.copy()
        if pos_end is None:
            self.pos_end: Position = pos_start.copy()
            self.pos_end.advance()  # the pos end is pos_start + 1
        else:
            self.pos_end: Position = pos_end.copy()

    def __repr__(self) -> str:
        if self.value is not None:
            if isinstance(self.value, str):
                return f'{self.type}:"{self.value}"'
            return f'{self.type}:{self.value}'
        return f'{self.type}'

    def __str__(self):
        return repr(self)
    
    def __eq__(self, other: object):
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.value == other.value

    def __ne__(self, other: object):
        return not self == other

    def matches(self, type_: str, value: str):
        """Check if the token have the given type and the given value"""
        return self.type == type_ and self.value == value

    def copy(self):
        """Returns a copy of self"""
        return Token(self.type, self.pos_start, self.pos_end, self.value)

    def set_value(self, value: str | int | float | None):
        self.value = value
        return self
