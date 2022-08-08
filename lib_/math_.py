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

""" Math module

    Math is a module that contains mathematical stuff, such as functions and constants, that is very useful to do math
    things.
"""

# IMPORTS
# nougaro modules imports
from src.values.functions.builtin_function import *
# Above line : Context, RTResult, errors and values are imported in builtin_function.py
# built-in python imports
from math import sqrt as math_sqrt, degrees as math_degrees, radians as math_radians, sin as math_sin, cos as math_cos
from math import tan as math_tan, asin as math_asin, acos as math_acos, atan as math_atan, e, pi

# constants
PI = Number(pi)
SQRT_PI = Number(math_sqrt(pi))
E = Number(e)


class Math(BaseBuiltInFunction):
    """ Math Module """
    def __init__(self, name):
        super().__init__(name)

    def __repr__(self):
        return f'<built-in function math_{self.name}>'

    def execute(self, args, interpreter_, run, exec_from: str = "<invalid>"):
        # execute a function of the 'math' module
        # create the result
        result = RTResult()

        # generate the context and change the symbol table for the context
        exec_context = self.generate_new_context()
        exec_context.symbol_table.set("__exec_from__", String(exec_from))
        exec_context.symbol_table.set("__actual_context__", String(self.name))

        # get the method name and the method
        method_name = f'execute_math_{self.name}'
        method: CustomBuiltInFuncMethod = getattr(self, method_name, self.no_visit_method)

        # populate arguments
        result.register(self.check_and_populate_args(method.arg_names, args, exec_context,
                                                     optional_params=method.optional_args,
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
        print(f"NOUGARO INTERNAL ERROR : No execute_math_{self.name} method defined in lib_.math_.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with all informations "
              f"above.")
        raise Exception(f'No execute_math_{self.name} method defined in lib_.math_.')

    def copy(self):
        """Return a copy of self"""
        copy = Math(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    # =========
    # FUNCTIONS
    # =========
    def execute_math_sqrt(self, exec_context: Context):
        """Calculates square root of 'value'
        It returns the same as math_root(value, 2) or """
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in module function 'math_sqrt' must be a number.",
                exec_context
            ))

        if value.value < 0:  # we check if the value is greater than (or equal to) 0
            return RTResult().failure(RTArithmeticError(
                value.pos_start, value.pos_end,
                "first argument of built-in module function 'math_sqrt' must be greater than (or equal to) 0.",
                exec_context
            ))

        sqrt_ = math_sqrt(value.value)  # we calculate the square root
        return RTResult().success(Number(sqrt_))

    execute_math_sqrt.arg_names = ['value']
    execute_math_sqrt.optional_args = []
    execute_math_sqrt.should_respect_args_number = True

    def execute_math_root(self, exec_context: Context):
        """Calculates the n-root of 'value' (ⁿ√value)
        Default value for 'n' is 2 (sqrt)."""
        # Params:
        # * value
        # Optional params:
        # * n
        value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in module function 'math_math_root' must be a number.",
                exec_context
            ))

        if value.value < 0:  # we check if the value is greater than (or equal to) 0
            return RTResult().failure(RTArithmeticError(
                value.pos_start, value.pos_end,
                "first argument of built-in module function 'math_math_root' must be greater than (or equal to) 0.",
                exec_context
            ))

        n = exec_context.symbol_table.get('n')  # we get 'n'
        if n is None:  # if 'n' parameter is not filled, we set it to 2
            n = Number(2).set_pos(value.pos_end, self.pos_end)

        if not isinstance(n, Number):  # we check if 'n' is a number
            return RTResult().failure(RunTimeError(
                n.pos_start, n.pos_end,
                "second argument of built-in module function 'math_math_root' must be a number.",
                exec_context
            ))

        value_to_return = Number(value.value ** (1 / n.value))  # we calculate the root

        return RTResult().success(value_to_return)

    execute_math_root.arg_names = ['value']
    execute_math_root.optional_args = ['n']
    execute_math_root.should_respect_args_number = True

    def execute_math_degrees(self, exec_context: Context):
        """Converts 'value' (radians) to degrees"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in module function 'math_degrees' must be a number (angle in radians).",
                exec_context
            ))
        degrees = math_degrees(value.value)
        return RTResult().success(Number(degrees))

    execute_math_degrees.arg_names = ['value']
    execute_math_degrees.optional_args = []
    execute_math_degrees.should_respect_args_number = True

    def execute_math_radians(self, exec_context: Context):
        """Converts 'value' (degrees) to radians"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in module function 'math_radians' must be a number (angle in degrees).",
                exec_context
            ))
        radians = math_radians(value.value)
        return RTResult().success(Number(radians))

    execute_math_radians.arg_names = ['value']
    execute_math_radians.optional_args = []
    execute_math_radians.should_respect_args_number = True

    def execute_math_sin(self, exec_context: Context):
        """Calculates sin('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in module function 'math_sin' must be a number (angle in radians).",
                exec_context
            ))
        sin = math_sin(value.value)
        return RTResult().success(Number(sin))

    execute_math_sin.arg_names = ['value']
    execute_math_sin.optional_args = []
    execute_math_sin.should_respect_args_number = True

    def execute_math_cos(self, exec_context: Context):
        """Calculates cos('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in module function 'math_cos' must be a number (angle in radians).",
                exec_context
            ))
        cos = math_cos(value.value)
        return RTResult().success(Number(cos))

    execute_math_cos.arg_names = ['value']
    execute_math_cos.optional_args = []
    execute_math_cos.should_respect_args_number = True

    def execute_math_tan(self, exec_context: Context):
        """Calculates tan('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in module function 'math_tan' must be a number (angle in radians).",
                exec_context
            ))
        tan = math_tan(value.value)
        return RTResult().success(Number(tan))

    execute_math_tan.arg_names = ['value']
    execute_math_tan.optional_args = []
    execute_math_tan.should_respect_args_number = True

    def execute_math_asin(self, exec_context: Context):
        """Calculates asin('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in module function 'math_asin' must be a number.",
                exec_context
            ))
        try:
            asin = math_asin(value.value)
        except ValueError:
            return RTResult().failure(RTArithmeticError(
                value.pos_start, value.pos_end,
                "first argument of built-in module function 'math_asin' must be a number between -1 and 1.",
                exec_context
            ))
        return RTResult().success(Number(asin))

    execute_math_asin.arg_names = ['value']
    execute_math_asin.optional_args = []
    execute_math_asin.should_respect_args_number = True

    def execute_math_acos(self, exec_context: Context):
        """Calculates acos('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in module function 'math_acos' must be a number.",
                exec_context
            ))
        try:
            acos = math_acos(value.value)
        except ValueError:  # 1 < value or value < -1
            return RTResult().failure(RTArithmeticError(
                value.pos_start, value.pos_end,
                "first argument of built-in module function 'math_acos' must be a number between -1 and 1.",
                exec_context
            ))
        return RTResult().success(Number(acos))

    execute_math_acos.arg_names = ['value']
    execute_math_acos.optional_args = []
    execute_math_acos.should_respect_args_number = True

    def execute_math_atan(self, exec_context: Context):
        """Calculates atan('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in module function 'math_atan' must be a number.",
                exec_context
            ))
        atan = math_atan(value.value)
        return RTResult().success(Number(atan))

    execute_math_atan.arg_names = ['value']
    execute_math_atan.optional_args = []
    execute_math_atan.should_respect_args_number = True

    def execute_math_abs(self, exec_context: Context):
        """Exactly like python `abs()` (absolute value)"""
        # Params:
        # * value
        value: Value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in module function 'math_abs' must be a number.",
                exec_context
            ))

        value_to_return = value.abs_()

        return RTResult().success(value_to_return)

    execute_math_abs.arg_names = ['value']
    execute_math_abs.optional_args = []
    execute_math_abs.should_respect_args_number = True


WHAT_TO_IMPORT = {  # what are the new entries in the symbol table when the module is imported
    # Constants
    "pi": PI,
    "sqrt_pi": SQRT_PI,
    "e": E,

    # Functions
    "sqrt": Math("sqrt"),
    "root": Math("root"),
    "radians": Math("radians"),
    "degrees": Math("degrees"),
    "sin": Math("sin"),
    "cos": Math("cos"),
    "tan": Math("tan"),
    "asin": Math("asin"),
    "acos": Math("acos"),
    "atan": Math("atan"),
    "abs": Math("abs"),
}
