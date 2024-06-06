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
from src.runtime.values.basevalues.value import Value
from src.runtime.runtime_result import RTResult
from src.runtime.symbol_table import SymbolTable
from src.runtime.context import Context
from src.errors.errors import RunTimeError, RTArithmeticError, RTIndexError, RTOverflowError
from src.lexer.position import Position as _Position
# built-in python imports
# no imports


# IMPORTANT NOTE: THE DOC FOR ALL THE FUNCTIONS IN THIS FILE ARE IN value.py :)


class String(Value):
    def __init__(self, value: String | str, pos_start: _Position, pos_end: _Position):
        super().__init__(pos_start, pos_end)
        if isinstance(value, String):
            self.value: str = value.value
        else:
            self.value: str = value
        self.type_ = "str"

    def __repr__(self):
        return f'"{self.value}"'

    def __len__(self):
        return len(self.value)

    def to_python_str(self) -> str:
        """Returns self.value, as a python str"""
        return self.value

    def added_to(self, other: Value):
        if isinstance(other, String):
            try:
                return String(self.value + other.value, self.pos_start, other.pos_end).set_context(self.context), None
            except UnicodeEncodeError as e:
                assert self.context is not None
                return None, RunTimeError(
                    self.pos_start, other.pos_end,
                    str(e), self.context,
                    origin_file="src.runtime.values.basevalues.basevalues.String.added_to"
                )
        else:
            return None, self.illegal_operation(other)

    def multiplied_by(self, other: Value):
        if isinstance(other, Number) and isinstance(other.value, int):
            try:
                return String(self.value * other.value, self.pos_start, other.pos_end).set_context(self.context), None
            except OverflowError as e:
                assert self.context is not None
                return None, RTOverflowError(
                    self.pos_start, other.pos_end,
                    str(e), self.context,
                    "src.runtime.values.basevalues.basevalues.String.multiplied_by"
                )
        else:
            return None, self.illegal_operation(other)

    def is_true(self):
        return len(self.value) > 0

    def to_str(self) -> tuple[String, None]:
        return self.copy(), None

    def to_int(self):
        """Returns a nougaro int"""
        value_to_convert = self.value
        if value_to_convert in ["null", "False"]:
            value_to_convert = "0"
        elif value_to_convert in ["True"]:
            value_to_convert = "1"

        try:
            return Number(int(float(value_to_convert)), self.pos_start, self.pos_end).set_context(self.context), None
        except ValueError:
            assert self.context is not None
            return None, RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"str '{self.value}' can not be converted to int.",
                self.context,
                origin_file="src.values.basevalues.String.to_int"
            ))

    def to_float(self):
        try:
            return Number(float(self.value), self.pos_start, self.pos_end).set_context(self.context), None
        except ValueError:
            assert self.context is not None
            return None, RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"str '{self.value}' can not be converted to float.",
                self.context,
                origin_file="src.values.basevalues.String.to_float"))

    def to_list(self):
        list_: list[Value] = []
        for char in self.value:
            list_.append(String(char, self.pos_start, self.pos_end))
        return List(list_, self.pos_start, self.pos_end).set_context(self.context), None

    def get_comparison_eq(self, other: Value):
        if isinstance(other, String):
            return Number(self.value == other.value, self.pos_start, other.pos_end).set_context(self.context), None
        else:
            return Number(False, self.pos_start, other.pos_end).set_context(self.context), None

    def get_comparison_ne(self, other: Value):
        is_eq = bool(self.get_comparison_eq(other)[0].value)
        is_ne = not is_eq
        return Number(is_ne, self.pos_start, other.pos_end).set_context(self.context), None

    def get_comparison_gt(self, other: Value):
        if isinstance(other, String):
            return Number(self.value > other.value, self.pos_start, other.pos_end).set_context(self.context), None
        return Number(False, self.pos_start, other.pos_end).set_context(self.context), None

    def get_comparison_gte(self, other: Value):
        is_eq = bool(self.get_comparison_eq(other)[0].value)
        is_gt = bool(self.get_comparison_gt(other)[0].value)
        return Number(is_eq or is_gt, self.pos_start, other.pos_end).set_context(self.context), None

    def get_comparison_lt(self, other: Value):
        if isinstance(other, String):
            return Number(self.value < other.value, self.pos_start, other.pos_end).set_context(self.context), None
        return Number(False, self.pos_start, other.pos_end).set_context(self.context), None

    def get_comparison_lte(self, other: Value):
        is_eq = bool(self.get_comparison_eq(other)[0].value)
        is_lt = bool(self.get_comparison_lt(other)[0].value)
        return Number(is_eq or is_lt, self.pos_start, other.pos_end).set_context(self.context), None

    def and_(self, other: Value):
        return Number(
            self.is_true() and other.is_true(),
            self.pos_start, self.pos_end
        ).set_context(self.context), None

    def or_(self, other: Value):
        return Number(
            self.is_true() or other.is_true(),
            self.pos_start, self.pos_end
        ).set_context(self.context), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        xor = (
            not self.is_true() and other.is_true()
        ) or (
            self.is_true() and not other.is_true()
        )
        return Number(xor, self.pos_start, other.pos_end).set_context(self.context), None

    def is_in(self, other: Value):
        if isinstance(other, List):
            for x in other.elements:
                if self.get_comparison_eq(x)[0].is_true():
                    return Number(True, self.pos_start, other.pos_end).set_context(self.context), None
            return Number(False, self.pos_start, other.pos_end).set_context(self.context), None
        elif isinstance(other, String):
            return Number(
                self.value in other.value,
                self.pos_start, self.pos_end
            ).set_context(self.context), None
        else:
            return None, self.can_not_be_in(other)

    def copy(self):
        """Return a copy of self"""
        copy = String(self.value, self.pos_start, self.pos_end)
        copy.set_context(self.context)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy


