#!/usr/bin/env python3
# coding:utf-8
# this file is part of NOUGARO language, created by Jean Dubois (github.com/jd-develop)
# Public Domain
# Actually running with Python 3.9.8, works with Python 3.10

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
MATHEMATICAL_FUNCTIONS = ["sqrt", "degrees", "radians", "sin", "cos", "tan", "asin", "acos", "atan"]
BUILTIN_FUNCTIONS = ["print", "print_ret", "input", "input_int", "clear", "is_num", "is_str", "is_list", "is_func",
                     "append", "pop", "extend", "exit", "type", *MATHEMATICAL_FUNCTIONS]
MATHEMATICAL_CONSTANTS = ["math_pi", "sqrt_pi", "math_e"]
VARS_CANNOT_MODIFY = ["null", "True", "False", 'noug_version', *KEYWORDS, *BUILTIN_FUNCTIONS, *MATHEMATICAL_CONSTANTS]
