#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.runtime.values.basevalues.value import Value
from src.runtime.runtime_result import RTResult
from src.errors.errors import RunTimeError, RTArithmeticError, RTIndexError, RTOverflowError
# built-in python imports
from typing import Literal


# IMPORTANT NOTE : THE DOC FOR ALL THE FUNCTIONS IN THIS FILE ARE IN value.py :)


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value: str | Literal = value
        self.type_ = "str"

    def __repr__(self):
        return f'"{self.value}"'

    def __len__(self):
        return len(self.value)

    def to_str(self):
        """Returns self.value, as a python str"""
        return self.value

    def added_to(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def multiplied_by(self, other):
        if isinstance(other, Number) and other.is_int():
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def is_true(self):
        return len(self.value) > 0

    def to_str_(self):
        return self.copy(), None

    def to_int_(self):
        value_to_convert = self.value
        if value_to_convert in ["null", "False"]:
            value_to_convert = "0"
        elif value_to_convert in ["True"]:
            value_to_convert = "1"

        try:
            return Number(int(float(value_to_convert))).set_context(self.context), None
        except ValueError:
            return None, RTResult().failure(RunTimeError(self.pos_start, self.pos_end,
                                                         f"str '{self.value}' can not be converted to int.",
                                                         self.context,
                                                         origin_file="src.values.basevalues.String.to_int"))

    def to_float_(self):
        try:
            return Number(float(self.value)).set_context(self.context), None
        except ValueError:
            return None, RTResult().failure(RunTimeError(self.pos_start, self.pos_end,
                                                         f"str '{self.value}' can not be converted to float.",
                                                         self.context,
                                                         origin_file="src.values.basevalues.String.to_float"))

    def to_list_(self):
        list_ = []
        for element in list(self.value):
            list_.append(String(element).set_context(self.context))
        return List(list_).set_context(self.context), None

    def get_comparison_eq(self, other):
        if isinstance(other, String):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_ne(self, other):
        is_eq = bool(self.get_comparison_eq(other)[0].value)
        is_ne = not is_eq
        return Number(int(is_ne)), None

    def get_comparison_gt(self, other): return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_gte(self, other):
        is_eq = bool(self.get_comparison_eq(other)[0].value)
        if is_eq:
            return Number.TRUE.copy().set_context(self.context), None
        else:
            return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_lt(self, other): return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_lte(self, other):
        is_eq = bool(self.get_comparison_eq(other)[0].value)
        if is_eq:
            return Number.TRUE.copy().set_context(self.context), None
        else:
            return Number.FALSE.copy().set_context(self.context), None

    def and_(self, other: Value):
        return Number(int(self.is_true() and other.is_true())), None

    def or_(self, other):
        return Number(int(self.is_true() or other.is_true())), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        if not self.is_true() and other.is_true():
            return Number.TRUE.copy().set_context(self.context), None
        if self.is_true() and not other.is_true():
            return Number.TRUE.copy().set_context(self.context), None
        else:
            return Number.FALSE.copy().set_context(self.context), None

    def is_in(self, other):
        if isinstance(other, List):
            for x in other.elements:
                if self.value == x.value:
                    return Number.TRUE.copy().set_context(self.context), None
            return Number.FALSE.set_context(self.context), None
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
    def __init__(self, value):
        super().__init__()
        self.value = value
        if isinstance(self.value, int):
            self.type_ = 'int'
        elif isinstance(self.value, float):
            self.type_ = 'float'

    def __repr__(self):
        try:
            return str(self.value)
        except ValueError:
            return "This number can not be displayed. However, Nougaro can deal with it."

    def added_to(self, other):  # ADDITION
        if isinstance(other, Number):
            try:
                return Number(self.value + other.value).set_context(self.context), None
            except OverflowError as e:
                return None, RTOverflowError(self.pos_start, self.pos_end, e, self.context,
                                             origin_file="src.values.basevalues.Number.added_to")
        else:
            return None, self.illegal_operation(other)

    def subbed_by(self, other):  # SUBTRACTION
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def multiplied_by(self, other):  # MULTIPLICATION
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        elif isinstance(other, String) and self.is_int():
            return String(self.value * other.value).set_context(self.context), None
        elif isinstance(other, List) and self.is_int():
            new_list = other.copy()
            new_list.elements = new_list.elements * self.value
            return new_list, None
        else:
            return None, self.illegal_operation(other)

    def dived_by(self, other):  # DIVISION
        if isinstance(other, Number):
            try:
                val = self.value / other.value
            except ZeroDivisionError:
                return None, RTArithmeticError(
                    other.pos_start, other.pos_end, 'division by zero is not possible.', self.context,
                    "src.values.basevalues.Number.dived_by"
                )
            except OverflowError as e:  # I hate python
                return None, RTOverflowError(
                    self.pos_start, other.pos_end, e, self.context,
                    "src.values.basevalues.Number.dived_by"
                )
            return Number(val).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def modded_by(self, other):  # MODULO
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTArithmeticError(
                    other.pos_start, other.pos_end, 'division by zero is not possible.', self.context,
                    "src.values.basevalues.Number.modded_by"
                )
            return Number(self.value % other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def floor_dived_by(self, other):  # FLOOR_DIVISION
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTArithmeticError(
                    other.pos_start, other.pos_end, 'division by zero is not possible.', self.context,
                    "src.values.basevalues.Number.floor_dived_by"
                )
            return Number(self.value // other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def powered_by(self, other):  # POWER
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_ne(self, other):
        is_eq = bool(self.get_comparison_eq(other)[0].value)
        is_ne = not is_eq
        return Number(int(is_ne)), None

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            is_eq = bool(self.get_comparison_eq(other)[0].value)
            if is_eq:
                return Number.TRUE.copy().set_context(self.context), None
            else:
                return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            is_eq = bool(self.get_comparison_eq(other)[0].value)
            if is_eq:
                return Number.TRUE.copy().set_context(self.context), None
            else:
                return Number.FALSE.copy().set_context(self.context), None

    def and_(self, other: Value):
        return Number(int(self.is_true() and other.is_true())), None

    def or_(self, other):
        return Number(int(self.is_true() or other.is_true())), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        if not self.is_true() and other.is_true():
            return Number.TRUE.copy().set_context(self.context), None
        if self.is_true() and not other.is_true():
            return Number.TRUE.copy().set_context(self.context), None
        else:
            return Number.FALSE.copy().set_context(self.context), None

    def not_(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def bitwise_and(self, other):
        if isinstance(other, Number):
            return Number(self.value & other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def bitwise_or(self, other):
        if isinstance(other, Number):
            return Number(self.value | other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def bitwise_xor(self, other):
        if isinstance(other, Number):
            return Number(self.value ^ other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def bitwise_not(self):
        return Number(~self.value).set_context(self.context), None

    def is_true(self):
        return self.value != 0

    def abs_(self):
        return Number(abs(self.value))

    def to_str_(self):
        return String(self.__repr__()).set_context(self.context), None

    def to_int_(self):
        return Number(int(self.value)).set_context(self.context), None

    def to_float_(self):
        return Number(float(self.value)).set_context(self.context), None

    def to_list_(self):
        list_ = []
        for element in self.to_str_()[0].to_list_()[0]:
            if isinstance(element, String):
                if element.value == "0":
                    list_.append(Number(0))
                elif element.value == "-":
                    list_.append(String('-'))
                elif element.value == ".":
                    list_.append(String('.'))
                elif element.value == "e":  # try 10^-100 -> 10e-100
                    list_.append(String('e'))
                else:
                    element_to_int = element.to_int_()[0]
                    if element_to_int is None:
                        list_.append(NoneValue())
                    else:
                        list_.append(element.to_int_()[0])
            elif element is None:  # error in converting...
                list_.append(NoneValue())
        return List(list_).set_context(self.context), None

    def is_in(self, other):
        if isinstance(other, List):
            for x in other.elements:
                if self.value == x.value:
                    return Number.TRUE.copy().set_context(self.context), None
            return Number.FALSE.set_context(self.context), None
        elif isinstance(other, String):
            return Number(int(self.to_str_()[0].value in other.value)).set_context(self.context), None
        else:
            return None, self.can_not_be_in(other)

    def is_int(self):
        return self.type_ == 'int'

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


Number.NULL = Number(0)
Number.FALSE = Number(0)
Number.TRUE = Number(1)


class List(Value):
    def __init__(self, elements: list):
        super().__init__()
        self.elements: list = elements
        self.type_ = 'list'
        self.update_should_print()

    def __repr__(self):
        return f'[{", ".join([x.__str__() for x in self.elements])}]'

    def __getitem__(self, item):
        """If there is foo[bar] in the python code and that foo is a Nougaro List, it works ^^ !!"""
        return self.elements.__getitem__(item)

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

    def added_to(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None

    def subbed_by(self, other):
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except IndexError:
                return None, RTIndexError(
                    other.pos_start, other.pos_end,
                    f'pop index {other.value} out of range.',
                    self.context, "src.values.basevalues.List.subbed_by"
                )
        else:
            return None, self.illegal_operation(other)

    def multiplied_by(self, other):
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        elif isinstance(other, Number):
            if other.is_int():
                new_list = self.copy()
                new_list.elements = new_list.elements * other.value
                return new_list, None
            else:
                return None, self.illegal_operation(other)
        else:
            return None, self.illegal_operation(other)

    def dived_by(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except IndexError:
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

    def is_eq(self, other):
        # think this is very slow
        # TODO: maybe find something to improve speed of this method (is_eq in List)
        if isinstance(other, List):
            if len(self.elements) != len(other.elements):
                return False
            else:
                for index, element in enumerate(self.elements):
                    if element.get_comparison_eq(other.elements[index]):
                        continue
                    else:
                        return False
                return True
        else:
            return None

    def get_comparison_eq(self, other):
        is_eq = self.is_eq(other)
        if is_eq is None:
            return None, self.can_not_compare(other)
        elif is_eq:
            return Number.TRUE.copy().set_context(self.context), None
        else:
            return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_ne(self, other):
        is_eq = self.is_eq(other)
        if is_eq is None:
            return None, self.can_not_compare(other)
        elif is_eq:
            return Number.FALSE.copy().set_context(self.context), None
        else:
            return Number.TRUE.copy().set_context(self.context), None

    def get_comparison_gt(self, other):
        return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_gte(self, other):
        if self.is_eq(other):
            return Number.TRUE.copy().set_context(self.context), None
        return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_lt(self, other):
        return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_lte(self, other):
        if self.is_eq(other):
            return Number.TRUE.copy().set_context(self.context), None
        return Number.FALSE.copy().set_context(self.context), None

    def and_(self, other: Value):
        return Number(int(self.is_true() and other.is_true())), None

    def or_(self, other):
        return Number(int(self.is_true() or other.is_true())), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        if not self.is_true() and other.is_true():
            return Number.TRUE.copy().set_context(self.context), None
        if self.is_true() and not other.is_true():
            return Number.TRUE.copy().set_context(self.context), None
        else:
            return Number.FALSE.copy().set_context(self.context), None

    def is_in(self, other):
        if isinstance(other, List):
            return Number(int(self.elements in other.elements)).set_context(self.context), None
        elif isinstance(other, String):
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


class Module(Value):
    def __init__(self, name, functions_and_constants: dict):
        super().__init__()
        self.name = name
        self.type_ = "module"
        self.attributes = functions_and_constants.copy()

    def __repr__(self):
        return f"<module {self.name}>"

    def is_true(self):
        return False

    def is_eq(self, other):
        if isinstance(other, Module) and other.name == self.name:
            return True
        else:
            return False

    def get_comparison_eq(self, other):
        return Number(int(self.is_eq(other))).set_context(self.context), None

    def get_comparison_ne(self, other):
        return Number(int(not self.is_eq(other))).set_context(self.context), None

    def get_comparison_gt(self, other):
        return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_gte(self, other):
        if self.is_eq(other):
            return Number.TRUE.copy().set_context(self.context), None
        return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_lt(self, other):
        return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_lte(self, other):
        if self.is_eq(other):
            return Number.TRUE.copy().set_context(self.context), None
        return Number.FALSE.copy().set_context(self.context), None

    def and_(self, other: Value):
        return Number(int(self.is_true() and other.is_true())), None

    def or_(self, other):
        return Number(int(self.is_true() or other.is_true())), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        if not self.is_true() and other.is_true():
            return Number.TRUE.copy().set_context(self.context), None
        if self.is_true() and not other.is_true():
            return Number.TRUE.copy().set_context(self.context), None
        else:
            return Number.FALSE.copy().set_context(self.context), None

    def copy(self):
        """Return a copy of self"""
        copy = Module(self.name, self.attributes)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy


class Constructor(Value):
    def __init__(self, name, symbol_table, attributes: dict, parent=None):
        super().__init__()
        self.name = name if name is not None else '<class>'
        self.symbol_table = symbol_table
        self.attributes = attributes.copy()
        self.parent = parent
        self.type_ = "constructor"

    def __repr__(self):
        return f"<class {self.name}>"

    def is_true(self):
        return False

    def get_comparison_eq(self, other):
        return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_ne(self, other):
        return Number.TRUE.copy().set_context(self.context), None

    def get_comparison_gt(self, other):
        return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_gte(self, other):
        return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_lt(self, other):
        return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_lte(self, other):
        return Number.FALSE.copy().set_context(self.context), None

    def and_(self, other: Value):
        return Number(int(self.is_true() and other.is_true())), None

    def or_(self, other):
        return Number(int(self.is_true() or other.is_true())), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        if not self.is_true() and other.is_true():
            return Number.TRUE.copy().set_context(self.context), None
        if self.is_true() and not other.is_true():
            return Number.TRUE.copy().set_context(self.context), None
        else:
            return Number.FALSE.copy().set_context(self.context), None

    def copy(self):
        """Return a copy of self"""
        copy = Constructor(self.name, self.symbol_table, self.attributes, self.parent)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        copy.module_context = self.module_context
        copy.attributes = self.attributes.copy()
        return copy


class Object(Value):
    def __init__(self, attributes: dict, constructor: Constructor, inner_ctx=None):
        super().__init__()
        self.attributes = attributes.copy()
        self.constructor: Constructor = constructor
        self.type_ = constructor.name
        self.inner_context = inner_ctx

    def __repr__(self):
        return f"<{self.type_} object>"

    def get_comparison_eq(self, other):
        return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_ne(self, other):
        return Number.TRUE.copy().set_context(self.context), None

    def get_comparison_gt(self, other):
        return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_gte(self, other):
        return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_lt(self, other):
        return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_lte(self, other):
        return Number.FALSE.copy().set_context(self.context), None

    def and_(self, other: Value):
        return Number(int(self.is_true() and other.is_true())), None

    def or_(self, other):
        return Number(int(self.is_true() or other.is_true())), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        if not self.is_true() and other.is_true():
            return Number.TRUE.copy().set_context(self.context), None
        if self.is_true() and not other.is_true():
            return Number.TRUE.copy().set_context(self.context), None
        else:
            return Number.FALSE.copy().set_context(self.context), None

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

    def get_comparison_eq(self, other):
        if isinstance(other, NoneValue):
            return Number.TRUE.copy(), None
        else:
            return Number.FALSE.copy(), None

    def get_comparison_ne(self, other):
        if isinstance(other, NoneValue):
            return Number.FALSE.copy(), None
        else:
            return Number.TRUE.copy(), None

    def get_comparison_gt(self, other):
        return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_gte(self, other):
        if isinstance(other, NoneValue):
            return Number.TRUE.copy().set_context(self.context), None
        return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_lt(self, other):
        return Number.FALSE.copy().set_context(self.context), None

    def get_comparison_lte(self, other):
        if isinstance(other, NoneValue):
            return Number.TRUE.copy().set_context(self.context), None
        return Number.FALSE.copy().set_context(self.context), None

    def and_(self, other: Value):
        return Number(int(self.is_true() and other.is_true())), None

    def or_(self, other):
        return Number(int(self.is_true() or other.is_true())), None

    def xor_(self, other: Value):
        """ Exclusive or (xor) """
        if not self.is_true() and other.is_true():
            return Number.TRUE.copy().set_context(self.context), None
        if self.is_true() and not other.is_true():
            return Number.TRUE.copy().set_context(self.context), None
        else:
            return Number.FALSE.copy().set_context(self.context), None

    def to_str_(self):
        return String('None').set_context(self.context), None

    def to_list_(self):
        return List([String('None')]).set_context(self.context), None

    def to_int_(self):
        return Number(0).set_context(self.context), None

    def to_float_(self):
        return Number(0.0).set_context(self.context), None

    def is_in(self, other):
        if isinstance(other, List):
            for element in other.elements:
                if isinstance(element, NoneValue):
                    return Number.TRUE.copy().set_context(self.context), None
            return Number.FALSE.copy().set_context(self.context), None
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
