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
# built-in python imports
# no imports


# IMPORTANT NOTE: THE DOC FOR ALL THE FUNCTIONS IN THIS FILE ARE IN value.py :)


class String(Value):
    def __init__(self, value: String | str):
        super().__init__()
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
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def multiplied_by(self, other: Value):
        if isinstance(other, Number) and isinstance(other.value, int):
            try:
                return String(self.value * other.value).set_context(self.context), None
            except OverflowError as e:
                assert self.context is not None
                assert self.pos_start is not None
                assert other.pos_end is not None
                return None, RTOverflowError(
                    self.pos_start, other.pos_end,
                    str(e), self.context,
                    "src.runtime.values.basevalues.basevalues.String.multiplied_by"
                )
        else:
            return None, self.illegal_operation(other)

    def is_true(self):
        return len(self.value) > 0

    def to_str_(self) -> tuple[String, None]:
        return self.copy(), None

    def to_int_(self):
        """Returns a nougaro int"""
        value_to_convert = self.value
        if value_to_convert in ["null", "False"]:
            value_to_convert = "0"
        elif value_to_convert in ["True"]:
            value_to_convert = "1"

        try:
            return Number(int(float(value_to_convert))).set_context(self.context), None
        except ValueError:
            assert self.pos_start is not None
            assert self.pos_end is not None
            assert self.context is not None
            return None, RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"str '{self.value}' can not be converted to int.",
                self.context,
                origin_file="src.values.basevalues.String.to_int"
            ))

    def to_float_(self):
        try:
            return Number(float(self.value)).set_context(self.context), None
        except ValueError:
            assert self.pos_start is not None
            assert self.pos_end is not None
            assert self.context is not None
            return None, RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"str '{self.value}' can not be converted to float.",
                self.context,
                origin_file="src.values.basevalues.String.to_float"))

    def to_list_(self):
        list_: list[Value] = list(map(String, list(self.value)))
        return List(list_).set_context(self.context), None

    def get_comparison_eq(self, other: Value):
        if isinstance(other, String):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return FALSE.copy().set_context(self.context), None

    def get_comparison_ne(self, other: Value):
        is_eq = bool(self.get_comparison_eq(other)[0].value)
        is_ne = not is_eq
        return Number(int(is_ne)), None

    def get_comparison_gt(self, other: Value):
        return FALSE.copy().set_context(self.context), None

    def get_comparison_gte(self, other: Value):
        is_eq = bool(self.get_comparison_eq(other)[0].value)
        if is_eq:
            return TRUE.copy().set_context(self.context), None
        else:
            return FALSE.copy().set_context(self.context), None

    def get_comparison_lt(self, other: Value):
        return FALSE.copy().set_context(self.context), None

    def get_comparison_lte(self, other: Value):
        is_eq = bool(self.get_comparison_eq(other)[0].value)
        if is_eq:
            return TRUE.copy().set_context(self.context), None
        else:
            return FALSE.copy().set_context(self.context), None

    def and_(self, other: Value):
        return Number(int(self.is_true() and other.is_true())), None

    def or_(self, other: Value):
        return Number(int(self.is_true() or other.is_true())), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        if not self.is_true() and other.is_true():
            return TRUE.copy().set_context(self.context), None
        if self.is_true() and not other.is_true():
            return TRUE.copy().set_context(self.context), None
        else:
            return FALSE.copy().set_context(self.context), None

    def is_in(self, other: Value):
        if isinstance(other, List):
            for x in other.elements:
                if self.get_comparison_eq(x)[0].is_true():
                    return TRUE.copy().set_context(self.context), None
            return FALSE.set_context(self.context), None
        elif isinstance(other, String):
            return Number(int(self.value in other.value)).set_context(self.context), None
        else:
            return None, self.can_not_be_in(other)

    def copy(self):
        """Return a copy of self"""
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy


