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
from src.token_constants import KEYWORDS
from lib_.__TABLE_OF_MODULES__ import TABLE_OF_MODULES
# built-in python imports
import string

# ##########
# CONSTANTS
# ##########
DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS
BUILTIN_FUNCTIONS = [
    "void",
    "print",
    "print_ret",
    "input",
    "input_int",
    "input_num",
    "clear",
    "is_int",
    "is_float",
    "is_num",
    "is_str",
    "is_list",
    "is_func",
    "is_none",
    "append",
    "pop",
    "insert",
    "extend",
    "get",
    "replace",
    "exit",
    "type",
    "str",
    "list",
    "int",
    "float",
    "max",
    "min",
    "system_call",
    "run",
    "example",
    "len",
    'split',
    'lower',
    'upper',
    'nougaro',
]
MODULES = {*TABLE_OF_MODULES.keys()}
PROTECTED_VARS = [
    "null",
    "True",
    "False",
    "None",
    '__noug_version__',
    '__exec_from__',
    '__symbol_table__',
    '__os_name__',
    '__os_release__',
    '__os_version__',
    '__base_value__',
    'answerToTheLifeTheUniverseAndEverything',
    *KEYWORDS,
    *BUILTIN_FUNCTIONS,
    *MODULES
]
