#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
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

UNICODEDATA_VERSION = unicodedata.unidata_version


class UnicodeData(ModuleFunction):
    functions: dict[str, builtin_function_dict] = {}

    """ unicodedata module """
    def __init__(self, name: str):
        super().__init__('unicodedata', name, functions=self.functions)

    def copy(self):
        """Return a copy of self"""
        copy = UnicodeData(self.name)
        return self.set_context_and_pos_to_a_copy(copy)

    @staticmethod
    def is_unicode_char(char: Value, exec_ctx: Context, function: str) -> RTResult | None:
        if not isinstance(char, String):
            return RTResult().failure(RTTypeErrorF(
                char.pos_start, char.pos_end,
                "first", f"unicodedata.{function}", "str", char, exec_ctx,
                origin_file=f"lib_.unicodedata_.UnicodeData.is_unicode_char"
            ))
        if len(char) != 1:
            return RTResult().failure(RunTimeError(
                char.pos_start, char.pos_end,
                f"first argument of function unicodedata.{function} should be only one unicode character, not "
                f"{len(char)}.",
                exec_ctx,
                origin_file=f"lib_.unicodedata_.UnicodeData.is_unicode_char"
            ))
        return None

    @staticmethod
    def is_valid_form_and_uni_str(form: Value, uni_str: Value, exec_ctx: Context, function: str) -> RTResult | None:
        if not isinstance(form, String):
            return RTResult().failure(RTTypeErrorF(
                form.pos_start, form.pos_end,
                "first", f"unicodedata.{function}", "str", form, exec_ctx,
                origin_file="lib_.unicodedata_.UnicodeData.is_valid_form_and_uni_str"
            ))
        if form.value not in ["NFC", "NFKC", "NFD", "NFKD"]:
            return RTResult().failure(RunTimeError(
                form.pos_start, form.pos_end,
                f"first argument of builtin function unicodedata.{function} should be 'NFC', 'NFKC', 'NFD' or 'NFKD', "
                f"not '{form.value}'.",
                exec_ctx, origin_file="lib_.unicodedata_.UnicodeData.is_valid_form_and_uni_str"
            ))
        if not isinstance(uni_str, String):
            return RTResult().failure(RTTypeErrorF(
                uni_str.pos_start, uni_str.pos_end,
                "second", f"unicodedata.{function}", "str", uni_str, exec_ctx,
                origin_file="lib_.unicodedata_.UnicodeData.is_valid_form_and_uni_str"
            ))
        return None

    # =========
    # FUNCTIONS
    # =========
    def execute_unicodedata_lookup(self, exec_ctx: Context):
        """ Like python unicodedata.lookup """
        # Params:
        # * name
        assert exec_ctx.symbol_table is not None
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

    functions["lookup"] = {
        "function": execute_unicodedata_lookup,
        "param_names": ["name"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_unicodedata_name(self, exec_ctx: Context):
        """ Like python unicodedata.name """
        # Params:
        # * char
        assert exec_ctx.symbol_table is not None
        char = exec_ctx.symbol_table.getf("char")
        is_unicode_char = self.is_unicode_char(char, exec_ctx, "name")
        if is_unicode_char is not None:
            return is_unicode_char

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

    functions["name"] = {
        "function": execute_unicodedata_name,
        "param_names": ["char"],
        "optional_params": ["default"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_unicodedata_category(self, exec_ctx: Context):
        """ Like python unicodedata.category """
        # Params:
        # * char
        assert exec_ctx.symbol_table is not None
        char = exec_ctx.symbol_table.getf("char")
        is_unicode_char = self.is_unicode_char(char, exec_ctx, "category")
        if is_unicode_char is not None:
            return is_unicode_char

        return RTResult().success(String(unicodedata.category(char.value)))

    functions["category"] = {
        "function": execute_unicodedata_category,
        "param_names": ["char"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_unicodedata_bidirectional(self, exec_ctx: Context):
        """ Like python unicodedata.bidirectional """
        # Params:
        # * char
        assert exec_ctx.symbol_table is not None
        char = exec_ctx.symbol_table.getf("char")
        is_unicode_char = self.is_unicode_char(char, exec_ctx, "bidirectional")
        if is_unicode_char is not None:
            return is_unicode_char

        return RTResult().success(String(unicodedata.bidirectional(char.value)))

    functions["bidirectional"] = {
        "function": execute_unicodedata_bidirectional,
        "param_names": ["char"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_unicodedata_combining(self, exec_ctx: Context):
        """ Like python unicodedata.combining """
        # Params:
        # * char
        assert exec_ctx.symbol_table is not None
        char = exec_ctx.symbol_table.getf("char")
        is_unicode_char = self.is_unicode_char(char, exec_ctx, "combining")
        if is_unicode_char is not None:
            return is_unicode_char

        return RTResult().success(Number(unicodedata.combining(char.value)))

    functions["combining"] = {
        "function": execute_unicodedata_combining,
        "param_names": ["char"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_unicodedata_east_asian_width(self, exec_ctx: Context):
        """ Like python unicodedata.east_asian_width """
        # Params:
        # * char
        assert exec_ctx.symbol_table is not None
        char = exec_ctx.symbol_table.getf("char")
        is_unicode_char = self.is_unicode_char(char, exec_ctx, "east_asian_width")
        if is_unicode_char is not None:
            return is_unicode_char

        return RTResult().success(String(unicodedata.east_asian_width(char.value)))

    functions["east_asian_width"] = {
        "function": execute_unicodedata_east_asian_width,
        "param_names": ["char"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_unicodedata_mirrored(self, exec_ctx: Context):
        """ Like python unicodedata.mirrored """
        # Params:
        # * char
        assert exec_ctx.symbol_table is not None
        char = exec_ctx.symbol_table.getf("char")
        is_unicode_char = self.is_unicode_char(char, exec_ctx, "mirrored")
        if is_unicode_char is not None:
            return is_unicode_char

        return RTResult().success(Number(unicodedata.mirrored(char.value)))

    functions["mirrored"] = {
        "function": execute_unicodedata_mirrored,
        "param_names": ["char"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_unicodedata_decomposition(self, exec_ctx: Context):
        """ Like python unicodedata.decomposition """
        # Params:
        # * char
        assert exec_ctx.symbol_table is not None
        char = exec_ctx.symbol_table.getf("char")
        is_unicode_char = self.is_unicode_char(char, exec_ctx, "decomposition")
        if is_unicode_char is not None:
            return is_unicode_char

        return RTResult().success(String(unicodedata.decomposition(char.value)))

    functions["decomposition"] = {
        "function": execute_unicodedata_decomposition,
        "param_names": ["char"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_unicodedata_normalize(self, exec_ctx: Context):
        """ Like python unicodedata.normalize """
        # Params:
        # * form
        # * uni_str
        assert exec_ctx.symbol_table is not None
        form = exec_ctx.symbol_table.getf("form")
        uni_str = exec_ctx.symbol_table.getf("uni_str")
        is_valid_form_and_uni_str = self.is_valid_form_and_uni_str(form, uni_str, exec_ctx, "normalize")
        if is_valid_form_and_uni_str is not None:
            return is_valid_form_and_uni_str

        return RTResult().success(String(unicodedata.normalize(form.value, uni_str.value)))

    functions["normalize"] = {
        "function": execute_unicodedata_normalize,
        "param_names": ["form", "uni_str"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_unicodedata_is_normalized(self, exec_ctx: Context):
        """ Like python unicodedata.is_normalized """
        # Params:
        # * form
        # * uni_str
        assert exec_ctx.symbol_table is not None
        form = exec_ctx.symbol_table.getf("form")
        uni_str = exec_ctx.symbol_table.getf("uni_str")
        is_valid_form_and_uni_str = self.is_valid_form_and_uni_str(form, uni_str, exec_ctx, "is_normalized")
        if is_valid_form_and_uni_str is not None:
            return is_valid_form_and_uni_str

        return RTResult().success(Number(int(unicodedata.is_normalized(form.value, uni_str.value))))

    functions["is_normalized"] = {
        "function": execute_unicodedata_is_normalized,
        "param_names": ["form", "uni_str"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }


WHAT_TO_IMPORT = {  # what are the new entries in the symbol table when the module is imported
    # constants
    "unicodedata_version": String(UNICODEDATA_VERSION),
    # functions
    "lookup": UnicodeData("lookup"),
    "name": UnicodeData("name"),
    "category": UnicodeData("category"),
    "bidirectional": UnicodeData("bidirectional"),
    "combining": UnicodeData("combining"),
    "east_asian_width": UnicodeData("east_asian_width"),
    "mirrored": UnicodeData("mirrored"),
    "decomposition": UnicodeData("decomposition"),
    "normalize": UnicodeData("normalize"),
    "is_normalized": UnicodeData("is_normalized")
}
