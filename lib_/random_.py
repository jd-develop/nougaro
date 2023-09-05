#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
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


class Random(ModuleFunction):
    """ Random module """
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
        a = exec_ctx.symbol_table.getf("a")
        b = exec_ctx.symbol_table.getf("b")
        if not isinstance(a, Number) or not a.is_int():  # we check if 'a' is an integer
            return RTResult().failure(RTTypeErrorF(
                a.pos_start, a.pos_end, "first", "random.randint", "int", a,
                exec_ctx, "lib_.random_.Random.execute_random_randint"
            ))

        if not isinstance(b, Number) or not b.is_int():  # we check if 'b' is an integer
            return RTResult().failure(RTTypeErrorF(
                b.pos_start, b.pos_end, "second", "random.randint", "int", b,
                exec_ctx, "lib_.random_.Random.execute_random_randint"
            ))

        if a.value > b.value:  # e.g. randint(4, -3) : it does not make ANY sense x)
            return RTResult().failure(RunTimeError(
                a.pos_start, b.pos_end,
                "first argument of the built-in function 'random.randint' MUST be less than or equal to its second"
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
        list_ = exec_ctx.symbol_table.getf("list_")  # we get the 'list' argument
        if not isinstance(list_, List):  # we check if it is a list
            return RTResult().failure(RTTypeErrorF(
                list_.pos_start, list_.pos_end, "first", "random.choice", "list", list_,
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
