#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

""" UnicodeData module

    This module provides useful unicode tools.
"""

# IMPORTS
# nougaro modules imports
from lib_.lib_to_make_libs import *
# Comment about the above line : Context, RTResult and values are imported in lib_to_make_libs.py
# built-in python imports
import unicodedata


class UnicodeData(ModuleFunction):
    """ unicodedata module """
    def __init__(self, name):
        super().__init__('unicodedata', name)

    def copy(self):
        """Return a copy of self"""
        copy = UnicodeData(self.name)
        return self.set_context_and_pos_to_a_copy(copy)

    # =========
    # FUNCTIONS
    # =========
    def execute_unicodedata_lookup(self, exec_ctx: Context):
        """ Like python unicodedata.lookup """
        # Params:
        # * name
        name = exec_ctx.symbol_table.getf("name")
        if not isinstance(name, String):
            return RTResult().failure(RTTypeErrorF(
                name.pos_start, name.pos_end,
                "first", "unicodedata.lookup", "str", name, exec_ctx,
                origin_file="lib_.unicodedata_.UnicodeData.execute_unicodedata_lookup"
            ))
        try:
            char = unicodedata.lookup(name.value)
        except KeyError as e:
            return RTResult().failure(RTNotDefinedError(
                name.pos_start, name.pos_end,
                str(e).replace('"', ''),
                exec_ctx,
                origin_file="lib_.unicodedata_.UnicodeData.execute_unicodedata_lookup"
            ))
        return RTResult().success(String(char))

    execute_unicodedata_lookup.param_names = ['name']
    execute_unicodedata_lookup.optional_params = []
    execute_unicodedata_lookup.should_respect_args_number = True

    def execute_unicodedata_name(self, exec_ctx: Context):
        """ Like python unicodedata.name """
        # Params:
        # * char
        char = exec_ctx.symbol_table.getf("char")
        if not isinstance(char, String):
            return RTResult().failure(RTTypeErrorF(
                char.pos_start, char.pos_end,
                "first", "unicodedata.name", "str", char, exec_ctx,
                origin_file="lib_.unicodedata_.UnicodeData.execute_unicodedata_name"
            ))
        if len(char) != 1:
            return RTResult().failure(RunTimeError(
                char.pos_start, char.pos_end,
                f"first argument of function unicodedata.name should be only one unicode character, not {len(char)}.",
                exec_ctx,
                origin_file="lib_.unicodedata_.UnicodeData.execute_unicodedata_name"
            ))
        default = exec_ctx.symbol_table.getf("default")

        try:
            name = String(unicodedata.name(char.value))
        except ValueError as e:
            if default is None:
                return RTResult().failure(RunTimeError(
                    char.pos_start, char.pos_end,
                    e,
                    exec_ctx,
                    origin_file="lib_.unicodedata_.UnicodeData.execute_unicodedata_name"
                ))
            name = default
        return RTResult().success(name)

    execute_unicodedata_name.param_names = ['char']
    execute_unicodedata_name.optional_params = ['default']
    execute_unicodedata_name.should_respect_args_number = True

    def execute_unicodedata_category(self, exec_ctx: Context):
        """ Like python unicodedata.category """
        # Params:
        # * char
        char = exec_ctx.symbol_table.getf("char")
        if not isinstance(char, String):
            return RTResult().failure(RTTypeErrorF(
                char.pos_start, char.pos_end,
                "first", "unicodedata.category", "str", char, exec_ctx,
                origin_file="lib_.unicodedata_.UnicodeData.execute_unicodedata_category"
            ))
        if len(char) != 1:
            return RTResult().failure(RunTimeError(
                char.pos_start, char.pos_end,
                f"first argument of function unicodedata.category should be only one unicode character, not {len(char)}.",
                exec_ctx,
                origin_file="lib_.unicodedata_.UnicodeData.execute_unicodedata_category"
            ))

        return RTResult().success(String(unicodedata.category(char.value)))

    execute_unicodedata_category.param_names = ['char']
    execute_unicodedata_category.optional_params = []
    execute_unicodedata_category.should_respect_args_number = True

    # todo: add others functions


WHAT_TO_IMPORT = {  # what are the new entries in the symbol table when the module is imported
    # functions
    "lookup": UnicodeData("lookup"),
    "name": UnicodeData("name"),
    "category": UnicodeData("category")
}
