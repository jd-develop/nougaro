#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
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

__LIB_VERSION__ = 4

# CONSTANTS
TIMEZONE = Number(time.timezone, *default_pos())


class Time(ModuleFunction):
    """ Time module """
    functions: dict[str, BuiltinFunctionDict] = {}

    def __init__(self, name: str):
        super().__init__('time', name, functions=self.functions)

    def copy(self):
        """Return a copy of self"""
        copy = Time(self.name)
        return self.set_context_and_pos_to_a_copy(copy)
    
    def is_eq(self, other: Value):
        return isinstance(other, Time) and self.name == other.name

    # =========
    # FUNCTIONS
    # =========
    def execute_time_sleep(self, exec_ctx: Context):
        """Like python time.sleep()"""
        # Params:
        # * seconds
        assert exec_ctx.symbol_table is not None
        seconds = exec_ctx.symbol_table.getf('seconds')  # we get the number of seconds we have to sleep
        if not isinstance(seconds, Number):  # we check if it is a number
            assert seconds is not None
            return RTResult().failure(RTTypeErrorF(
                seconds.pos_start, seconds.pos_end, "first", "time.sleep", "number", seconds,
                exec_ctx, "lib_.time_.Time.execute_time_sleep"
            ))

        time.sleep(seconds.value)  # we sleep
        return RTResult().success(NoneValue(self.pos_start, self.pos_end, False))

    functions["sleep"] = {
        "function": execute_time_sleep,
        "param_names": ["seconds"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir": False,
        "noug_dir": False
    }

    def execute_time_sleep_milliseconds(self, exec_ctx: Context):
        """Like python time.sleep() but the value is in milliseconds"""
        # Params:
        # * milliseconds
        assert exec_ctx.symbol_table is not None
        milliseconds = exec_ctx.symbol_table.getf('milliseconds')  # we get the number of milliseconds we have to sleep
        if not isinstance(milliseconds, Number) or not milliseconds.is_int():  # we check if it is a number
            assert milliseconds is not None
            return RTResult().failure(RTTypeErrorF(
                milliseconds.pos_start, milliseconds.pos_end, "first", "time.sleep_milliseconds", "integer",
                milliseconds,
                exec_ctx, "lib_.time_.Time.execute_time_sleep_milliseconds"
            ))

        time.sleep(milliseconds.value / 1000)  # ms/1000 = sec
        return RTResult().success(NoneValue(self.pos_start, self.pos_end, False))

    functions["sleep_milliseconds"] = {
        "function": execute_time_sleep_milliseconds,
        "param_names": ["milliseconds"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir": False,
        "noug_dir": False
    }

    def execute_time_time(self):
        """Like python time.time()"""
        return RTResult().success(Number(time.time(), self.pos_start, self.pos_end))

    functions["time"] = {
        "function": execute_time_time,
        "param_names": [],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir": False,
        "noug_dir": False
    }

    def execute_time_epoch(self):
        """Like python time.gmtime(0), but returns a string"""
        epoch = time.gmtime(0)
        return RTResult().success(
            String(
                f"{epoch.tm_year}/{epoch.tm_mon}/{epoch.tm_mday} {epoch.tm_hour}:{epoch.tm_min}:{epoch.tm_sec}",
                self.pos_start, self.pos_end
            )
        )

    functions["epoch"] = {
        "function": execute_time_epoch,
        "param_names": [],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir": False,
        "noug_dir": False
    }


WHAT_TO_IMPORT = {  # what are the new entries in the symbol table when the module is imported
    # functions
    "sleep": Time("sleep"),
    "sleep_milliseconds": Time("sleep_milliseconds"),
    "time": Time("time"),
    "epoch": Time("epoch"),
    # constants
    "timezone": TIMEZONE,
}
