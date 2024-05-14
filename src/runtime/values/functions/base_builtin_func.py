#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.lexer.position import Position
from src.runtime.values.basevalues.value import Value
from src.runtime.values.basevalues.basevalues import NoneValue, String
from src.runtime.values.functions.base_function import BaseFunction
from src.runtime.context import Context
from src.runtime.runtime_result import RTResult
from src.runtime.interpreter import Interpreter
from src.misc import RunFunction
# built-in python imports
# no imports


class BaseBuiltInFunction(BaseFunction):
    """Parent class for all the built-in function classes (even in modules)"""
    def __init__(self, name: str, pos_start: Position, pos_end: Position, call_with_module_context: bool = False):
        super().__init__(name, pos_start, pos_end, call_with_module_context)
        self.type_ = 'built-in func'

    def __repr__(self):
        return f'<built-in function {self.name}>'
    
    def to_python_str(self):
        return self.__repr__()

    def execute(self, args: list[Value], interpreter_: type[Interpreter], run: RunFunction, noug_dir: str,
                lexer_metas: dict[str, str | bool], exec_from: str = "<invalid>", use_context: Context | None = None,
                cli_args: list[String] | None = None, work_dir: str | None = None):
        return RTResult().success(NoneValue(self.pos_start, self.pos_end, False))

    def no_visit_method(self, exec_ctx: Context):
        """Method called when the func name given through self.name is not defined"""
        print(exec_ctx)
        print(f"NOUGARO INTERNAL ERROR: No execute_{self.name} method defined in "
              f"src.values.functions.base_builtin_function.BaseBuiltInFunction.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with all informations "
              f"above.")
        raise Exception(f'No execute_{self.name} method defined in '
                        f'src.values.functions.base_builtin_function.BaseBuiltInFunction.')

    def copy(self):
        """Return a copy of self"""
        copy = BaseBuiltInFunction(self.name, self.pos_start, self.pos_end, self.call_with_module_context)
        copy.set_context(self.context)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy
