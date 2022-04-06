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
    'lower',
    'upper',
    'nougaro',
]
MODULES = [
    "random",
    "math"
]
VARS_CANNOT_MODIFY = [
    "null",
    "True",
    "False",
    "None",
    'noug_version',
    'os_name',
    'os_release',
    'os_version',
    'answerToTheLifeTheUniverseAndEverything',
    *KEYWORDS,
    *BUILTIN_FUNCTIONS,
    *MODULES
]
