#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.runtime.context import Context
from src.parser.nodes import Node
from src.runtime.values.basevalues.basevalues import String
# built-in python imports
from typing import Protocol, Any
import os
try:
    from colorama import init as colorama_init, Fore
    colorama_installed = True
except ModuleNotFoundError:
    colorama_installed = False

if colorama_installed:
    colorama_init()


# ##########
# COLORS
# ##########
# prints text in red.
if colorama_installed:
    def print_in_red(txt: str = ""): print(Fore.RED + txt + Fore.RESET)
else:
    print_in_red = print


# ##########
# TOOLS
# ##########
def is_num(value: Any):
    """Return True if `value` is a python `int` or `float`. Return False in the other cases, including `bool`"""
    return (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool)


def does_tok_type_exist(tok_type: str):
    """Return True if the token type exists (e.g. 'TT_EQ' exists, but 'TT_FOO' does not)"""
    from src.lexer.token_types import TT
    return tok_type in TT


def is_keyword(word: str):
    """Return True if the str is a valid Nougaro keyword, such as 'import' or 'if'."""
    from src.lexer.token_types import KEYWORDS
    return word in KEYWORDS


def clear_screen():
    # depends on the os
    # if windows -> 'cls'
    # if Linux, macOS or UNIX -> 'clear'
    # TODO: find more OSes to include here OR find another way to clear the screen
    os.system('cls' if (os.name.lower() == "nt" or os.name.lower().startswith("windows")) else 'clear')


def nice_str_from_idk(idk):
    """Returns a NOUGARO string from either a PYTHON value either a NOUGARO string"""
    if isinstance(idk, String):
        return idk
    elif isinstance(idk, str):
        return String(idk)
    else:
        return String(str(idk))


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

    def __call__(self, exec_context: Context = None, run=None, noug_dir: str = None, work_dir: str = None) -> Any:
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
    def __call__(self, node: Node = None, exec_context: Context = None,
                 other_context: Context = None, methods_instead_of_funcs: bool = False) -> Any:
        ...
