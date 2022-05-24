#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

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
