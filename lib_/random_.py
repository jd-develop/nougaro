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

""" Random module

    Random is a module that provides pseudo-random functions.
"""

# IMPORTS
# nougaro modules imports
from lib_.lib_to_make_libs import *
# Comment about the above line : Context, RTResult, errors and values are imported in lib_to_make_libs.py
# built-in python imports
import random


class Random(Module):
    """ Random Module """
    def __init__(self, name):
        super().__init__("random", name)

    def copy(self):
        """Return a copy of self"""
        copy = Random(self.name)
        return self.set_context_and_pos_to_a_copy(copy)

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
            return RTResult().failure(RTTypeError(
                a.pos_start, a.pos_end,
                "first argument of built-in module function 'random_randint' must be an int.",
                exec_ctx, "lib_.random_.Random.execute_random_randint"
            ))
        if a.type_ != 'int':  # we check if 'a' is an int
            return RTResult().failure(RTTypeError(
                a.pos_start, a.pos_end,
                "first argument of built-in module function 'random_randint' must be an int.",
                exec_ctx, "lib_.random_.Random.execute_random_randint"
            ))

        if not isinstance(b, Number):  # we check if 'b' is a number
            return RTResult().failure(RTTypeError(
                b.pos_start, b.pos_end,
                "second argument of built-in module function 'random_randint' must be an int.",
                exec_ctx, "lib_.random_.Random.execute_random_randint"
            ))
        if b.type_ != 'int':  # we check if 'b' is an int
            return RTResult().failure(RTTypeError(
                b.pos_start, b.pos_end,
                "second argument of built-in module function 'random_randint' must be an int.",
                exec_ctx, "lib_.random_.Random.execute_random_randint"
            ))

        if a.value > b.value:  # e.g. randint(4, -3) : it does not make ANY sense x)
            return RTResult().failure(RunTimeError(
                a.pos_start, b.pos_end,
                "first argument of built-in module function 'random_randint' MUST be less than or equal to its second"
                " argument.",
                exec_ctx, origin_file="lib_.random_.Random.execute_random_randint"
            ))

        random_number = random.randint(a.value, b.value)
        return RTResult().success(Number(random_number))

    execute_random_randint.param_names = ['a', 'b']
    execute_random_randint.optional_params = []
    execute_random_randint.should_respect_args_number = True

    def execute_random_random(self):
        """Pick randomly a 16-digits float between 0 included and 1 included"""
        # No params.
        return RTResult().success(Number(random.random()))

    execute_random_random.param_names = []
    execute_random_random.optional_params = []
    execute_random_random.should_respect_args_number = True

    def execute_random_choice(self, exec_ctx: Context):
        """Return a random element of a list"""
        # Params:
        # * list_
        list_ = exec_ctx.symbol_table.get("list_")  # we get the 'list' argument
        if not isinstance(list_, List):  # we check if it is a list
            return RTResult().failure(RTTypeError(
                list_.pos_start, list_.pos_end,
                "first argument of built-in module function 'random_choice' must be a list.",
                exec_ctx, "lib_.random_.Random.execute_random_choice"
            ))
        if len(list_.elements) == 0:  # if the list is empty, we raise an error
            return RTResult().failure(RunTimeError(
                list_.pos_start, list_.pos_end,
                "list is empty.",
                exec_ctx, origin_file="lib_.random_.Random.execute_random_choice"
            ))
        return RTResult().success(random.choice(list_.elements))  # then we return a random element of the list

    execute_random_choice.param_names = ['list_']
    execute_random_choice.optional_params = []
    execute_random_choice.should_respect_args_number = True


WHAT_TO_IMPORT = {  # what are the new entries in the symbol table when the module is imported
    # functions
    "randint": Random("randint"),
    "random": Random("random"),
    "choice": Random("choice"),
}
