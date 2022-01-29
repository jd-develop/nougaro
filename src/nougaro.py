#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain
# Actually running with Python 3.9, works with Python 3.10

# IMPORTS
# nougaro modules imports
from src.token_constants import *
from src.constants import VARS_CANNOT_MODIFY
from src.lexer import Lexer
from src.context import Context
from src.symbol_table import SymbolTable
from src.set_symbol_table import set_symbol_table
from src.errors import *
from src.misc import CustomBuiltInFuncMethod
from src.nodes import *
from src.parser import Parser
# built-in python imports
import os
import math
# import pprint


# ##########
# RUNTIME RESULT
# ##########
class RTResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, result):
        if result is None:
            return Number.NULL
        if result.error is not None:
            self.error = result.error
        return result.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self


# ##########
# VALUES
# ##########
class Value:
    def __init__(self):
        self.pos_start = self.pos_end = self.context = None
        self.set_pos()
        self.set_context()
        self.type_ = "BaseValue"

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context: Context = None):
        self.context = context
        return self

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multiplied_by(self, other):
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        return None, self.illegal_operation(other)

    def powered_by(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        return None, self.can_not_compare(other)

    def get_comparison_ne(self, other):
        return None, self.can_not_compare(other)

    def get_comparison_lt(self, other):
        return None, self.can_not_compare(other)

    def get_comparison_gt(self, other):
        return None, self.can_not_compare(other)

    def get_comparison_lte(self, other):
        return None, self.can_not_compare(other)

    def get_comparison_gte(self, other):
        return None, self.can_not_compare(other)

    def and_(self, other):
        return None, self.illegal_operation(other)

    def or_(self, other):
        return None, self.illegal_operation(other)

    def not_(self):
        return None, self.illegal_operation()

    def excl_or(self, other):
        """ Exclusive or """
        return None, self.illegal_operation(other)

    def execute(self, args):
        return RTResult().failure(self.illegal_operation())

    def abs_(self):
        return RTResult().failure(self.illegal_operation())

    def to_str_(self):
        return None, RTResult().failure(self.illegal_operation())

    def to_int_(self):
        return None, RTResult().failure(self.illegal_operation())

    def to_float_(self):
        return None, RTResult().failure(self.illegal_operation())

    def to_list_(self):
        return None, RTResult().failure(self.illegal_operation())

    def copy(self):
        print(self.context)
        print('NOUGARO INTERNAL ERROR : No copy method defined in Value.copy().\n'
              'Please report this bug at https://jd-develop.github.io/nougaro/redirect1.html with the information below'
              )
        raise Exception('No copy method defined in Value.copy().')

    @staticmethod
    def is_true():
        return False

    def illegal_operation(self, other=None):
        if other is None:
            return RunTimeError(
                self.pos_start, self.pos_end, f'illegal operation with {self.type_}.', self.context
            )
        return RunTimeError(
            self.pos_start, other.pos_end, f'illegal operation between {self.type_} and {other.type_}.', self.context
        )

    def can_not_compare(self, other):
        return RunTimeError(
            self.pos_start, other.pos_end, f'can not compare {self.type_} and {other.type_}.', self.context
        )


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
        if isinstance(other, Number):
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

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy


Number.NULL = Number(0)
Number.FALSE = Number(0)
Number.TRUE = Number(1)
Number.MATH_PI = Number(math.pi)
Number.MATH_E = Number(math.e)
Number.MATH_SQRT_PI = Number(math.sqrt(math.pi))


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

    def copy(self):
        copy = List(self.elements)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy


class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name if name is not None else '<function>'
        self.type_ = 'BaseFunction'

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args, optional_args: list = None, have_to_respect_args_number: bool = True):
        result = RTResult()
        if optional_args is None:
            optional_args = []

        if (len(args) > len(arg_names + optional_args)) and have_to_respect_args_number:
            return result.failure(
                RunTimeError(
                    self.pos_start, self.pos_end,
                    f"{len(args) - len(arg_names + optional_args)} too many args passed into '{self.name}'.",
                    self.context
                )
            )

        if len(args) < len(arg_names) and have_to_respect_args_number:
            return result.failure(
                RunTimeError(
                    self.pos_start, self.pos_end,
                    f"{len(arg_names) - len(args)} too few args passed into '{self.name}'.",
                    self.context
                )
            )

        return result.success(None)

    @staticmethod
    def populate_args(arg_names, args, exec_context: Context, optional_args: list = None,
                      have_to_respect_args_number: bool = True):
        # We need the context for the symbol table :)
        if optional_args is None:
            optional_args = []
        if have_to_respect_args_number:
            for i in range(len(args)):
                if i + 1 < len(arg_names) + 1:
                    arg_name = arg_names[i]
                    arg_value = args[i]
                    arg_value.set_context(exec_context)
                    exec_context.symbol_table.set(arg_name, arg_value)
                else:
                    arg_name = optional_args[len(arg_names) - i]
                    arg_value = args[i]
                    arg_value.set_context(exec_context)
                    exec_context.symbol_table.set(arg_name, arg_value)
        else:
            for i in range(len(args)):
                if i + 1 < len(arg_names) + 1:
                    arg_name = arg_names[i]
                    arg_value = args[i]
                    arg_value.set_context(exec_context)
                    exec_context.symbol_table.set(arg_name, arg_value)
                elif ((i - len(args)) + 1) < len(optional_args):
                    print(i)
                    print((i - len(args)) + 1)
                    print(len(optional_args) + 1)
                    arg_name = optional_args[i]
                    arg_value = args[i]
                    arg_value.set_context(exec_context)
                    exec_context.symbol_table.set(arg_name, arg_value)
                else:
                    pass

    def check_and_populate_args(self, arg_names, args, exec_context: Context, optional_args: list = None,
                                have_to_respect_args_number: bool = True):
        # We still need the context for the symbol table ;)
        result = RTResult()
        result.register(self.check_args(arg_names, args, optional_args, have_to_respect_args_number))
        if result.error is not None:
            return result
        self.populate_args(arg_names, args, exec_context, optional_args, have_to_respect_args_number)
        return result.success(None)


