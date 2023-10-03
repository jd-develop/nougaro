#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
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
    def __init__(self, index: int, line_number: int, colon: int, file_name: str, file_txt: str):
        """
        index       starts at 0
        line_number starts at 0
        colon       starts at 0
        """
        self.index:       int = index
        self.line_number: int = line_number
        self.colon:       int = colon
        self.file_name:   str = file_name
        self.file_txt:    str = file_txt

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
