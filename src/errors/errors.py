#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.errors.strings_with_arrows import string_with_arrows
from src.runtime.context import Context
# built-in python imports
import os
import pathlib


# parent twice (this file.parent = src, src.parent = nougaro root
_noug_dir = os.path.abspath(pathlib.Path(__file__).parent.parent.parent.absolute())
with open(os.path.abspath(_noug_dir + "/config/debug.conf")) as debug:
    _PRINT_ORIGIN_FILE = bool(int(debug.read()))


# ##########
# ERRORS
# ##########
class Error:
    """Parent class for all the Nougaro errors."""
    def __init__(self, pos_start, pos_end, error_name, details, origin_file: str = "(undetermined)"):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name  # e.g. IllegalCharError
        self.details = details  # e.g. "'ù' is an illegal character."
        self.origin_file: str = origin_file

    def as_string(self):
        """Returns a printable clean error message with all the information.
        It includes the file name, the problematic line number and the line itself, the error name and the details.
        """
        assert self.pos_start is not None, f"error from {self.origin_file}, {self.details=}"
        assert self.pos_end is not None, f"error from {self.origin_file}, {self.details=}"
        string_line = string_with_arrows(self.pos_start.file_txt, self.pos_start, self.pos_end)
        while string_line[0] in " ":
            # delete spaces at the start of the str.
            # Add chars after the space in the string after the "while string_line[0] in" to delete them.
            string_line = string_line[1:]
        if _PRINT_ORIGIN_FILE:
            result = f"(from {self.origin_file})\n" \
                     f"In file {self.pos_start.file_name}, line {self.pos_start.line_number + 1} : " + '\n \t' + \
                     string_line + '\n '
        else:
            result = f"In file {self.pos_start.file_name}, line {self.pos_start.line_number + 1} : " + '\n \t' + \
                     string_line + '\n '
        result += f'{self.error_name}: {self.details}' if self.details != '' else f'{self.error_name}'
        return result


class IllegalCharError(Error):
    """Illegal Character (like 'ù')"""
    def __init__(self, pos_start, pos_end, details, origin_file: str = "(undetermined)"):
        super().__init__(pos_start, pos_end, "IllegalCharError", details, origin_file=origin_file)


class InvalidSyntaxError(Error):
    """Invalid Syntax"""
    def __init__(self, pos_start, pos_end, details, origin_file: str = "(undetermined)"):
        super().__init__(pos_start, pos_end, "InvalidSyntaxError", details, origin_file=origin_file)


class RunTimeError(Error):
    """Parent class for all the run-time Nougaro errors (happens when interpreting code with interpreter.py)"""
    def __init__(self, pos_start, pos_end, details, context: Context, rt_error: bool = True, error_name: str = "",
                 origin_file: str = "(undetermined)"):
        """

        :param pos_start: position start
        :param pos_end: position end
        :param details: details of the error (like 'division by zero is not possible.')
        :param context: context where the error happens
        :param rt_error: if the error name is RunTimeError or not. (bool)
        :param error_name: the error name if rt_error==False
        :param origin_file: the original python file from where this error is called
        """
        super().__init__(pos_start, pos_end, "RunTimeError" if rt_error else error_name, details,
                         origin_file=origin_file)
        self.context = context

    def as_string(self):
        """Returns a printable clean error message with all the information.
        It includes a traceback with the file(s) name, the line(s) number with and the line itself,
        the error name and the details.
        """
        assert self.pos_start is not None, f"error from {self.origin_file}, {self.details=}"
        assert self.pos_end is not None, f"error from {self.origin_file}, {self.details=}"
        string_line = string_with_arrows(self.pos_start.file_txt, self.pos_start, self.pos_end)
        while string_line[0] in " ":
            # delete spaces at the start of the str.
            # Add chars after the space in the string after the "while string_line[0] in" to delete them.
            string_line = string_line[1:]
        result = self.generate_traceback()
        result += '\n \t' + string_line + '\n '
        result += f'{self.error_name}: {self.details}' if self.details != '' else f'{self.error_name}'
        return result

    def generate_traceback(self):
        """Generate a traceback with the file(s) name, the line(s) number and the name of the function"""
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx is not None:
            if pos is not None:
                result = f' In file {pos.file_name}, line {pos.line_number + 1}, in {ctx.display_name}:\n' + result
            else:
                result = f' In file (unknown), line (unknown), in {ctx.display_name}:\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        if _PRINT_ORIGIN_FILE:
            return f"(from {self.origin_file})\nTraceback (more recent call last) :\n" + result
        else:
            return "Traceback (more recent call last) :\n" + result

    def set_pos(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


class RTIndexError(RunTimeError):
    """Index error (like '[1, 2](2)')"""
    def __init__(self, pos_start, pos_end, details, context: Context, origin_file: str = "(undetermined)"):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="IndexError",
                         origin_file=origin_file)
        self.context = context


