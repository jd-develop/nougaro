#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2022  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# NO IMPORTS

"""File for Token class. For token types list, please refer to ./token_types.py"""


# ##########
# TOKENS
# ##########
class Token:
    """Token class.
    A token have a type (keyboard, int, str, statement,..) and sometimes a value ("foo", 123, break)"""
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_  # type
        self.value = value  # value
        self.pos_start = self.pos_end = None

        if pos_start is not None:  # if there is a pos start given
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()  # the pos end is pos_start + 1
            self.pos_end.advance()
        if pos_end is not None:
            self.pos_end = pos_end.copy()  # if there is a pos_end, the pos_end is no longer pos_start+1

    def __repr__(self) -> str:
        if self.value is not None:
            if isinstance(self.value, str):
                return f'{self.type}:"{self.value}"'
            return f'{self.type}:{self.value}'
        return f'{self.type}'

    def matches(self, type_, value):
        """Check if the token have the given type and the given value"""
        return self.type == type_ and self.value == value

    def copy(self):
        """Returns a copy of self"""
        return Token(self.type, self.value, self.pos_start, self.pos_end)
