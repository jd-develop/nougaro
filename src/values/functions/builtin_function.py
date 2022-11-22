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
from src.values.functions.base_function import BaseFunction
from src.context import Context
from src.values.basevalues import *
from src.values.specific_values.number import *
from src.misc import CustomBuiltInFuncMethod, CustomBuiltInFuncMethodWithRunParam, is_keyword, does_tok_type_exist
from src.errors import RTFileNotFoundError, RTTypeError
# built-in python imports
from os import system as os_system, name as os_name
import os.path
import random
import sys


class BaseBuiltInFunction(BaseFunction):
    """Parent class for all the built-in function classes (even in modules)"""
    def __init__(self, name):
        super().__init__(name)
        self.type_ = 'built-in func'

    def __repr__(self):
        return f'<built-in function {self.name}>'

    def execute(self, args, interpreter_, run, exec_from: str = "<invalid>"):
        return RTResult().success(NoneValue(False))

    def no_visit_method(self, exec_context: Context):
        """Method called when the func name given through self.name is not defined"""
        print(exec_context)
        print(f"NOUGARO INTERNAL ERROR : No execute_{self.name} method defined in "
              f"src.values.functions.builtin_function.BaseBuiltInFunction.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with all informations "
              f"above.")
        raise Exception(f'No execute_{self.name} method defined in '
                        f'src.values.functions.builtin_function.BaseBuiltInFunction.')

    def copy(self):
        """Return a copy of self"""
        copy = BaseBuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy


