#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# IMPORTS
# nougaro modules imports
from src.values.value import Value
from src.runtime_result import RTResult
from src.errors import RunTimeError, RTArithmeticError, RTIndexError
# built-in python imports
from math import pi, e as euler, sqrt


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.type_ = "str"

    def __repr__(self):
        return f'"{self.value}"'

    def to_str(self):
        return self.value

    def added_to(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def multiplied_by(self, other):
        if isinstance(other, Number) and other.type_ == 'int':
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def is_true(self):
        return len(self.value) > 0

    def to_str_(self):
        return self, None

    def to_int_(self):
        try:
            return Number(int(float(self.value))).set_context(self.context), None
        except ValueError:
            return None, RTResult().failure(RunTimeError(self.pos_start, self.pos_end,
                                                         f"str {self.value} can not be converted to int.",
                                                         self.context))

    def to_float_(self):
        try:
            return Number(float(self.value)).set_context(self.context), None
        except ValueError:
            return None, RTResult().failure(RunTimeError(self.pos_start, self.pos_end,
                                                         f"str {self.value} can not be converted to int.",
                                                         self.context))

    def to_list_(self):
        list_ = []
        for element in list(self.value):
            list_.append(String(element).set_context(self.context))
        return List(list_).set_context(self.context), None

    def get_comparison_eq(self, other):
        if isinstance(other, String):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, self.can_not_compare(other)

    def get_comparison_ne(self, other):
        if isinstance(other, String):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, self.can_not_compare(other)

    def is_in(self, other):
        if isinstance(other, List):
            for x in other.elements:
                if self.value == x.value:
                    return Number.TRUE.set_context(self.context), None
            return Number.FALSE.set_context(self.context), None
        elif isinstance(other, String):
            return Number(int(self.value in other.value)).set_context(self.context), None
        else:
            return None, self.can_not_be_in(other)

    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
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
        return str(self.value)

    def added_to(self, other):  # ADDITION
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
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
        elif isinstance(other, String) and self.type_ == "int":
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def dived_by(self, other):  # DIVISION
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTArithmeticError(
                    other.pos_start, other.pos_end, 'division by zero is not possible.', self.context
                )
            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def modded_by(self, other):  # MODULO
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTArithmeticError(
                    other.pos_start, other.pos_end, 'division by zero is not possible.', self.context
                )
            return Number(self.value % other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def floor_dived_by(self, other):  # FLOOR_DIVISION
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTArithmeticError(
                    other.pos_start, other.pos_end, 'division by zero is not possible.', self.context
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
            return None, self.can_not_compare(other)

    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, self.can_not_compare(other)

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, self.can_not_compare(other)

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, self.can_not_compare(other)

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, self.can_not_compare(other)

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, self.can_not_compare(other)

    def and_(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def or_(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def excl_or(self, other):
        """ Exclusive or (xor) """
        if isinstance(other, Number):
            return Number(int(self.value ^ other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def not_(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def is_true(self):
        return self.value != 0

    def abs_(self):
        return Number(abs(self.value))

    def to_str_(self):
        return String(str(self.value)).set_context(self.context), None

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
                    return Number.TRUE.set_context(self.context), None
            return Number.FALSE.set_context(self.context), None
        elif isinstance(other, String):
            return Number(int(self.to_str_()[0].value in other.value)).set_context(self.context), None
        else:
            return None, self.can_not_be_in(other)

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy


Number.NULL = Number(0)
Number.FALSE = Number(0)
Number.TRUE = Number(1)
Number.MATH_PI = Number(pi)
Number.MATH_E = Number(euler)
Number.MATH_SQRT_PI = Number(sqrt(pi))


class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements
        self.type_ = 'list'

    def __repr__(self):
        return f'[{", ".join([x.__str__() for x in self.elements])}]'

    def __getitem__(self, item):
        return self.elements.__getitem__(item)

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
            except Exception:
                return None, RTIndexError(
                    other.pos_start, other.pos_end,
                    f'pop index {other.value} out of range.',
                    self.context
                )
        else:
            return None, self.illegal_operation(other)

    def multiplied_by(self, other):
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, self.illegal_operation(other)

    def dived_by(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except Exception:
                return None, RTIndexError(
                    other.pos_start, other.pos_end,
                    f'list index {other.value} out of range.',
                    self.context
                )
        else:
            return None, self.illegal_operation(other)

    def to_str_(self):
        return String(str(self.elements)).set_context(self.context), None

    def to_list_(self):
        return self, None

    def is_eq(self, other):
        if isinstance(other, List):
            if len(self.elements) != len(other.elements):
                return False
            else:
                for index, element in enumerate(self.elements):
                    if isinstance(element, Number) and isinstance(other.elements[index], Number):
                        if element.value == other.elements[index].value:
                            continue
                        else:
                            return False
                    elif isinstance(element, String) and isinstance(other.elements[index], String):
                        if element.value == other.elements[index].value:
                            continue
                        else:
                            return False
                    elif isinstance(element, List) and isinstance(other.elements[index], List):
                        if element.is_eq(other.elements[index]):
                            continue
                        else:
                            return False
                    else:
                        return False
                return True
        else:
            return None

    def get_comparison_eq(self, other):
        # does not work
        is_eq = self.is_eq(other)
        if is_eq is None:
            return None, self.can_not_compare(other)
        elif is_eq:
            return Number.TRUE.set_context(self.context), None
        else:
            return Number.FALSE.set_context(self.context), None

    def get_comparison_ne(self, other):
        is_eq = self.is_eq(other)
        if is_eq is None:
            return None, self.can_not_compare(other)
        elif is_eq:
            return Number.FALSE.set_context(self.context), None
        else:
            return Number.TRUE.set_context(self.context), None

    def is_in(self, other):
        if isinstance(other, List):
            return Number(int(self.elements in other.elements)).set_context(self.context), None
        elif isinstance(other, String):
            return Number(int(self.to_str_()[0].value in other.value)).set_context(self.context), None
        else:
            return None, self.can_not_be_in(other)

    def copy(self):
        copy = List(self.elements)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy


class NoneValue(Value):
    def __init__(self, do_i_print: bool = True):
        super().__init__()
        self.type_ = 'NoneValue'
        self.do_i_print = do_i_print

    def __repr__(self):
        if self.do_i_print:
            return 'None'
        else:
            return None

    def __str__(self):
        return 'None'

    def get_comparison_eq(self, other):
        if isinstance(other, NoneValue):
            return Number(Number.TRUE), None
        else:
            return Number(Number.FALSE), None

    def get_comparison_ne(self, other):
        if isinstance(other, NoneValue):
            return Number(Number.FALSE), None
        else:
            return Number(Number.TRUE), None

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
                    return Number.TRUE.set_context(self.context), None
            return Number.FALSE.set_context(self.context), None
        elif isinstance(other, String):
            return Number(int('none' in other.value.lower())).set_context(self.context), None
        else:
            return None, self.can_not_be_in(other)

    def copy(self):
        copy = NoneValue(self.do_i_print)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
