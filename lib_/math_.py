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

""" Math module

    Math is a module that contains mathematical stuff, such as functions and constants, that is very useful to do math
    things.
"""

# IMPORTS
# nougaro modules imports
from lib_.lib_to_make_libs import *
# Above line : Context, RTResult, errors and values are imported in lib_to_make_libs.py
# built-in python imports
from math import sqrt as math_sqrt, degrees as math_degrees, radians as math_radians, sin as math_sin, cos as math_cos
from math import tan as math_tan, asin as math_asin, acos as math_acos, atan as math_atan, log, log2, e, pi

# constants
PI = Number(pi)
SQRT_PI = Number(math_sqrt(pi))
E = Number(e)


class Math(ModuleFunction):
    """ Math module """
    def __init__(self, name):
        super().__init__("math", name)

    def copy(self):
        """Return a copy of self"""
        copy = Math(self.name)
        return self.set_context_and_pos_to_a_copy(copy)

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
            return RTResult().failure(RTTypeError(
                value.pos_start, value.pos_end,
                "first argument of the built-in function 'math.sqrt' must be a number.",
                exec_context, "lib_.math_.Math.execute_math_sqrt"
            ))

        if value.value < 0:  # we check if the value is greater than (or equal to) 0
            return RTResult().failure(RTArithmeticError(
                value.pos_start, value.pos_end,
                "first argument of the built-in function 'math.sqrt' must be greater than (or equal to) 0.",
                exec_context, "lib_.math_.Math.execute_math_sqrt"
            ))

        sqrt_ = math_sqrt(value.value)  # we calculate the square root
        return RTResult().success(Number(sqrt_))

    execute_math_sqrt.param_names = ['value']
    execute_math_sqrt.optional_params = []
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
            return RTResult().failure(RTTypeError(
                value.pos_start, value.pos_end,
                "first argument of the built-in function 'math.math_root' must be a number.",
                exec_context, "lib_.math_.Math.execute_math_root"
            ))

        if value.value < 0:  # we check if the value is greater than (or equal to) 0
            return RTResult().failure(RTArithmeticError(
                value.pos_start, value.pos_end,
                "first argument of the built-in function 'math.math_root' must be greater than (or equal to) 0.",
                exec_context, "lib_.math_.Math.execute_math_root"
            ))

        n = exec_context.symbol_table.get('n')  # we get 'n'
        if n is None:  # if 'n' parameter is not filled, we set it to 2
            n = Number(2).set_pos(value.pos_end, self.pos_end)

        if not isinstance(n, Number):  # we check if 'n' is a number
            return RTResult().failure(RTTypeError(
                n.pos_start, n.pos_end,
                "second argument of the built-in function 'math.math_root' must be a number.",
                exec_context, "lib_.math_.Math.execute_math_root"
            ))

        value_to_return = Number(value.value ** (1 / n.value))  # we calculate the root

        return RTResult().success(value_to_return)

    execute_math_root.param_names = ['value']
    execute_math_root.optional_params = ['n']
    execute_math_root.should_respect_args_number = True

    def execute_math_degrees(self, exec_context: Context):
        """Converts 'value' (radians) to degrees"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RTTypeError(
                value.pos_start, value.pos_end,
                "first argument of the built-in function 'math.degrees' must be a number (angle in radians).",
                exec_context, "lib_.math_.Math.execute_math_degrees"
            ))
        degrees = math_degrees(value.value)
        return RTResult().success(Number(degrees))

    execute_math_degrees.param_names = ['value']
    execute_math_degrees.optional_params = []
    execute_math_degrees.should_respect_args_number = True

    def execute_math_radians(self, exec_context: Context):
        """Converts 'value' (degrees) to radians"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RTTypeError(
                value.pos_start, value.pos_end,
                "first argument of the built-in function 'math.radians' must be a number (angle in degrees).",
                exec_context, "lib_.math_.Math.execute_math_radians"
            ))
        radians = math_radians(value.value)
        return RTResult().success(Number(radians))

    execute_math_radians.param_names = ['value']
    execute_math_radians.optional_params = []
    execute_math_radians.should_respect_args_number = True

    def execute_math_sin(self, exec_context: Context):
        """Calculates sin('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RTTypeError(
                value.pos_start, value.pos_end,
                "first argument of the built-in function 'math.sin' must be a number (angle in radians).",
                exec_context, "lib_.math_.Math.execute_math_sin"
            ))
        sin = math_sin(value.value)
        return RTResult().success(Number(sin))

    execute_math_sin.param_names = ['value']
    execute_math_sin.optional_params = []
    execute_math_sin.should_respect_args_number = True

    def execute_math_cos(self, exec_context: Context):
        """Calculates cos('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RTTypeError(
                value.pos_start, value.pos_end,
                "first argument of the built-in function 'math.cos' must be a number (angle in radians).",
                exec_context, "lib_.math_.Math.execute_math_cos"
            ))
        cos = math_cos(value.value)
        return RTResult().success(Number(cos))

    execute_math_cos.param_names = ['value']
    execute_math_cos.optional_params = []
    execute_math_cos.should_respect_args_number = True

    def execute_math_tan(self, exec_context: Context):
        """Calculates tan('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RTTypeError(
                value.pos_start, value.pos_end,
                "first argument of the built-in function 'math.tan' must be a number (angle in radians).",
                exec_context, "lib_.math_.Math.execute_math_tan"
            ))
        tan = math_tan(value.value)
        return RTResult().success(Number(tan))

    execute_math_tan.param_names = ['value']
    execute_math_tan.optional_params = []
    execute_math_tan.should_respect_args_number = True

    def execute_math_asin(self, exec_context: Context):
        """Calculates asin('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RTTypeError(
                value.pos_start, value.pos_end,
                "first argument of the built-in function 'math.asin' must be a number.",
                exec_context, "lib_.math_.Math.execute_math_asin"
            ))
        try:
            asin = math_asin(value.value)
        except ValueError:
            return RTResult().failure(RTArithmeticError(
                value.pos_start, value.pos_end,
                "first argument of the built-in function 'math.asin' must be a number between -1 and 1.",
                exec_context, "lib_.math_.Math.execute_math_asin"
            ))
        return RTResult().success(Number(asin))

    execute_math_asin.param_names = ['value']
    execute_math_asin.optional_params = []
    execute_math_asin.should_respect_args_number = True

    def execute_math_acos(self, exec_context: Context):
        """Calculates acos('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RTTypeError(
                value.pos_start, value.pos_end,
                "first argument of the built-in function 'math.acos' must be a number.",
                exec_context, "lib_.math_.Math.execute_math_acos"
            ))
        try:
            acos = math_acos(value.value)
        except ValueError:  # 1 < value or value < -1
            return RTResult().failure(RTArithmeticError(
                value.pos_start, value.pos_end,
                "first argument of the built-in function 'math.acos' must be a number between -1 and 1.",
                exec_context, "lib_.math_.Math.execute_math_acos"
            ))
        return RTResult().success(Number(acos))

    execute_math_acos.param_names = ['value']
    execute_math_acos.optional_params = []
    execute_math_acos.should_respect_args_number = True

    def execute_math_atan(self, exec_context: Context):
        """Calculates atan('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RTTypeError(
                value.pos_start, value.pos_end,
                "first argument of the built-in function 'math.atan' must be a number.",
                exec_context, "lib_.math_.Math.execute_math_atan"
            ))
        atan = math_atan(value.value)
        return RTResult().success(Number(atan))

    execute_math_atan.param_names = ['value']
    execute_math_atan.optional_params = []
    execute_math_atan.should_respect_args_number = True

    def execute_math_abs(self, exec_context: Context):
        """Exactly like python `abs()` (absolute value)"""
        # Params:
        # * value
        value: Value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RTTypeError(
                value.pos_start, value.pos_end,
                "first argument of the built-in function 'math.abs' must be a number.",
                exec_context, "lib_.math_.Math.execute_math_abs"
            ))

        value_to_return = value.abs_()

        return RTResult().success(value_to_return)

    execute_math_abs.param_names = ['value']
    execute_math_abs.optional_params = []
    execute_math_abs.should_respect_args_number = True

    def execute_math_log(self, exec_context: Context):
        """Exactly like python 'log()'. Default base is 'e' (math_e)."""
        # Params:
        # * value
        # Optional params:
        # * base
        value: Value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RTTypeError(
                value.pos_start, value.pos_end,
                "first argument of the built-in function 'math.log' must be a number.",
                exec_context, "lib_.math_.Math.execute_math_log"
            ))

        base: Value = exec_context.symbol_table.get('base')  # we get the base
        if base is None:
            value_to_return = Number(log(value.value))
        else:
            if not isinstance(base, Number):  # we check if the base is a number
                return RTResult().failure(RTTypeError(
                    base.pos_start, base.pos_end,
                    "second argument of the built-in function 'math.log' must be a number.",
                    exec_context, "lib_.math_.Math.execute_math_log"
                ))
            value_to_return = Number(log(value.value, base.value))

        return RTResult().success(value_to_return)

    execute_math_log.param_names = ['value']
    execute_math_log.optional_params = ['base']
    execute_math_log.should_respect_args_number = True

    def execute_math_log2(self, exec_context: Context):
        """Exactly like python 'log2()', is log(n, 2)"""
        # Params:
        # * value
        value: Value = exec_context.symbol_table.get('value')  # we get the value
        if not isinstance(value, Number):  # we check if the value is a number
            return RTResult().failure(RTTypeError(
                value.pos_start, value.pos_end,
                "first argument of the built-in function 'math.log2' must be a number.",
                exec_context, "lib_.math_.Math.execute_math_log2"
            ))

        value_to_return = Number(log2(value.value))

        return RTResult().success(value_to_return)

    execute_math_log2.param_names = ['value']
    execute_math_log2.optional_params = []
    execute_math_log2.should_respect_args_number = True


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
    "log": Math("log"),
    "log2": Math("log2"),
}