class BuiltInFunction(BaseBuiltInFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args, interpreter_, run, exec_from: str = "<invalid>"):
        # execute a built-in function
        # create the result
        result = RTResult()

        # generate the context and change the symbol table for the context
        exec_context = self.generate_new_context()
        exec_context.symbol_table.set("__exec_from__", String(exec_from))
        exec_context.symbol_table.set("__actual_context__", String(self.name))

        # get the method name and the method
        method_name = f'execute_{self.name}'
        method: CustomBuiltInFuncMethod = getattr(self, method_name, self.no_visit_method)

        # populate arguments
        try:
            result.register(self.check_and_populate_args(method.param_names, args, exec_context,
                                                         optional_params=method.optional_params,
                                                         should_respect_args_number=method.should_respect_args_number))
        except Exception:  # it is self.no_visit_method :)
            method(exec_context)

        # if there is an error
        if result.should_return():
            return result

        # special built-in functions that needs the 'run' function (in nougaro.py) in their arguments
        if method_name in ['execute_run', 'execute_example', 'execute___test__']:
            method: CustomBuiltInFuncMethodWithRunParam  # re-define the custom type
            return_value = result.register(method(exec_context, run))

            # if there is any error
            if result.should_return():
                return result
            return result.success(return_value)

        try:
            # we try to execute the function
            return_value = result.register(method(exec_context))
        except TypeError:  # there is no `exec_context` parameter
            try:
                return_value = result.register(method())
            except TypeError:  # it only executes when coding
                return_value = result.register(method(exec_context))
        if result.should_return():  # check for any error
            return result
        # if all is OK, return what we should return
        return result.success(return_value)

    def no_visit_method(self, exec_context: Context):
        """Method called when the func name given through self.name is not defined"""
        print(exec_context)
        print(f"NOUGARO INTERNAL ERROR : No execute_{self.name} method defined in "
              f"src.values.functions.builtin_function.BuiltInFunction.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with all informations "
              f"above.")
        raise Exception(f'No execute_{self.name} method defined in '
                        f'src.values.functions.builtin_function.BuiltInFunction.')

    def copy(self):
        """Return a copy of self"""
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    # ==================
    # BUILD IN FUNCTIONS
    # ==================

    def execute_void(self):
        """Return nothing"""
        # No params.
        return RTResult().success(NoneValue(False))

    execute_void.param_names = []
    execute_void.optional_params = []
    execute_void.should_respect_args_number = False

    def execute_print(self, exec_context: Context):
        """Print 'value'"""
        # Optional params:
        # * value
        value = exec_context.symbol_table.get('value')
        if value is not None:  # if the value is defined
            try:
                print(value.to_str())
            except Exception:
                print(str(value))
        else:  # the value is not defined, we just print a new line like in regular print() python builtin func
            print()
        return RTResult().success(NoneValue(False))

    execute_print.param_names = []
    execute_print.optional_params = ["value"]
    execute_print.should_respect_args_number = True

    def execute_print_ret(self, exec_context: Context):
        """Print 'value' and returns 'value'"""
        # Optional params:
        # * value
        value = exec_context.symbol_table.get('value')
        if value is not None:  # if the value is defined
            try:
                print(value.to_str())
                return RTResult().success(String(value.to_str()))
            except Exception:
                print(str(value))
                return RTResult().success(String(str(value)))
        else:
            # the value is not defined, we just print a new line like in regular print() python builtin func and return
            # an empty str
            print()
            return RTResult().success(String(''))

    execute_print_ret.param_names = []
    execute_print_ret.optional_params = ['value']
    execute_print_ret.should_respect_args_number = True

    def execute_input(self, exec_context: Context):
        """Basic input (str)"""
        # Optional params:
        # * text_to_display
        text_to_display = exec_context.symbol_table.get('text_to_display')  # we get the text to display
        if isinstance(text_to_display, String) or isinstance(text_to_display, Number):
            text = input(text_to_display.value)
        else:  # other types and not defined
            text = input()
        return RTResult().success(String(text))

    execute_input.param_names = []
    execute_input.optional_params = ['text_to_display']
    execute_input.should_respect_args_number = True

    def execute_input_int(self, exec_context: Context):
        """Basic input (int). Repeat while entered value is not an int."""
        # Optional params:
        # * text_to_display
        text_to_display = exec_context.symbol_table.get('text_to_display')  # we get the text to display
        while True:
            if isinstance(text_to_display, String) or isinstance(text_to_display, Number):
                text = input(text_to_display.value)
            else:  # other types and not defined
                text = input()

            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer. Try again :")
        return RTResult().success(Number(number))

    execute_input_int.param_names = []
    execute_input_int.optional_params = ['text_to_display']
    execute_input_int.should_respect_args_number = True

    def execute_input_num(self, exec_context: Context):
        """Basic input (int or float). Repeat while entered value is not a num."""
        # Optional params:
        # * text_to_display
        text_to_display = exec_context.symbol_table.get('text_to_display')  # we get the text to display
        while True:
            if isinstance(text_to_display, String) or isinstance(text_to_display, Number):
                text = input(text_to_display.value)
            else:
                text = input()

            try:  # other types and not defined
                number = float(text)
                break
            except ValueError:
                print(f"'{text}' must be a number. Try again :")
        return RTResult().success(Number(number))

    execute_input_num.param_names = []
    execute_input_num.optional_params = ['text_to_display']
    execute_input_num.should_respect_args_number = True

    def execute_clear(self):
        """Clear the screen"""
        # No params.
        # depends on the os
        # if windows -> 'cls'
        # if Linux or MacOS -> 'clear'
        # TODO: find more OSes to include here OR find another way to clear the screen
        os_system('cls' if (os_name.lower() == "nt" or os_name.lower().startswith("windows")) else 'clear')
        return RTResult().success(NoneValue(False))

    execute_clear.param_names = []
    execute_clear.optional_params = []
    execute_clear.should_respect_args_number = False

    def execute_is_int(self, exec_context: Context):
        """Check if 'value' is an integer"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        is_number = isinstance(value, Number)  # we check if the value is a number
        if is_number:
            if value.type_ == 'int':  # then we check if the number is an integer
                is_int = True
            else:
                is_int = False
        else:
            is_int = False
        # TRUE and FALSE are defined in src/values/specific_values/number.py
        return RTResult().success(TRUE if is_int else FALSE)

    execute_is_int.param_names = ['value']
    execute_is_int.optional_params = []
    execute_is_int.should_respect_args_number = True

    def execute_is_float(self, exec_context: Context):
        """Check if 'value' is a float"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        is_number = isinstance(value, Number)  # we check if the value is a number
        if is_number:
            if value.type_ == 'float':  # then we check if the number is a float
                is_float = True
            else:
                is_float = False
        else:
            is_float = False
        # TRUE and FALSE are defined in src/values/specific_values/number.py
        return RTResult().success(TRUE if is_float else FALSE)

    execute_is_float.param_names = ['value']
    execute_is_float.optional_params = []
    execute_is_float.should_respect_args_number = True

    def execute_is_num(self, exec_context: Context):
        """Check if 'value' is an int or a float"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')  # we get the value
        is_number = isinstance(value, Number)  # we check if the value is a number
        # TRUE and FALSE are defined in src/values/specific_values/number.py
        return RTResult().success(TRUE if is_number else FALSE)

    execute_is_num.param_names = ['value']
    execute_is_num.optional_params = []
    execute_is_num.should_respect_args_number = True

    def execute_is_list(self, exec_context: Context):
        """Check if 'value' is a List"""
        # Params:
        # * value
        is_list = isinstance(exec_context.symbol_table.get('value'), List)  # we get the value and check if it is a list
        # TRUE and FALSE are defined in src/values/specific_values/number.py
        return RTResult().success(TRUE if is_list else FALSE)

    execute_is_list.param_names = ['value']
    execute_is_list.optional_params = []
    execute_is_list.should_respect_args_number = True

    def execute_is_str(self, exec_context: Context):
        """Check if 'value' is a String"""
        # Params:
        # * value
        is_str = isinstance(exec_context.symbol_table.get('value'), String)  # we get the value and check if it is a str
        # TRUE and FALSE are defined in src/values/specific_values/number.py
        return RTResult().success(TRUE if is_str else FALSE)

    execute_is_str.param_names = ['value']
    execute_is_str.optional_params = []
    execute_is_str.should_respect_args_number = True

    def execute_is_func(self, exec_context: Context):
        """Check if 'value' is a BaseFunction"""
        # Params:
        # * value
        is_func = isinstance(exec_context.symbol_table.get('value'), BaseFunction)  # we get the value and check if it
        #                                                                             is a function
        # TRUE and FALSE are defined in src/values/specific_values/number.py
        return RTResult().success(TRUE if is_func else FALSE)

    execute_is_func.param_names = ['value']
    execute_is_func.optional_params = []
    execute_is_func.should_respect_args_number = True

    def execute_is_none(self, exec_context: Context):
        """Check if 'value' is a NoneValue"""
        # Params:
        # * value
        # we get the value and check if it is None
        is_none = isinstance(exec_context.symbol_table.get('value'), NoneValue)
        # TRUE and FALSE are defined in src/values/specific_values/number.py
        return RTResult().success(TRUE if is_none else FALSE)

    execute_is_none.param_names = ['value']
    execute_is_none.optional_params = []
    execute_is_none.should_respect_args_number = True

    def execute_append(self, exec_context: Context):
        """Append 'value' to 'list'"""
        # Params:
        # * list
        # * value
        # we get list and value
        list_ = exec_context.symbol_table.get('list')
        value = exec_context.symbol_table.get('value')

        if not isinstance(list_, List):  # we check if the list is a list
            return RTResult().failure(RTTypeError(
                list_.pos_start, list_.pos_end,
                "first argument of built-in function 'append' must be a list.",
                exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_append"
            ))

        list_.elements.append(value)  # we append the element to the list (changes in the symbol table too)
        return RTResult().success(list_)

    execute_append.param_names = ['list', 'value']
    execute_append.optional_params = []
    execute_append.should_respect_args_number = True

    def execute_pop(self, exec_context: Context):
        """Remove element at 'index' from 'list'"""
        # Params:
        # * list
        # Optional params:
        # * index
        # we get the list and the index
        list_ = exec_context.symbol_table.get('list')
        index = exec_context.symbol_table.get('index')

        if not isinstance(list_, List):  # we check if the list is a list
            return RTResult().failure(RTTypeError(
                list_.pos_start, list_.pos_end,
                "first argument of built-in function 'pop' must be a list.",
                exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_pop"
            ))

        if index is None:
            index = Number(-1)
        if not isinstance(index, Number):  # we check if the index is a number
            return RTResult().failure(RTTypeError(
                index.pos_start, index.pos_end,
                "second argument of built-in function 'pop' must be a number.",
                exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_pop"
            ))

        try:  # we try to pop the element
            list_.elements.pop(index.value)
        except Exception:  # except if the index is out of range
            return RTResult().failure(RTIndexError(
                list_.pos_start, index.pos_end,
                f'pop index {index.value} out of range.',
                exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_pop"
            ))
        return RTResult().success(list_)

    execute_pop.param_names = ['list']
    execute_pop.optional_params = ['index']
    execute_pop.should_respect_args_number = True

    def execute_insert(self, exec_context: Context):
        """Remove element at 'index' from 'list'"""
        # Params:
        # * list
        # * value
        # * index
        # we get all we need
        list_ = exec_context.symbol_table.get('list')
        value = exec_context.symbol_table.get('value')
        index = exec_context.symbol_table.get('index')

        # we check if everything ok
        if not isinstance(list_, List):
            return RTResult().failure(RTTypeError(
                list_.pos_start, list_.pos_end,
                "first argument of built-in function 'insert' must be a list.",
                exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_insert"
            ))

        if index is None:
            index = Number(len(list_.elements))

        if not isinstance(index, Number):
            return RTResult().failure(RTTypeError(
                index.pos_start, index.pos_end,
                "third argument of built-in function 'insert' must be a number.",
                exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_insert"
            ))

        # if everything ok, we insert the element to the list at the right index
        list_.elements.insert(index.value, value)
        return RTResult().success(list_)

    execute_insert.param_names = ['list', 'value']
    execute_insert.optional_params = ['index']
    execute_insert.should_respect_args_number = True

    def execute_extend(self, exec_context: Context):
        """Extend list 'list1' with the elements of 'list2'"""
        # Params:
        # * list1
        # * list2
        # Optional params:
        # * delete_duplicates
        # we get our arguments
        list1 = exec_context.symbol_table.get('list1')
        list2 = exec_context.symbol_table.get('list2')
        delete_duplicates = exec_context.symbol_table.get('delete_duplicates')

        # we check the types
        if not isinstance(list1, List):
            return RTResult().failure(RTTypeError(
                list1.pos_start, list1.pos_end,
                "first argument of built-in function 'extend' must be a list.",
                exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_extend"
            ))

        if not isinstance(list2, List):
            return RTResult().failure(RTTypeError(
                list2.pos_start, list2.pos_end,
                "second argument of built-in function 'extend' must be a list.",
                exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_extend"
            ))

        # if delete_duplicates is defined
        if delete_duplicates is not None:
            if not isinstance(delete_duplicates, Number):
                return RTResult().failure(RTTypeError(
                    list2.pos_start, list2.pos_end,
                    "third argument of built-in function 'extend' must be a number.",
                    exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_extend"
                ))
            if delete_duplicates.value != FALSE.value:  # we have to delete duplicates
                list1_e = list1.elements
                list2_e = list2.elements
                final_list = list1_e.copy()  # we append all the elements of the first list to the final one
                for e in list2_e:
                    can_append = True
                    for e1 in list1_e:
                        # very slow thing : for each element of a list we have to check all the other one ones
                        # TODO: find another way to do that (instead of this for loop) (extend > delete_duplicates)
                        equal, error = e.get_comparison_eq(e1)
                        if error is not None:  # there is an error, there are not the same
                            continue
                        if equal is not None:  # there is no error
                            if equal.value == TRUE.value:  # there are equals, so duplicates
                                can_append = False
                    if can_append:  # if not duplicate, we append the element to the final list
                        final_list.append(e)
                return RTResult().success(List(final_list))

        list1.elements.extend(list2.elements)  # we finally extend
        return RTResult().success(list1)

    execute_extend.param_names = ['list1', 'list2']
    execute_extend.optional_params = ['delete_duplicates']
    execute_extend.should_respect_args_number = True

    def execute_get(self, exec_context: Context):
        # Params:
        # * list
        # * index
        # we get the list and the index
        list_ = exec_context.symbol_table.get('list')
        index_ = exec_context.symbol_table.get('index')

        if not isinstance(list_, List):  # we check if the list is a list
            return RTResult().failure(
                RTTypeError(
                    list_.pos_start, list_.pos_end,
                    "first argument of built-in function 'get' must be a list.",
                    exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_get"
                )
            )

        if not isinstance(index_, Number):  # we check if the index is a number
            return RTResult().failure(
                RTTypeError(
                    index_.pos_start, index_.pos_end,
                    "second argument of built-in function 'get' must be an int.",
                    exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_get"
                )
            )

        try:
            return RTResult().success(list_[index_.value])  # we return the element at the index
        except Exception:  # except if the index is out of range
            return RTResult().failure(RTIndexError(
                list_.pos_start, index_.pos_end,
                f'list index {index_.value} out of range.',
                exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_get"
            ))

    execute_get.param_names = ['list', 'index']
    execute_get.optional_params = []
    execute_get.should_respect_args_number = True

    def execute_replace(self, exec_context: Context):
        """Replace an element in a list by another"""
        # Params:
        # * list
        # * index
        # * value
        # we get our args
        list_ = exec_context.symbol_table.get("list")
        index_ = exec_context.symbol_table.get('index')
        value = exec_context.symbol_table.get('value')

        # we check the values
        if not isinstance(list_, List):
            return RTResult().failure(
                RTTypeError(
                    list_.pos_start, list_.pos_end,
                    "first argument of built-in function 'replace' must be a list.",
                    exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_replace"
                )
            )

        if not isinstance(index_, Number):
            return RTResult().failure(
                RTTypeError(
                    index_.pos_start, index_.pos_end,
                    "second argument of built-in function 'replace' must be an int.",
                    exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_replace"
                )
            )

        # everything ok : we replace the element
        try:
            list_.elements[index_.value] = value
        except IndexError:  # except if the index is out of range
            return RTResult().failure(RTIndexError(
                list_.pos_start, index_.pos_end,
                f'list index {index_.value} out of range.',
                exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_replace"
            ))

        return RTResult().success(list_)

    execute_replace.param_names = ['list', 'index', 'value']
    execute_replace.optional_params = []
    execute_replace.should_respect_args_number = True

    def execute_max(self, exec_context: Context):
        """Calculates the max value of a list"""
        # Params:
        # * value
        # Optional params:
        # * ignore_not_num (default False)

        # first we get the list
        list_ = exec_context.symbol_table.get('list')
        if not isinstance(list_, List):
            return RTResult().failure(
                RTTypeError(
                    list_.pos_start, list_.pos_end,
                    "first argument of builtin function 'max' must be a list.",
                    exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_max"
                )
            )

        # then we get "ignore_not_num"
        ignore_not_num = exec_context.symbol_table.get('ignore_not_num')
        if ignore_not_num is None:
            ignore_not_num = FALSE
        if not isinstance(ignore_not_num, Number):
            return RTResult().failure(
                RTTypeError(
                    ignore_not_num.pos_start, ignore_not_num.pos_end,
                    "second argument of builtin function 'max' must be a number.",
                    exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_max"
                )
            )

        # then we check if the list is good
        if ignore_not_num.value == FALSE.value:
            if any(not isinstance(e, Number) for e in list_.elements):
                return RTResult().failure(
                    RTTypeError(
                        list_.pos_start, list_.pos_end,
                        "first argument of builtin function 'max' must be a list containing only numbers. "
                        "You can execute the function with True as the second argument to avoid this error.",
                        exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_max"
                    )
                )

        # we transform our list
        list_ = [e.value for e in list_.elements if isinstance(e, Number)]

        if len(list_) == 0:
            return RTResult().success(NoneValue())

        max_ = max(list_)
        return RTResult().success(Number(max_))

    execute_max.param_names = ['list']
    execute_max.optional_params = ['ignore_not_num']
    execute_max.should_respect_args_number = True

    def execute_min(self, exec_context: Context):
        """Calculates the min value of a list"""
        # Params:
        # * value
        # Optional params:
        # * ignore_not_num (default False)

        # first we get the list
        list_ = exec_context.symbol_table.get('list')
        if not isinstance(list_, List):
            return RTResult().failure(
                RTTypeError(
                    list_.pos_start, list_.pos_end,
                    "first argument of builtin function 'min' must be a list.",
                    exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_min"
                )
            )

        # then we get "ignore_not_num"
        ignore_not_num = exec_context.symbol_table.get('ignore_not_num')
        if ignore_not_num is None:
            ignore_not_num = FALSE
        if not isinstance(ignore_not_num, Number):
            return RTResult().failure(
                RTTypeError(
                    ignore_not_num.pos_start, ignore_not_num.pos_end,
                    "second argument of builtin function 'min' must be a number.",
                    exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_min"
                )
            )

        # then we check if the list is good
        if ignore_not_num.value == FALSE.value:
            if any(not isinstance(e, Number) for e in list_.elements):
                return RTResult().failure(
                    RTTypeError(
                        list_.pos_start, list_.pos_end,
                        "first argument of builtin function 'min' must be a list containing only numbers. "
                        "You can execute the function with True as the second argument to avoid this error.",
                        exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_min"
                    )
                )

        # we transform our list
        list_ = [e.value for e in list_.elements if isinstance(e, Number)]

        if len(list_) == 0:
            return RTResult().success(NoneValue())

        max_ = min(list_)
        return RTResult().success(Number(max_))

    execute_min.param_names = ['list']
    execute_min.optional_params = ['ignore_not_num']
    execute_min.should_respect_args_number = True

    def execute_split(self, exec_context: Context):
        """Splits a str into a list."""
        # Optional params:
        # * char
        # we get our args
        str_ = exec_context.symbol_table.get('str')
        char = exec_context.symbol_table.get('char')

        # we check the types
        if not isinstance(str_, String):
            return RTResult().failure(
                RTTypeError(
                    self.pos_start, self.pos_end,
                    "first argument of builtin function 'split' must be a str.",
                    exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_split"
                )
            )
        if char is None or isinstance(char, NoneValue):
            char = String(' ')  # if there is no split char given, we split at the spaces
        if not isinstance(char, String):
            return RTResult().failure(
                RTTypeError(
                    self.pos_start, self.pos_end,
                    "second argument of builtin function 'split' must be a str or None.",
                    exec_context, "src.values.functions.builtin_function.BuiltInFunction.execute_split"
                )
            )
        # we split and make the list that we return
        split_res = str_.value.split(char.value)
        new_list = []
        for e in split_res:
            new_list.append(String(e))
        final_list = List(new_list)

        return RTResult().success(final_list)

    execute_split.param_names = ['str']
    execute_split.optional_params = ['char']
    execute_split.should_respect_args_number = True

    def execute_exit(self, exec_context: Context):
        """Stops the Nougaro Interpreter"""
        # Optional params:
        # * code
        code = exec_context.symbol_table.get('code')
        if isinstance(code, Number) or isinstance(code, String):
            sys.exit(code.value)  # !!!!!!!!!!!!!!! ALWAYS USE sys.exit() INSTEAD OF exit() OR quit() !!!!!!!!!!!!!!!
        sys.exit()

    execute_exit.param_names = []
    execute_exit.optional_params = ['code']
    execute_exit.should_respect_args_number = True

    def execute_type(self, exec_context: Context):
        """Get the type of 'value'"""
        # Params :
        # * value
        value_to_get_type = exec_context.symbol_table.get('value')  # we get the value
        return RTResult().success(String(value_to_get_type.type_))  # we return its type

    execute_type.param_names = ['value']
    execute_type.optional_params = []
    execute_type.should_respect_args_number = True

    def execute_str(self, exec_context: Context):
        """Python 'str()'"""
        # Params :
        # * value
        result = RTResult()
        value = exec_context.symbol_table.get('value')  # we get the value
        str_value, error = value.to_str_()  # we convert
        if error is not None:
            return error  # error is already an RTResult in convert methods in all Value classes

        return result.success(str_value)

    execute_str.param_names = ['value']
    execute_str.optional_params = []
    execute_str.should_respect_args_number = True

    def execute_int(self, exec_context: Context):
        """Python 'int()'"""
        # Params :
        # * value
        result = RTResult()
        value = exec_context.symbol_table.get('value')  # we get the value
        int_value, error = value.to_int_()  # we convert
        if error is not None:
            return error  # error is already an RTResult in convert methods in all Value classes

        return result.success(int_value)

    execute_int.param_names = ['value']
    execute_int.optional_params = []
    execute_int.should_respect_args_number = True

    def execute_float(self, exec_context: Context):
        """Python 'float()'"""
        # Params :
        # * value
        result = RTResult()
        value = exec_context.symbol_table.get('value')  # we get the value
        float_value, error = value.to_float_()  # we convert
        if error is not None:
            return error  # error is already an RTResult in convert methods in all Value classes

        return result.success(float_value)

    execute_float.param_names = ['value']
    execute_float.optional_params = []
    execute_float.should_respect_args_number = True

    def execute_list(self, exec_context: Context):
        """Python 'list()'"""
        # Params :
        # * value
        result = RTResult()
        value = exec_context.symbol_table.get('value')  # we get the value
        list_value, error = value.to_list_()  # we convert
        if error is not None:
            return error  # error is already an RTResult in convert methods in all Value classes

        return result.success(list_value)

    execute_list.param_names = ['value']
    execute_list.optional_params = []
    execute_list.should_respect_args_number = True

    def execute_len(self, exec_ctx: Context):
        """Returns the length of a list or a str"""
        # Params :
        # * list
        value_ = exec_ctx.symbol_table.get('value')  # we get the value

        # we check if the value is a list or a str
        if not isinstance(value_, List) and not isinstance(value_, String):
            return RTResult().failure(RTTypeError(
                value_.pos_start, value_.pos_end,
                "first argument of built-in function 'len' must be a list or a str.",
                exec_ctx, "src.values.functions.builtin_function.BuiltInFunction.execute_len"
            ))

        if isinstance(value_, List):
            return RTResult().success(Number(len(value_.elements)))
        else:
            return RTResult().success(Number(len(value_.value)))

    execute_len.param_names = ['value']
    execute_len.optional_params = []
    execute_len.should_respect_args_number = True

    def execute_rickroll(self):
        """Hum... You haven't seen anything. Close the doc please. Right now."""  # Close this file too. RIGHT NOW !
        # no params
        import webbrowser
        webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ", new=2)
        return RTResult().success(String("I think you've been rickrolled..."))

    execute_rickroll.param_names = []
    execute_rickroll.optional_params = []
    execute_rickroll.should_respect_args_number = False

    def execute_run(self, exec_ctx: Context, run):
        """Run code from another file. Param 'run' is the 'run' function in nougaro.py"""
        # Params :
        # * file_name
        file_name = exec_ctx.symbol_table.get("file_name")  # we get the file name

        if not isinstance(file_name, String):  # we check if the file name's a str
            return RTResult().failure(RTTypeError(
                file_name.pos_start, file_name.pos_end,
                "first argument of built-in function 'run' must be a str.",
                exec_ctx, "src.values.functions.builtin_function.BuiltInFunction.execute_run"
            ))

        file_name = file_name.value

        try:  # we try to open the file
            with open(file_name, 'r+', encoding='UTF-8') as file:
                script = file.read()
                file.close()
        except FileNotFoundError:
            return RTResult().failure(RTFileNotFoundError(
                self.pos_start, self.pos_end,
                file_name,
                exec_ctx, "src.values.functions.builtin_function.BuiltInFunction.execute_run"
            ))
        except Exception as e:
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"failed to load script '{file_name}' due to internal error '{str(e.__class__.__name__)}: {str(e)}'.",
                exec_ctx, origin_file="src.values.function.builtin_function.BuiltInFunction.execute_run"
            ))

        # we run the script
        value, error = run(file_name, script, exec_from=f"{exec_ctx.display_name} from {exec_ctx.parent.display_name}",
                           actual_context=f"{exec_ctx.parent.display_name}")

        # we check for errors
        if error is not None:
            return RTResult().failure(error)

        return RTResult().success(value)

    execute_run.param_names = ["file_name"]
    execute_run.optional_params = []
    execute_run.should_respect_args_number = True

    def execute_example(self, exec_ctx: Context, run):
        """Run code from an example file. Param 'run' is the 'run' function in nougaro.py"""
        # Params :
        # * example_name
        example_name = exec_ctx.symbol_table.get("example_name")  # we get the example name
        if example_name is None:
            example_name = String("../example")

        if not isinstance(example_name, String):  # we check if it is a str
            return RTResult().failure(RTTypeError(
                example_name.pos_start, example_name.pos_end,
                "first argument of built-in function 'example' must be a str.",
                exec_ctx, "src.values.functions.builtin_function.BuiltInFunction.execute_example"
            ))

        return_example_value = exec_ctx.symbol_table.get("return_example_value")
        if return_example_value is None:
            return_example_value = FALSE

        if not isinstance(return_example_value, Number):
            return RTResult().failure(RTTypeError(
                return_example_value.pos_start, return_example_value.pos_end,
                "second argument of built-in function 'example' must be a number.",
                exec_ctx, "src.values.functions.builtin_function.BuiltInFunction.execute_example"
            ))

        return_example_value = bool(return_example_value.value)

        file_name = "examples/" + example_name.value + ".noug"  # we put the right extension

        try:  # we try to open the example file
            with open(file_name, 'r+', encoding='UTF-8') as file:
                script = file.read()
                file.close()
        except FileNotFoundError:
            return RTResult().failure(RTFileNotFoundError(
                self.pos_start, self.pos_end,
                file_name,
                exec_ctx, "src.values.functions.builtin_function.BuiltInFunction.execute_example"
            ))
        except Exception as e:
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"failed to load script '{file_name}' due to internal error '{str(e.__class__.__name__)}: {str(e)}'.",
                exec_ctx, origin_file="src.values.function.builtin_function.BuiltInFunction.execute_example"
            ))

        # then we execute the file
        value, error = run(file_name, script, exec_from=f"{exec_ctx.display_name} from {exec_ctx.parent.display_name}",
                           actual_context=f"{exec_ctx.parent.display_name}")

        if error is not None:  # we check for errors
            return RTResult().failure(error)

        if return_example_value:
            return RTResult().success(value)
        return RTResult().success(NoneValue(False))

    execute_example.param_names = []
    execute_example.optional_params = ["example_name", "return_example_value"]
    execute_example.should_respect_args_number = True

    def execute_system_call(self, exec_ctx: Context):
        """System call. e.g. system_call('ls') lists the directory on bash."""
        # Params :
        # * cmd
        cmd = exec_ctx.symbol_table.get("cmd")  # we get the command
        if not isinstance(cmd, String):  # we check if it is a string
            return RTResult().failure(RTTypeError(
                cmd.pos_start, cmd.pos_end,
                f"first argument of builtin function 'system_call' must be a str.",
                exec_ctx, "src.values.functions.builtin_function.BuiltInFunction.execute_system_call"
            ))

        try:  # we execute the command
            to_return_value = os_system(str(cmd.value))
            return RTResult().success(String(to_return_value))
        except Exception as e:
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"failed to call '{cmd}' due to internal error '{str(e.__class__.__name__)}: {str(e)}'.",
                exec_ctx, origin_file="src.values.function.builtin_function.BuiltInFunction.execute_system_call"
            ))

    execute_system_call.param_names = ["cmd"]
    execute_system_call.optional_params = []
    execute_system_call.should_respect_args_number = True

    def execute_lower(self, exec_ctx: Context):
        """Return lower-cased string. e.g. lower('NOUGARO') returns 'nougaro'."""
        # Params :
        # * value
        value = exec_ctx.symbol_table.get("value")  # we get the value
        if not isinstance(value, String):  # we check if it is a string
            return RTResult().failure(RTTypeError(
                value.pos_start, value.pos_end,
                f"first argument of builtin function 'lower' must be a str.",
                exec_ctx, "src.values.functions.builtin_function.BuiltInFunction.execute_lower"
            ))
        return RTResult().success(String(value.value.lower()))  # we return the lower str

    execute_lower.param_names = ["value"]
    execute_lower.optional_params = []
    execute_lower.should_respect_args_number = True

    def execute_upper(self, exec_ctx: Context):
        """Return upper-cased string. e.g. upper('nougaro') returns 'NOUGARO'."""
        # Params :
        # * value
        value = exec_ctx.symbol_table.get("value")  # we get the value
        if not isinstance(value, String):  # we check if it is a string
            return RTResult().failure(RTTypeError(
                value.pos_start, value.pos_end,
                f"first argument of builtin function 'upper' must be a str.",
                exec_ctx, "src.values.functions.builtin_function.BuiltInFunction.execute_upper"
            ))
        return RTResult().success(String(value.value.upper()))  # we return the upper str

    execute_upper.param_names = ["value"]
    execute_upper.optional_params = []
    execute_upper.should_respect_args_number = True

    def execute_nougaro(self, exec_ctx: Context):
        """Open a random song of Claude Nougaro. If argument 'song' is filled, open this song (if in database)."""
        # Optional params :
        # * song
        song = exec_ctx.symbol_table.get("song")  # we get the song name
        songs = {
            "Toulouse": "https://www.youtube.com/watch?v=wehrXJTA3vI",
            "Armstrong": "https://www.youtube.com/watch?v=Dkqsh0kkjFw",
            "Bidonville": "https://www.youtube.com/watch?v=sh6jpbxjFKY",
            "Tu verras": "https://www.youtube.com/watch?v=rK3r-AqlNjU",
        }  # PR if you want to add more songs :)
        if song is None:  # if the song is not given, we pick up a random one
            import webbrowser
            song = random.choice(list(songs.keys()))
            webbrowser.open(songs[song], new=2)
            return RTResult().success(String(song))
        if not isinstance(song, String):  # we check if the song is a str
            return RTResult().failure(RTTypeError(
                song.pos_start, song.pos_end,
                f"first argument of builtin function 'nougaro' must be a str.",
                exec_ctx, "src.values.functions.builtin_function.BuiltInFunction.execute_nougaro"
            ))

        if song.value == "help":  # help message
            return RTResult().success(String(f"The available songs are: {', '.join(list(songs.keys()))}"))

        import webbrowser
        try:
            webbrowser.open(songs[song.value], new=2)  # we open the song in the web browser
            return RTResult().success(NoneValue(False))
        except KeyError:
            return RTResult().failure(RunTimeError(
                song.pos_start, song.pos_end,
                f"'{song.value}' is not a song in the actual database. Available songs: "
                f"{', '.join(list(songs.keys()))}",
                exec_ctx, origin_file="src.values.function.builtin_function.BuiltInFunction.execute_nougaro"
            ))

    execute_nougaro.param_names = []
    execute_nougaro.optional_params = ["song"]
    execute_nougaro.should_respect_args_number = True

    def execute___gpl__(self, exec_ctx: Context):
        """Open or print the GNU GPL 3.0."""
        # Optional params :
        # * print_in_term

        print_in_term = exec_ctx.symbol_table.get("print_in_term")  # we get 'print_in_term' value
        if print_in_term is None:  # if print_in_term is None, we put it false
            print_in_term = FALSE

        if not isinstance(print_in_term, Number):  # we check if it is a number
            return RTResult().failure(RTTypeError(
                print_in_term.pos_start, print_in_term.pos_end,
                f"first argument of builtin function '__gpl__' must be an int.",
                exec_ctx, "src.values.functions.builtin_function.BuiltInFunction.execute___gpl__"
            ))

        if not os.path.exists("LICENSE"):  # the GPL3 file is not found
            print("A problem occurred while opening or printing the license.\n"
                  "You can read the license online by following this link :\n"
                  "https://www.gnu.org/licenses/gpl-3.0.txt")
            return RTResult().success(NoneValue(False))

        if print_in_term.is_true():  # we print the GPL3 in the terminal
            with open("LICENSE", 'r+') as license_file:
                print(license_file.read())
                license_file.close()
                return RTResult().success(NoneValue(False))
        else:  # we open the GPL3 in the default system app
            import platform
            system = platform.system()
            if system == "Darwin":  # macOS
                import subprocess

                subprocess.call(('open', "LICENSE"))
            elif system == 'Windows':  # Windows
                print("Make sure to select a *text editor/reader* (like notepad or n++) in the list that will pop :)")
                os.startfile(os.path.realpath("LICENSE"))
            elif system == "Linux":  # Linux
                import subprocess

                subprocess.call(('xdg-open', "LICENSE"))
            else:
                print(f"<built-in function __gpl__> said:\n"
                      f"Sorry, your OS is not recognized. (platform.system() is '{system}')\n"
                      f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html\n"
                      f"In your report, please copy this error message.\n"
                      f"To read the license, you can use __gpl__(False) or read it online."
                      f"To read the license online, follow this link:\n"
                      f"https://www.gnu.org/licenses/gpl-3.0.txt")
            return RTResult().success(NoneValue(False))

    execute___gpl__.param_names = []
    execute___gpl__.optional_params = ["print_in_term"]
    execute___gpl__.should_respect_args_number = True

    def execute___is_keyword__(self, exec_ctx: Context):
        """Check if the word is a nougaro keyword."""
        # Params :
        # * word

        # we get the word
        word = exec_ctx.symbol_table.get("word")
        if not isinstance(word, String):  # we check if it is a string
            return RTResult().failure(RTTypeError(
                word.pos_start, word.pos_end,
                f"first argument of builtin function '__is_keyword__' must be a str.",
                exec_ctx, "src.values.functions.builtin_function.BuiltInFunction.execute___is_keyword__"
            ))
        result = RTResult()
        # then we return if this is a keyword or not.
        return result.success(TRUE) if is_keyword(word.value) else result.success(FALSE)

    execute___is_keyword__.param_names = ["word"]
    execute___is_keyword__.optional_params = []
    execute___is_keyword__.should_respect_args_number = True

    def execute___is_valid_token_type__(self, exec_ctx: Context):
        """Check if the type is a nougaro token type."""
        # Params :
        # * type

        # we get the type to check
        type_ = exec_ctx.symbol_table.get("type")
        if not isinstance(type_, String):  # we check if it is a string
            return RTResult().failure(RTTypeError(
                type_.pos_start, type_.pos_end,
                f"first argument of builtin function '__is_valid_token_type__' must be a str.",
                exec_ctx, "src.values.functions.builtin_function.BuiltInFunction.execute___is_valid_token_type__"
            ))
        result = RTResult()
        # then we return if this is a valid tok type or not.
        return result.success(TRUE) if does_tok_type_exist(type_.value) else result.success(FALSE)

    execute___is_valid_token_type__.param_names = ["type"]
    execute___is_valid_token_type__.optional_params = []
    execute___is_valid_token_type__.should_respect_args_number = True

    def execute___test__(self, exec_ctx: Context, run):
        """Execute the test file."""
        # no params
        exec_ctx.symbol_table.set("file_name", String("test_file.noug"))
        return self.execute_run(exec_ctx, run)

    execute___test__.param_names = []
    execute___test__.optional_params = []
    execute___test__.should_respect_args_number = True

    def execute_ord(self, exec_ctx: Context):
        """like python ord"""
        # params:
        # * chr
        chr_ = exec_ctx.symbol_table.get("chr")  # we get the char
        if not isinstance(chr_, String):  # we check if it is a string
            return RTResult().failure(RTTypeError(
                chr_.pos_start, chr_.pos_end,
                f"first argument of builtin function 'ord' must be a str.",
                exec_ctx, "src.values.functions.builtin_function.BuiltInFunction.execute_ord"
            ))

        if len(chr_.value) != 1:
            return RTResult().failure(RTTypeError(
                chr_.pos_start, chr_.pos_end,
                f"ord() expected a character, but string of length {len(chr_.value)} found.",
                exec_ctx, "src.values.functions.builtin_function.BuiltInFunction.execute_ord"
            ))

        try:
            return RTResult().success(Number(ord(chr_.to_str())))
        except Exception as e:
            return RTResult().failure(
                RunTimeError(
                    self.pos_start, self.pos_end,
                    f'Python error: {e.__class__.__name__}: {e}',
                    exec_ctx, origin_file="src.values.functions.builtin_function.BuiltInFunction.execute_ord"
                )
            )

    execute_ord.param_names = ["chr"]
    execute_ord.optional_params = []
    execute_ord.should_respect_args_number = True

    def execute_chr(self, exec_ctx: Context):
        """like python chr"""
        # params:
        # * ord
        ord_ = exec_ctx.symbol_table.get("ord")  # we get the char
        if not isinstance(ord_, Number):  # we check if it is a string
            return RTResult().failure(RTTypeError(
                ord_.pos_start, ord_.pos_end,
                f"first argument of builtin function 'chr' must be an int.",
                exec_ctx, "src.values.functions.builtin_function.BuiltInFunction.execute_chr"
            ))

        if not ord_.is_int():
            return RTResult().failure(RTTypeError(
                ord_.pos_start, ord_.pos_end,
                f"first argument of builtin function 'chr' must be an int.",
                exec_ctx, "src.values.functions.builtin_function.BuiltInFunction.execute_chr"
            ))

        try:
            return RTResult().success(String(chr(ord_.value)))
        except Exception as e:
            return RTResult().failure(
                RunTimeError(
                    self.pos_start, self.pos_end,
                    f'Python error: {e.__class__.__name__}: {e}',
                    exec_ctx, origin_file="src.values.functions.builtin_function.BuiltInFunction.execute_chr"
                )
            )

    execute_chr.param_names = ["ord"]
    execute_chr.optional_params = []
    execute_chr.should_respect_args_number = True

    # ==================
