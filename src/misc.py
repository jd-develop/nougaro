#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
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
from src.runtime.context import Context
from src.parser.nodes import Node
# built-in python imports
from typing import Protocol, Any
from colorama import init as colorama_init, Fore

colorama_init()


# ##########
# COLORS
# ##########
# prints text in red.
def print_in_red(txt): print(Fore.RED + txt + Fore.RESET)


# ##########
# TOOLS
# ##########
def is_num(value: Any): return isinstance(value, int) or isinstance(value, float)  # returns True if the value is a
#                                                                                    python int or float


def does_tok_type_exist(tok_type: str):
    """Return True if the token type exists (e.g. 'TT_EQ' exists, but 'TT_FOO' does not)"""
    from src.lexer.token_types import TT
    return tok_type in TT


def is_keyword(word: str):
    """Return True if the str is a valid Nougaro keyword, such as 'import' or 'if'."""
    from src.lexer.token_types import KEYWORDS
    return word in KEYWORDS


# ##########
# CUSTOM BUILTIN FUNC METHODS
# thanks to lancelote (https://github.com/lancelote) that works at JetBrains for these tricks
# ##########
class CustomBuiltInFuncMethod(Protocol):
    """The type of the methods `execute_{name}` in BuiltInFunction"""
    # This class was made to bypass a pycharm bug.
    param_names: list[str]
    optional_params: list[str]
    should_respect_args_number: bool

    def __call__(self, exec_context: Context = None) -> Any:
        ...


class CustomBuiltInFuncMethodWithRunParam(CustomBuiltInFuncMethod):
    """The type of the methods `execute_{name}` with `run` parameter in BuiltInFunction"""
    # This class was made to bypass a pycharm bug.

    def __call__(self, exec_context: Context = None, run=None, noug_dir: str = None) -> Any:
        ...


class CustomBuiltInFuncMethodWithNougDirButNotRun(CustomBuiltInFuncMethod):
    """The type of the methods `execute_{name}` with `run` parameter in BuiltInFunction"""
    # This class was made to bypass a pycharm bug.

    def __call__(self, exec_context: Context = None, noug_dir: str = None) -> Any:
        ...


# ##########
# CUSTOM INTERPRETER VISIT METHOD
# ##########
class CustomInterpreterVisitMethod(Protocol):
    """The type of the methods `visit_{name}` in Interpreter"""
    # This class was made to bypass a pycharm bug.
    def __call__(self, node: Node = None, exec_context: Context = None, other_context: Context = None) -> Any:
        ...
