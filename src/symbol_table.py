#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

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

    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent is not None:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]

    def exists(self, name):
        return name in self.symbols
