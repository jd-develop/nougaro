#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
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


class Time(ModuleFunction):
    """ Time module """
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
        seconds = exec_ctx.symbol_table.getf('seconds')  # we get the number of seconds we have to sleep
        if not isinstance(seconds, Number):  # we check if it is a number
            return RTResult().failure(RTTypeErrorF(
                seconds.pos_start, seconds.pos_end, "first", "time.sleep", "number", seconds,
                exec_ctx, "lib_.time_.Time.execute_time_sleep"
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
        milliseconds = exec_ctx.symbol_table.getf('milliseconds')  # we get the number of milliseconds we have to sleep
        if not isinstance(milliseconds, Number) or not milliseconds.is_int():  # we check if it is a number
            return RTResult().failure(RTTypeErrorF(
                milliseconds.pos_start, milliseconds.pos_end, "first", "time.sleep_milliseconds", "integer",
                milliseconds,
                exec_ctx, "lib_.time_.Time.execute_time_sleep_milliseconds"
            ))

        time.sleep(milliseconds.value / 1000)  # ms/1000 = sec
        return RTResult().success(NoneValue(False))

    execute_time_sleep_milliseconds.param_names = ['milliseconds']
    execute_time_sleep_milliseconds.optional_params = []
    execute_time_sleep_milliseconds.should_respect_args_number = True

    def execute_time_time(self, exec_ctx: Context):
        """Like python time.time()"""
        return RTResult().success(Number(time.time()))

    execute_time_time.param_names = []
    execute_time_time.optional_params = []
    execute_time_time.should_respect_args_number = True


WHAT_TO_IMPORT = {  # what are the new entries in the symbol table when the module is imported
    # functions
    "sleep": Time("sleep"),
    "sleep_milliseconds": Time("sleep_milliseconds"),
    "time": Time("time"),
    # constants
    "timezone": TIMEZONE,
}
