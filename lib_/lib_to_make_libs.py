#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from __future__ import annotations

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# THIS FILE CAN NOT BE IMPORTED FROM NOUGARO

# IMPORTS
# nougaro modules imports
from src.runtime.values.functions.builtin_function import *
from src.runtime.values.tools.py2noug import *
from src.errors.errors import *
# Above line : Context, RTResult, errors and values are imported in builtin_function.py
# built-in python imports
# no imports


class ModuleFunction(BaseBuiltInFunction):
    """ Parent class for all the modules """
    def __init__(self, module_name: str, function_name: str,
                 link_for_bug_report: str = "https://jd-develop.github.io/nougaro/bugreport.html"):
        super().__init__(function_name)
        self.module_name = module_name
        self.link_for_bug_report: str = link_for_bug_report

    def __repr__(self):
        return f'<built-in lib function {self.module_name}.{self.name}>'

    def execute(self, args: list[Value], interpreter_: type[Interpreter], run: RunFunction, noug_dir: str,
                exec_from: str = "<invalid>", use_context: Context | None = None, work_dir: str | None = None,
                cli_args: list[str | String] | None = None):
        # execute a function of the 'math' module
        # create the result
        result = RTResult()

        # generate the context and change the symbol table for the context
        exec_context = self.generate_new_context()
        assert exec_context.symbol_table is not None
        exec_context.symbol_table.set("__exec_from__", String(exec_from))
        exec_context.symbol_table.set("__actual_context__", String(self.name))
        if cli_args is None:
            exec_context.symbol_table.set("__args__", List([]))
        else:
            cli_args_values: list[Value] = list(map(nice_str_from_idk, cli_args))
            exec_context.symbol_table.set("__args__", List(cli_args_values))

        # get the method name and the method
        method_name = f'execute_{self.module_name}_{self.name}'
        method: CustomBuiltInFuncMethod = getattr(self, method_name, self.no_visit_method)

        # populate arguments
        result.register(self.check_and_populate_args(
            method.param_names, args, exec_context, optional_params=method.optional_params,
            should_respect_args_number=method.should_respect_args_number
        ))

        # if there is any error
        if result.should_return():
            return result

        try:
            # we try to execute the function
            return_value = result.register(method(exec_context))
        except TypeError:  # there is no `exec_context` parameter
            try:
                return_value = result.register(method())
            except TypeError:  # it only executes when coding
                return_value = result.register(method(exec_context))
        if result.should_return():  # check for any error
            return result
        # if all is OK, return what we should return
        return result.success(return_value)

    def no_visit_method(self, exec_ctx: Context):
        """Method called when the func name given through self.name is not defined"""
        print(exec_ctx)
        print(f"NOUGARO INTERNAL ERROR : No execute_{self.module_name}_{self.name} method defined in "
              f"lib_.{self.module_name}_.\n"
              f"Please report this bug at {self.link_for_bug_report} with all informations above.")
        raise Exception(f'No execute_{self.module_name}_{self.name} method defined in lib_.{self.module_name}_.')

    def copy(self):
        """Return a copy of self"""
        copy = ModuleFunction(self.module_name, self.name, self.link_for_bug_report)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return self.set_context_and_pos_to_a_copy(copy)

    def set_context_and_pos_to_a_copy(self, copy: ModuleFunction):
        """Also sets attributes (name not changed for retro-compatibility)"""
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.attributes = self.attributes.copy()
        return copy
