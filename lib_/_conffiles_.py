#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

""" _Conffiles module

    _Conffiles is a module that give access to the `src.conffiles` internal API module.
"""

# IMPORTS
# nougaro modules imports
from lib_.lib_to_make_libs import *
import src.conffiles
# Above line : Context, RTResult, errors and values are imported in lib_to_make_libs.py
# built-in python imports
# no imports

# constants
CONFIG_DIRECTORY = String(src.conffiles.CONFIG_DIRECTORY)


class Conffiles(ModuleFunction):
    """ _conffiles module """
    functions: dict[str, builtin_function_dict] = {}

    def __init__(self, function_name: str):
        super().__init__("_conffiles", function_name, functions=self.functions)

    def copy(self):
        """Return a copy of self"""
        copy = Conffiles(self.name)
        return self.set_context_and_pos_to_a_copy(copy)
    
    # functions
    def execute__conffiles_access_data(self, context: Context):
        """Returns the asked data. RTFileNotFoundError if file not found, or None if not_found_ok=True"""
        assert context.symbol_table is not None
        file_name = context.symbol_table.getf("file_name")
        not_found_ok = context.symbol_table.getf("not_found_ok")
        if not isinstance(file_name, String):
            assert file_name is not None
            assert file_name.pos_start is not None
            assert file_name.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                file_name.pos_start, file_name.pos_end, "first", "_conffiles.access_data", "str", file_name,
                context, origin_file="lib_._conffiles_.Conffiles.execute__conffiles_access_data"
            ))
        
        if file_name.value == "please give me a syntax warning":
            eval("1 is 1")  # easter egg lol

        if not_found_ok is None:
            not_found_ok = FALSE.copy()
        if not (isinstance(not_found_ok, Number) and isinstance(not_found_ok.value, int)):
            assert not_found_ok.pos_start is not None
            assert not_found_ok.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                not_found_ok.pos_start, not_found_ok.pos_end, "second", "_conffiles.access_data", "int", not_found_ok,
                context, origin_file="lib_._conffiles_.Conffiles.execute__conffiles_access_data"
            ))
        
        data = src.conffiles.access_data(file_name.value)
        if data is None:
            if not_found_ok.is_true():
                return RTResult().success(NoneValue(False))
            assert file_name.pos_start is not None
            assert file_name.pos_end is not None
            return RTResult().failure(RTFileNotFoundError(
                file_name.pos_start, file_name.pos_end, f"config file not found: {file_name}.", context,
                origin_file="lib_._conffiles_.Conffiles.execute__conffiles_access_data", custom=True
            ))
        
        return RTResult().success(String(data))

    functions["access_data"] = {
        "function": execute__conffiles_access_data,
        "param_names": ["file_name"],
        "optional_params": ["not_found_ok"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute__conffiles_write_data(self, context: Context):
        """Writes the asked data. RunTimeError if the file is read-only, except if read_only_ok is True."""
        assert context.symbol_table is not None
        file_name = context.symbol_table.getf("file_name")
        data = context.symbol_table.getf("data")
        read_only_ok = context.symbol_table.getf("read_only_ok")
        if not isinstance(file_name, String):
            assert file_name is not None
            assert file_name.pos_start is not None
            assert file_name.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                file_name.pos_start, file_name.pos_end, "first", "_conffiles.write_data", "str", file_name,
                context, origin_file="lib_._conffiles_.Conffiles.execute__conffiles_write_data"
            ))
        
        data_to_write = nice_str_from_idk(data).value

        if read_only_ok is None:
            read_only_ok = FALSE.copy()
        if not (isinstance(read_only_ok, Number) and isinstance(read_only_ok.value, int)):
            assert read_only_ok.pos_start is not None
            assert read_only_ok.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                read_only_ok.pos_start, read_only_ok.pos_end, "second", "_conffiles.write_data", "int", read_only_ok,
                context, origin_file="lib_._conffiles_.Conffiles.execute__conffiles_write_data"
            ))
        
        errmsg = src.conffiles.write_data(file_name.value, data_to_write, silent=True, return_error_messages=True)

        if errmsg is not None:
            if read_only_ok.is_true():
                return RTResult().success(NoneValue(False))
            assert file_name.pos_start is not None
            assert file_name.pos_end is not None
            return RTResult().failure(RTFileNotFoundError(
                file_name.pos_start, file_name.pos_end, f"config file {file_name} is read-only.", context,
                origin_file="lib_._conffiles_.Conffiles.execute__conffiles_write_data", custom=True
            ))
        
        return RTResult().success(NoneValue(False))

    functions["write_data"] = {
        "function": execute__conffiles_write_data,
        "param_names": ["file_name", "data"],
        "optional_params": ["read_only_ok"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }


WHAT_TO_IMPORT = {
    "CONFIG_DIRECTORY": CONFIG_DIRECTORY,
    "access_data": Conffiles('access_data'),
    "write_data": Conffiles('write_data')
}
