#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# __future__ imports (must be first)
from __future__ import annotations
# nougaro modules imports
from src.lexer.token_types import KEYWORDS
# built-in python imports
import pprint
import difflib
from typing import Self
# special typing import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.runtime.values.basevalues.value import Value


# ##########
# SYMBOL TABLE
# ##########
class SymbolTable:
    def __init__(self, parent: Self | None = None):
        self.symbols = {}
        self.parent = parent

    def dict_(self):
        return {'symbols': self.symbols,
                'parent': self.parent}

    def __repr__(self) -> str:
        return pprint.pformat(self.dict_())

    def get(self, name: str, get_in_parent: bool = True, get_in_grandparent: bool = True) -> Value | None:
        value = self.symbols.get(name, None)
        if get_in_parent and value is None and self.parent is not None:
            return self.parent.get(name, get_in_grandparent)
        return value

    def getf(self, name: str) -> Value | None:
        """Like get, but with get_in_(grand)parent to False. For builtin functions and modules."""
        return self.get(name, False, False)

    def set(self, name: str, value: Value):
        self.symbols[name] = value

    def set_whole_table(self, new_table: dict[str, Value]):
        self.symbols = new_table.copy()

    def remove(self, name: str):
        del self.symbols[name]

    def exists(self, name: str, look_in_parent: bool = False) -> bool:
        if not look_in_parent or self.parent is None:
            return name in self.symbols
        else:
            return name in self.symbols or self.parent.exists(name, True)

    def set_parent(self, parent: Self):
        self.parent = parent
        return self

    def best_match(self, name: str) -> str | None:
        """Return the name in the symbol table that is the closest to 'name'. Return None if there is no close match."""
        if len(self.symbols) == 0 or name == "":
            return None
        min_best_match = 0.5
        best_match = min_best_match
        best_match_name = ""
        list_to_check = list(self.symbols.keys())
        list_to_check.extend(KEYWORDS)
        for key in list_to_check:
            ratio = difflib.SequenceMatcher(None, name, key).ratio()
            if ratio > best_match:
                best_match = ratio
                best_match_name = key
        if best_match_name == "":
            return None
        return best_match_name

    def copy(self):
        new_symbol_table = SymbolTable(self.parent)
        new_symbol_table.symbols = self.symbols.copy()
        return new_symbol_table
