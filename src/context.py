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
# nougaro modules imports
from src.symbol_table import SymbolTable
# built-in python imports
import pprint


# ##########
# CONTEXT
# ##########
class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table: SymbolTable = None

    def dict_(self) -> dict:
        repr_dict = {'symbol_table': self.symbol_table,
                     'parent': self.parent,
                     'parent_entry_pos': self.parent_entry_pos,
                     'display_name': self.display_name,
                     'NB': 'this is __repr__ from src.context.Context (internal)'}
        return repr_dict

    def __repr__(self):
        return pprint.pformat(self.dict_())

    def __str__(self) -> str:
        return str(self.__repr__())

    def copy(self):
        new_ctx = Context(self.display_name, self.parent, self.parent_entry_pos)
        new_ctx.symbol_table = self.symbol_table.copy()
        return new_ctx
