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
from src.context import Context
from src.runtime_result import RTResult
from src.errors import RunTimeError
# built-in python imports
# no imports


class Value:
    """The parent class to all the value classes (String, Number, List...)"""
    def __init__(self):
        self.pos_start = self.pos_end = self.context = None
        self.set_pos()
        self.set_context()
        self.type_ = "BaseValue"
        self.attributes = {}

    def __repr__(self):
        return "BaseValue"

    def set_pos(self, pos_start=None, pos_end=None):
        """Change self.pos_start and self.pos_end"""
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context: Context = None):
        """Change self.context."""
        self.context = context
        return self

    def added_to(self, other):
        """Add the other's value to self.value.
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        E.g. : num_1 is a Number object that have a value of 1 and num_2 is another Number object with a value of 1 too.
               Then, num_1.added_to(num_2) returns (num1 with the value of 2, None)

        E.g.2: num_1 is a Number object that have a value of 1 and str_1 is a String object with a value of "hello".
               However, you can't add a Number and a String.
               Then, num_1.added_to(str_1) returns (None, RunTimeError with correct context and error msg)
        """
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        """Subtract the other's value from self.value.
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        E.g. : num_1 is a Number object that have a value of 1 and num_2 is another Number object with a value of 1 too.
               Then, num_1.subbed_by(num_2) returns (num1 with the value of 0, None)

        E.g.2: num_1 is a Number object that have a value of 1 and str_1 is a String object with a value of "hello".
               However, you can't subtract a Number from a String.
               Then, num_1.subbed_by(str_1) returns (None, RunTimeError with correct context and error msg)
        """
        return None, self.illegal_operation(other)

    def multiplied_by(self, other):
        """Multiply the other's value with self.value.
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        E.g. : num_1 is a Number object that have a value of 3 and num_2 is another Number object with a value of 2.
               Then, num_1.multiplied_by(num_2) returns (num1 with the value of 6, None)

        E.g.2: list_1 is a List object that have a value of [1, "hello"] and num_1 is a Number object with a value of 1.
               However, you can't multiply a List with a Number.
               Then, list_1.multiplied_by(num_1) returns \
                                            (None, RunTimeError with correct context and error msg)
        """
        return None, self.illegal_operation(other)

    def modded_by(self, other):
        """self.value modded by other's value (modulo).
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def floor_dived_by(self, other):
        """Floor division between self.value and other's value.
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        """Division between self.value and other's value.
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def powered_by(self, other):
        """self.value powered by other's value.
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        """self.value==other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.can_not_compare(other)

    def get_comparison_ne(self, other):
        """self.value!=other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.can_not_compare(other)

    def get_comparison_lt(self, other):
        """self.value<other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.can_not_compare(other)

    def get_comparison_gt(self, other):
        """self.value>other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.can_not_compare(other)

    def get_comparison_lte(self, other):
        """self.value<=other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.can_not_compare(other)

    def get_comparison_gte(self, other):
        """self.value>=other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.can_not_compare(other)

    def is_in(self, other):
        """self.value in other.value (basically if an element is in a list)
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.can_not_be_in(other)

    def and_(self, other):
        """logical operation: self.value and other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def or_(self, other):
        """logical operation: self.value or other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def not_(self):
        """logical operation: not self.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation()

    def xor_(self, other):
        """logical operation: self.value xor other.value (exclusive or)
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def bitwise_and(self, other):
        """bitwise operation: self.value and other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def bitwise_or(self, other):
        """bitwise operation: self.value or other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def bitwise_xor(self, other):
        """bitwise operation: self.value xor other.value (exclusive or)
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def bitwise_not(self):
        """bitwise operation: not self.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation()

    def execute(self, args, interpreter_, run, exec_from: str = "<invalid>"):
        """Execute the function.
        Returns a result"""
        return RTResult().failure(self.illegal_operation())

    def abs_(self):
        """Absolute value
        Returns a result
        """
        return RTResult().failure(self.illegal_operation())

    def to_str_(self):
        """Converts to str.
        Returns (str, None) or (None, Error)
        """
        return None, RTResult().failure(self.illegal_operation())

    def to_int_(self):
        """Converts to int.
        Returns (int, None) or (None, Error)
        """
        return None, RTResult().failure(self.illegal_operation())

    def to_float_(self):
        """Converts to float.
        Returns (float, None) or (None, Error)
        """
        return None, RTResult().failure(self.illegal_operation())

    def to_list_(self):
        """Converts to list.
        Returns (list, None) or (None, Error)
        """
        return None, RTResult().failure(self.illegal_operation())

    def is_int(self):
        """Return PYTHON BOOLEAN True or False depending on if the value's type is INT or not"""
        return False

    def is_float(self):
        """Return PYTHON BOOLEAN True or False depending on if the value's type is FLOAT or not"""
        return False

    def is_true(self):
        """Return PYTHON BOOLEAN True or False depending on if the value is the NOUGARO VALUE for True or not"""
        return False

    def illegal_operation(self, other=None):
        """Returns a RunTimeError with message 'illegal operation (with self/between self and other)"""
        if other is None:
            return RunTimeError(
                self.pos_start, self.pos_end, f'illegal operation with {self.type_}.', self.context,
                origin_file="src.values.value.Value.illegal_operation"
            )
        return RunTimeError(
            self.pos_start, other.pos_end, f'illegal operation between {self.type_} and {other.type_}.', self.context,
            origin_file="src.values.value.Value.illegal_operation"
        )

    def can_not_compare(self, other):
        """Returns a RunTimeError with message 'can not compare self and other'"""
        return RunTimeError(
            self.pos_start, other.pos_end, f'can not compare {self.type_} and {other.type_}.', self.context,
            origin_file="src.values.value.Value.can_not_compare"
        )

    def can_not_be_in(self, other):
        """Returns a RunTimeError with message 'other is not iterable or can not contain self'"""
        return RunTimeError(
            self.pos_start, other.pos_end, f'{other.type_} is not iterable or can not contain {self.type_}.',
            self.context, origin_file="src.values.value.Value.can_not_be_in"
        )

    # =================
    # DANGER ZONE : DRAFT FOR ATTRIBUTES
    # DOESN'T WORK NOW
    # IN DEVELOPMENT
    # =================
    def set_attr(self, attribute: str, value):
        self.attributes[attribute] = value

    def del_attr(self, attribute: str):
        self.attributes.pop(attribute)

    def get_attr(self, attribute: str):
        return self.attributes[attribute]

    # =================
    # YOU ARE EXITING THE DANGER ZONE
    # =================

    def copy(self):
        """Return a copy of self"""
        return Value()
