#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# IMPORTS
# nougaro modules imports
from src.values.functions.builtin_function import BuiltInFunction
# built-in python imports
# no imports

VOID = BuiltInFunction('void')
RUN = BuiltInFunction('run')

PRINT = BuiltInFunction('print')
PRINT_RET = BuiltInFunction('print_ret')
INPUT = BuiltInFunction('input')
INPUT_INT = BuiltInFunction('input_int')
CLEAR = BuiltInFunction('clear')

IS_INT = BuiltInFunction('is_int')
IS_FLOAT = BuiltInFunction('is_float')
IS_NUM = BuiltInFunction('is_num')
IS_STRING = BuiltInFunction('is_str')
IS_LIST = BuiltInFunction('is_list')
IS_FUNCTION = BuiltInFunction('is_func')
IS_NONE = BuiltInFunction('is_none')
TYPE = BuiltInFunction('type')
INT = BuiltInFunction('int')
FLOAT = BuiltInFunction('float')
STR = BuiltInFunction('str')
LIST = BuiltInFunction('list')
LOWER = BuiltInFunction('lower')
UPPER = BuiltInFunction('upper')

APPEND = BuiltInFunction('append')
POP = BuiltInFunction('pop')
EXTEND = BuiltInFunction('extend')
GET = BuiltInFunction('get')
MAX = BuiltInFunction('max')
MIN = BuiltInFunction('min')
LEN = BuiltInFunction('len')

# Maths
SQRT = BuiltInFunction('sqrt')
MATH_ROOT = BuiltInFunction('math_root')
RADIANS = BuiltInFunction('radians')
DEGREES = BuiltInFunction('degrees')
SIN = BuiltInFunction('sin')
COS = BuiltInFunction('cos')
TAN = BuiltInFunction('tan')
ASIN = BuiltInFunction('asin')
ACOS = BuiltInFunction('acos')
ATAN = BuiltInFunction('atan')
ABS = BuiltInFunction('abs')

EXIT = BuiltInFunction('exit')
SYSTEM_CALL = BuiltInFunction('system_call')

RICKROLL = BuiltInFunction('rickroll')
NOUGARO = BuiltInFunction('nougaro')
