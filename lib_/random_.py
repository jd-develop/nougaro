#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# IMPORTS
# nougaro modules imports
from src.values.functions.builtin_function import *
# Comment about the above line : Context, RTResult and values are imported in builtin_function.py
# built-in python imports
import random


class Random(BaseBuiltInFunction):
    """ Module Random """
    def __init__(self, name):
        super().__init__(name)

    def __repr__(self):
        return f'<built-in function random_{self.name}>'

    def execute(self, args, interpreter_, run, exec_from: str = "<invalid>"):
        result = RTResult()
        exec_context = self.generate_new_context()
        exec_context.symbol_table.set("__exec_from__", String(exec_from))
        exec_context.symbol_table.set("__actual_context__", String(self.name))

        method_name = f'execute_random_{self.name}'
        method: CustomBuiltInFuncMethod = getattr(self, method_name, self.no_visit_method)

        result.register(self.check_and_populate_args(method.arg_names, args, exec_context,
                                                     optional_args=method.optional_args,
                                                     should_respect_args_number=method.should_respect_args_number))
        if result.should_return():
            return result

        try:
            return_value = result.register(method(exec_context))
        except TypeError:
            try:
                return_value = result.register(method())
            except TypeError:  # it only executes when coding
                return_value = result.register(method(exec_context))
        if result.should_return():
            return result
        return result.success(return_value)

    def no_visit_method(self, exec_context: Context):
        print(exec_context)
        print(f"NOUGARO INTERNAL ERROR : No execute_random_{self.name} method defined in lib_.random_.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with all informations "
              f"above.")
        raise Exception(f'No execute_random_{self.name} method defined in lib_.random_.')

    def copy(self):
        copy = Random(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    # =========
    # FUNCTIONS
    # =========
    def execute_random_randint(self, exec_ctx: Context):
        """Like python random.randint()"""
        # Params:
        # * a
        # * b
        a = exec_ctx.symbol_table.get("a")
        b = exec_ctx.symbol_table.get("b")
        if not isinstance(a, Number):
            return RTResult().failure(RunTimeError(
                a.pos_start, a.pos_end,
                "first argument of built-in module function 'random_randint' must be an int.",
                exec_ctx
            ))
        if a.type_ != 'int':
            return RTResult().failure(RunTimeError(
                a.pos_start, a.pos_end,
                "first argument of built-in module function 'random_randint' must be an int.",
                exec_ctx
            ))

        if not isinstance(b, Number):
            return RTResult().failure(RunTimeError(
                b.pos_start, b.pos_end,
                "second argument of built-in module function 'random_randint' must be an int.",
                exec_ctx
            ))
        if b.type_ != 'int':
            return RTResult().failure(RunTimeError(
                b.pos_start, b.pos_end,
                "second argument of built-in module function 'random_randint' must be an int.",
                exec_ctx
            ))
        random_number = random.randint(a.value, b.value)
        return RTResult().success(Number(random_number))

    execute_random_randint.arg_names = ['a', 'b']
    execute_random_randint.optional_args = []
    execute_random_randint.should_respect_args_number = True

    def execute_random_random(self):
        """Like python random.random()"""
        # No params.
        return RTResult().success(Number(random.random()))

    execute_random_random.arg_names = []
    execute_random_random.optional_args = []
    execute_random_random.should_respect_args_number = True

    def execute_random_choice(self, exec_ctx: Context):
        """Like python random.choice()"""
        # Params:
        # * list_
        list_ = exec_ctx.symbol_table.get("list_")
        if not isinstance(list_, List):
            return RTResult().failure(RunTimeError(
                list_.pos_start, list_.pos_end,
                "first argument of built-in module function 'random_choice' must be a list.",
                exec_ctx
            ))
        if len(list_.elements) == 0:
            return RTResult().failure(RunTimeError(
                list_.pos_start, list_.pos_end,
                "list is empty.",
                exec_ctx
            ))
        return RTResult().success(random.choice(list_.elements))

    execute_random_choice.arg_names = ['list_']
    execute_random_choice.optional_args = []
    execute_random_choice.should_respect_args_number = True


WHAT_TO_IMPORT = {
    "randint": Random("randint"),
    "random": Random("random"),
    "choice": Random("choice"),
}
