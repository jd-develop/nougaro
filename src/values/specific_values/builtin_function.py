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
from src.values.functions.builtin_function import BuiltInFunction
# built-in python imports
# no imports

VOID = BuiltInFunction('void')
RUN = BuiltInFunction('run')
EXAMPLE = BuiltInFunction('example')

PRINT = BuiltInFunction('print')
PRINT_RET = BuiltInFunction('print_ret')
INPUT = BuiltInFunction('input')
INPUT_INT = BuiltInFunction('input_int')
INPUT_NUM = BuiltInFunction('input_num')
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

APPEND = BuiltInFunction('append')
POP = BuiltInFunction('pop')
INSERT = BuiltInFunction('insert')
EXTEND = BuiltInFunction('extend')
GET = BuiltInFunction('get')
REPLACE = BuiltInFunction('replace')
MAX = BuiltInFunction('max')
MIN = BuiltInFunction('min')
LEN = BuiltInFunction('len')

SPLIT = BuiltInFunction('split')
LOWER = BuiltInFunction('lower')
UPPER = BuiltInFunction('upper')

EXIT = BuiltInFunction('exit')
SYSTEM_CALL = BuiltInFunction('system_call')

RICKROLL = BuiltInFunction('rickroll')
NOUGARO = BuiltInFunction('nougaro')

GPL = BuiltInFunction('__gpl__')
