#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.runtime.values.functions.base_function import BaseFunction
from src.runtime.context import Context
from src.runtime.runtime_result import RTResult
from src.runtime.values.basevalues.basevalues import NoneValue
# built-in python imports
# no imports


class BaseBuiltInFunction(BaseFunction):
    """Parent class for all the built-in function classes (even in modules)"""
    def __init__(self, name, call_with_module_context=False):
        super().__init__(name, call_with_module_context)
        self.type_ = 'built-in func'

    def __repr__(self):
        return f'<built-in function {self.name}>'

    def execute(self, args, interpreter_, run, noug_dir, exec_from: str = "<invalid>",
                use_context: Context | None = None):
        return RTResult().success(NoneValue(False))

    def no_visit_method(self, exec_context: Context):
        """Method called when the func name given through self.name is not defined"""
        print(exec_context)
        print(f"NOUGARO INTERNAL ERROR : No execute_{self.name} method defined in "
              f"src.values.functions.builtin_function.BaseBuiltInFunction.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with all informations "
              f"above.")
        raise Exception(f'No execute_{self.name} method defined in '
                        f'src.values.functions.builtin_function.BaseBuiltInFunction.')

    def copy(self):
        """Return a copy of self"""
        copy = BaseBuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.module_context = self.module_context
        return copy