#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# IMPORTS
# nougaro modules imports
from src.token_constants import KEYWORDS
# built-in python imports
import string

# ##########
# CONSTANTS
# ##########
DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS
MATHEMATICAL_FUNCTIONS = [
    "sqrt",
    "degrees",
    "radians",
    "sin",
    "cos",
    "tan",
    "asin",
    "acos",
    "atan",
    "math_root",
    "abs"
]
BUILTIN_FUNCTIONS = [
    "void",
    "print",
    "print_ret",
    "input",
    "input_int",
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
    "extend",
    "get",
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
    "len",
    *MATHEMATICAL_FUNCTIONS
]
MATHEMATICAL_CONSTANTS = [
    "math_pi",
    "sqrt_pi",
    "math_e"
]
VARS_CANNOT_MODIFY = [
    "null",
    "True",
    "False",
    "None",
    'noug_version',
    'answerToTheLifeTheUniverseAndEverything',
    *KEYWORDS,
    *BUILTIN_FUNCTIONS,
    *MATHEMATICAL_CONSTANTS
]
