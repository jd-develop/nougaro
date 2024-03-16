#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# __future__ import (must be first)
from __future__ import annotations
# nougaro modules imports
from src.runtime.context import Context
from src.parser.nodes import Node
from src.errors.errors import Error
from src.runtime.values.basevalues.basevalues import String
from src.runtime.values.basevalues.value import Value
from src.runtime.runtime_result import RTResult
# built-in python imports
from typing import Protocol, Any, TypedDict, Sequence, Callable
import os
try:
    from colorama import init as colorama_init, Fore
    foreRED: str = Fore.RED
    foreGREEN: str = Fore.GREEN
    foreRESET: str = Fore.RESET
except (ModuleNotFoundError, ImportError):
    def colorama_init():
        return None
    foreRED: str = ""
    foreGREEN: str = ""
    foreRESET: str = ""

colorama_init()


# ##########
# COLORS
# ##########
# prints text in red.
def print_in_red(txt: str = ""): print(foreRED + txt + foreRESET)
# prints text in green.
def print_in_green(txt: str = ""): print(foreGREEN + txt + foreRESET)


# ##########
# TOOLS
# ##########
def is_num(value: Any) -> bool:
    """Return True if `value` is a python `int` or `float`. Return False in the other cases, including `bool`"""
    if isinstance(value, bool):
        return False
    if isinstance(value, int) or isinstance(value, float):
        return True
    return False


def is_tok_type(tok_type: str):
    """Return True if the token type exists (e.g. 'TT_EQ' exists, but 'TT_FOO' does not)"""
    from src.lexer.token_types import TT
    return tok_type in TT


does_tok_type_exist = is_tok_type  # alias for retro-compatibility


def is_keyword(word: str):
    """Return True if the str is a valid Nougaro keyword, such as 'import' or 'if'."""
    from src.lexer.token_types import KEYWORDS
    return word in KEYWORDS


def clear_screen():
    # depends on the os
    # if windows -> 'cls'
    # if GNU/Linux, macOS or Unix -> 'clear'
    # TODO: find more OSes to include here OR find another way to clear the screen
    os.system('cls' if (os.name.lower() == "nt" or os.name.lower().startswith("windows")) else 'clear')


def nice_str_from_idk(idk: Any) -> String:
    """Returns a NOUGARO string from either a PYTHON value either a NOUGARO string"""
    if isinstance(idk, String):
        return idk
    elif isinstance(idk, Value):
        string, error = idk.to_str_()
        if error is None:
            assert string is not None
            return string
        return String(idk.to_python_str())
    elif isinstance(idk, str):
        return String(idk)
    else:
        return String(str(idk))


class RunFunction(Protocol):
    """The type of the run function found in nougaro.py"""

    def __call__(
        self,
        file_name: str,
        text: str | None,
        noug_dir: str,
        version: str | None = None,
        exec_from: str | None = "(shell)",
        actual_context: str = "<program>",
        use_default_symbol_table: bool = False,
        use_context: Context | None = None,
        args: Sequence[str | String] | None = None,
        work_dir: str | None = None,
        lexer_metas: dict[str, str | bool] | None = None
    ) -> tuple[Value, None, dict[str, str | bool] | None] | tuple[None, Error, dict[str, str | bool] | None]:
        ...


# ##########
# CUSTOM BUILTIN FUNC METHODS
# ##########
class BuiltinFunctionDict(TypedDict):
    function: Callable[..., RTResult]
    param_names: list[str]
    optional_params: list[str]
    should_respect_args_number: bool
    run_noug_dir_work_dir: bool
    noug_dir: bool  # if run_noug_dir_work_dir is True then this is False


# ##########
# CUSTOM INTERPRETER VISIT METHOD
# thanks to lancelote (https://github.com/lancelote) who works at JetBrains for these tricks
# ##########
class CustomInterpreterVisitMethod(Protocol):
    """The type of the methods `visit_{name}` in Interpreter"""
    # This class was made to bypass a pycharm bug.
    def __call__(self, node: Node | None = None, exec_context: Context | None = None,
                 other_context: Context | None = None, methods_instead_of_funcs: bool = False) -> RTResult:
        ...
