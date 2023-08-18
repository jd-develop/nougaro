#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
# no imports
# built-in python imports
import pprint


# ##########
# SYMBOL TABLE
# ##########
class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def dict_(self) -> dict:
        return {'symbols': self.symbols,
                'parent': self.parent}

    def __repr__(self) -> str:
        return pprint.pformat(self.dict_())

    def get(self, name, get_in_parent: bool = True, get_in_grandparent: bool = True):
        value = self.symbols.get(name, None)
        if get_in_parent and value is None and self.parent is not None:
            return self.parent.get(name, get_in_grandparent)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def set_whole_table(self, new_table: dict):
        self.symbols = new_table.copy()

    def remove(self, name):
        del self.symbols[name]

    def exists(self, name):
        return name in self.symbols

    def copy(self):
        new_symbol_table = SymbolTable(self.parent)
        new_symbol_table.symbols = self.symbols.copy()
        return new_symbol_table