class RTArithmeticError(RunTimeError):
    """Arithmetic error (like 1/0)"""
    def __init__(self, pos_start, pos_end, details, context: Context, origin_file: str = "(undetermined)"):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="ArithmeticError",
                         origin_file=origin_file)
        self.context = context


class RTNotDefinedError(RunTimeError):
    """When a name is not defined"""
    def __init__(self, pos_start, pos_end, details, context: Context, origin_file: str = "(undetermined)"):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="NotDefinedError",
                         origin_file=origin_file)
        self.context = context


class RTTypeError(RunTimeError):
    """Type error (like 'max("foo")')"""
    def __init__(self, pos_start, pos_end, details, context: Context, origin_file: str = "(undetermined)"):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="TypeError",
                         origin_file=origin_file)
        self.context = context


class RTTypeErrorF(RTTypeError):
    """Type error (like 'max("foo")'), for builtin functions"""
    def __init__(self, pos_start, pos_end, arg_num: str, func_name: str, type_: str, value, context: Context,
                 origin_file: str = "(undetermined)", or_: str = None):
        super().__init__(pos_start, pos_end, f"type of the {arg_num} argument of builtin function ‘{func_name}’ "
                                             f"should be ‘{type_}’{f' or ‘{or_}’' if or_ is not None else ''}, "
                                             f"got ‘{value.type_}’ instead.", context,
                         origin_file=origin_file)
        self.context = context


class RTFileNotFoundError(RunTimeError):
    """File not found (like `open "this_file_does_not_exist"`)"""
    def __init__(self, pos_start, pos_end, file_name, context: Context, origin_file: str = "(undetermined)"):
        super().__init__(pos_start, pos_end, f"file ‘{file_name}’ does not exist.", context, rt_error=False,
                         error_name="FileNotFoundError", origin_file=origin_file)
        self.context = context


class RTAssertionError(RunTimeError):
    """When an assertion is false (like 'assert False')"""
    def __init__(self, pos_start, pos_end, errmsg, context: Context, origin_file: str = "(undetermined)"):
        super().__init__(pos_start, pos_end, errmsg, context, rt_error=False, error_name="AssertionError",
                         origin_file=origin_file)
        self.context = context


class RTAttributeError(RunTimeError):
    """Object 'obj' has no attribute 'attr'."""
    def __init__(self, pos_start, pos_end, obj_type, attr_name, context: Context, origin_file: str = "(undetermined)"):
        errmsg = f"{obj_type} has no attribute '{attr_name}'."
        super().__init__(pos_start, pos_end, errmsg, context, rt_error=False, error_name="AttributeError",
                         origin_file=origin_file)
        self.context = context


class RTOverflowError(RunTimeError):
    """OverflowError."""
    def __init__(self, pos_start, pos_end, errmsg, context: Context, origin_file: str = "(undetermined)"):
        super().__init__(pos_start, pos_end, errmsg, context, rt_error=False, error_name="OverflowError",
                         origin_file=origin_file)
        self.context = context
