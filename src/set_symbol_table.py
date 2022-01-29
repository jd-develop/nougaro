#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)

# IMPORTS
# nougaro modules imports
from src.symbol_table import SymbolTable
# built-in python imports
# no imports


def set_symbol_table(symbol_table: SymbolTable, number, none_value, builtin_func):
    """Configures the global symbol table
    :param symbol_table: src.symbol_table.SymbolTable
    :param number: src.Nougaro.Number
    :param none_value: src.Nougaro.NoneValue
    :param builtin_func: src.Nougaro.BuiltInFunc
    """
    # Constants
    symbol_table.set("null", number.NULL)
    symbol_table.set("True", number.TRUE)
    symbol_table.set("False", number.FALSE)
    symbol_table.set("None", none_value(True))
    # MATHS
    symbol_table.set("math_pi", number.MATH_PI)
    symbol_table.set("math_e", number.MATH_E)
    symbol_table.set("sqrt_pi", number.MATH_SQRT_PI)
    # Built-in functions
    symbol_table.set("void", builtin_func.VOID)
    symbol_table.set("print", builtin_func.PRINT)
    symbol_table.set("print_ret", builtin_func.PRINT_RET)
    symbol_table.set("input", builtin_func.INPUT)
    symbol_table.set("input_int", builtin_func.INPUT_INT)
    symbol_table.set("clear", builtin_func.CLEAR)

    symbol_table.set("is_int", builtin_func.IS_INT)
    symbol_table.set("is_float", builtin_func.IS_FLOAT)
    symbol_table.set("is_str", builtin_func.IS_STRING)
    symbol_table.set("is_list", builtin_func.IS_LIST)
    symbol_table.set("is_func", builtin_func.IS_FUNCTION)
    symbol_table.set("is_none", builtin_func.IS_NONE)
    symbol_table.set("type", builtin_func.TYPE)
    symbol_table.set("str", builtin_func.STR)
    symbol_table.set("list", builtin_func.LIST)
    symbol_table.set("int", builtin_func.INT)
    symbol_table.set("float", builtin_func.FLOAT)

    symbol_table.set("append", builtin_func.APPEND)
    symbol_table.set("pop", builtin_func.POP)
    symbol_table.set("extend", builtin_func.EXTEND)
    symbol_table.set("get", builtin_func.GET)
    symbol_table.set("max", builtin_func.MAX)
    symbol_table.set("min", builtin_func.MIN)
    # Mathematical functions
    symbol_table.set("sqrt", builtin_func.SQRT)
    symbol_table.set("math_root", builtin_func.MATH_ROOT)
    symbol_table.set("radians", builtin_func.RADIANS)
    symbol_table.set("degrees", builtin_func.DEGREES)
    symbol_table.set("sin", builtin_func.SIN)
    symbol_table.set("cos", builtin_func.COS)
    symbol_table.set("tan", builtin_func.TAN)
    symbol_table.set("asin", builtin_func.ASIN)
    symbol_table.set("acos", builtin_func.ACOS)
    symbol_table.set("atan", builtin_func.ATAN)
    # Hum...
    symbol_table.set("answerToTheLifeTheUniverseAndEverything", number(42))
    symbol_table.set("numberOfHornsOnAnUnicorn", number(1))
    symbol_table.set("theLoneliestNumber", number(1))

    symbol_table.set("exit", builtin_func.EXIT)
