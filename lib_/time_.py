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

""" Time module

    Time module provides time-related function and constants, such as timezone or actual time.
"""

# IMPORTS
# nougaro modules imports
from lib_.lib_to_make_libs import *
# Comment about the above line : Context, RTResult and values are imported in lib_to_make_libs.py
# built-in python imports
import time

# CONSTANTS
TIMEZONE = Number(time.timezone)


class Time(Module):
    """Time Module"""
    def __init__(self, name):
        super().__init__('time', name)

    def copy(self):
        """Return a copy of self"""
        copy = Time(self.name)
        return self.set_context_and_pos_to_a_copy(copy)

    # =========
    # FUNCTIONS
    # =========
    def execute_time_sleep(self, exec_ctx: Context):
        """Like python time.sleep()"""
        # Params:
        # * seconds
        seconds = exec_ctx.symbol_table.get('seconds')  # we get the number of seconds we have to sleep
        if not isinstance(seconds, Number):  # we check if it is a number
            return RTResult().failure(RTTypeError(
                seconds.pos_start, seconds.pos_end,
                f"first argument of built-in module function 'time_sleep' must be a number, not {seconds.type_}.",
                exec_ctx
            ))

        time.sleep(seconds.value)  # we sleep
        return RTResult().success(NoneValue(False))

    execute_time_sleep.param_names = ['seconds']
    execute_time_sleep.optional_params = []
    execute_time_sleep.should_respect_args_number = True

    def execute_time_sleep_milliseconds(self, exec_ctx: Context):
        """Like python time.sleep() but the value is in milliseconds"""
        # Params:
        # * milliseconds
        milliseconds = exec_ctx.symbol_table.get('milliseconds')  # we get the number of milliseconds we have to sleep
        if not isinstance(milliseconds, Number):  # we check if it is a number
            return RTResult().failure(RTTypeError(
                milliseconds.pos_start, milliseconds.pos_end,
                f"first argument of built-in module function 'time_sleep_milliseconds' must be an integer, not"
                f" {milliseconds.type_}.",
                exec_ctx
            ))

        if milliseconds.is_float():  # we do not want a float
            return RTResult().failure(RTTypeError(
                milliseconds.pos_start, milliseconds.pos_end,
                "first argument of built-in module function 'time_sleep_milliseconds' must be an integer, not float.",
                exec_ctx
            ))

        time.sleep(milliseconds.value / 1000)  # ms/1000 = sec
        return RTResult().success(NoneValue(False))

    execute_time_sleep_milliseconds.param_names = ['milliseconds']
    execute_time_sleep_milliseconds.optional_params = []
    execute_time_sleep_milliseconds.should_respect_args_number = True


WHAT_TO_IMPORT = {  # what are the new entries in the symbol table when the module is imported
    # functions
    "sleep": Time("sleep"),
    "sleep_milliseconds": Time("sleep_milliseconds"),
    # constants
    "timezone": TIMEZONE,
}