class Number(Value):
    def __init__(self, value: int | float | bool, pos_start: _Position, pos_end: _Position):
        super().__init__(pos_start, pos_end)
        if isinstance(value, bool):
            value = int(value)
        self.value = value
        if self.is_int():
            self.type_ = 'int'
        else:
            self.type_ = 'float'

    def __repr__(self):
        try:
            return str(self.value)
        except ValueError:
            return "(this number can not be displayed)"
    
    def to_python_str(self) -> str:
        """Returns self.value, as a python str"""
        return self.__repr__()

    def added_to(self, other: Value):  # ADDITION
        if isinstance(other, Number):
            try:
                return Number(self.value + other.value, self.pos_start, other.pos_end).set_context(self.context), None
            except OverflowError as e:
                errmsg = str(e)
                assert self.context is not None
                return None, RTOverflowError(
                    self.pos_start, self.pos_end,
                    errmsg,
                    self.context,
                    origin_file="src.values.basevalues.Number.added_to"
                )
        else:
            return None, self.illegal_operation(other)

    def subbed_by(self, other: Value):  # SUBTRACTION
        if isinstance(other, Number):
            try:
                return Number(self.value - other.value, self.pos_start, other.pos_end).set_context(self.context), None
            except OverflowError as e:
                errmsg = str(e)
                assert self.context is not None
                return None, RTOverflowError(
                    self.pos_start, self.pos_end,
                    errmsg,
                    self.context,
                    origin_file="src.values.basevalues.Number.subbed_by"
                )
        else:
            return None, self.illegal_operation(other)

    def multiplied_by(self, other: Value):  # MULTIPLICATION
        try:
            if isinstance(other, Number):
                return Number(self.value * other.value, self.pos_start, other.pos_end).set_context(self.context), None
            elif isinstance(other, String) and isinstance(self.value, int):
                return String(other.value * self.value, self.pos_start, other.pos_end).set_context(self.context), None
            elif isinstance(other, List) and isinstance(self.value, int):
                new_list = other.copy()
                new_list.elements = new_list.elements * self.value
                return new_list, None
            else:
                return None, self.illegal_operation(other)
        except OverflowError as e:
            errmsg = str(e)
            assert self.context is not None
            return None, RTOverflowError(
                self.pos_start, other.pos_end,
                errmsg,
                self.context,
                origin_file="src.values.basevalues.Number.multiplied_by"
            )

    def dived_by(self, other: Value):  # DIVISION
        if isinstance(other, Number):
            try:
                val = self.value / other.value
            except ZeroDivisionError:
                assert self.context is not None
                return None, RTArithmeticError(
                    other.pos_start, other.pos_end,
                    'division by zero is not possible.',
                    self.context,
                    "src.values.basevalues.Number.dived_by"
                )
            except OverflowError as e:  # I hate python
                errmsg = str(e)
                assert self.context is not None
                return None, RTOverflowError(
                    self.pos_start, other.pos_end,
                    errmsg,
                    self.context,
                    "src.values.basevalues.Number.dived_by"
                )
            return Number(val, self.pos_start, other.pos_end).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def modded_by(self, other: Value):  # MODULO
        if isinstance(other, Number):
            if other.value == 0:
                assert self.context is not None
                return None, RTArithmeticError(
                    other.pos_start, other.pos_end,
                    'division by zero is not possible.',
                    self.context,
                    "src.values.basevalues.Number.modded_by"
                )
            try:
                return Number(self.value % other.value, self.pos_start, other.pos_end).set_context(self.context), None
            except OverflowError as e:
                errmsg = str(e)
                assert self.context is not None
                return None, RTOverflowError(
                    self.pos_start, other.pos_end,
                    errmsg,
                    self.context,
                    "src.values.basevalues.Number.modded_by"
                )
        else:
            return None, self.illegal_operation(other)

    def floor_dived_by(self, other: Value):  # FLOOR_DIVISION
        if isinstance(other, Number):
            if other.value == 0:
                assert self.context is not None
                return None, RTArithmeticError(
                    other.pos_start, other.pos_end,
                    'division by zero is not possible.',
                    self.context,
                    "src.values.basevalues.Number.floor_dived_by"
                )
            try:
                return Number(self.value // other.value, self.pos_start, other.pos_end).set_context(self.context), None
            except OverflowError as e:
                errmsg = str(e)
                assert self.context is not None
                return None, RTOverflowError(
                    self.pos_start, other.pos_end,
                    errmsg,
                    self.context,
                    "src.values.basevalues.Number.floor_dived_by"
                )
        else:
            return None, self.illegal_operation(other)

    def powered_by(self, other: Value):  # POWER
        if isinstance(other, Number):
            try:
                return Number(self.value ** other.value, self.pos_start, other.pos_end).set_context(self.context), None
            except OverflowError as e:
                assert self.context is not None
                return None, RTOverflowError(
                    self.pos_start, other.pos_end,
                    str(e), self.context,
                    "src.values.basevalues.Number.powered_by"
                )
        else:
            return None, self.illegal_operation(other)

    def get_comparison_eq(self, other: Value):
        if isinstance(other, Number):
            return Number(self.value == other.value, self.pos_start, other.pos_end).set_context(self.context), None
        else:
            return Number(False, self.pos_start, other.pos_end).set_context(self.context), None

    def get_comparison_ne(self, other: Value):
        is_eq = bool(self.get_comparison_eq(other)[0].value)
        is_ne = not is_eq
        return Number(is_ne, self.pos_start, other.pos_end).set_context(self.context), None

    def get_comparison_lt(self, other: Value):
        if isinstance(other, Number):
            return Number(self.value < other.value, self.pos_start, other.pos_end).set_context(self.context), None
        return None, self.illegal_operation(other)

    def get_comparison_gt(self, other: Value):
        if isinstance(other, Number):
            return Number(self.value > other.value, self.pos_start, other.pos_end).set_context(self.context), None
        return None, self.illegal_operation(other)

    def get_comparison_lte(self, other: Value):
        if isinstance(other, Number):
            return Number(self.value <= other.value, self.pos_start, other.pos_end).set_context(self.context), None
        return None, self.illegal_operation(other)

    def get_comparison_gte(self, other: Value):
        if isinstance(other, Number):
            return Number(self.value >= other.value, self.pos_start, other.pos_end).set_context(self.context), None
        return None, self.illegal_operation(other)

    def and_(self, other: Value):
        return Number(self.is_true() and other.is_true(), self.pos_start, other.pos_end), None

    def or_(self, other: Value):
        return Number(self.is_true() or other.is_true(), self.pos_start, other.pos_end), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        xor = (
            not self.is_true() and other.is_true()
        ) or (
            self.is_true() and not other.is_true()
        )
        return Number(xor, self.pos_start, other.pos_end).set_context(self.context), None

    def bitwise_and(self, other: Value):
        if isinstance(other, Number) and isinstance(self.value, int) and isinstance(other.value, int):
            return Number(self.value & other.value, self.pos_start, other.pos_end).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def bitwise_or(self, other: Value):
        if isinstance(other, Number) and isinstance(self.value, int) and isinstance(other.value, int):
            return Number(self.value | other.value, self.pos_start, other.pos_end).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def bitwise_xor(self, other: Value):
        if isinstance(other, Number) and isinstance(self.value, int) and isinstance(other.value, int):
            return Number(self.value ^ other.value, self.pos_start, other.pos_end).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def bitwise_not(self):
        if not isinstance(self.value, int):
            return None, self.illegal_operation()
        return Number(~self.value, self.pos_start, self.pos_end).set_context(self.context), None

    def is_true(self):
        return self.value != 0

    def abs_(self):
        return Number(abs(self.value), self.pos_start, self.pos_end), None

    def to_str(self):
        return String(self.__repr__(), self.pos_start, self.pos_end).set_context(self.context), None

    def to_int(self):
        return Number(int(self.value), self.pos_start, self.pos_end).set_context(self.context), None

    def to_float(self):
        return Number(float(self.value), self.pos_start, self.pos_end).set_context(self.context), None

    def to_list(self):
        list_: list[Value] = []
        for element in str(self.value):
            if element.isnumeric():
                list_.append(Number(int(element), self.pos_start, self.pos_end))
            else:
                list_.append(String(element, self.pos_start, self.pos_end))
        return List(list_, self.pos_start, self.pos_end).set_context(self.context), None

    def is_in(self, other: Value):
        if isinstance(other, List):
            for x in other.elements:
                if self.get_comparison_eq(x)[0].is_true():
                    return Number(True, self.pos_start, other.pos_end).set_context(self.context), None
            return Number(False, self.pos_start, other.pos_end).set_context(self.context), None
        elif isinstance(other, String):
            return Number(
                str(self.value) in other.value,
                self.pos_start, other.pos_end
            ).set_context(self.context), None
        else:
            return None, self.can_not_be_in(other)

    def is_int(self):
        return isinstance(self.value, int)

    def is_float(self):
        return isinstance(self.value, float)

    def copy(self):
        """Return a copy of self"""
        copy = Number(self.value, self.pos_start, self.pos_end)
        copy.set_context(self.context)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy


class List(Value):
    def __init__(self, elements: list[Value], pos_start: _Position, pos_end: _Position):
        super().__init__(pos_start, pos_end)
        self.elements = elements
        self.type_ = 'list'
        self.update_should_print()

    def __repr__(self):
        return f'[{", ".join([x.__str__() for x in self.elements])}]'
    
    def to_python_str(self) -> str:
        return self.__repr__()

    def __getitem__(self, item: int):
        """If there is foo[bar] in the python code and that foo is a Nougaro List, it works ^^ !!"""
        return self.elements[item]

    def update_should_print(self):
        should_print = False

        if len(self.elements) == 0:
            should_print = True
        else:
            for e in self.elements:
                if e.should_print:
                    should_print = True
                    break

        self.should_print = should_print

    def added_to(self, other: Value):
        new_list = self.copy()
        new_list.elements.append(other)
        new_list.update_should_print()
        return new_list, None

    def subbed_by(self, other: Value):
        if isinstance(other, Number) and isinstance(other.value, int):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                new_list.update_should_print()
                return new_list, None
            except IndexError:
                assert self.context is not None
                return None, RTIndexError(
                    other.pos_start, other.pos_end,
                    f'pop index {other.value} out of range.',
                    self.context, "src.values.basevalues.List.subbed_by"
                )
        else:
            return None, self.illegal_operation(other)

    def multiplied_by(self, other: Value):
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            new_list.update_should_print()
            new_list.set_pos(self.pos_start, other.pos_end)
            return new_list, None
        elif isinstance(other, Number) and isinstance(other.value, int):
            if other.is_int():
                new_list = self.copy()
                new_list.elements = new_list.elements * other.value
                new_list.update_should_print()
                new_list.set_pos(self.pos_start, other.pos_end)
                return new_list, None
            else:
                return None, self.illegal_operation(other)
        else:
            return None, self.illegal_operation(other)

    def dived_by(self, other: Value):
        if isinstance(other, Number) and isinstance(other.value, int):
            try:
                return self.elements[other.value], None
            except IndexError:
                assert self.context is not None
                return None, RTIndexError(
                    other.pos_start, other.pos_end,
                    f'list index {other.value} out of range.',
                    self.context, "src.values.basevalues.List.dived_by"
                )
        else:
            return None, self.illegal_operation(other)

    def to_str(self):
        return String(str(self.elements), self.pos_start, self.pos_end).set_context(self.context), None

    def to_list(self):
        return self.copy(), None

    def is_eq(self, other: Value):
        # think this is very slow
        # TODO: maybe find something to improve speed of this method (is_eq in List)
        if isinstance(other, List):
            if len(self.elements) != len(other.elements):
                return False
            for index, element in enumerate(self.elements):
                comparison, error = element.get_comparison_eq(other.elements[index])
                if error is not None:
                    comparison = Number(0, self.pos_start, self.pos_end)
                assert comparison is not None
                if not comparison.is_true():
                    return False
            return True
        else:
            return False

    def get_comparison_eq(self, other: Value):
        is_eq = self.is_eq(other)
        return Number(is_eq, self.pos_start, other.pos_end).set_context(self.context), None

    def get_comparison_ne(self, other: Value):
        is_eq = self.is_eq(other)
        return Number(not is_eq, self.pos_start, other.pos_end).set_context(self.context), None

    def get_comparison_gt(self, other: Value):
        return None, self.can_not_compare(other)

    def get_comparison_gte(self, other: Value):
        return None, self.can_not_compare(other)

    def get_comparison_lt(self, other: Value):
        return None, self.can_not_compare(other)

    def get_comparison_lte(self, other: Value):
        return None, self.can_not_compare(other)

    def and_(self, other: Value):
        return Number(self.is_true() and other.is_true(), self.pos_start, other.pos_end).set_context(self.context), None

    def or_(self, other: Value):
        return Number(self.is_true() or other.is_true(), self.pos_start, other.pos_end).set_context(self.context), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        xor = (
            not self.is_true() and other.is_true()
        ) or (
            self.is_true() and not other.is_true()
        )
        return Number(xor, self.pos_start, other.pos_end).set_context(self.context), None

    def is_in(self, other: Value):
        if isinstance(other, String):
            return Number(
                self.to_str()[0].value in other.value,
                self.pos_start, other.pos_end
            ).set_context(self.context), None
        else:
            return None, self.can_not_be_in(other)
    
    def is_true(self):
        return bool(len(self.elements))

    def copy(self):
        """Return a copy of self"""
        copy = List(self.elements, self.pos_start, self.pos_end)
        copy.set_context(self.context)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy

    def true_copy(self):
        """Return a copy of self where elements is also a copy"""
        copy = List(self.elements.copy(), self.pos_start, self.pos_end)
        copy.set_context(self.context)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy

    def __copy__(self):
        return self.copy()


class Module(Value):
    def __init__(self, name: str, functions_and_constants: dict[str, Value], pos_start: _Position, pos_end: _Position):
        super().__init__(pos_start, pos_end)
        self.name = name
        self.type_ = "module"
        self.attributes = functions_and_constants.copy()

    def __repr__(self):
        return f"<module {self.name}>"
    
    def to_python_str(self) -> str:
        return self.__repr__()

    def is_true(self):
        return False

    def is_eq(self, other: Value):
        return isinstance(other, Module) and other.name == self.name

    def get_comparison_eq(self, other: Value):
        return Number(self.is_eq(other), self.pos_start, other.pos_end).set_context(self.context), None

    def get_comparison_ne(self, other: Value):
        return Number(not self.is_eq(other), self.pos_start, other.pos_end).set_context(self.context), None

    def get_comparison_gt(self, other: Value):
        return None, self.can_not_compare(other)

    def get_comparison_gte(self, other: Value):
        return None, self.can_not_compare(other)

    def get_comparison_lt(self, other: Value):
        return None, self.can_not_compare(other)

    def get_comparison_lte(self, other: Value):
        return None, self.can_not_compare(other)

    def and_(self, other: Value):
        return Number(self.is_true() and other.is_true(), self.pos_start, other.pos_end), None

    def or_(self, other: Value):
        return Number(self.is_true() or other.is_true(), self.pos_start, other.pos_end), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        xor = (
            not self.is_true() and other.is_true()
        ) or (
            self.is_true() and not other.is_true()
        )
        return Number(xor, self.pos_start, other.pos_end).set_context(self.context), None

    def copy(self):
        """Return a copy of self"""
        copy = Module(self.name, self.attributes, self.pos_start, self.pos_end)
        copy.set_context(self.context)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy


class Constructor(Value):
    def __init__(self, name: str | None, symbol_table: SymbolTable, attributes: dict[str, Value],
                 pos_start: _Position, pos_end: _Position, parent: Constructor | None = None):
        super().__init__(pos_start, pos_end)
        self.name = name if name is not None else '<class>'
        self.symbol_table = symbol_table
        self.attributes = attributes.copy()
        self.parent = parent
        self.type_ = "constructor"

    def __repr__(self):
        return f"<class {self.name}>"
    
    def to_python_str(self) -> str:
        return self.__repr__()

    def is_true(self):
        return False
    
    def is_eq(self, other: Value):
        if not isinstance(other, Constructor):
            return False
        names_eq = self.name == other.name
        symbol_tables_eq = self.symbol_table == other.symbol_table
        same_attributes = self.attributes == other.attributes
        same_parent = self.parent == other.parent
        return names_eq and symbol_tables_eq and same_attributes and same_parent

    def get_comparison_eq(self, other: Value):
        return Number(self.is_eq(other), self.pos_start, other.pos_end).set_context(self.context), None

    def get_comparison_ne(self, other: Value):
        return Number(not self.is_eq(other), self.pos_start, other.pos_end).set_context(self.context), None

    def get_comparison_gt(self, other: Value):
        return None, self.can_not_compare(other)

    def get_comparison_gte(self, other: Value):
        return None, self.can_not_compare(other)

    def get_comparison_lt(self, other: Value):
        return None, self.can_not_compare(other)

    def get_comparison_lte(self, other: Value):
        return None, self.can_not_compare(other)

    def and_(self, other: Value):
        return Number(
            self.is_true() and other.is_true(),
            self.pos_start, other.pos_end
        ).set_context(self.context), None

    def or_(self, other: Value):
        return Number(
            self.is_true() or other.is_true(),
            self.pos_start, other.pos_end
        ).set_context(self.context), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        xor = (
            not self.is_true() and other.is_true()
        ) or (
            self.is_true() and not other.is_true()
        )
        return Number(xor, self.pos_start, other.pos_end).set_context(self.context), None

    def copy(self):
        """Return a copy of self"""
        copy = Constructor(
            self.name, self.symbol_table, self.attributes, self.pos_start, self.pos_end, self.parent
        )
        copy.set_context(self.context)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy


class Object(Value):
    def __init__(self, attributes: dict[str, Value], constructor: Constructor,
                 pos_start: _Position, pos_end: _Position, inner_ctx: Context | None = None):
        super().__init__(pos_start, pos_end)
        self.attributes = attributes.copy()
        self.constructor: Constructor = constructor
        self.type_ = constructor.name
        self.inner_context = inner_ctx

    def __repr__(self):
        return f"<{self.type_} object>"
    
    def to_python_str(self) -> str:
        return self.__repr__()
    
    def is_eq(self, other: Value):
        if not isinstance(other, Object):
            return False
        attributes_eq = self.attributes == other.attributes
        constructors_eq = self.constructor == other.constructor
        types_eq = self.type_ == other.type_
        return attributes_eq and constructors_eq and types_eq

    def get_comparison_eq(self, other: Value):
        return Number(self.is_eq(other), self.pos_start, other.pos_end).set_context(self.context), None

    def get_comparison_ne(self, other: Value):
        return Number(not self.is_eq(other), self.pos_start, other.pos_end).set_context(self.context), None

    def get_comparison_gt(self, other: Value):
        return None, self.can_not_compare(other)

    def get_comparison_gte(self, other: Value):
        return None, self.can_not_compare(other)

    def get_comparison_lt(self, other: Value):
        return None, self.can_not_compare(other)

    def get_comparison_lte(self, other: Value):
        return None, self.can_not_compare(other)

    def and_(self, other: Value):
        return Number(
            self.is_true() and other.is_true(),
            self.pos_start, other.pos_end
        ).set_context(self.context), None

    def or_(self, other: Value):
        return Number(
            self.is_true() or other.is_true(),
            self.pos_start, other.pos_end
        ).set_context(self.context), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        xor = (
            not self.is_true() and other.is_true()
        ) or (
            self.is_true() and not other.is_true()
        )
        return Number(xor, self.pos_start, other.pos_end).set_context(self.context), None

    def copy(self):
        """Return a copy of self"""
        copy = Object(self.attributes, self.constructor, self.pos_start, self.pos_end, self.inner_context)
        copy.set_context(self.context)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy


class NoneValue(Value):
    def __init__(self, pos_start: _Position, pos_end: _Position, should_print: bool = True):
        super().__init__(pos_start, pos_end)
        self.type_ = 'NoneValue'
        self.should_print = should_print

    def __repr__(self):
        return 'None'

    def __str__(self):
        return 'None'
    
    def to_python_str(self) -> str:
        return self.__repr__()

    def get_comparison_eq(self, other: Value):
        return Number(isinstance(other, NoneValue), self.pos_start, other.pos_end).set_context(self.context), None

    def get_comparison_ne(self, other: Value):
        return Number(not isinstance(other, NoneValue), self.pos_start, other.pos_end).set_context(self.context), None

    def get_comparison_gt(self, other: Value):
        return None, self.can_not_compare(other)

    def get_comparison_gte(self, other: Value):
        return None, self.can_not_compare(other)

    def get_comparison_lt(self, other: Value):
        return None, self.can_not_compare(other)

    def get_comparison_lte(self, other: Value):
        return None, self.can_not_compare(other)

    def and_(self, other: Value):
        return Number(
            self.is_true() and other.is_true(),
            self.pos_start, other.pos_end
        ).set_context(self.context), None

    def or_(self, other: Value):
        return Number(
            self.is_true() or other.is_true(),
            self.pos_start, other.pos_end
        ).set_context(self.context), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        xor = (
            not self.is_true() and other.is_true()
        ) or (
            self.is_true() and not other.is_true()
        )
        return Number(xor, self.pos_start, other.pos_end).set_context(self.context), None

    def to_str(self):
        return String('None', self.pos_start, self.pos_end).set_context(self.context), None

    def to_list(self):
        return String('None', self.pos_start, self.pos_end).to_list()[0].set_context(self.context), None

    def to_int(self):
        return Number(0, self.pos_start, self.pos_end).set_context(self.context), None

    def to_float(self):
        return Number(0.0, self.pos_start, self.pos_end).set_context(self.context), None

    def is_in(self, other: Value):
        if isinstance(other, List):
            for element in other.elements:
                if isinstance(element, NoneValue):
                    return Number(True, self.pos_start, other.pos_end).set_context(self.context), None
            return Number(False, self.pos_start, other.pos_end).set_context(self.context), None
        elif isinstance(other, String):
            return Number('none' in other.value.lower(), self.pos_start, other.pos_end).set_context(self.context), None
        else:
            return None, self.can_not_be_in(other)

    def copy(self):
        """Return a copy of self"""
        copy = NoneValue(self.pos_start, self.pos_end, self.should_print)
        copy.set_context(self.context)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy
