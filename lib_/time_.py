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

# IMPORTS
# nougaro modules imports
from src.values.functions.builtin_function import *
# Comment about the above line : Context, RTResult and values are imported in builtin_function.py
# built-in python imports
import time


class Time(BaseBuiltInFunction):
    """Module Time"""
    def __init__(self, name):
        super().__init__(name)

    def __repr__(self):
        return f'<built-in function time_{self.name}>'

    def execute(self, args, interpreter_, run, exec_from: str = "<invalid>"):
        result = RTResult()
        exec_context = self.generate_new_context()
        exec_context.symbol_table.set("__exec_from__", String(exec_from))
        exec_context.symbol_table.set("__actual_context__", String(self.name))

        method_name = f'execute_time_{self.name}'
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
        print(f"NOUGARO INTERNAL ERROR : No execute_time_{self.name} method defined in lib_.time_.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with all informations "
              f"above.")
        raise Exception(f'No execute_time_{self.name} method defined in lib_.time_.')

    def copy(self):
        copy = Time(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    # =========
    # FUNCTIONS
    # =========
    def execute_time_sleep(self, exec_ctx: Context):
        """Like python time.sleep()"""
        # Params:
        # * seconds
        seconds = exec_ctx.symbol_table.get('seconds')
        if not isinstance(seconds, Number):
            return RTResult().failure(RunTimeError(
                seconds.pos_start, seconds.pos_end,
                f"first argument of built-in module function 'time_sleep' must be a number, not {seconds.type_}.",
                exec_ctx
            ))

        time.sleep(seconds.value)
        return RTResult().success(NoneValue(False))

    execute_time_sleep.arg_names = ['seconds']
    execute_time_sleep.optional_args = []
    execute_time_sleep.should_respect_args_number = True

    def execute_time_sleep_milliseconds(self, exec_ctx: Context):
        """Like python time.sleep() but the value is in milliseconds"""
        # Params:
        # * milliseconds
        milliseconds = exec_ctx.symbol_table.get('milliseconds')
        if not isinstance(milliseconds, Number):
            return RTResult().failure(RunTimeError(
                milliseconds.pos_start, milliseconds.pos_end,
                f"first argument of built-in module function 'time_sleep_milliseconds' must be an integer, not"
                f" {milliseconds.type_}.",
                exec_ctx
            ))

        if milliseconds.is_float():
            return RTResult().failure(RunTimeError(
                milliseconds.pos_start, milliseconds.pos_end,
                "first argument of built-in module function 'time_sleep_milliseconds' must be an integer, not float.",
                exec_ctx
            ))

        time.sleep(milliseconds.value / 1000)
        return RTResult().success(NoneValue(False))

    execute_time_sleep_milliseconds.arg_names = ['milliseconds']
    execute_time_sleep_milliseconds.optional_args = []
    execute_time_sleep_milliseconds.should_respect_args_number = True


TIMEZONE = Number(time.timezone)

WHAT_TO_IMPORT = {
    "sleep": Time("sleep"),
    "sleep_milliseconds": Time("sleep_milliseconds"),
    "timezone": TIMEZONE,
}
