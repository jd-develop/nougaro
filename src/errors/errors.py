#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# __future__ import (must be first)
from __future__ import annotations
# nougaro modules imports
from src.errors.strings_with_arrows import string_with_arrows
from src.lexer.position import Position
from src.runtime.context import Context
import src.conffiles
# built-in python imports
import traceback
# special typing import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.runtime.values.basevalues.value import Value


# ##########
# ERRORS
# ##########
class Error:
    """Parent class for all the Nougaro errors."""
    def __init__(
            self,
            pos_start: Position,
            pos_end: Position,
            error_name: str,
            details: str,
            origin_file: str = "(undetermined)"
    ):
        debug = src.conffiles.access_data("debug")
        if debug is None:
            debug = 0
        self.print_origin_file = bool(int(debug))
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name  # e.g. IllegalCharError
        self.details = details  # e.g. "'ù' is an illegal character."
        self.origin_file: str = origin_file

    def as_string(self):
        """Returns a printable clean error message with all the information.
        It includes the file name, the problematic line number and the line itself, the error name and the details.
        """
        string_line = string_with_arrows(self.pos_start.file_txt, self.pos_start, self.pos_end)

        if len(string_line) != 0 and string_line[0] == "\n":
            string_line = string_line[1:]

        string_line = string_line.split("\n")

        if len(string_line) != 0:
            for i in range(len(string_line)):
                if i % 2 == 1:
                    continue
                while len(string_line[i]) != 0 and string_line[i][0] in " ":
                    # delete spaces at the start of the str.
                    # Add chars after the space in the string after the "while string_line[0] in" to delete them.
                    string_line[i] = string_line[i][1:]
                    try:
                        string_line[i+1] = string_line[i+1][1:]
                    except IndexError:
                        pass

        if self.print_origin_file:
            result = f"(from {self.origin_file})\n" \
                     f" In file {self.pos_start.file_name}, line {self.pos_start.line_number + 1}: " + '\n'
        else:
            result = f" In file {self.pos_start.file_name}, line {self.pos_start.line_number + 1}: " + '\n'

        for i, line in enumerate(string_line):
            result += '\t' + line + '\n '
        result += f'{self.error_name}: {self.details}' if self.details != '' else f'{self.error_name}'
        return result
    
    def set_pos(self, pos_start: Position, pos_end: Position):
        self.pos_start = pos_start
        self.pos_end = pos_end


class IllegalCharError(Error):
    """Illegal Character (like 'ù')"""
    def __init__(self, pos_start: Position, pos_end: Position, details: str, origin_file: str = "(undetermined)"):
        super().__init__(pos_start, pos_end, "IllegalCharError", details, origin_file=origin_file)


class InvalidSyntaxError(Error):
    """Invalid Syntax"""
    def __init__(self, pos_start: Position, pos_end: Position, details: str,
                 origin_file: str = "(undetermined)"):
        super().__init__(pos_start, pos_end, "InvalidSyntaxError", details, origin_file=origin_file)


class RunTimeError(Error):
    """Parent class for all the run-time Nougaro errors (happens when interpreting code with interpreter.py)"""
    def __init__(self, pos_start: Position, pos_end: Position, details: str, context: Context, rt_error: bool = True,
                 error_name: str = "", origin_file: str = "(undetermined)"):
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
        string_line = string_with_arrows(self.pos_start.file_txt, self.pos_start, self.pos_end)

        if len(string_line) != 0 and string_line[0] == "\n":
            string_line = string_line[1:]

        string_line = string_line.split("\n")

        if len(string_line) != 0:
            for i in range(len(string_line)):
                if i % 2 == 1:
                    continue
                while string_line[i][0] in " ":
                    # delete spaces at the start of the str.
                    # Add chars after the space in the string after the "while string_line[0] in" to delete them.
                    string_line[i] = string_line[i][1:]
                    try:
                        string_line[i+1] = string_line[i+1][1:]
                    except IndexError:
                        pass

        result = self.generate_traceback() + "\n"
        for i, line in enumerate(string_line):
            result += '\t' + line + '\n '
        result += f'{self.error_name}: {self.details}' if self.details != '' else f'{self.error_name}'
        return result

    def generate_traceback(self):
        """Generate a traceback with the file(s) name, the line(s) number and the name of the function"""
        result = ''
        pos = self.pos_start
        ctx = self.context

        lines_to_append: list[tuple[str, int]] = []

        while ctx is not None:
            line_to_append = f' In file {pos.file_name}, line {pos.line_number + 1}, in {ctx.display_name}:\n'
            if len(lines_to_append) == 0:
                lines_to_append.append((line_to_append, 1))
            elif lines_to_append[-1][0] == line_to_append:
                line, count = lines_to_append.pop(-1)
                count += 1
                lines_to_append.append((line, count))
            else:
                lines_to_append.append((line_to_append, 1))
            pos = ctx.entry_pos
            ctx = ctx.parent
        
        for line, count in lines_to_append:
            if count <= 5:
                for _ in range(count):
                    result = line + result
            else:
                result = line + f"    (previous line repeated {count-1} more times)\n" + result

        if self.print_origin_file:
            return f"(from {self.origin_file})\nTraceback (most recent call last):\n" + result
        else:
            return "Traceback (most recent call last):\n" + result
        

