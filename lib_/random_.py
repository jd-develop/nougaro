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

""" Random module

    Random is a module that provides pseudo-random functions.
"""

# IMPORTS
# nougaro modules imports
from src.values.functions.builtin_function import *
# Comment about the above line : Context, RTResult, errors and values are imported in builtin_function.py
# built-in python imports
import random


class Random(BaseBuiltInFunction):
    """ Random Module """
    def __init__(self, name):
        super().__init__(name)

    def __repr__(self):
        return f'<built-in function random_{self.name}>'

    def execute(self, args, interpreter_, run, exec_from: str = "<invalid>"):
        # execute a function of the 'random' module
        # create the result
        result = RTResult()

        # generate the context and change the symbol table for the context
        exec_context = self.generate_new_context()
        exec_context.symbol_table.set("__exec_from__", String(exec_from))
        exec_context.symbol_table.set("__actual_context__", String(self.name))

        # get the method name and the method
        method_name = f'execute_random_{self.name}'
        method: CustomBuiltInFuncMethod = getattr(self, method_name, self.no_visit_method)

        # populate arguments
        result.register(self.check_and_populate_args(method.arg_names, args, exec_context,
                                                     optional_args=method.optional_args,
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
        print(f"NOUGARO INTERNAL ERROR : No execute_random_{self.name} method defined in lib_.random_.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with all informations "
              f"above.")
        raise Exception(f'No execute_random_{self.name} method defined in lib_.random_.')

    def copy(self):
        """Return a copy of self"""
        copy = Random(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    # =========
    # FUNCTIONS
    # =========
    def execute_random_randint(self, exec_ctx: Context):
        """Pick a random integer number in [a, b] mathematical range. a SHOULD BE lesser than b"""
        # Params:
        # * a
        # * b
        # we get 'a' and 'b' values
        a = exec_ctx.symbol_table.get("a")
        b = exec_ctx.symbol_table.get("b")
        if not isinstance(a, Number):  # we check if 'a' is a number
            return RTResult().failure(RunTimeError(
                a.pos_start, a.pos_end,
                "first argument of built-in module function 'random_randint' must be an int.",
                exec_ctx
            ))
        if a.type_ != 'int':  # we check if 'a' is an int
            return RTResult().failure(RunTimeError(
                a.pos_start, a.pos_end,
                "first argument of built-in module function 'random_randint' must be an int.",
                exec_ctx
            ))

        if not isinstance(b, Number):  # we check if 'b' is a number
            return RTResult().failure(RunTimeError(
                b.pos_start, b.pos_end,
                "second argument of built-in module function 'random_randint' must be an int.",
                exec_ctx
            ))
        if b.type_ != 'int':  # we check if 'b' is an int
            return RTResult().failure(RunTimeError(
                b.pos_start, b.pos_end,
                "second argument of built-in module function 'random_randint' must be an int.",
                exec_ctx
            ))

        if a.value > b.value:  # e.g. randint(4, -3) : it does not make ANY sense x)
            return RTResult().failure(RunTimeError(
                a.pos_start, b.pos_end,
                "first argument of built-in module function 'random_randint' MUST be less than or equal to its second"
                " argument.",
                exec_ctx
            ))

        random_number = random.randint(a.value, b.value)
        return RTResult().success(Number(random_number))

    execute_random_randint.arg_names = ['a', 'b']
    execute_random_randint.optional_args = []
    execute_random_randint.should_respect_args_number = True

    def execute_random_random(self):
        """Pick randomly a 16-digits float between 0 included and 1 included"""
        # No params.
        return RTResult().success(Number(random.random()))

    execute_random_random.arg_names = []
    execute_random_random.optional_args = []
    execute_random_random.should_respect_args_number = True

    def execute_random_choice(self, exec_ctx: Context):
        """Return a random element of a list"""
        # Params:
        # * list_
        list_ = exec_ctx.symbol_table.get("list_")  # we get the 'list' argument
        if not isinstance(list_, List):  # we check if it is a list
            return RTResult().failure(RunTimeError(
                list_.pos_start, list_.pos_end,
                "first argument of built-in module function 'random_choice' must be a list.",
                exec_ctx
            ))
        if len(list_.elements) == 0:  # if the list is empty, we raise an error
            return RTResult().failure(RunTimeError(
                list_.pos_start, list_.pos_end,
                "list is empty.",
                exec_ctx
            ))
        return RTResult().success(random.choice(list_.elements))  # then we return a random element of the list

    execute_random_choice.arg_names = ['list_']
    execute_random_choice.optional_args = []
    execute_random_choice.should_respect_args_number = True


WHAT_TO_IMPORT = {  # what are the new entries in the symbol table when the module is imported
    # functions
    "randint": Random("randint"),
    "random": Random("random"),
    "choice": Random("choice"),
}
