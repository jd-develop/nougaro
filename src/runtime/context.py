#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.runtime.symbol_table import SymbolTable
from src.lexer.position import Position
# built-in python imports
import pprint
from typing import Self


# ##########
# CONTEXT
# ##########
class Context:
    """Class for the interpreter Context"""
    def __init__(self, display_name: str | None, parent: Self | None = None, parent_entry_pos: Position | None = None):
        self.display_name = display_name  # name of the function we are in
        self.parent: Context | None = parent  # parent context
        # self.parent_entry_pos is the pos_start of the parent context. It is used in errors tracebacks
        self.parent_entry_pos: Position | None = parent_entry_pos
        # ABOUT self.parent_entry_pos:
        # I actually don't know why there is a parent_entry_pos to every context, but there is no pos_start.
        # The entry pos seems to be the pos start of a context, but... Well, I don't know....
        self.symbol_table = None
        self.what_to_export: SymbolTable = SymbolTable()

    def dict_(self):
        """Repr the context under a dict form."""
        repr_dict = {'symbol_table': self.symbol_table,
                     'parent': self.parent,
                     'parent_entry_pos': self.parent_entry_pos,
                     'display_name': self.display_name,
                     'NB': 'this is __repr__ from src.context.Context (internal)'}
        return repr_dict

    def __repr__(self):
        """Convert the dict returned by Context.dict_ method into a string-like object.
        If you want a string, use the Context.__str__ method"""
        return pprint.pformat(self.dict_())

    def __str__(self) -> str:
        """Return the dict returned by Context.dict_ under a str form."""
        return str(self.__repr__())

    def set_symbol_table(self, new_symbol_table: SymbolTable):
        """Sets symbol table then returns self"""
        self.symbol_table = new_symbol_table
        return self

    def set_symbol_table_to_parent_symbol_table(self):
        """Sets symbol table to parent’s one then return self. If current symbol table is None and parent is None,
        create a blank symbol table."""
        if self.parent is not None and self.parent.symbol_table is not None:
            self.symbol_table = self.parent.symbol_table.copy()
        elif self.symbol_table is None:
            self.symbol_table = SymbolTable()
        return self

    def set_symbol_table_with_parent_symbol_table_as_parent(self, new_symbol_table: SymbolTable):
        """Sets symbol table, sets its parent to parent’s one (if it exists) then return self."""
        if self.parent is not None and self.parent.symbol_table is not None:
            self.symbol_table = new_symbol_table.copy().set_parent(self.parent.symbol_table)
        elif self.symbol_table is None:
            self.symbol_table = new_symbol_table.copy()
        return self

    def copy(self):
        """Return a copy of self."""
        new_ctx = Context(self.display_name, self.parent, self.parent_entry_pos)
        assert self.symbol_table is not None
        new_ctx.symbol_table = self.symbol_table.copy()
        return new_ctx
