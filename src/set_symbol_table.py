#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)

# IMPORTS
# nougaro modules imports
from src.symbol_table import SymbolTable
from src.values.basevalues import NoneValue
from src.values.specific_values.number import *
from src.values.specific_values.builtin_function import *
# built-in python imports
# no imports


def set_symbol_table(symbol_table: SymbolTable):
    """Configures the global symbol table
    :param symbol_table: src.symbol_table.SymbolTable
    """
    # Constants
    symbol_table.set("null", NULL)
    symbol_table.set("True", TRUE)
    symbol_table.set("False", FALSE)
    symbol_table.set("None", NoneValue(True))
    # MATHS
    symbol_table.set("math_pi", MATH_PI)
    symbol_table.set("math_e", MATH_E)
    symbol_table.set("sqrt_pi", MATH_SQRT_PI)
    # Built-in functions
    symbol_table.set("void", VOID)
    symbol_table.set("print", PRINT)
    symbol_table.set("print_ret", PRINT_RET)
    symbol_table.set("input", INPUT)
    symbol_table.set("input_int", INPUT_INT)
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
    symbol_table.set("extend", EXTEND)
    symbol_table.set("get", GET)
    symbol_table.set("max", MAX)
    symbol_table.set("min", MIN)
    # Mathematical functions
    symbol_table.set("sqrt", SQRT)
    symbol_table.set("math_root", MATH_ROOT)
    symbol_table.set("radians", RADIANS)
    symbol_table.set("degrees", DEGREES)
    symbol_table.set("sin", SIN)
    symbol_table.set("cos", COS)
    symbol_table.set("tan", TAN)
    symbol_table.set("asin", ASIN)
    symbol_table.set("acos", ACOS)
    symbol_table.set("atan", ATAN)
    # Hum...
    symbol_table.set("answerToTheLifeTheUniverseAndEverything", Number(42))
    symbol_table.set("numberOfHornsOnAnUnicorn", Number(1))
    symbol_table.set("theLoneliestNumber", Number(1))
    symbol_table.set("rickroll", RICKROLL)

    symbol_table.set("exit", EXIT)
