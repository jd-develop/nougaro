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
    def __init__(self, display_name: str | None, entry_pos: Position, parent: Self | None = None,
                 value_im_attribute_of: str | None = None):
        """Note on value_im_attribute_of:
        
        In commit a17aa2bc was introduced a bug where `(1).b` returned:
        > `AttributeError: attribute of 1 has no attribute 'b'.`

        This is because `display_name` was "attribute of 1".
        `value_im_attribute_of` is now therefore used in such case.
        If value_im_attribute_of is None, it is by default set to `display_name`.
        """
        self.display_name = display_name  # name of the function we are in
        if value_im_attribute_of is None:
            value_im_attribute_of = display_name
        self.value_im_attribute_of = value_im_attribute_of
        self.parent: Context | None = parent  # parent context
        # self.entry_pos is the pos_start of the current context.
        # It is used in errors tracebacks (class src.errors.errors.RunTimeError.generate_traceback)
        self.entry_pos: Position = entry_pos
        self.symbol_table = None
        self.what_to_export: SymbolTable = SymbolTable()

    def dict_(self):
        """Repr the context under a dict form."""
        repr_dict = {'symbol_table': self.symbol_table,
                     'parent': self.parent,
                     'entry_pos': self.entry_pos,
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
        new_ctx = Context(self.display_name, self.entry_pos, self.parent)
        assert self.symbol_table is not None
        new_ctx.symbol_table = self.symbol_table.copy()
        return new_ctx
