#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# IMPORTS
# nougaro modules imports
from src.context import Context
# built-in python imports
from typing import Protocol, Any
from colorama import Fore


# ##########
# COLORS
# ##########
def print_in_red(txt): print(Fore.RED + txt + Fore.RESET)


# ##########
# TOOL
# ##########
def is_num(value: Any): return isinstance(value, int) or isinstance(value, float)


# ##########
# CUSTOM BUILTIN FUNC METHOD
# ##########
class CustomBuiltInFuncMethod(Protocol):
    """
        Just a class for typing the methods `execute_{name}` in BuiltInFunction
    """
    # This class was made to bypass a pycharm bug.
    arg_names: list[str]
    optional_args: list[str]
    should_respect_args_number: bool

    def __call__(self, exec_context: Context = None) -> Any:
        ...


# ##########
# CUSTOM INTERPRETER VISIT METHOD
# ##########
class CustomInterpreterVisitMethod(Protocol):
    """
        Just a class for typing the methods `visit_{name}` in Interpreter
    """
    # This class was made to bypass a pycharm bug.
    def __call__(self, exec_context: Context = None, node=None) -> Any:
        ...
