#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
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
    functions: dict[str, BuiltinFunctionDict] = {}

    def __init__(self, name: str):
        super().__init__("random", name, functions=self.functions)

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
        assert exec_ctx.symbol_table is not None
        a = exec_ctx.symbol_table.getf("a")
        b = exec_ctx.symbol_table.getf("b")
        if not (isinstance(a, Number) and isinstance(a.value, int)):  # we check if 'a' is an integer
            assert a is not None
            return RTResult().failure(RTTypeErrorF(
                a.pos_start, a.pos_end, "first", "random.randint", "int", a,
                exec_ctx, "lib_.random_.Random.execute_random_randint"
            ))

        if not (isinstance(b, Number) and isinstance(b.value, int)):  # we check if 'b' is an integer
            assert b is not None
            return RTResult().failure(RTTypeErrorF(
                b.pos_start, b.pos_end, "second", "random.randint", "int", b,
                exec_ctx, "lib_.random_.Random.execute_random_randint"
            ))

        if a.value > b.value:  # e.g. randint(4, -3)
            return RTResult().failure(RunTimeError(
                a.pos_start, b.pos_end,
                "first argument of the built-in function 'random.randint' MUST be less than or equal to its second"
                " argument.",
                exec_ctx, origin_file="lib_.random_.Random.execute_random_randint"
            ))

        random_number = random.randint(a.value, b.value)
        return RTResult().success(Number(random_number, self.pos_start, self.pos_end))

    functions["randint"] = {
        "function": execute_random_randint,
        "param_names": ["a", "b"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_random_random(self):
        """Pick randomly a 16-digits float between 0 included and 1 included"""
        # No params.
        return RTResult().success(Number(random.random(), self.pos_start, self.pos_end))

    functions["random"] = {
        "function": execute_random_random,
        "param_names": [],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_random_choice(self, exec_ctx: Context):
        """Return a random element of a list"""
        # Params:
        # * list_
        assert exec_ctx.symbol_table is not None
        list_ = exec_ctx.symbol_table.getf("list_")  # we get the 'list' argument
        if not isinstance(list_, List):  # we check if it is a list
            assert list_ is not None
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

    functions["choice"] = {
        "function": execute_random_choice,
        "param_names": ["list_"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_random_shuffle(self, exec_ctx: Context):
        """Shuffle a list and returns it."""
        # Params:
        # * list_
        assert exec_ctx.symbol_table is not None
        list_ = exec_ctx.symbol_table.getf("list_")  # we get the 'list' argument
        if not isinstance(list_, List):  # we check if it is a list
            assert list_ is not None
            return RTResult().failure(RTTypeErrorF(
                list_.pos_start, list_.pos_end, "first", "random.shuffle", "list", list_,
                exec_ctx, "lib_.random_.Random.execute_random_shuffle"
            ))
        
        py_list = list_.elements.copy()
        random.shuffle(py_list)
        list_.elements = py_list

        return RTResult().success(list_)
    
    functions["shuffle"] = {
        "function": execute_random_shuffle,
        "param_names": ["list_"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }
    
    def execute_random_seed(self, exec_ctx: Context):
        """Set the seed to generate pseudo-random numbers."""
        # Params:
        # * seed
        assert exec_ctx.symbol_table is not None
        seed = exec_ctx.symbol_table.getf("seed")
        if not (isinstance(seed, Number) or isinstance(seed, String)):
            assert seed is not None
            return RTResult().failure(RTTypeErrorF(
                seed.pos_start, seed.pos_end, "first", "random.seed", "number or string", seed,
                exec_ctx, "lib_.random_.Random.execute_random_seed"
            ))
        random.seed(seed.value)
        return RTResult().success(NoneValue(self.pos_start, self.pos_end, False))
    
    functions["seed"] = {
        "function": execute_random_seed,
        "param_names": ["seed"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }


WHAT_TO_IMPORT = {  # what are the new entries in the symbol table when the module is imported
    # functions
    "randint": Random("randint"),
    "random": Random("random"),
    "choice": Random("choice"),
    "shuffle": Random("shuffle"),
    "seed": Random("seed"),
}
