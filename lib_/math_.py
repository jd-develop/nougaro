#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# IMPORTS
# nougaro modules imports
from src.values.functions.builtin_function import *
# Comment about the above line : Context, RTResult and values are imported in builtin_function.py
# built-in python imports
from math import sqrt as math_sqrt, degrees as math_degrees, radians as math_radians, sin as math_sin, cos as math_cos
from math import tan as math_tan, asin as math_asin, acos as math_acos, atan as math_atan, e, pi

PI = Number(pi)
SQRT_PI = Number(math_sqrt(pi))
E = Number(e)


class Math(BuiltInFunction):
    """ Module Math """
    def __init__(self, name):
        super().__init__(name)

    def __repr__(self):
        return f'<built-in function math_{self.name}>'

    def execute(self, args, interpreter_, run, exec_from: str = "<invalid>"):
        result = RTResult()
        exec_context = self.generate_new_context()
        exec_context.symbol_table.set("__exec_from__", String(exec_from))
        exec_context.symbol_table.set("__actual_context__", String(self.name))

        method_name = f'execute_math_{self.name}'
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
        print(f"NOUGARO INTERNAL ERROR : No execute_math_{self.name} method defined in lib.math_.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/redirect1.html with all informations "
              f"above.")
        raise Exception(f'No execute_math_{self.name} method defined in lib.math_.')

    def copy(self):
        copy = Math(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    # =========
    # FUNCTIONS
    # =========
    def execute_math_sqrt(self, exec_context: Context):
        """Calculates square root of 'value'"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in function 'sqrt' must be a number.",
                exec_context
            ))

        if not value.value >= 0:
            return RTResult().failure(RTArithmeticError(
                value.pos_start, value.pos_end,
                "first argument of built-in function 'sqrt' must be greater than (or equal to) 0.",
                exec_context
            ))

        sqrt_ = math_sqrt(value.value)
        return RTResult().success(Number(sqrt_))

    execute_math_sqrt.arg_names = ['value']
    execute_math_sqrt.optional_args = []
    execute_math_sqrt.should_respect_args_number = True

    def execute_math_root(self, exec_context: Context):
        """Calculates ⁿ√value"""
        # Params:
        # * value
        # Optional params:
        # * n
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in function 'math_root' must be a number.",
                exec_context
            ))

        if value.value < 0:
            return RTResult().failure(RTArithmeticError(
                value.pos_start, value.pos_end,
                "first argument of built-in function 'math_root' must be greater than (or equal to) 0.",
                exec_context
            ))

        n = exec_context.symbol_table.get('n')
        if n is None:
            n = Number(2).set_pos(value.pos_end, self.pos_end)

        if not isinstance(n, Number):
            return RTResult().failure(RunTimeError(
                n.pos_start, n.pos_end,
                "second argument of built-in function 'math_root' must be a number.",
                exec_context
            ))

        value_to_return = Number(value.value ** (1 / n.value))

        return RTResult().success(value_to_return)

    execute_math_root.arg_names = ['value']
    execute_math_root.optional_args = ['n']
    execute_math_root.should_respect_args_number = True

    def execute_math_degrees(self, exec_context: Context):
        """Converts 'value' (radians) to degrees"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in function 'degrees' must be a number (angle in radians).",
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
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in function 'radians' must be a number (angle in degrees).",
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
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in function 'sin' must be a number (angle in radians).",
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
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in function 'cos' must be a number (angle in radians).",
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
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in function 'tan' must be a number (angle in radians).",
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
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in function 'asin' must be a number.",
                exec_context
            ))
        try:
            asin = math_asin(value.value)
        except ValueError:
            return RTResult().failure(RTArithmeticError(
                value.pos_start, value.pos_end,
                "first argument of built-in function 'asin' must be a number between -1 and 1.",
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
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in function 'acos' must be a number.",
                exec_context
            ))
        try:
            acos = math_acos(value.value)
        except ValueError:
            return RTResult().failure(RTArithmeticError(
                value.pos_start, value.pos_end,
                "first argument of built-in function 'acos' must be a number between -1 and 1.",
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
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in function 'atan' must be a number.",
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
        value: Value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                value.pos_start, value.pos_end,
                "first argument of built-in function 'abs' must be a number.",
                exec_context
            ))

        value_to_return = value.abs_()

        return RTResult().success(value_to_return)

    execute_math_abs.arg_names = ['value']
    execute_math_abs.optional_args = []
    execute_math_abs.should_respect_args_number = True


WHAT_TO_IMPORT = {
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
