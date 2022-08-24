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

# IMPORTS
# no imports

# ##########
# POSITION
# ##########
class Position:
    """Contain file name, index in file, line number and colon"""
    def __init__(self, index, line_number, colon, file_name, file_txt):
        self.index = index
        self.line_number = line_number
        self.colon = colon
        self.file_name = file_name
        self.file_txt = file_txt

    def advance(self, current_char=None):
        """Add 1 to the index, automatically make back lines."""
        self.index += 1
        self.colon += 1

        if current_char == '\n':
            self.line_number += 1
            self.colon = 0

        return self

    def __repr__(self):
        return f"Position at index {self.index} line {self.line_number} colon {self.colon}, in file {self.file_name}."

    def copy(self):
        """Return a copy of self"""
        return Position(self.index, self.line_number, self.colon, self.file_name, self.file_txt)
