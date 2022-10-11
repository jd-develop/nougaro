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
from src.token_types import KEYWORDS
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
    '__gpl__',
]
PROTECTED_VARS = [  # finally, the list with all the names that can't be defined by the user
    "null",
    "True",
    "False",
    "None",
    '__noug_version__',
    '__python_version__',
    '__exec_from__',
    '__symbol_table__',
    '__os_name__',
    '__os_release__',
    '__os_version__',
    '__base_value__',
    '__disclaimer_of_warranty__',
    '__is_keyword__',
    '__does_tok_type_exist__',
    'answerToTheLifeTheUniverseAndEverything',
    *KEYWORDS,  # all the keywords
    *BUILTIN_FUNCTIONS,  # all the builtin function names
]
