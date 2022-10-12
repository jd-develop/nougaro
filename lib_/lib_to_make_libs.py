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

# THIS FILE CAN NOT BE IMPORTED FROM NOUGARO

# IMPORTS
# nougaro modules imports
from src.values.functions.builtin_function import *
from src.values.py2noug import *
from src.errors import *
# Above line : Context, RTResult, errors and values are imported in builtin_function.py
# built-in python imports
# no imports


class Module(BaseBuiltInFunction):
    """ Parent class for all the modules """
    def __init__(self, module_name, function_name,
                 link_for_bug_report: str = "https://jd-develop.github.io/nougaro/bugreport.html"):
        super().__init__(function_name)
        self.module_name = module_name
        self.link_for_bug_report: str = link_for_bug_report

    def __repr__(self):
        return f'<built-in lib function {self.module_name}_{self.name}>'

    def execute(self, args, interpreter_, run, exec_from: str = "<invalid>"):
        # execute a function of the 'math' module
        # create the result
        result = RTResult()

        # generate the context and change the symbol table for the context
        exec_context = self.generate_new_context()
        exec_context.symbol_table.set("__exec_from__", String(exec_from))
        exec_context.symbol_table.set("__actual_context__", String(self.name))

        # get the method name and the method
        method_name = f'execute_{self.module_name}_{self.name}'
        method: CustomBuiltInFuncMethod = getattr(self, method_name, self.no_visit_method)

        # populate arguments
        result.register(self.check_and_populate_args(method.param_names, args, exec_context,
                                                     optional_params=method.optional_params,
                                                     should_respect_args_number=method.should_respect_args_number))

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

    def no_visit_method(self, exec_context: Context):
        """Method called when the func name given through self.name is not defined"""
        print(exec_context)
        print(f"NOUGARO INTERNAL ERROR : No execute_{self.module_name}_{self.name} method defined in "
              f"lib_.{self.module_name}_.\n"
              f"Please report this bug at {self.link_for_bug_report} with all informations above.")
        raise Exception(f'No execute_{self.module_name}_{self.name} method defined in lib_.{self.module_name}_.')

    def copy(self):
        """Return a copy of self"""
        copy = Module(self.module_name, self.name, self.link_for_bug_report)
        return self.set_context_and_pos_to_a_copy(copy)

    def set_context_and_pos_to_a_copy(self, copy):
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
