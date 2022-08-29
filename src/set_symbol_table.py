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
from src.symbol_table import SymbolTable
from src.values.specific_values.number import *
from src.values.basevalues import String, Value, NoneValue
from src.values.specific_values.builtin_function import *
from src.constants import PROTECTED_VARS
# built-in python imports
import platform
import pprint
import sys


def set_symbol_table(symbol_table: SymbolTable):
    """Configures the global symbol table
    :param symbol_table: src.symbol_table.SymbolTable
    """
    # Constants
    symbol_table.set("null", NULL)
    symbol_table.set("True", TRUE)
    symbol_table.set("False", FALSE)
    symbol_table.set("None", NoneValue(True))

    # Built-in functions
    symbol_table.set("void", VOID)
    symbol_table.set("run", RUN)
    symbol_table.set("example", EXAMPLE)

    symbol_table.set("print", PRINT)
    symbol_table.set("print_ret", PRINT_RET)
    symbol_table.set("input", INPUT)
    symbol_table.set("input_int", INPUT_INT)
    symbol_table.set("input_num", INPUT_NUM)
    symbol_table.set("clear", CLEAR)

    symbol_table.set("is_int", IS_INT)
    symbol_table.set("is_float", IS_FLOAT)
    symbol_table.set("is_num", IS_NUM)
    symbol_table.set("is_str", IS_STRING)
    symbol_table.set("is_list", IS_LIST)
    symbol_table.set("is_func", IS_FUNCTION)
    symbol_table.set("is_none", IS_NONE)
    symbol_table.set("type", TYPE)
    symbol_table.set("str", STR)
    symbol_table.set("list", LIST)
    symbol_table.set("int", INT)
    symbol_table.set("float", FLOAT)

    symbol_table.set("append", APPEND)
    symbol_table.set("pop", POP)
    symbol_table.set("insert", INSERT)
    symbol_table.set("extend", EXTEND)
    symbol_table.set("get", GET)
    symbol_table.set("replace", REPLACE)
    symbol_table.set("max", MAX)
    symbol_table.set("min", MIN)
    symbol_table.set("len", LEN)

    symbol_table.set("split", SPLIT)
    symbol_table.set("upper", UPPER)
    symbol_table.set("lower", LOWER)

    # Hum...
    symbol_table.set("answerToTheLifeTheUniverseAndEverything", Number(42))
    symbol_table.set("numberOfHornsOnAnUnicorn", Number(1))
    symbol_table.set("theLoneliestNumber", Number(1))
    symbol_table.set("rickroll", RICKROLL)
    symbol_table.set("nougaro", NOUGARO)

    # Technical
    symbol_table.set("exit", EXIT)
    symbol_table.set("system_call", SYSTEM_CALL)
    symbol_table.set('__os_name__', String(platform.system()))
    symbol_table.set('__os_release__', String(platform.uname().release))
    symbol_table.set('__os_version__', String(platform.uname().version))
    symbol_table.set('__python_version__',
                     String(
                         str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "." + str(sys.version_info[2])
                     ))
    # platform.system() may be 'Linux', 'Windows', 'Darwin', 'Java', etc. according to Python doc
    symbol_table.set('__base_value__', Value())

    # GPL
    symbol_table.set('__disclaimer_of_warranty__',
                     String(
                         "GNU GPL 3.0, 15, Disclaimer of Warranty :\n\n"
                         "  THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY\n"
                         "APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT\n"
                         "HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM \"AS IS\" WITHOUT WARRANTY\n"
                         "OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,\n"
                         "THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR\n"
                         "PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM\n"
                         "IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF\n"
                         "ALL NECESSARY SERVICING, REPAIR OR CORRECTION."
                     ))
    symbol_table.set("__gpl__", GPL)
    symbol_table.set("__is_keyword__", IS_KEYWORD)

    symbol_table.set('__symbol_table__', String(pprint.pformat(symbol_table.symbols)))
    # test_protected_vars(symbol_table)


def test_protected_vars(symbol_table: SymbolTable):
    """Test if all the variables in the symbol table are protected in writing or not. Used while coding."""
    error_count = 0
    for symbol in symbol_table.symbols:
        if symbol not in PROTECTED_VARS:
            if symbol != "numberOfHornsOnAnUnicorn" and symbol != "theLoneliestNumber" and symbol != "rickroll":
                print(f"missing {symbol} in PROTECTED_VARS")
                error_count += 1
    if error_count == 0:
        print("Good job! Basic SymbolTable does not contain unprotected vars! :)")
