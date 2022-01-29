#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# IMPORTS
# nougaro modules imports
from src.context import Context
# built-in python imports
from typing import Protocol, Any


# ##########
# COLORS
# ##########
def print_in_red(txt): print(u"\033[91m" + txt + u"\033[00m")


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
    have_to_respect_args_number: bool

    def __call__(self, exec_context: Context = None) -> Any:
        ...