class RTIndexError(RunTimeError):
    """Index error (like '[1, 2](2)')"""
    def __init__(self, pos_start: Position, pos_end: Position, details: str, context: Context,
                 origin_file: str = "(undetermined)"):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="IndexError",
                         origin_file=origin_file)


class RTArithmeticError(RunTimeError):
    """Arithmetic error (like 1/0)"""
    def __init__(self, pos_start: Position, pos_end: Position, details: str, context: Context,
                 origin_file: str = "(undetermined)"):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="ArithmeticError",
                         origin_file=origin_file)


class RTNotDefinedError(RunTimeError):
    """When a name is not defined"""
    def __init__(self, pos_start: Position, pos_end: Position, details: str, context: Context,
                 origin_file: str = "(undetermined)"):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="NotDefinedError",
                         origin_file=origin_file)


class RTTypeError(RunTimeError):
    """Type error (like 'max("foo")')"""
    def __init__(self, pos_start: Position, pos_end: Position, details: str, context: Context,
                 origin_file: str = "(undetermined)"):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="TypeError",
                         origin_file=origin_file)


class RTTypeErrorF(RTTypeError):
    """Type error (like 'max("foo")'), for builtin functions"""
    def __init__(self, pos_start: Position, pos_end: Position, arg_num: str, func_name: str, type_: str, value: Value,
                 context: Context, origin_file: str = "(undetermined)", or_: str | None = None):
        super().__init__(
            pos_start, pos_end,
            f"type of the {arg_num} argument of builtin function ‘{func_name}’ "
            f"should be ‘{type_}’{f' or ‘{or_}’' if or_ is not None else ''}, "
            f"got ‘{value.type_}’ instead.", context,
            origin_file=origin_file
        )


class RTFileNotFoundError(RunTimeError):
    """File not found (like `open "this_file_does_not_exist"`). Set `custom` to True to use `file_name` as the error message."""
    def __init__(self, pos_start: Position, pos_end: Position, file_name: str, context: Context,
                 origin_file: str = "(undetermined)", folder: bool = False, custom: bool = False):
        if custom:
            message: str = file_name
        elif folder:
            message = f"directory '{file_name}' does not exist."
        else:
            message = f"file '{file_name}' does not exist."
        super().__init__(pos_start, pos_end, message, context, rt_error=False,
                         error_name="FileNotFoundError", origin_file=origin_file)


class RTAssertionError(RunTimeError):
    """When an assertion is false (like 'assert False')"""
    def __init__(self, pos_start: Position, pos_end: Position, errmsg: str, context: Context,
                 origin_file: str = "(undetermined)"):
        super().__init__(pos_start, pos_end, errmsg, context, rt_error=False, error_name="AssertionError",
                         origin_file=origin_file)


class RTAttributeError(RunTimeError):
    """Object 'obj' has no attribute 'attr'."""
    def __init__(self, pos_start: Position, pos_end: Position, obj_type: str | None, attr_name: str, context: Context,
                 origin_file: str = "(undetermined)"):
        errmsg = f"{obj_type} has no attribute '{attr_name}'."
        super().__init__(pos_start, pos_end, errmsg, context, rt_error=False, error_name="AttributeError",
                         origin_file=origin_file)


class RTOverflowError(RunTimeError):
    """OverflowError."""
    def __init__(self, pos_start: Position, pos_end: Position, errmsg: str, context: Context,
                 origin_file: str = "(undetermined)"):
        super().__init__(pos_start, pos_end, errmsg, context, rt_error=False, error_name="OverflowError",
                         origin_file=origin_file)


class RTRecursionError(RunTimeError):
    """RecursionError"""
    def __init__(self, pos_start: Position, pos_end: Position, errmsg: str, context: Context,
                 origin_file: str = "(undetermined)"):
        super().__init__(pos_start, pos_end, errmsg, context, rt_error=False, error_name="RecursionError",
                         origin_file=origin_file)


class PythonError(RunTimeError):
    """Python error"""
    def __init__(self, pos_start: Position, pos_end: Position, error: Exception, context: Context,
                 origin_file: str = "(undetermined)"):
        errmsg = f"{error.__class__.__name__}: {error}"
        super().__init__(pos_start, pos_end, errmsg, context, rt_error=False, error_name="PythonError",
                         origin_file=origin_file)
        self.error: Exception = error

    def generate_traceback(self):
        tb = super().generate_traceback()
        tb += "========= The following is python traceback =========\n"
        py_tb = traceback.format_tb(self.error.__traceback__)
        for line in py_tb:
            tb += line
        tb += "============ End of the python traceback ============\n"

        return tb
