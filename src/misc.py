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
from src.errors.errors import Error
from src.runtime.values.basevalues.basevalues import String
from src.runtime.values.basevalues.value import Value
from src.runtime.runtime_result import RTResult
# built-in python imports
from typing import Protocol, Any, TypedDict, Callable
import os
try:
    from colorama import init as colorama_init, Fore
    ForeRED: str = Fore.RED
    ForeRESET: str = Fore.RESET
except ModuleNotFoundError:
    colorama_init = lambda: None  # this is to avoid type checking errors
    ForeRED: str = ""
    ForeRESET: str = ""

colorama_init()


# ##########
# COLORS
# ##########
# prints text in red.
def print_in_red(txt: str = ""): print(ForeRED + txt + ForeRESET)


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


def nice_str_from_idk(idk: Any) -> String:
    """Returns a NOUGARO string from either a PYTHON value either a NOUGARO string"""
    if isinstance(idk, String):
        return idk
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
        exec_from: str = "(shell)",
        actual_context: str = "<program>",
        use_default_symbol_table: bool = False,
        use_context: Context | None = None,
        args: list[str | String] | None = None,
        work_dir: str | None = None
    ) -> tuple[Value, None] | tuple[None, Error]:
        ...

# ##########
# CUSTOM BUILTIN FUNC METHODS
# thanks to lancelote (https://github.com/lancelote) who works at JetBrains for these tricks
# ##########
class CustomBuiltInFuncMethod(Protocol):
    """The type of the methods `execute_{name}` in BuiltInFunction"""

    def __call__(self, exec_context: Context | None = None) -> RTResult:
        ...


class CustomBuiltInFuncMethodWithRunParam(CustomBuiltInFuncMethod):
    """The type of the methods `execute_{name}` with `run` parameter in BuiltInFunction"""

    def __call__(self, exec_context: Context | None = None, run: RunFunction | None = None, noug_dir: str | None = None, work_dir: str | None = None) -> RTResult:
        ...


class CustomBuiltInFuncMethodWithNougDirButNotRun(CustomBuiltInFuncMethod):
    """The type of the methods `execute_{name}` with `run` parameter in BuiltInFunction"""

    def __call__(self, exec_context: Context | None = None, noug_dir: str | None = None) -> RTResult:
        ...


class builtin_function_dict(TypedDict):
        function: Callable
        param_names: list[str]
        optional_params: list[str]
        should_respect_args_number: bool
        run_noug_dir_work_dir: bool
        noug_dir: bool  # if run_noug_dir_work_dir is True then this is False


# ##########
# CUSTOM INTERPRETER VISIT METHOD
# ##########
class CustomInterpreterVisitMethod(Protocol):
    """The type of the methods `visit_{name}` in Interpreter"""
    # This class was made to bypass a pycharm bug.
    def __call__(self, node: Node | None = None, exec_context: Context | None = None,
                 other_context: Context | None = None, methods_instead_of_funcs: bool = False) -> Any:
        ...
