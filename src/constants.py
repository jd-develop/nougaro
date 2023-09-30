#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.lexer.token_types import KEYWORDS
# built-in python imports
import string

# ##########
# CONSTANTS
# ##########
DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS
IDENTIFIERS_LEGAL_CHARS = LETTERS + '_'
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
    "is_module",
    "is_none",
    "append",
    "pop",
    "insert",
    "extend",
    "get",
    "replace",
    "exit",
    "type",
    "__py_type__",
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
    "__test__",
    "sort",
    "reverse"
]
PROTECTED_VARS = [  # finally, the list with all the names that can't be defined by the user
    "null",
    "True",
    "False",
    "None",
    *KEYWORDS,  # all the keywords
    *BUILTIN_FUNCTIONS,  # all the builtin function names
]