class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, should_return_none):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_return_none = should_return_none
        self.type_ = "func"

    def __repr__(self):
        return f'<function {self.name}>'

    def execute(self, args):
        result = RTResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()

        result.register(self.check_and_populate_args(self.arg_names, args, exec_context))
        if result.error is not None:
            return result

        value = result.register(interpreter.visit(self.body_node, exec_context))
        if result.error is not None:
            return result
        return result.success(NoneValue(False) if self.should_return_none else value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names, self.should_return_none)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy


class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)
        self.type_ = 'built-in func'

    def __repr__(self):
        return f'<built-in function {self.name}>'

    def execute(self, args):
        result = RTResult()
        exec_context = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method: CustomBuiltInFuncMethod = getattr(self, method_name, self.no_visit_method)

        result.register(self.check_and_populate_args(method.arg_names, args, exec_context,
                                                     optional_args=method.optional_args,
                                                     have_to_respect_args_number=method.have_to_respect_args_number))
        if result.error is not None:
            return result

        try:
            return_value = result.register(method(exec_context))
        except TypeError:
            try:
                return_value = result.register(method())
            except TypeError:  # it only executes when coding
                return_value = result.register(method(exec_context))
        if result.error is not None:
            return result
        return result.success(return_value)

    def no_visit_method(self, exec_context: Context):
        print(exec_context)
        print(f"NOUGARO INTERNAL ERROR : No execute_{self.name} method defined in nougaro.BuildInFunction.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/redirect1.html with all informations "
              f"above.")
        raise Exception(f'No execute_{self.name} method defined in nougaro.BuildInFunction.')

    # ==================
    # BUILD IN FUNCTIONS
    # ==================

    def execute_void(self):
        """Return nothing"""
        # No params.
        result = RTResult()
        return result.success(NoneValue(False))

    execute_void.arg_names = []
    execute_void.optional_args = []
    execute_void.have_to_respect_args_number = False

    def execute_print(self, exec_context: Context):
        """Print 'value'"""
        # Params:
        # * value
        try:
            print(exec_context.symbol_table.get('value').to_str())
        except Exception:
            print(str(exec_context.symbol_table.get('value')))
        return RTResult().success(NoneValue(False))

    execute_print.arg_names = ["value"]
    execute_print.optional_args = []
    execute_print.have_to_respect_args_number = True

    def execute_print_ret(self, exec_context: Context):
        """Print 'value' and returns 'value'"""
        # Params:
        # * value
        try:
            print(exec_context.symbol_table.get('value').to_str())
            return RTResult().success(
                String(
                    exec_context.symbol_table.get('value').to_str()
                )
            )
        except Exception:
            print(str(exec_context.symbol_table.get('value')))
            return RTResult().success(
                String(
                    str(exec_context.symbol_table.get('value'))
                )
            )

    execute_print_ret.arg_names = ["value"]
    execute_print_ret.optional_args = []
    execute_print_ret.have_to_respect_args_number = True

    def execute_input(self, exec_context: Context):
        """Basic input (str)"""
        # Optional params:
        # * text_to_display
        text_to_display = exec_context.symbol_table.get('text_to_display')
        if text_to_display is None:
            text = input()
        elif isinstance(text_to_display, String) or isinstance(text_to_display, Number):
            text = input(text_to_display.value)
        else:
            text = input()
        return RTResult().success(String(text))

    execute_input.arg_names = []
    execute_input.optional_args = ['text_to_display']
    execute_input.have_to_respect_args_number = True

    def execute_input_int(self, exec_context: Context):
        """Basic input (int). Repeat while entered value is not an int."""
        # Optional params:
        # * text_to_display
        while True:
            text_to_display = exec_context.symbol_table.get('text_to_display')
            if text_to_display is None:
                text = input()
            elif isinstance(text_to_display, String) or isinstance(text_to_display, Number):
                text = input(text_to_display.value)
            else:
                text = input()

            try:
                number = int(text)
                break
            except ValueError:
                print(f'{text} must be an integer. Try again :')
        return RTResult().success(Number(number))

    execute_input_int.arg_names = []
    execute_input_int.optional_args = ['text_to_display']
    execute_input_int.have_to_respect_args_number = True

    def execute_clear(self):
        """Clear the screen"""
        # No params.
        os.system('cls' if (os.name == "nt" or os.name == "Windows") else 'clear')
        return RTResult().success(NoneValue(False))

    execute_clear.arg_names = []
    execute_clear.optional_args = []
    execute_clear.have_to_respect_args_number = False

    def execute_is_int(self, exec_context: Context):
        """Check if 'value' is an integer"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        is_number = isinstance(value, Number)
        if is_number:
            if value.type_ == 'int':
                is_int = True
            else:
                is_int = False
        else:
            is_int = False
        return RTResult().success(Number.TRUE if is_int else Number.FALSE)

    execute_is_int.arg_names = ['value']
    execute_is_int.optional_args = []
    execute_is_int.have_to_respect_args_number = True

    def execute_is_float(self, exec_context: Context):
        """Check if 'value' is a float"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        is_number = isinstance(value, Number)
        if is_number:
            if value.type_ == 'float':
                is_float = True
            else:
                is_float = False
        else:
            is_float = False
        return RTResult().success(Number.TRUE if is_float else Number.FALSE)

    execute_is_float.arg_names = ['value']
    execute_is_float.optional_args = []
    execute_is_float.have_to_respect_args_number = True

    def execute_is_list(self, exec_context: Context):
        """Check if 'value' is a List"""
        # Params:
        # * value
        is_list = isinstance(exec_context.symbol_table.get('value'), List)
        return RTResult().success(Number.TRUE if is_list else Number.FALSE)

    execute_is_list.arg_names = ['value']
    execute_is_list.optional_args = []
    execute_is_list.have_to_respect_args_number = True

    def execute_is_str(self, exec_context: Context):
        """Check if 'value' is a String"""
        # Params:
        # * value
        is_str = isinstance(exec_context.symbol_table.get('value'), String)
        return RTResult().success(Number.TRUE if is_str else Number.FALSE)

    execute_is_str.arg_names = ['value']
    execute_is_str.optional_args = []
    execute_is_str.have_to_respect_args_number = True

    def execute_is_func(self, exec_context: Context):
        """Check if 'value' is a BaseFunction"""
        # Params:
        # * value
        is_func = isinstance(exec_context.symbol_table.get('value'), BaseFunction)
        return RTResult().success(Number.TRUE if is_func else Number.FALSE)

    execute_is_func.arg_names = ['value']
    execute_is_func.optional_args = []
    execute_is_func.have_to_respect_args_number = True

    def execute_is_none(self, exec_context: Context):
        """Check if 'value' is a NoneValue"""
        # Params:
        # * value
        is_none = isinstance(exec_context.symbol_table.get('value'), NoneValue)
        return RTResult().success(Number.TRUE if is_none else Number.FALSE)

    execute_is_none.arg_names = ['value']
    execute_is_none.optional_args = []
    execute_is_none.have_to_respect_args_number = True

    def execute_append(self, exec_context: Context):
        """Append 'value' to 'list'"""
        # Params:
        # * list
        # * value
        list_ = exec_context.symbol_table.get('list')
        value = exec_context.symbol_table.get('value')

        if not isinstance(list_, List):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'append' must be a list.",
                exec_context
            ))

        list_.elements.append(value)
        return RTResult().success(list_)

    execute_append.arg_names = ['list', 'value']
    execute_append.optional_args = []
    execute_append.have_to_respect_args_number = True

    def execute_pop(self, exec_context: Context):
        """Remove element at 'index' from 'list'"""
        # Params:
        # * list
        # * index
        list_ = exec_context.symbol_table.get('list')
        index = exec_context.symbol_table.get('index')

        if not isinstance(list_, List):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'pop' must be a list.",
                exec_context
            ))

        if not isinstance(index, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "second argument of built-in function 'pop' must be a number.",
                exec_context
            ))

        try:
            list_.elements.pop(index.value)
        except Exception:
            return RTResult().failure(RTIndexError(
                self.pos_start, self.pos_end,
                f'pop index {index.value} out of range.',
                self.context
            ))
        return RTResult().success(list_)

    execute_pop.arg_names = ['list', 'index']
    execute_pop.optional_args = []
    execute_pop.have_to_respect_args_number = True

    def execute_extend(self, exec_context: Context):
        """Extend list 'list1' with the elements of 'list2'"""
        # Params:
        # * list1
        # * list2
        list1 = exec_context.symbol_table.get('list1')
        list2 = exec_context.symbol_table.get('list2')

        if not isinstance(list1, List):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'extend' must be a list.",
                exec_context
            ))

        if not isinstance(list2, List):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "second argument of built-in function 'extend' must be a list.",
                exec_context
            ))

        list1.elements.extend(list2.elements)
        return RTResult().success(list1)

    execute_extend.arg_names = ['list1', 'list2']
    execute_extend.optional_args = []
    execute_extend.have_to_respect_args_number = True

    def execute_get(self, exec_context: Context):
        # Params:
        # * list
        # * index
        list_ = exec_context.symbol_table.get('list')
        index_ = exec_context.symbol_table.get('index')

        if not isinstance(list_, List):
            return RTResult().failure(
                RunTimeError(
                    self.pos_start, self.pos_end,
                    "first argument of built-in function 'get' must be a list.",
                    exec_context
                )
            )

        if not isinstance(index_, Number):
            return RTResult().failure(
                RunTimeError(
                    self.pos_start, self.pos_end,
                    "second argument of built-in function 'get' must be an int.",
                    exec_context
                )
            )
        index_ = index_.value

        try:
            return RTResult().success(list_[index_])
        except Exception:
            return RTResult().failure(RTIndexError(
                self.pos_start, self.pos_end,
                f'index {index_} out of range.',
                exec_context
            ))

    execute_get.arg_names = ['list', 'index']
    execute_get.optional_args = []
    execute_get.have_to_respect_args_number = True

    def execute_max(self, exec_context: Context):
        """Calculates the max value of a list"""
        # Params:
        # * value
        # Optional params:
        # * ignore_not_num (default False)
        list_ = exec_context.symbol_table.get('list')
        if not isinstance(list_, List):
            return RTResult().failure(
                RunTimeError(
                    self.pos_start, self.pos_end,
                    "first argument of builtin function 'max' must be a list.",
                    exec_context
                )
            )
        ignore_not_num = exec_context.symbol_table.get('ignore_not_num')
        if ignore_not_num is None:
            ignore_not_num = Number.FALSE
        if not isinstance(ignore_not_num, Number):
            return RTResult().failure(
                RunTimeError(
                    self.pos_start, self.pos_end,
                    "second argument of builtin function 'max' must be a number.",
                    exec_context
                )
            )
        max_ = None
        for element in list_.elements:
            if isinstance(element, Number):
                max_ = element
                break
            else:
                if ignore_not_num.value == Number.FALSE.value:
                    return RTResult().failure(
                        RunTimeError(
                            self.pos_start, self.pos_end,
                            "first argument of builtin function 'max' must be a list containing only numbers. "
                            "You can execute the function with True as the second argument to avoid this error.",
                            exec_context
                        )
                    )
        if max_ is None:
            return RTResult().success(NoneValue())
        for element in list_.elements:
            if isinstance(element, Number):
                if element.value > max_.value:
                    max_ = element
            else:
                if ignore_not_num.value == Number.FALSE.value:
                    return RTResult().failure(
                        RunTimeError(
                            self.pos_start, self.pos_end,
                            "first argument of builtin function 'max' must be a list containing only numbers. "
                            "You can execute the function with True as the second argument to avoid this error.",
                            exec_context
                        )
                    )
        return RTResult().success(max_)

    execute_max.arg_names = ['list']
    execute_max.optional_args = ['ignore_not_num']
    execute_max.have_to_respect_args_number = True

    def execute_min(self, exec_context: Context):
        """Calculates the min value of a list"""
        # Params:
        # * value
        # Optional params:
        # * ignore_not_num (default False)
        list_ = exec_context.symbol_table.get('list')
        if not isinstance(list_, List):
            return RTResult().failure(
                RunTimeError(
                    self.pos_start, self.pos_end,
                    "first argument of builtin function 'min' must be a list.",
                    exec_context
                )
            )
        ignore_not_num = exec_context.symbol_table.get('ignore_not_num')
        if ignore_not_num is None:
            ignore_not_num = Number.FALSE
        if not isinstance(ignore_not_num, Number):
            return RTResult().failure(
                RunTimeError(
                    self.pos_start, self.pos_end,
                    "second argument of builtin function 'min' must be a number.",
                    exec_context
                )
            )
        min_ = None
        for element in list_.elements:
            if isinstance(element, Number):
                min_ = element
                break
            else:
                if ignore_not_num.value == Number.FALSE.value:
                    return RTResult().failure(
                        RunTimeError(
                            self.pos_start, self.pos_end,
                            "first argument of builtin function 'min' must be a list containing only numbers. "
                            "You can execute the function with True as the second argument to avoid this error.",
                            exec_context
                        )
                    )
        if min_ is None:
            return RTResult().success(NoneValue())
        for element in list_.elements:
            if isinstance(element, Number):
                if element.value < min_.value:
                    min_ = element
            else:
                if ignore_not_num.value == Number.FALSE.value:
                    return RTResult().failure(
                        RunTimeError(
                            self.pos_start, self.pos_end,
                            "first argument of builtin function 'min' must be a list containing only numbers. "
                            "You can execute the function with True as the second argument to avoid this error.",
                            exec_context
                        )
                    )
        return RTResult().success(min_)

    execute_min.arg_names = ['list']
    execute_min.optional_args = ['ignore_not_num']
    execute_min.have_to_respect_args_number = True

    def execute_sqrt(self, exec_context: Context):
        """Calculates square root of 'value'"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'sqrt' must be a number.",
                exec_context
            ))

        if not value.value >= 0:
            return RTResult().failure(RTArithmeticError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'sqrt' must be greater than (or equal to) 0.",
                exec_context
            ))

        sqrt = math.sqrt(value.value)
        return RTResult().success(Number(sqrt))

    execute_sqrt.arg_names = ['value']
    execute_sqrt.optional_args = []
    execute_sqrt.have_to_respect_args_number = True

    def execute_math_root(self, exec_context: Context):
        """Calculates ⁿ√value"""
        # Params:
        # * value
        # Optional params:
        # * n
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'math_root' must be a number.",
                exec_context
            ))

        if value.value < 0:
            return RTResult().failure(RTArithmeticError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'math_root' must be greater than (or equal to) 0.",
                exec_context
            ))

        n = exec_context.symbol_table.get('n')
        if n is None:
            n = Number(2)

        if not isinstance(n, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "second argument of built-in function 'math_root' must be a number.",
                exec_context
            ))

        value_to_return = Number(value.value ** (1 / n.value))

        return RTResult().success(value_to_return)

    execute_math_root.arg_names = ['value']
    execute_math_root.optional_args = ['n']
    execute_math_root.have_to_respect_args_number = True

    def execute_degrees(self, exec_context: Context):
        """Converts 'value' (radians) to degrees"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'degrees' must be a number (angle in radians).",
                exec_context
            ))
        degrees = math.degrees(value.value)
        return RTResult().success(Number(degrees))

    execute_degrees.arg_names = ['value']
    execute_degrees.optional_args = []
    execute_degrees.have_to_respect_args_number = True

    def execute_radians(self, exec_context: Context):
        """Converts 'value' (degrees) to radians"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'radians' must be a number (angle in degrees).",
                exec_context
            ))
        radians = math.radians(value.value)
        return RTResult().success(Number(radians))

    execute_radians.arg_names = ['value']
    execute_radians.optional_args = []
    execute_radians.have_to_respect_args_number = True

    def execute_sin(self, exec_context: Context):
        """Calculates sin('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'sin' must be a number (angle in radians).",
                exec_context
            ))
        sin = math.sin(value.value)
        return RTResult().success(Number(sin))

    execute_sin.arg_names = ['value']
    execute_sin.optional_args = []
    execute_sin.have_to_respect_args_number = True

    def execute_cos(self, exec_context: Context):
        """Calculates cos('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'cos' must be a number (angle in radians).",
                exec_context
            ))
        cos = math.cos(value.value)
        return RTResult().success(Number(cos))

    execute_cos.arg_names = ['value']
    execute_cos.optional_args = []
    execute_cos.have_to_respect_args_number = True

    def execute_tan(self, exec_context: Context):
        """Calculates tan('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'tan' must be a number (angle in radians).",
                exec_context
            ))
        tan = math.tan(value.value)
        return RTResult().success(Number(tan))

    execute_tan.arg_names = ['value']
    execute_tan.optional_args = []
    execute_tan.have_to_respect_args_number = True

    def execute_asin(self, exec_context: Context):
        """Calculates asin('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'asin' must be a number.",
                exec_context
            ))
        try:
            asin = math.asin(value.value)
        except ValueError:
            return RTResult().failure(RTArithmeticError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'asin' must be a number between -1 and 1.",
                exec_context
            ))
        return RTResult().success(Number(asin))

    execute_asin.arg_names = ['value']
    execute_asin.optional_args = []
    execute_asin.have_to_respect_args_number = True

    def execute_acos(self, exec_context: Context):
        """Calculates acos('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'acos' must be a number.",
                exec_context
            ))
        try:
            acos = math.acos(value.value)
        except ValueError:
            return RTResult().failure(RTArithmeticError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'acos' must be a number between -1 and 1.",
                exec_context
            ))
        return RTResult().success(Number(acos))

    execute_acos.arg_names = ['value']
    execute_acos.optional_args = []
    execute_acos.have_to_respect_args_number = True

    def execute_atan(self, exec_context: Context):
        """Calculates atan('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'atan' must be a number.",
                exec_context
            ))
        atan = math.atan(value.value)
        return RTResult().success(Number(atan))

    execute_atan.arg_names = ['value']
    execute_atan.optional_args = []
    execute_atan.have_to_respect_args_number = True

    def execute_exit(self, exec_context: Context):
        """Stops the Nougaro Interpreter"""
        # Optional params:
        # * code
        code = exec_context.symbol_table.get('code')
        if isinstance(code, Number) or isinstance(code, String):
            exit(code.value)
        exit()

    execute_exit.arg_names = []
    execute_exit.optional_args = ['code']
    execute_exit.have_to_respect_args_number = True

    def execute_type(self, exec_context: Context):
        """Get the type of 'value'"""
        # Params :
        # * value
        value_to_get_type = exec_context.symbol_table.get('value')
        return RTResult().success(String(value_to_get_type.type_))

    execute_type.arg_names = ['value']
    execute_type.optional_args = []
    execute_type.have_to_respect_args_number = True

    def execute_str(self, exec_context: Context):
        """Python 'str()'"""
        # Params :
        # * value
        result = RTResult()
        value = exec_context.symbol_table.get('value')
        str_value, error = value.to_str_()
        if error is not None:
            return error

        return result.success(str_value)

    execute_str.arg_names = ['value']
    execute_str.optional_args = []
    execute_str.have_to_respect_args_number = True

    def execute_int(self, exec_context: Context):
        """Python 'int()'"""
        # Params :
        # * value
        result = RTResult()
        value = exec_context.symbol_table.get('value')
        int_value, error = value.to_int_()
        if error is not None:
            return error

        return result.success(int_value)

    execute_int.arg_names = ['value']
    execute_int.optional_args = []
    execute_int.have_to_respect_args_number = True

    def execute_float(self, exec_context: Context):
        """Python 'float()'"""
        # Params :
        # * value
        result = RTResult()
        value = exec_context.symbol_table.get('value')
        float_value, error = value.to_float_()
        if error is not None:
            return error

        return result.success(float_value)

    execute_float.arg_names = ['value']
    execute_float.optional_args = []
    execute_float.have_to_respect_args_number = True

    def execute_list(self, exec_context: Context):
        """Python 'list()'"""
        # Params :
        # * value
        result = RTResult()
        value = exec_context.symbol_table.get('value')
        list_value, error = value.to_list_()
        if error is not None:
            return error

        return result.success(list_value)

    execute_list.arg_names = ['value']
    execute_list.optional_args = []
    execute_list.have_to_respect_args_number = True

    # ==================

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy


BuiltInFunction.VOID = BuiltInFunction('void')
BuiltInFunction.PRINT = BuiltInFunction('print')
BuiltInFunction.PRINT_RET = BuiltInFunction('print_ret')
BuiltInFunction.INPUT = BuiltInFunction('input')
BuiltInFunction.INPUT_INT = BuiltInFunction('input_int')
BuiltInFunction.CLEAR = BuiltInFunction('clear')

BuiltInFunction.IS_INT = BuiltInFunction('is_int')
BuiltInFunction.IS_FLOAT = BuiltInFunction('is_float')
BuiltInFunction.IS_STRING = BuiltInFunction('is_str')
BuiltInFunction.IS_LIST = BuiltInFunction('is_list')
BuiltInFunction.IS_FUNCTION = BuiltInFunction('is_func')
BuiltInFunction.IS_NONE = BuiltInFunction('is_none')
BuiltInFunction.TYPE = BuiltInFunction('type')
BuiltInFunction.INT = BuiltInFunction('int')
BuiltInFunction.FLOAT = BuiltInFunction('float')
BuiltInFunction.STR = BuiltInFunction('str')
BuiltInFunction.LIST = BuiltInFunction('list')

BuiltInFunction.APPEND = BuiltInFunction('append')
BuiltInFunction.POP = BuiltInFunction('pop')
BuiltInFunction.EXTEND = BuiltInFunction('extend')
BuiltInFunction.GET = BuiltInFunction('get')
BuiltInFunction.MAX = BuiltInFunction('max')
BuiltInFunction.MIN = BuiltInFunction('min')

# Maths
BuiltInFunction.SQRT = BuiltInFunction('sqrt')
BuiltInFunction.MATH_ROOT = BuiltInFunction('math_root')
BuiltInFunction.RADIANS = BuiltInFunction('radians')
BuiltInFunction.DEGREES = BuiltInFunction('degrees')
BuiltInFunction.SIN = BuiltInFunction('sin')
BuiltInFunction.COS = BuiltInFunction('cos')
BuiltInFunction.TAN = BuiltInFunction('tan')
BuiltInFunction.ASIN = BuiltInFunction('asin')
BuiltInFunction.ACOS = BuiltInFunction('acos')
BuiltInFunction.ATAN = BuiltInFunction('atan')

BuiltInFunction.EXIT = BuiltInFunction('exit')


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

    def copy(self):
        copy = NoneValue(self.do_i_print)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy


# ##########
# ERRORS
# ##########
class RunTimeError(Error):
    def __init__(self, pos_start, pos_end, details, context: Context, rt_error: bool = True, error_name: str = ""):

        super().__init__(pos_start, pos_end, "RunTimeError" if rt_error else error_name, details)
        self.context = context

    def as_string(self):
        string_line = string_with_arrows(self.pos_start.file_txt, self.pos_start, self.pos_end)
        while string_line[0] in " ":
            # delete spaces at the start of the str.
            # Add chars after the space in the string after the "while string_line[0] in" to delete them.
            string_line = string_line[1:]
        result = self.generate_traceback()
        result += '\n \t' + string_line + '\n ' + f'{self.error_name} : {self.details}'
        return result

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx is not None:
            result = f' In file {pos.file_name}, line {pos.line_number + 1}, in {ctx.display_name} :\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return "Traceback (more recent call last) :\n" + result


class RTIndexError(RunTimeError):
    def __init__(self, pos_start, pos_end, details, context: Context):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="IndexError")
        self.context = context


class RTArithmeticError(RunTimeError):
    def __init__(self, pos_start, pos_end, details, context: Context):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="ArithmeticError")
        self.context = context


class NotDefinedError(RunTimeError):
    def __init__(self, pos_start, pos_end, details, context: Context):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="NotDefinedError")
        self.context = context


# ##########
# INTERPRETER
# ##########
class Interpreter:
    # this class does not have __init__ method
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    @staticmethod
    def no_visit_method(node, context: Context):
        print(context)
        print(f"NOUGARO INTERNAL ERROR : No visit_{type(node).__name__} method defined in nougaro.Interpreter.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/redirect1.html with all informations "
              f"above.")
        raise Exception(f'No visit_{type(node).__name__} method defined in nougaro.Interpreter.')

    @staticmethod
    def visit_NumberNode(node: NumberNode, context: Context):
        return RTResult().success(Number(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    @staticmethod
    def visit_StringNode(node: StringNode, context: Context):
        return RTResult().success(
            String(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_ListNode(self, node: ListNode, context: Context):
        result = RTResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(result.register(self.visit(element_node, context)))
            if result.error is not None:
                return result

        return result.success(List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_BinOpNode(self, node: BinOpNode, context: Context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error is not None:
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.error is not None:
            return res

        if node.op_token.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_token.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_token.type == TT_MUL:
            result, error = left.multiplied_by(right)
        elif node.op_token.type == TT_DIV:
            result, error = left.dived_by(right)
        elif node.op_token.type == TT_POW:
            result, error = left.powered_by(right)
        elif node.op_token.type == TT_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_token.type == TT_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_token.type == TT_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_token.type == TT_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_token.type == TT_LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_token.type == TT_GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_token.matches(TT_KEYWORD, 'and'):
            result, error = left.and_(right)
        elif node.op_token.matches(TT_KEYWORD, 'or'):
            result, error = left.or_(right)
        elif node.op_token.matches(TT_KEYWORD, 'xor'):
            result, error = left.excl_or(right)
        else:
            print(context)
            print("NOUGARO INTERNAL ERROR : Result is not defined after executing nougaro.Interpreter.visit_BinOpNode "
                  "because of an invalid token.\n"
                  "Please report this bug at https://jd-develop.github.io/nougaro/redirect1.html with the information "
                  "below")
            raise Exception("Result is not defined after executing nougaro.Interpreter.visit_BinOpNode")

        if error is not None:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node: UnaryOpNode, context: Context):
        result = RTResult()
        number = result.register(self.visit(node.node, context))
        if result.error is not None:
            return result

        error = None

        if node.op_token.type == TT_MINUS:
            number, error = number.multiplied_by(Number(-1))
        elif node.op_token.matches(TT_KEYWORD, 'not'):
            number, error = number.not_()

        if error is not None:
            return result.failure(error)
        else:
            return result.success(number.set_pos(node.pos_start, node.pos_end))

    @staticmethod
    def visit_VarAccessNode(node: VarAccessNode, context: Context):
        result = RTResult()
        var_name = node.var_name_token.value
        value = context.symbol_table.get(var_name)

        if value is None:
            return result.failure(
                NotDefinedError(
                    node.pos_start, node.pos_end, f'{var_name} is not defined.', context
                )
            )

        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return result.success(value)

    def visit_VarAssignNode(self, node: VarAssignNode, context: Context):
        result = RTResult()
        var_name = node.var_name_token.value
        value = result.register(self.visit(node.value_node, context))
        if result.error is not None:
            return result

        if var_name not in VARS_CANNOT_MODIFY:
            context.symbol_table.set(var_name, value)
        else:
            return result.failure(RunTimeError(node.pos_start, node.pos_end,
                                               f"can not create a variable with builtin name '{var_name}'.",
                                               value.context))
        return result.success(value)

    @staticmethod
    def visit_VarDeleteNode(node: VarDeleteNode, context: Context):
        result = RTResult()
        var_name = node.var_name_token.value

        if var_name not in context.symbol_table.symbols:
            return result.failure(NotDefinedError(node.pos_start, node.pos_end, f"{var_name} is not defined.", context))

        if var_name not in VARS_CANNOT_MODIFY:
            context.symbol_table.remove(var_name)
        else:
            return result.failure(RunTimeError(node.pos_start, node.pos_end,
                                               f"can not delete builtin variable '{var_name}'.",
                                               context))
        return result.success(NoneValue(False))

    def visit_IfNode(self, node: IfNode, context: Context):
        result = RTResult()
        for condition, expr, should_return_none in node.cases:
            condition_value = result.register(self.visit(condition, context))
            if result.error is not None:
                return result

            if condition_value.is_true():
                expr_value = result.register(self.visit(expr, context))
                if result.error is not None:
                    return result
                return result.success(NoneValue(False) if should_return_none else expr_value)

        if node.else_case is not None:
            expr, should_return_none = node.else_case
            else_value = result.register(self.visit(expr, context))
            if result.error is not None:
                return result
            return result.success(NoneValue(False) if should_return_none else else_value)

        return result.success(NoneValue(False))

    def visit_ForNode(self, node: ForNode, context: Context):
        result = RTResult()
        elements = []

        start_value = result.register(self.visit(node.start_value_node, context))
        if result.error is not None:
            return result

        end_value = result.register(self.visit(node.end_value_node, context))
        if result.error is not None:
            return result

        if node.step_value_node is not None:
            step_value = result.register(self.visit(node.step_value_node, context))
            if result.error is not None:
                return result
        else:
            step_value = Number(1)

        i = start_value.value
        condition = (lambda: i < end_value.value) if step_value.value >= 0 else (lambda: i > end_value.value)

        while condition():
            context.symbol_table.set(node.var_name_token.value, Number(i))
            i += step_value.value

            elements.append(result.register(self.visit(node.body_node, context)))
            if result.error is not None:
                return result

        return result.success(
            NoneValue(False) if node.should_return_none else
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_ForNodeList(self, node: ForNodeList, context: Context):
        result = RTResult()
        elements = []

        list_ = result.register(self.visit(node.list_node, context))
        if result.error is not None:
            return result

        if isinstance(list_, List):
            for i in list_.elements:
                context.symbol_table.set(node.var_name_token.value, i)
                elements.append(result.register(self.visit(node.body_node, context)))
                if result.error is not None:
                    return result
            return result.success(
                NoneValue(False) if node.should_return_none else
                List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
            )
        else:
            return result.failure(
                RunTimeError(node.list_node.pos_start, node.list_node.pos_end,
                             f"expected a list after 'in', but found {list_.type_}.",
                             context)
            )

    def visit_WhileNode(self, node: WhileNode, context: Context):
        result = RTResult()
        elements = []

        while True:
            condition = result.register(self.visit(node.condition_node, context))
            if result.error is not None:
                return result

            if not condition.is_true():
                break

            elements.append(result.register(self.visit(node.body_node, context)))
            if result.error is not None:
                return result

        return result.success(
            NoneValue(False) if node.should_return_none else
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    @staticmethod
    def visit_FuncDefNode(node: FuncDefNode, context: Context):
        result = RTResult()
        func_name = node.var_name_token.value if node.var_name_token is not None else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_tokens]
        func_value = Function(func_name, body_node, arg_names, node.should_return_none).set_context(context).set_pos(
            node.pos_start, node.pos_end
        )

        if node.var_name_token is not None:
            if func_name not in VARS_CANNOT_MODIFY:
                context.symbol_table.set(func_name, func_value)
            else:
                return result.failure(RunTimeError(node.pos_start, node.pos_end,
                                                   f"can not create a function with builtin name '{func_name}'.",
                                                   context))

        return result.success(func_value)

    def visit_CallNode(self, node: CallNode, context: Context):
        result = RTResult()
        args = []

        value_to_call = result.register(self.visit(node.node_to_call, context))
        if result.error is not None:
            return result
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        if isinstance(value_to_call, BaseFunction):
            # call the function
            for arg_node in node.arg_nodes:
                args.append(result.register(self.visit(arg_node, context)))
                if result.error is not None:
                    return result

            return_value = result.register(value_to_call.execute(args))
            if result.error is not None:
                return result
            return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
            return result.success(return_value)

        elif isinstance(value_to_call, List):
            # get the element at the index given
            if len(node.arg_nodes) == 1:
                index = result.register(self.visit(node.arg_nodes[0], context))
                if isinstance(index, Number):
                    index = index.value
                    try:
                        return_value = value_to_call[index]
                        return result.success(return_value)
                    except Exception:
                        return result.failure(
                            RTIndexError(
                                node.arg_nodes[0].pos_start, node.arg_nodes[0].pos_end,
                                f'list index {index} out of range.',
                                context
                            )
                        )
                else:
                    return result.failure(RunTimeError(
                        node.pos_start, node.pos_end,
                        f"indexes must be integers, not {index.type_}.",
                        context
                    ))
            elif len(node.arg_nodes) > 1:
                return_value = []
                for arg_node in node.arg_nodes:
                    index = result.register(self.visit(arg_node, context))
                    if isinstance(index, Number):
                        index = index.value
                        try:
                            return_value.append(value_to_call[index])
                        except Exception:
                            return result.failure(
                                RTIndexError(
                                    arg_node.pos_start, arg_node.pos_end,
                                    f'list index {index} out of range.',
                                    context
                                )
                            )
                    else:
                        return result.failure(RunTimeError(
                            arg_node.pos_start, arg_node.pos_end,
                            f"indexes must be integers, not {index.type_}.",
                            context
                        ))
                return result.success(List(return_value).set_context(context).set_pos(node.pos_start, node.pos_end))
            else:
                return result.failure(RunTimeError(
                    node.pos_start, node.pos_end,
                    f"please give at least one index.",
                    context
                ))
        else:
            return result.failure(RunTimeError(
                node.pos_start, node.pos_end,
                f"{value_to_call.type_} is not callable.",
                context
            ))

    def visit_AbsNode(self, node: AbsNode, context: Context):
        result = RTResult()

        value_to_abs = result.register(self.visit(node.node_to_abs, context))
        if result.error is not None:
            return result
        value_to_abs = value_to_abs.copy().set_pos(node.pos_start, node.pos_end)

        if not isinstance(value_to_abs, Number):
            return result.failure(RunTimeError(
                node.pos_start, node.pos_end,
                f"expected int or float, but found {value_to_abs.type_}.",
                context
            ))

        return_value = value_to_abs.abs_()
        return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return result.success(return_value)

    @staticmethod
    def visit_NoNode(node: NoNode, context: Context):
        return RTResult().success(NoneValue(do_i_print=False))


# ##########
# SYMBOL TABLE
# ##########
global_symbol_table = SymbolTable()
set_symbol_table(global_symbol_table, Number, NoneValue, BuiltInFunction)  # This function is in src.set_symbol_table


# ##########
# RUN
# ##########
def run(file_name, text, version: str = "not defined"):
    """Run the given code"""
    # set version in symbol table
    global_symbol_table.set("noug_version", String(version))

    # make tokens
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()
    if error is not None:
        return None, error
    # print(tokens)

    # make the abstract syntax tree (parser)
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error is not None:
        return None, ast.error

    # run the code (interpreter)
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)
    # print(context)
    # pprint.pprint(global_symbol_table)

    return result.value, result.error
