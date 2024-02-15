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
from src.lexer.position import Position
from src.runtime.context import Context
from src.runtime.runtime_result import RTResult
from src.errors.errors import RunTimeError
# built-in python imports
# no imports
# special typing import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.runtime.interpreter import Interpreter
    from src.runtime.values.basevalues.basevalues import String, Number, List
    from src.misc import RunFunction


class Value:
    """The parent class to all the value classes (String, Number, List...)"""
    def __init__(self):
        self.pos_start = self.pos_end = self.context = None
        self.set_pos()
        self.set_context()
        self.type_ = "BaseValue"
        self.attributes: dict[str, Value] = {}
        self.call_with_module_context = False
        self.module_context: Context | None = None
        self.should_print = True

    def __repr__(self) -> str:
        return "BaseValue"
    
    def to_python_str(self) -> str:
        return "BaseValue"

    def set_pos(self, pos_start: Position | None = None, pos_end: Position | None = None):
        """Change self.pos_start and self.pos_end"""
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context: Context | None = None):
        """Change self.context."""
        self.context = context
        return self

    def added_to(self, other: Value) -> tuple[Value, None] | tuple[None, RunTimeError]:
        """Add the other's value to self.value.
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        E.g. : num_1 is a Number object that have a value of 1 and num_2 is another Number object with a value of 1 too.
               Then, num_1.added_to(num_2) returns (num1 with the value of 2, None)

        E.g.2: num_1 is a Number object that have a value of 1 and str_1 is a String object with a value of "hello".
               However, you can't add a Number and a String.
               Then, num_1.added_to(str_1) returns (None, RunTimeError with correct context and error msg)
        """
        return None, self.illegal_operation(other)

    def subbed_by(self, other: Value) -> tuple[Value, None] | tuple[None, RunTimeError]:
        """Subtract the other's value from self.value.
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        E.g. : num_1 is a Number object that have a value of 1 and num_2 is another Number object with a value of 1 too.
               Then, num_1.subbed_by(num_2) returns (num1 with the value of 0, None)

        E.g.2: num_1 is a Number object that have a value of 1 and str_1 is a String object with a value of "hello".
               However, you can't subtract a Number from a String.
               Then, num_1.subbed_by(str_1) returns (None, RunTimeError with correct context and error msg)
        """
        return None, self.illegal_operation(other)

    def multiplied_by(self, other: Value) -> tuple[Value, None] | tuple[None, RunTimeError]:
        """Multiply the other's value with self.value.
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        E.g. : num_1 is a Number object that have a value of 3 and num_2 is another Number object with a value of 2.
               Then, num_1.multiplied_by(num_2) returns (num1 with the value of 6, None)

        E.g.2: list_1 is a List object that have a value of [1, "hello"] and str_1 is a String object with a value of\
                "azerty".
               However, you can't multiply a List with a String.
               Then, list_1.multiplied_by(str_1) returns \
                                            (None, RunTimeError with correct context and error msg)
        """
        return None, self.illegal_operation(other)

    def modded_by(self, other: Value) -> tuple[Value, None] | tuple[None, RunTimeError]:
        """self.value modded by other's value (modulo).
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def floor_dived_by(self, other: Value) -> tuple[Value, None] | tuple[None, RunTimeError]:
        """Floor division between self.value and other's value.
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def dived_by(self, other: Value) -> tuple[Value, None] | tuple[None, RunTimeError]:
        """Division between self.value and other's value.
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def powered_by(self, other: Value) -> tuple[Value, None] | tuple[None, RunTimeError]:
        """self.value powered by other's value.
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other: Value) -> tuple[Number, None] | tuple[None, RunTimeError]:
        """self.value==other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.can_not_compare(other)

    def get_comparison_ne(self, other: Value) -> tuple[Number, None] | tuple[None, RunTimeError]:
        """self.value!=other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.can_not_compare(other)

    def get_comparison_lt(self, other: Value) -> tuple[Number, None] | tuple[None, RunTimeError]:
        """self.value<other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.can_not_compare(other)

    def get_comparison_gt(self, other: Value) -> tuple[Number, None] | tuple[None, RunTimeError]:
        """self.value>other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.can_not_compare(other)

    def get_comparison_lte(self, other: Value) -> tuple[Number, None] | tuple[None, RunTimeError]:
        """self.value<=other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.can_not_compare(other)

    def get_comparison_gte(self, other: Value) -> tuple[Number, None] | tuple[None, RunTimeError]:
        """self.value>=other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.can_not_compare(other)

    def is_in(self, other: Value) -> tuple[Number, None] | tuple[None, RunTimeError]:
        """self.value in other.value (basically if an element is in a list)
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.can_not_be_in(other)

    def and_(self, other: Value) -> tuple[Value, None] | tuple[None, RunTimeError]:
        """logical operation: self.value and other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def or_(self, other: Value) -> tuple[Value, None] | tuple[None, RunTimeError]:
        """logical operation: self.value or other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def not_(self) -> tuple[Value, None] | tuple[None, RunTimeError]:
        """logical operation: not self.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation()

    def xor_(self, other: Value) -> tuple[Value, None] | tuple[None, RunTimeError]:
        """logical operation: self.value xor other.value (exclusive or)
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def bitwise_and(self, other: Value) -> tuple[Value, None] | tuple[None, RunTimeError]:
        """bitwise operation: self.value and other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def bitwise_or(self, other: Value) -> tuple[Value, None] | tuple[None, RunTimeError]:
        """bitwise operation: self.value or other.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def bitwise_xor(self, other: Value) -> tuple[Value, None] | tuple[None, RunTimeError]:
        """bitwise operation: self.value xor other.value (exclusive or)
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation(other)

    def bitwise_not(self) -> tuple[Value, None] | tuple[None, RunTimeError]:
        """bitwise operation: not self.value
        Return a tuple with a valid value (or None if there is an error), then an error (or None if there is no error)
        Please refer to documentation of other operations (like self.multiplied_by()) to see examples of returned
         tuples.
        """
        return None, self.illegal_operation()

    def execute(self, args: list[Value], interpreter_: type[Interpreter], run: RunFunction, noug_dir: str,
                exec_from: str = "<invalid>", use_context: Context | None = None, cli_args: list[String] | None = None,
                work_dir: str | None = None):
        """Execute the function.
        Returns a result"""
        return RTResult().failure(self.illegal_operation())

    def abs_(self) -> tuple[Value, None] | tuple[None, RunTimeError]:
        """Absolute value
        Returns a result
        """
        return None, self.illegal_operation()

    def to_str_(self) -> tuple[String, None] | tuple[None, RTResult]:
        """Converts to str.
        Returns (str, None) or (None, Error)
        """
        return None, RTResult().failure(self.illegal_operation())

    def to_int_(self) -> tuple[Number, None] | tuple[None, RTResult]:
        """Converts to int.
        Returns (int, None) or (None, Error)
        """
        return None, RTResult().failure(self.illegal_operation())

    def to_float_(self) -> tuple[Number, None] | tuple[None, RTResult]:
        """Converts to float.
        Returns (float, None) or (None, Error)
        """
        return None, RTResult().failure(self.illegal_operation())

    def to_list_(self) -> tuple[List, None] | tuple[None, RTResult]:
        """Converts to list.
        Returns (list, None) or (None, Error)
        """
        return None, RTResult().failure(self.illegal_operation())

    def is_int(self) -> bool:
        """Return PYTHON BOOLEAN True or False depending on if the value's type is INT or not"""
        return False

    def is_float(self) -> bool:
        """Return PYTHON BOOLEAN True or False depending on if the value's type is FLOAT or not"""
        return False

    def is_true(self) -> bool:
        """Return PYTHON BOOLEAN True or False depending on if the value is the NOUGARO VALUE for True or not"""
        return False

    def is_false(self) -> bool:
        """Return PYTHON BOOLEAN True or False depending on if the value is the NOUGARO VALUE for False or not"""
        return not self.is_true()

    def illegal_operation(self, other: Value | None = None) -> RunTimeError:
        """Returns a RunTimeError with message 'illegal operation (with self/between self and other)"""
        assert self.pos_start is not None
        if other is None:
            assert self.pos_end is not None
            assert self.context is not None
            return RunTimeError(
                self.pos_start, self.pos_end, f'illegal operation with {self.type_}.', self.context,
                origin_file="src.values.value.Value.illegal_operation"
            )
        assert other.pos_end is not None
        assert self.context is not None
        return RunTimeError(
            self.pos_start, other.pos_end, f'illegal operation between {self.type_} and {other.type_}.', self.context,
            origin_file="src.values.value.Value.illegal_operation"
        )

    def can_not_compare(self, other: Value) -> RunTimeError:
        """Returns a RunTimeError with message 'can not compare self and other'"""
        assert self.context is not None
        assert self.pos_start is not None
        assert other.pos_end is not None
        return RunTimeError(
            self.pos_start, other.pos_end, f'can not compare {self.type_} and {other.type_}.', self.context,
            origin_file="src.values.value.Value.can_not_compare"
        )

    def can_not_be_in(self, other: Value):
        """Returns a RunTimeError with message 'other is not iterable or can not contain self'"""
        assert self.context is not None
        assert self.pos_start is not None
        assert other.pos_end is not None
        return RunTimeError(
            self.pos_start, other.pos_end, f'{other.type_} is not iterable or can not contain {self.type_}.',
            self.context, origin_file="src.values.value.Value.can_not_be_in"
        )

    def set_attr(self, attribute: str, value: Value):
        self.attributes[attribute] = value

    def del_attr(self, attribute: str):
        self.attributes.pop(attribute)

    def get_attr(self, attribute: str):
        return self.attributes[attribute]

    def copy(self):
        """Return a copy of self"""
        value = Value().set_pos(self.pos_start, self.pos_end).set_context(self.context)
        value.attributes = self.attributes.copy()
        value.call_with_module_context = self.call_with_module_context
        value.module_context = self.module_context
        value.should_print = self.should_print
        return value
