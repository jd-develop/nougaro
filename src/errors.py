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
from src.strings_with_arrows import string_with_arrows
from src.context import Context
# built-in python imports
# no imports


# ##########
# ERRORS
# ##########
class Error:
    """Parent class for all the Nougaro errors."""
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name  # e.g. IllegalCharError
        self.details = details  # e.g. "'ù' is an illegal character."

    def as_string(self):
        """Returns a printable clean error message with all the information.
        It includes the file name, the problematic line number and the line itself, the error name and the details.
        """
        string_line = string_with_arrows(self.pos_start.file_txt, self.pos_start, self.pos_end)
        while string_line[0] in " ":
            # delete spaces at the start of the str.
            # Add chars after the space in the string after the "while string_line[0] in" to delete them.
            string_line = string_line[1:]
        result = f"In file {self.pos_start.file_name}, line {self.pos_start.line_number + 1} : " + '\n \t' + \
                 string_line + '\n '
        result += f'{self.error_name}: {self.details}' if self.details != '' else f'{self.error_name}'
        return result


class IllegalCharError(Error):
    """Illegal Character (like 'ù')"""
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "IllegalCharError", details)


class InvalidSyntaxError(Error):
    """Invalid Syntax"""
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "InvalidSyntaxError", details)


class RunTimeError(Error):
    """Parent class for all the run-time Nougaro errors (happens when interpreting code with interpreter.py)"""
    def __init__(self, pos_start, pos_end, details, context: Context, rt_error: bool = True, error_name: str = ""):
        """

        :param pos_start: position start
        :param pos_end: position end
        :param details: details of the error (like 'division by zero is not possible.')
        :param context: context where the error happens
        :param rt_error: if the error name is RunTimeError or not. (bool)
        :param error_name: the error name if rt_error==False
        """
        super().__init__(pos_start, pos_end, "RunTimeError" if rt_error else error_name, details)
        self.context = context

    def as_string(self):
        """Returns a printable clean error message with all the information.
        It includes a traceback with the file(s) name, the line(s) number with and the line itself,
        the error name and the details.
        """
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
            result = f' In file {pos.file_name}, line {pos.line_number + 1}, in {ctx.display_name} :\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return "Traceback (more recent call last) :\n" + result

    def set_pos(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


class RTIndexError(RunTimeError):
    """Index error (like '[1, 2](2)')"""
    def __init__(self, pos_start, pos_end, details, context: Context):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="IndexError")
        self.context = context


class RTArithmeticError(RunTimeError):
    """Arithmetic error (like 1/0)"""
    def __init__(self, pos_start, pos_end, details, context: Context):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="ArithmeticError")
        self.context = context


class RTNotDefinedError(RunTimeError):
    """When a name is not defined"""
    def __init__(self, pos_start, pos_end, details, context: Context):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="NotDefinedError")
        self.context = context


class RTTypeError(RunTimeError):
    """Type error (like 'max("foo")')"""
    def __init__(self, pos_start, pos_end, details, context: Context):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="TypeError")
        self.context = context


class RTFileNotFoundError(RunTimeError):
    """File not found (like `open "this_file_does_not_exist"`)"""
    def __init__(self, pos_start, pos_end, file_name, context: Context):
        super().__init__(pos_start, pos_end, f"file '{file_name}' does not exist.", context, rt_error=False,
                         error_name="FileNotFoundError")
        self.context = context


class RTAssertionError(RunTimeError):
    """When an assertion is false (like 'assert False')"""
    def __init__(self, pos_start, pos_end, errmsg, context: Context):
        super().__init__(pos_start, pos_end, errmsg, context, rt_error=False, error_name="AssertionError")
        self.context = context