class Number(Value):
    def __init__(self, value: int | float | bool):
        super().__init__()
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
                return Number(self.value + other.value).set_context(self.context), None
            except OverflowError as e:
                errmsg = str(e)
                assert self.pos_start is not None
                assert self.pos_end is not None
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
                return Number(self.value - other.value).set_context(self.context), None
            except OverflowError as e:
                errmsg = str(e)
                assert self.pos_start is not None
                assert self.pos_end is not None
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
                return Number(self.value * other.value).set_context(self.context), None
            elif isinstance(other, String) and isinstance(self.value, int):
                return String(other.value * self.value).set_context(self.context), None
            elif isinstance(other, List) and isinstance(self.value, int):
                new_list = other.copy()
                new_list.elements = new_list.elements * self.value
                return new_list, None
            else:
                return None, self.illegal_operation(other)
        except OverflowError as e:
            errmsg = str(e)
            assert self.pos_start is not None
            assert other.pos_end is not None
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
                assert other.pos_start is not None
                assert other.pos_end is not None
                assert self.context is not None
                return None, RTArithmeticError(
                    other.pos_start, other.pos_end,
                    'division by zero is not possible.',
                    self.context,
                    "src.values.basevalues.Number.dived_by"
                )
            except OverflowError as e:  # I hate python
                errmsg = str(e)
                assert self.pos_start is not None
                assert other.pos_end is not None
                assert self.context is not None
                return None, RTOverflowError(
                    self.pos_start, other.pos_end,
                    errmsg,
                    self.context,
                    "src.values.basevalues.Number.dived_by"
                )
            return Number(val).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def modded_by(self, other: Value):  # MODULO
        if isinstance(other, Number):
            if other.value == 0:
                assert other.pos_start is not None
                assert other.pos_end is not None
                assert self.context is not None
                return None, RTArithmeticError(
                    other.pos_start, other.pos_end,
                    'division by zero is not possible.',
                    self.context,
                    "src.values.basevalues.Number.modded_by"
                )
            try:
                return Number(self.value % other.value).set_context(self.context), None
            except OverflowError as e:
                errmsg = str(e)
                assert self.pos_start is not None
                assert other.pos_end is not None
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
                assert other.pos_start is not None
                assert other.pos_end is not None
                assert self.context is not None
                return None, RTArithmeticError(
                    other.pos_start, other.pos_end,
                    'division by zero is not possible.',
                    self.context,
                    "src.values.basevalues.Number.floor_dived_by"
                )
            try:
                return Number(self.value // other.value).set_context(self.context), None
            except OverflowError as e:
                errmsg = str(e)
                assert self.pos_start is not None
                assert other.pos_end is not None
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
                return Number(self.value ** other.value).set_context(self.context), None
            except OverflowError as e:
                assert self.context is not None
                assert self.pos_start is not None, str(self)
                assert other.pos_end is not None
                return None, RTOverflowError(
                    self.pos_start, other.pos_end,
                    str(e), self.context,
                    "src.values.basevalues.Number.powered_by"
                )
        else:
            return None, self.illegal_operation(other)

    def get_comparison_eq(self, other: Value):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return FALSE.copy().set_context(self.context), None

    def get_comparison_ne(self, other: Value):
        is_eq = bool(self.get_comparison_eq(other)[0].value)
        is_ne = not is_eq
        return Number(int(is_ne)), None

    def get_comparison_lt(self, other: Value):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return FALSE.copy().set_context(self.context), None

    def get_comparison_gt(self, other: Value):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return FALSE.copy().set_context(self.context), None

    def get_comparison_lte(self, other: Value):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            is_eq = bool(self.get_comparison_eq(other)[0].value)
            if is_eq:
                return TRUE.copy().set_context(self.context), None
            else:
                return FALSE.copy().set_context(self.context), None

    def get_comparison_gte(self, other: Value):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            is_eq = bool(self.get_comparison_eq(other)[0].value)
            if is_eq:
                return TRUE.copy().set_context(self.context), None
            else:
                return FALSE.copy().set_context(self.context), None

    def and_(self, other: Value):
        return Number(int(self.is_true() and other.is_true())), None

    def or_(self, other: Value):
        return Number(int(self.is_true() or other.is_true())), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        if not self.is_true() and other.is_true():
            return TRUE.copy().set_context(self.context), None
        if self.is_true() and not other.is_true():
            return TRUE.copy().set_context(self.context), None
        else:
            return FALSE.copy().set_context(self.context), None

    def not_(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def bitwise_and(self, other: Value):
        if isinstance(other, Number) and isinstance(self.value, int) and isinstance(other.value, int):
            return Number(self.value & other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def bitwise_or(self, other: Value):
        if isinstance(other, Number) and isinstance(self.value, int) and isinstance(other.value, int):
            return Number(self.value | other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def bitwise_xor(self, other: Value):
        if isinstance(other, Number) and isinstance(self.value, int) and isinstance(other.value, int):
            return Number(self.value ^ other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def bitwise_not(self):
        if not isinstance(self.value, int):
            return None, self.illegal_operation()
        return Number(~self.value).set_context(self.context), None

    def is_true(self):
        return self.value != 0

    def abs_(self):
        return Number(abs(self.value)), None

    def to_str_(self):
        return String(self.__repr__()).set_context(self.context), None

    def to_int_(self):
        return Number(int(self.value)).set_context(self.context), None

    def to_float_(self):
        return Number(float(self.value)).set_context(self.context), None

    def to_list_(self):
        list_: list[Value] = []
        for element in str(self.value):
            if element.isnumeric():
                list_.append(Number(int(element)))
            else:
                list_.append(String(element))
        return List(list_).set_context(self.context), None

    def is_in(self, other: Value):
        if isinstance(other, List):
            for x in other.elements:
                if self.get_comparison_eq(x)[0].is_true():
                    return TRUE.copy().set_context(self.context), None
            return FALSE.set_context(self.context), None
        elif isinstance(other, String):
            return Number(int(str(self.value) in other.value)).set_context(self.context), None
        else:
            return None, self.can_not_be_in(other)

    def is_int(self):
        return isinstance(self.value, int)

    def is_float(self):
        return not self.is_int()

    def copy(self):
        """Return a copy of self"""
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy


NULL = Number(0)
FALSE = Number(0)
TRUE = Number(1)


class List(Value):
    def __init__(self, elements: list[Value]):
        super().__init__()
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
                assert other.pos_start is not None
                assert other.pos_end is not None
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
            new_list.update_should_print
            return new_list, None
        elif isinstance(other, Number) and isinstance(other.value, int):
            if other.is_int():
                new_list = self.copy()
                new_list.elements = new_list.elements * other.value
                new_list.update_should_print()
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
                assert other.pos_start is not None
                assert other.pos_end is not None
                assert self.context is not None
                return None, RTIndexError(
                    other.pos_start, other.pos_end,
                    f'list index {other.value} out of range.',
                    self.context, "src.values.basevalues.List.dived_by"
                )
        else:
            return None, self.illegal_operation(other)

    def to_str_(self):
        return String(str(self.elements)).set_context(self.context), None

    def to_list_(self):
        return self.copy(), None

    def is_eq(self, other: Value):
        # think this is very slow
        # TODO: maybe find something to improve speed of this method (is_eq in List)
        if isinstance(other, List):
            if len(self.elements) != len(other.elements):
                return False
            else:
                for index, element in enumerate(self.elements):
                    comparison, error = element.get_comparison_eq(other.elements[index])
                    if error is not None:
                        return None
                    assert comparison is not None
                    if comparison.is_true():
                        continue
                    else:
                        return False
                return True
        else:
            return None

    def get_comparison_eq(self, other: Value):
        is_eq = self.is_eq(other)
        if is_eq is None:
            return None, self.can_not_compare(other)
        elif is_eq:
            return TRUE.copy().set_context(self.context), None
        else:
            return FALSE.copy().set_context(self.context), None

    def get_comparison_ne(self, other: Value):
        is_eq = self.is_eq(other)
        if is_eq is None:
            return None, self.can_not_compare(other)
        elif is_eq:
            return FALSE.copy().set_context(self.context), None
        else:
            return TRUE.copy().set_context(self.context), None

    def get_comparison_gt(self, other: Value):
        return FALSE.copy().set_context(self.context), None

    def get_comparison_gte(self, other: Value):
        if self.is_eq(other):
            return TRUE.copy().set_context(self.context), None
        return FALSE.copy().set_context(self.context), None

    def get_comparison_lt(self, other: Value):
        return FALSE.copy().set_context(self.context), None

    def get_comparison_lte(self, other: Value):
        if self.is_eq(other):
            return TRUE.copy().set_context(self.context), None
        return FALSE.copy().set_context(self.context), None

    def and_(self, other: Value):
        return Number(int(self.is_true() and other.is_true())), None

    def or_(self, other: Value):
        return Number(int(self.is_true() or other.is_true())), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        if not self.is_true() and other.is_true():
            return TRUE.copy().set_context(self.context), None
        if self.is_true() and not other.is_true():
            return TRUE.copy().set_context(self.context), None
        else:
            return FALSE.copy().set_context(self.context), None

    def is_in(self, other: Value):
        if isinstance(other, String):
            return Number(int(self.to_str_()[0].value in other.value)).set_context(self.context), None
        else:
            return None, self.can_not_be_in(other)
    
    def is_true(self):
        return bool(len(self.elements))

    def copy(self):
        """Return a copy of self"""
        copy = List(self.elements)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy

    def true_copy(self):
        """Return a copy of self where elements is also a copy"""
        copy = List(self.elements.copy())
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy

    def __copy__(self):
        return self.copy()


class Module(Value):
    def __init__(self, name: str, functions_and_constants: dict[str, Value]):
        super().__init__()
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
        if isinstance(other, Module) and other.name == self.name:
            return True
        else:
            return False

    def get_comparison_eq(self, other: Value):
        return Number(int(self.is_eq(other))).set_context(self.context), None

    def get_comparison_ne(self, other: Value):
        return Number(int(not self.is_eq(other))).set_context(self.context), None

    def get_comparison_gt(self, other: Value):
        return FALSE.copy().set_context(self.context), None

    def get_comparison_gte(self, other: Value):
        if self.is_eq(other):
            return TRUE.copy().set_context(self.context), None
        return FALSE.copy().set_context(self.context), None

    def get_comparison_lt(self, other: Value):
        return FALSE.copy().set_context(self.context), None

    def get_comparison_lte(self, other: Value):
        if self.is_eq(other):
            return TRUE.copy().set_context(self.context), None
        return FALSE.copy().set_context(self.context), None

    def and_(self, other: Value):
        return Number(int(self.is_true() and other.is_true())), None

    def or_(self, other: Value):
        return Number(int(self.is_true() or other.is_true())), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        if not self.is_true() and other.is_true():
            return TRUE.copy().set_context(self.context), None
        if self.is_true() and not other.is_true():
            return TRUE.copy().set_context(self.context), None
        else:
            return FALSE.copy().set_context(self.context), None

    def copy(self):
        """Return a copy of self"""
        copy = Module(self.name, self.attributes)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy


class Constructor(Value):
    def __init__(self, name: str | None, symbol_table: SymbolTable, attributes: dict[str, Value],
                 parent: Constructor | None = None):
        super().__init__()
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

    def get_comparison_eq(self, other: Value):
        return FALSE.copy().set_context(self.context), None

    def get_comparison_ne(self, other: Value):
        return TRUE.copy().set_context(self.context), None

    def get_comparison_gt(self, other: Value):
        return FALSE.copy().set_context(self.context), None

    def get_comparison_gte(self, other: Value):
        return FALSE.copy().set_context(self.context), None

    def get_comparison_lt(self, other: Value):
        return FALSE.copy().set_context(self.context), None

    def get_comparison_lte(self, other: Value):
        return FALSE.copy().set_context(self.context), None

    def and_(self, other: Value):
        return Number(int(self.is_true() and other.is_true())), None

    def or_(self, other: Value):
        return Number(int(self.is_true() or other.is_true())), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        if not self.is_true() and other.is_true():
            return TRUE.copy().set_context(self.context), None
        if self.is_true() and not other.is_true():
            return TRUE.copy().set_context(self.context), None
        else:
            return FALSE.copy().set_context(self.context), None

    def copy(self):
        """Return a copy of self"""
        copy = Constructor(self.name, self.symbol_table, self.attributes, self.parent)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy


class Object(Value):
    def __init__(self, attributes: dict[str, Value], constructor: Constructor, inner_ctx: Context | None = None):
        super().__init__()
        self.attributes = attributes.copy()
        self.constructor: Constructor = constructor
        self.type_ = constructor.name
        self.inner_context = inner_ctx

    def __repr__(self):
        return f"<{self.type_} object>"
    
    def to_python_str(self) -> str:
        return self.__repr__()

    def get_comparison_eq(self, other: Value):
        return FALSE.copy().set_context(self.context), None

    def get_comparison_ne(self, other: Value):
        return TRUE.copy().set_context(self.context), None

    def get_comparison_gt(self, other: Value):
        return FALSE.copy().set_context(self.context), None

    def get_comparison_gte(self, other: Value):
        return FALSE.copy().set_context(self.context), None

    def get_comparison_lt(self, other: Value):
        return FALSE.copy().set_context(self.context), None

    def get_comparison_lte(self, other: Value):
        return FALSE.copy().set_context(self.context), None

    def and_(self, other: Value):
        return Number(int(self.is_true() and other.is_true())), None

    def or_(self, other: Value):
        return Number(int(self.is_true() or other.is_true())), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        if not self.is_true() and other.is_true():
            return TRUE.copy().set_context(self.context), None
        if self.is_true() and not other.is_true():
            return TRUE.copy().set_context(self.context), None
        else:
            return FALSE.copy().set_context(self.context), None

    def copy(self):
        """Return a copy of self"""
        copy = Object(self.attributes, self.constructor, self.inner_context)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy


class NoneValue(Value):
    def __init__(self, should_print: bool = True):
        super().__init__()
        self.type_ = 'NoneValue'
        self.should_print = should_print

    def __repr__(self):
        return 'None'

    def __str__(self):
        return 'None'
    
    def to_python_str(self) -> str:
        return self.__repr__()

    def get_comparison_eq(self, other: Value):
        if isinstance(other, NoneValue):
            return TRUE.copy(), None
        else:
            return FALSE.copy(), None

    def get_comparison_ne(self, other: Value):
        if isinstance(other, NoneValue):
            return FALSE.copy(), None
        else:
            return TRUE.copy(), None

    def get_comparison_gt(self, other: Value):
        return FALSE.copy().set_context(self.context), None

    def get_comparison_gte(self, other: Value):
        if isinstance(other, NoneValue):
            return TRUE.copy().set_context(self.context), None
        return FALSE.copy().set_context(self.context), None

    def get_comparison_lt(self, other: Value):
        return FALSE.copy().set_context(self.context), None

    def get_comparison_lte(self, other: Value):
        if isinstance(other, NoneValue):
            return TRUE.copy().set_context(self.context), None
        return FALSE.copy().set_context(self.context), None

    def and_(self, other: Value):
        return Number(int(self.is_true() and other.is_true())), None

    def or_(self, other: Value):
        return Number(int(self.is_true() or other.is_true())), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        if not self.is_true() and other.is_true():
            return TRUE.copy().set_context(self.context), None
        if self.is_true() and not other.is_true():
            return TRUE.copy().set_context(self.context), None
        else:
            return FALSE.copy().set_context(self.context), None

    def to_str_(self):
        return String('None').set_context(self.context), None

    def to_list_(self):
        return List([String('None')]).set_context(self.context), None

    def to_int_(self):
        return Number(0).set_context(self.context), None

    def to_float_(self):
        return Number(0.0).set_context(self.context), None

    def is_in(self, other: Value):
        if isinstance(other, List):
            for element in other.elements:
                if isinstance(element, NoneValue):
                    return TRUE.copy().set_context(self.context), None
            return FALSE.copy().set_context(self.context), None
        elif isinstance(other, String):
            return Number(int('none' in other.value.lower())).set_context(self.context), None
        else:
            return None, self.can_not_be_in(other)

    def copy(self):
        """Return a copy of self"""
        copy = NoneValue(self.should_print)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy
