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


class CustomBuiltInFuncMethodWithRunParam(CustomBuiltInFuncMethod):
    """
        Just a class for typing the methods `execute_{name}` with `run` parameter in BuiltInFunction
    """
    # This class was made to bypass a pycharm bug.

    def __call__(self, exec_context: Context = None, run=None) -> Any:
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
