#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)

# IMPORTS
# nougaro modules imports
from src.symbol_table import SymbolTable
from src.values.basevalues import NoneValue
from src.values.specific_values.number import *
from src.values.basevalues import String
from src.values.specific_values.builtin_function import *
from src.constants import VARS_CANNOT_MODIFY
# built-in python imports
import platform


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
    symbol_table.set("upper", UPPER)
    symbol_table.set("lower", LOWER)

    symbol_table.set("append", APPEND)
    symbol_table.set("pop", POP)
    symbol_table.set("extend", EXTEND)
    symbol_table.set("get", GET)
    symbol_table.set("max", MAX)
    symbol_table.set("min", MIN)
    symbol_table.set("len", LEN)

    # Hum...
    symbol_table.set("answerToTheLifeTheUniverseAndEverything", Number(42))
    symbol_table.set("numberOfHornsOnAnUnicorn", Number(1))
    symbol_table.set("theLoneliestNumber", Number(1))
    symbol_table.set("rickroll", RICKROLL)
    symbol_table.set("nougaro", NOUGARO)

    symbol_table.set("exit", EXIT)
    symbol_table.set("system_call", SYSTEM_CALL)
    symbol_table.set('os_name', String(platform.system()))
    symbol_table.set('os_release', String(platform.uname().release))
    symbol_table.set('os_version', String(platform.uname().version))
    # platform.system() may be 'Linux', 'Windows', 'Darwin', 'Java', etc. according to Python doc
    # test_protected_vars(symbol_table)


def test_protected_vars(symbol_table: SymbolTable):
    error_count = 0
    for symbol in symbol_table.symbols:
        if symbol not in VARS_CANNOT_MODIFY:
            if symbol != "numberOfHornsOnAnUnicorn" and symbol != "theLoneliestNumber" and symbol != "rickroll":
                print(f"missing {symbol} in VARS_CANNOT_MODIFY")
                error_count += 1
    if error_count == 0:
        print("Basic SymbolTable do not contain unprotected vars ! :)")
