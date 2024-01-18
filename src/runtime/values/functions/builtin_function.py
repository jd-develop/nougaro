#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# Future import
from __future__ import annotations
# nougaro modules imports
from src.runtime.values.functions.base_builtin_func import BaseBuiltInFunction
from src.runtime.values.functions.base_function import BaseFunction
from src.runtime.context import Context
from src.runtime.values.basevalues.basevalues import *
from src.runtime.values.number_constants import *
from src.misc import *
from src.errors.errors import *
from src.runtime.values.tools.py2noug import py2noug, noug2py
# built-in python imports
from os import system as os_system
import os.path
import random
import sys
import subprocess
from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
    from src.runtime.interpreter import Interpreter


class BuiltInFunction(BaseBuiltInFunction):
    def __init__(self, name: str, call_with_module_context: bool = False):
        super().__init__(name, call_with_module_context)
        self.cli_args = []

    def execute(self, args: list[Value], interpreter_: type[Interpreter], run: RunFunction, noug_dir: str,
                exec_from: str = "<invalid>", use_context: Context | None = None, cli_args: list[String] | None = None,
                work_dir: str | None = None) -> RTResult:
        # execute a built-in function
        # create the result
        result = RTResult()

        # generate the context and change the symbol table for the context
        exec_ctx = self.generate_new_context()
        assert exec_ctx.symbol_table is not None
        exec_ctx.symbol_table.set("__exec_from__", String(exec_from))
        exec_ctx.symbol_table.set("__actual_context__", String(self.name))
        if cli_args is None:
            self.cli_args = []
            exec_ctx.symbol_table.set("__args__", List([]))
        else:
            self.cli_args = cli_args.copy()
            new_cli_args: list[Value] = list(map(nice_str_from_idk, cli_args))
            exec_ctx.symbol_table.set("__args__", List(new_cli_args))

        # get the method name and the method
        try:
            method_dict: BuiltinFunctionDict = self.builtin_functions[self.name]
        except KeyError:
            self.no_visit_method(exec_ctx)
            return result
        method = method_dict["function"]

        # populate arguments
        result.register(self.check_and_populate_args(
            method_dict["param_names"], args, exec_ctx,
            optional_params=method_dict["optional_params"],
            should_respect_args_number=method_dict["should_respect_args_number"]
        ))

        # if there is an error
        if result.should_return():
            return result

        # special built-in functions that needs the 'run' function (in nougaro.py) in their arguments
        if method_dict["run_noug_dir_work_dir"]:
            return_value = result.register(method(self, exec_ctx, run, noug_dir, work_dir))

            # if there is any error
            if result.should_return():
                return result
            assert return_value is not None
            return result.success(return_value)

        # special built-in functions that needs the 'noug_dir' value
        if method_dict["noug_dir"]:
            return_value = result.register(method(self, exec_ctx, noug_dir))

            # if there is any error
            if result.should_return() or return_value is None:
                return result
            return result.success(return_value)

        try:
            # we try to execute the function
            return_value = result.register(method(self, exec_ctx))
        except TypeError:  # there is no `exec_ctx` parameter
            try:
                return_value = result.register(method(self))
            except TypeError:  # it only executes when coding
                return_value = result.register(method(self, exec_ctx))
        if result.should_return() or return_value is None:  # check for any error
            return result
        # if all is OK, return what we should return
        return result.success(return_value)

    def no_visit_method(self, exec_ctx: Context):
        """Method called when the func name given through self.name is not defined"""
        print(exec_ctx)
        print(f"NOUGARO INTERNAL ERROR: No execute_{self.name} method defined in "
              f"src.runtime.values.functions.builtin_function.BuiltInFunction.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with all informations "
              f"above.")
        raise Exception(f'No execute_{self.name} method defined in '
                        f'src.runtime.values.functions.builtin_function.BuiltInFunction.')

    def copy(self):
        """Return a copy of self"""
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.attributes = self.attributes.copy()
        return copy

    builtin_functions: dict[str, BuiltinFunctionDict] = {}

    # ==================
    # BUILT-IN FUNCTIONS
    # ==================

    def execute_void(self):
        """Return nothing"""
        # No params.
        return RTResult().success(NoneValue(False))

    builtin_functions["void"] = {
        "function": execute_void,
        "param_names": [],
        "optional_params": [],
        "should_respect_args_number": False,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }
    
    def execute_print(self, exec_ctx: Context):
        """Print 'value'"""
        # Optional params:
        # * value
        assert exec_ctx.symbol_table is not None
        value = exec_ctx.symbol_table.getf('value')
        if value is not None:  # if the value is defined
            try:
                print(value.to_python_str())
            except AttributeError:
                print(str(value))
        else:  # the value is not defined, we just print a new line like in regular print() python builtin func
            print()
        return RTResult().success(NoneValue(False))

    builtin_functions["print"] = {
        "function": execute_print,
        "param_names": [],
        "optional_params": ["value"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_print_in_red(self, exec_ctx: Context):
        """Print 'value' in red"""
        # Optional params:
        # * value
        assert exec_ctx.symbol_table is not None
        value = exec_ctx.symbol_table.getf('value')
        if value is not None:  # if the value is defined
            try:
                print_in_red(value.to_python_str())
            except AttributeError:
                print_in_red(str(value))
        else:  # the value is not defined, we just print a new line like in regular print() python builtin func
            print_in_red()
        return RTResult().success(NoneValue(False))

    builtin_functions["print_in_red"] = {
        "function": execute_print_in_red,
        "param_names": [],
        "optional_params": ["value"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_print_ret(self, exec_ctx: Context):
        """Print 'value' and returns 'value'"""
        # Optional params:
        # * value
        assert exec_ctx.symbol_table is not None
        value = exec_ctx.symbol_table.getf('value')
        if value is not None:  # if the value is defined
            try:
                print(value.to_python_str())
                return RTResult().success(String(value.to_python_str()))
            except AttributeError:
                print(str(value))
                return RTResult().success(String(str(value)))
        else:
            # the value is not defined, we just print a new line like in regular print() python builtin func and return
            # an empty str
            print()
            return RTResult().success(String(''))

    builtin_functions["print_ret"] = {
        "function": execute_print_ret,
        "param_names": [],
        "optional_params": ["value"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_print_in_red_ret(self, exec_ctx: Context):
        """Print 'value' and returns 'value'"""
        # Optional params:
        # * value
        assert exec_ctx.symbol_table is not None
        value = exec_ctx.symbol_table.getf('value')
        easter_egg = exec_ctx.symbol_table.getf('easteregg?')
        if value is not None:  # if the value is defined
            try:
                print_in_red(value.to_python_str())
                if easter_egg is not None and value.to_python_str() == "Is there an easter egg in this program? That " \
                                                                       "would be so cool!":
                    if isinstance(easter_egg, String) and easter_egg.value == "thanks":
                        print("You’re welcome :)")
                    return RTResult().success(String("Here you go!"))
                return RTResult().success(String(value.to_python_str()))
            except AttributeError:
                print_in_red(str(value))
                return RTResult().success(String(str(value)))
        else:
            # the value is not defined, we just print a new line like in regular print() python builtin func and return
            # an empty str
            print_in_red()
            return RTResult().success(String(''))

    builtin_functions["print_in_red_ret"] = {
        "function": execute_print_in_red_ret,
        "param_names": [],
        "optional_params": ["value", "easteregg?"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_input(self, exec_ctx: Context):
        """Basic input (str)"""
        # Optional params:
        # * text_to_display
        assert exec_ctx.symbol_table is not None
        text_to_display = exec_ctx.symbol_table.getf('text_to_display')  # we get the text to display
        if isinstance(text_to_display, String) or isinstance(text_to_display, Number):
            text = input(text_to_display.value)
        else:  # other types and not defined
            text = input()
        return RTResult().success(String(text))

    builtin_functions["input"] = {
        "function": execute_input,
        "param_names": [],
        "optional_params": ["text_to_display"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_input_int(self, exec_ctx: Context):
        """Basic input (int). Repeat while entered value is not an int."""
        # Optional params:
        # * text_to_display
        assert exec_ctx.symbol_table is not None
        text_to_display = exec_ctx.symbol_table.getf('text_to_display')  # we get the text to display
        while True:
            if isinstance(text_to_display, String) or isinstance(text_to_display, Number):
                text = input(text_to_display.value)
            else:  # other types and not defined
                text = input()

            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer. Try again: ")
        return RTResult().success(Number(number))

    builtin_functions["input_int"] = {
        "function": execute_input_int,
        "param_names": [],
        "optional_params": ["text_to_display"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_input_num(self, exec_ctx: Context):
        """Basic input (int or float). Repeat while entered value is not a num."""
        # Optional params:
        # * text_to_display
        assert exec_ctx.symbol_table is not None
        text_to_display = exec_ctx.symbol_table.getf('text_to_display')  # we get the text to display
        while True:
            if isinstance(text_to_display, String) or isinstance(text_to_display, Number):
                text = input(text_to_display.value)
            else:
                text = input()

            try:  # other types and not defined
                number = float(text)
                break
            except ValueError:
                print(f"'{text}' must be a number. Try again: ")
        return RTResult().success(Number(number))
    
    builtin_functions["input_num"] = {
        "function": execute_input_num,
        "param_names": [],
        "optional_params": ["text_to_display"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_clear(self):
        """Clear the screen"""
        # No params.
        clear_screen()
        return RTResult().success(NoneValue(False))

    builtin_functions["clear"] = {
        "function": execute_clear,
        "param_names": [],
        "optional_params": [],
        "should_respect_args_number": False,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_is_int(self, exec_ctx: Context):
        """Check if 'value' is an integer"""
        # Params:
        # * value
        assert exec_ctx.symbol_table is not None
        value = exec_ctx.symbol_table.getf('value')  # we get the value
        is_number = isinstance(value, Number)  # we check if the value is a number
        if is_number:
            if value.type_ == 'int':  # then we check if the number is an integer
                is_int = True
            else:
                is_int = False
        else:
            is_int = False
        # TRUE and FALSE are defined in src/values/number_constants.py
        return RTResult().success(TRUE.copy() if is_int else FALSE.copy())

    builtin_functions["is_int"] = {
        "function": execute_is_int,
        "param_names": ["value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_is_float(self, exec_ctx: Context):
        """Check if 'value' is a float"""
        # Params:
        # * value
        assert exec_ctx.symbol_table is not None
        value = exec_ctx.symbol_table.getf('value')  # we get the value
        is_number = isinstance(value, Number)  # we check if the value is a number
        if is_number:
            if value.type_ == 'float':  # then we check if the number is a float
                is_float = True
            else:
                is_float = False
        else:
            is_float = False
        # TRUE and FALSE are defined in src/values/number_constants.py
        return RTResult().success(TRUE.copy() if is_float else FALSE.copy())

    builtin_functions["is_float"] = {
        "function": execute_is_float,
        "param_names": ["value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_is_num(self, exec_ctx: Context):
        """Check if 'value' is an int or a float"""
        # Params:
        # * value
        assert exec_ctx.symbol_table is not None
        value = exec_ctx.symbol_table.getf('value')  # we get the value
        is_number = isinstance(value, Number)  # we check if the value is a number
        # TRUE and FALSE are defined in src/values/number_constants.py
        return RTResult().success(TRUE.copy() if is_number else FALSE.copy())

    builtin_functions["is_num"] = {
        "function": execute_is_num,
        "param_names": ["value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_is_list(self, exec_ctx: Context):
        """Check if 'value' is a List"""
        # Params:
        # * value
        # we get the value and check if it is a list
        assert exec_ctx.symbol_table is not None
        is_list = isinstance(exec_ctx.symbol_table.getf('value'), List)
        # TRUE and FALSE are defined in src/values/number_constants.py
        return RTResult().success(TRUE.copy() if is_list else FALSE.copy())

    builtin_functions["is_list"] = {
        "function": execute_is_list,
        "param_names": ["value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_is_str(self, exec_ctx: Context):
        """Check if 'value' is a String"""
        # Params:
        # * value
        # we get the value and check if it is a str
        assert exec_ctx.symbol_table is not None
        is_str = isinstance(exec_ctx.symbol_table.getf('value'), String)
        # TRUE and FALSE are defined in src/values/number_constants.py
        return RTResult().success(TRUE.copy() if is_str else FALSE.copy())

    builtin_functions["is_str"] = {
        "function": execute_is_str,
        "param_names": ["value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_is_func(self, exec_ctx: Context):
        """Check if 'value' is a BaseFunction"""
        # Params:
        # * value
        assert exec_ctx.symbol_table is not None
        is_func = isinstance(exec_ctx.symbol_table.getf('value'), BaseFunction)  # we get the value and check if it
        #                                                                             is a function
        # TRUE and FALSE are defined in src/values/number_constants.py
        return RTResult().success(TRUE.copy() if is_func else FALSE.copy())

    builtin_functions["is_func"] = {
        "function": execute_is_func,
        "param_names": ["value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_is_none(self, exec_ctx: Context):
        """Check if 'value' is a NoneValue"""
        # Params:
        # * value
        # we get the value and check if it is None
        assert exec_ctx.symbol_table is not None
        is_none = isinstance(exec_ctx.symbol_table.getf('value'), NoneValue)
        # TRUE and FALSE are defined in src/values/number_constants.py
        return RTResult().success(TRUE.copy() if is_none else FALSE.copy())

    builtin_functions["is_none"] = {
        "function": execute_is_none,
        "param_names": ["value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_is_module(self, exec_ctx: Context):
        """Check if 'value' is a Module"""
        # Params:
        # * value
        # we get the value and check if it is a module
        assert exec_ctx.symbol_table is not None
        is_none = isinstance(exec_ctx.symbol_table.getf('value'), Module)
        # TRUE and FALSE are defined in src/values/number_constants.py
        return RTResult().success(TRUE.copy() if is_none else FALSE.copy())

    builtin_functions["is_module"] = {
        "function": execute_is_module,
        "param_names": ["value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_append(self, exec_ctx: Context):
        """Append 'value' to 'list'"""
        # Params:
        # * list
        # * value
        # we get list and value
        assert exec_ctx.symbol_table is not None
        list_ = exec_ctx.symbol_table.getf('list')
        value = exec_ctx.symbol_table.getf('value')

        if not isinstance(list_, List):  # we check if the list is a list
            assert list_ is not None
            assert list_.pos_start is not None
            assert list_.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                list_.pos_start, list_.pos_end, "first", "append", "list", list_,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_append"
            ))

        assert value is not None
        list_.elements.append(value)  # we append the element to the list (changes in the symbol table too)
        list_.update_should_print()
        return RTResult().success(list_)

    builtin_functions["append"] = {
        "function": execute_append,
        "param_names": ["list", "value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_pop(self, exec_ctx: Context):
        """Remove element at 'index' from 'list'"""
        # Params:
        # * list
        # Optional params:
        # * index
        # we get the list and the index
        assert exec_ctx.symbol_table is not None
        list_ = exec_ctx.symbol_table.getf('list')
        index = exec_ctx.symbol_table.getf('index')

        if not isinstance(list_, List):  # we check if the list is a list
            assert list_ is not None
            assert list_.pos_start is not None
            assert list_.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                list_.pos_start, list_.pos_end, "first", "pop", "list", list_,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_pop"
            ))

        if index is None:
            index = Number(-1)
        if not isinstance(index, Number) or not isinstance(index.value, int):  # we check if the index is an int
            assert index is not None
            assert index.pos_start is not None
            assert index.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                index.pos_start, index.pos_end, "second", "pop", "integer", index,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_pop"
            ))

        try:  # we try to pop the element
            element = list_.elements.pop(index.value)
            list_.update_should_print()
        except IndexError:  # except if the index is out of range
            if index.pos_end is not None:
                error_pos_start = list_.pos_start
                error_pos_end = index.pos_end
            else:
                error_pos_start = self.pos_start
                error_pos_end = self.pos_end
            assert error_pos_start is not None
            assert error_pos_end is not None
            return RTResult().failure(RTIndexError(
                error_pos_start, error_pos_end,
                f'pop index {index.value} out of range.',
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_pop"
            ))
        return RTResult().success(element)

    builtin_functions["pop"] = {
        "function": execute_pop,
        "param_names": ["list"],
        "optional_params": ["index"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_insert(self, exec_ctx: Context):
        """Remove element at 'index' from 'list'"""
        # Params:
        # * list
        # * value
        # * index
        # we get all we need
        assert exec_ctx.symbol_table is not None
        list_ = exec_ctx.symbol_table.getf('list')
        value = exec_ctx.symbol_table.getf('value')
        index = exec_ctx.symbol_table.getf('index')

        # we check if everything OK
        if not isinstance(list_, List):
            assert list_ is not None
            assert list_.pos_start is not None
            assert list_.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                list_.pos_start, list_.pos_end, "first", "insert", "list", list_,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_insert"
            ))

        if index is None:
            index = Number(len(list_.elements))

        if not isinstance(index, Number) or not isinstance(index.value, int):
            assert index.pos_start is not None
            assert index.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                index.pos_start, index.pos_end, "third", "insert", "integer", index,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_insert"
            ))

        # if everything OK, we insert the element to the list at the right index
        assert value is not None
        list_.elements.insert(index.value, value)
        list_.update_should_print()
        return RTResult().success(list_)

    builtin_functions["insert"] = {
        "function": execute_insert,
        "param_names": ["list", "value"],
        "optional_params": ["index"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_extend(self, exec_ctx: Context):
        """Extend list 'list1' with the elements of 'list2'"""
        # Params:
        # * list1
        # * list2
        # Optional params:
        # * delete_duplicates
        # we get our arguments
        assert exec_ctx.symbol_table is not None
        list1 = exec_ctx.symbol_table.getf('list1')
        list2 = exec_ctx.symbol_table.getf('list2')
        delete_duplicates = exec_ctx.symbol_table.getf('delete_duplicates')

        # we check the types
        if not isinstance(list1, List):
            assert list1 is not None
            assert list1.pos_start is not None
            assert list1.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                list1.pos_start, list1.pos_end, "first", "extend", "list", list1,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_extend"
            ))

        assert list2 is not None
        assert list2.pos_start is not None
        assert list2.pos_end is not None
        if not isinstance(list2, List):
            return RTResult().failure(RTTypeErrorF(
                list2.pos_start, list2.pos_end, "second", "extend", "list", list2,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_extend"
            ))

        # if delete_duplicates is defined
        if delete_duplicates is not None:
            if not isinstance(delete_duplicates, Number):
                return RTResult().failure(RTTypeErrorF(
                    list2.pos_start, list2.pos_end, "third", "extend", "number", delete_duplicates,
                    exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_extend"
                ))
            if delete_duplicates.is_true():  # we have to delete duplicates
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
        list1.update_should_print()
        return RTResult().success(list1)

    builtin_functions["extend"] = {
        "function": execute_extend,
        "param_names": ["list1", "list2"],
        "optional_params": ["delete_duplicates"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_get(self, exec_ctx: Context):
        # Params:
        # * list
        # * index
        # we get the list and the index
        assert exec_ctx.symbol_table is not None
        list_ = exec_ctx.symbol_table.getf('list')
        index_ = exec_ctx.symbol_table.getf('index')

        assert list_ is not None
        assert list_.pos_start is not None
        assert list_.pos_end is not None
        if not isinstance(list_, List):  # we check if the list is a list
            return RTResult().failure(RTTypeErrorF(
                list_.pos_start, list_.pos_end, "first", "get", "list", list_,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_get"
            ))

        assert index_ is not None
        assert index_.pos_start is not None
        assert index_.pos_end is not None
        if not isinstance(index_, Number) or not isinstance(index_.value, int):  # we check if the index is a number
            return RTResult().failure(RTTypeErrorF(
                index_.pos_start, index_.pos_end, "second", "get", "integer", index_,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_get"
            ))

        try:
            return RTResult().success(list_[index_.value])  # we return the element at the index
        except IndexError:  # except if the index is out of range
            return RTResult().failure(RTIndexError(
                list_.pos_start, index_.pos_end,
                f'list index {index_.value} out of range.',
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_get"
            ))
    
    builtin_functions["get"] = {
        "function": execute_get,
        "param_names": ["list", "index"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_replace(self, exec_ctx: Context):
        """Replace an element in a list by another"""
        # Params:
        # * list
        # * index
        # * value
        # we get our args
        assert exec_ctx.symbol_table is not None
        list_ = exec_ctx.symbol_table.getf("list")
        index_ = exec_ctx.symbol_table.getf('index')
        value = exec_ctx.symbol_table.getf('value')

        assert list_ is not None
        assert list_.pos_start is not None
        assert list_.pos_end is not None
        # we check the values
        if not isinstance(list_, List):
            return RTResult().failure(RTTypeErrorF(
                list_.pos_start, list_.pos_end, "first", "replace", "list", list_,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_replace"
            ))

        assert index_ is not None
        assert index_.pos_start is not None
        assert index_.pos_end is not None
        if not isinstance(index_, Number) or not isinstance(index_.value, int):
            return RTResult().failure(RTTypeErrorF(
                index_.pos_start, index_.pos_end, "second", "replace", "integer", index_,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_replace"
            ))

        assert value is not None
        # everything OK : we replace the element
        try:
            list_.elements[index_.value] = value
            list_.update_should_print()
        except IndexError:  # except if the index is out of range
            return RTResult().failure(RTIndexError(
                list_.pos_start, index_.pos_end,
                f'list index {index_.value} out of range.',
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_replace"
            ))

        return RTResult().success(list_)

    builtin_functions["replace"] = {
        "function": execute_replace,
        "param_names": ["list", "index", "value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_max(self, exec_ctx: Context):
        """Calculates the max value of a list"""
        # Params:
        # * value
        # Optional params:
        # * ignore_not_num (default False)

        # first we get the list
        assert exec_ctx.symbol_table is not None
        list_ = exec_ctx.symbol_table.getf('list')
        assert list_ is not None
        assert list_.pos_start is not None
        assert list_.pos_end is not None
        if not isinstance(list_, List):
            return RTResult().failure(RTTypeErrorF(
                list_.pos_start, list_.pos_end, "first", "max", "list", list_,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_max"
            ))

        # then we get "ignore_not_num"
        ignore_not_num = exec_ctx.symbol_table.getf('ignore_not_num')
        if ignore_not_num is None:
            ignore_not_num = FALSE.copy()
        if not isinstance(ignore_not_num, Number):
            assert ignore_not_num is not None
            assert ignore_not_num.pos_start is not None
            assert ignore_not_num.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                ignore_not_num.pos_start, ignore_not_num.pos_end, "second", "max", "number", ignore_not_num,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_max"
            ))

        # then we check if the list is good
        if ignore_not_num.is_false():
            if not all(isinstance(e, Number) for e in list_.elements):
                return RTResult().failure(RTTypeError(
                    list_.pos_start, list_.pos_end,
                    "first argument of builtin function `max` must be a list containing only numbers. "
                    "You can execute the function with True as the second argument to avoid this error.",
                    exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_max"
                ))

        # we transform our list
        list_ = [e.value for e in list_.elements if isinstance(e, Number)]

        if len(list_) == 0:
            return RTResult().success(NoneValue())

        max_ = max(list_)
        return RTResult().success(Number(max_))
    
    builtin_functions["max"] = {
        "function": execute_max,
        "param_names": ["list"],
        "optional_params": ["ignore_not_num"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_min(self, exec_ctx: Context):
        """Calculates the min value of a list"""
        # Params:
        # * value
        # Optional params:
        # * ignore_not_num (default False)

        # first we get the list
        assert exec_ctx.symbol_table is not None
        list_ = exec_ctx.symbol_table.getf('list')

        assert list_ is not None
        assert list_.pos_start is not None
        assert list_.pos_end is not None
        if not isinstance(list_, List):
            return RTResult().failure(RTTypeErrorF(
                list_.pos_start, list_.pos_end, "first", "min", "list", list_,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_min"
            ))

        # then we get "ignore_not_num"
        ignore_not_num = exec_ctx.symbol_table.getf('ignore_not_num')
        if ignore_not_num is None:
            ignore_not_num = FALSE.copy()
        if not isinstance(ignore_not_num, Number):
            assert ignore_not_num is not None
            assert ignore_not_num.pos_start is not None
            assert ignore_not_num.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                ignore_not_num.pos_start, ignore_not_num.pos_end, "second", "min", "number", ignore_not_num,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_min"
            ))

        # then we check if the list is good
        if ignore_not_num.is_false():
            if not all(isinstance(e, Number) for e in list_.elements):
                return RTResult().failure(RTTypeError(
                    list_.pos_start, list_.pos_end,
                    "first argument of builtin function `min` must be a list containing only numbers. "
                    "You can execute the function with True as the second argument to avoid this error.",
                    exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_min"
                ))

        # we transform our list
        list_ = [e.value for e in list_.elements if isinstance(e, Number)]

        if len(list_) == 0:
            return RTResult().success(NoneValue())

        max_ = min(list_)
        return RTResult().success(Number(max_))

    builtin_functions["min"] = {
        "function": execute_min,
        "param_names": ["list"],
        "optional_params": ["ignore_not_num"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_split(self, exec_ctx: Context):
        """Splits a str into a list."""
        # Optional params:
        # * char
        # we get our args
        assert exec_ctx.symbol_table is not None
        str_ = exec_ctx.symbol_table.getf('str')
        char = exec_ctx.symbol_table.getf('char')

        # we check the types
        if not isinstance(str_, String):
            assert str_ is not None
            assert str_.pos_start is not None
            assert str_.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                str_.pos_start, str_.pos_end, "first", "split", "str", str_,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_split"
            ))
        if char is None or isinstance(char, NoneValue):
            char = String(' ')  # if there is no split char given, we split at the spaces
        if not isinstance(char, String):
            assert char is not None
            assert char.pos_start is not None
            assert char .pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                char.pos_start, char.pos_end, "second", "split", "str", char,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_split",
                or_="None"
            ))
        # we split and make the list that we return
        split_res = str_.value.split(char.value)
        new_list: list[Value] = []
        for e in split_res:
            new_list.append(String(e))
        final_list = List(new_list)

        return RTResult().success(final_list)
    
    builtin_functions["split"] = {
        "function": execute_split,
        "param_names": ["str"],
        "optional_params": ["char"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_exit(self, exec_ctx: Context):
        """Stops the Nougaro Interpreter"""
        # Optional params:
        # * code
        assert exec_ctx.symbol_table is not None
        code = exec_ctx.symbol_table.getf('code')
        if isinstance(code, Number) or isinstance(code, String):
            if isinstance(code.value, int) or isinstance(code.value, str):
                sys.exit(code.value)  # !!!!!!!!!!!!!! ALWAYS USE sys.exit() INSTEAD OF exit() OR quit() !!!!!!!!!!!!!!!
        sys.exit()

    builtin_functions["exit"] = {
        "function": execute_exit,
        "param_names": [],
        "optional_params": ["code"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_type(self, exec_ctx: Context):
        """Get the type of 'value'"""
        # Params :
        # * value
        assert exec_ctx.symbol_table is not None
        value_to_get_type = exec_ctx.symbol_table.getf('value')  # we get the value
        assert value_to_get_type is not None
        return RTResult().success(String(value_to_get_type.type_))  # we return its type

    builtin_functions["type"] = {
        "function": execute_type,
        "param_names": ["value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_py_type(self, exec_ctx: Context):
        """Get the python type of 'value'"""
        # Params :
        # * value
        assert exec_ctx.symbol_table is not None
        value_to_get_type = exec_ctx.symbol_table.getf('value')  # we get the value
        return RTResult().success(String(str(type(value_to_get_type))))  # we return its python type

    builtin_functions["py_type"] = {
        "function": execute_py_type,
        "param_names": ["value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_str(self, exec_ctx: Context):
        """Python 'str()'"""
        # Params :
        # * value
        assert exec_ctx.symbol_table is not None
        value = exec_ctx.symbol_table.getf('value')  # we get the value
        assert value is not None
        str_value, error = value.to_str_()  # we convert
        if error is not None:
            return error  # error is already an RTResult in convert methods in all Value classes
        assert str_value is not None

        return RTResult().success(str_value)

    builtin_functions["str"] = {
        "function": execute_str,
        "param_names": ["value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_int(self, exec_ctx: Context):
        """Python 'int()'"""
        # Params :
        # * value
        assert exec_ctx.symbol_table is not None
        value = exec_ctx.symbol_table.getf('value')  # we get the value
        assert value is not None
        int_value, error = value.to_int_()  # we convert
        if error is not None:
            return error  # error is already an RTResult in convert methods in all Value classes
        assert int_value is not None

        return RTResult().success(int_value)

    builtin_functions["int"] = {
        "function": execute_int,
        "param_names": ["value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_float(self, exec_ctx: Context):
        """Python 'float()'"""
        # Params :
        # * value
        assert exec_ctx.symbol_table is not None
        value = exec_ctx.symbol_table.getf('value')  # we get the value
        assert value is not None
        float_value, error = value.to_float_()  # we convert
        if error is not None:
            return error  # error is already an RTResult in convert methods in all Value classes
        assert float_value is not None

        return RTResult().success(float_value)

    builtin_functions["float"] = {
        "function": execute_float,
        "param_names": ["value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_list(self, exec_ctx: Context):
        """Python 'list()'"""
        # Params :
        # * value
        assert exec_ctx.symbol_table is not None
        value = exec_ctx.symbol_table.getf('value')  # we get the value
        assert value is not None
        list_value, error = value.to_list_()  # we convert
        if error is not None:
            return error  # error is already an RTResult in convert methods in all Value classes
        assert list_value is not None

        return RTResult().success(list_value)

    builtin_functions["list"] = {
        "function": execute_list,
        "param_names": ["value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_len(self, exec_ctx: Context):
        """Returns the length of a list or a str"""
        # Params :
        # * list
        assert exec_ctx.symbol_table is not None
        value_ = exec_ctx.symbol_table.getf('value')  # we get the value

        # we check if the value is a list or a str
        if not isinstance(value_, List) and not isinstance(value_, String):
            assert value_ is not None
            assert value_.pos_start is not None
            assert value_.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                value_.pos_start, value_.pos_end, "first", "len", "list", value_,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_len", or_="str"
            ))

        if isinstance(value_, List):
            return RTResult().success(Number(len(value_.elements)))
        else:
            return RTResult().success(Number(len(value_.value)))

    builtin_functions["len"] = {
        "function": execute_len,
        "param_names": ["value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_rickroll(self):
        """Hum... You haven't seen anything"""
        # no params
        import webbrowser
        webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ", new=2)
        return RTResult().success(String("I think you've been rickrolled..."))

    builtin_functions["rickroll"] = {
        "function": execute_rickroll,
        "param_names": [],
        "optional_params": [],
        "should_respect_args_number": False,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_run(self, exec_ctx: Context, run: RunFunction, noug_dir: str, work_dir: str):
        """Run code from another file. Param 'run' is the 'run' function in nougaro.py"""
        # Params :
        # * file_name
        assert exec_ctx.symbol_table is not None
        file_name = exec_ctx.symbol_table.getf("file_name")  # we get the file name

        if not isinstance(file_name, String):  # we check if the file name's a str
            assert file_name is not None
            assert file_name.pos_start is not None
            assert file_name.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                file_name.pos_start, file_name.pos_end, "first", "run", "str", file_name,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_run"
            ))

        file_name = file_name.value

        assert self.pos_start is not None
        assert self.pos_end is not None
        try:  # we try to open the file
            with open(file_name, 'r+', encoding='UTF-8') as file:
                script = file.read()
                file.close()
        except FileNotFoundError:
            try:
                with open(os.path.abspath(noug_dir + '/' + file_name), 'r+', encoding='UTF-8') as file:
                    script = file.read()
                    file.close()
            except FileNotFoundError:
                return RTResult().failure(RTFileNotFoundError(
                    self.pos_start, self.pos_end,
                    file_name,
                    exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_run"
                ))
            except Exception as e:
                return RTResult().failure(RunTimeError(
                    self.pos_start, self.pos_end,
                    f"failed to load script '{file_name}' due to internal error '{str(e.__class__.__name__)}: {str(e)}'"
                    f".",
                    exec_ctx, origin_file="src.runtime.values.function.builtin_function.BuiltInFunction.execute_run"
                ))
        except Exception as e:
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"failed to load script '{file_name}' due to internal error '{str(e.__class__.__name__)}: {str(e)}'.",
                exec_ctx, origin_file="src.runtime.values.function.builtin_function.BuiltInFunction.execute_run"
            ))

        # we run the script
        assert exec_ctx.parent is not None
        value, error = run(
            file_name, script, noug_dir,
            exec_from=f"{exec_ctx.display_name} from {exec_ctx.parent.display_name}",
            actual_context=f"{exec_ctx.parent.display_name}",
            args=self.cli_args,
            work_dir=work_dir
        )

        # we check for errors
        if error is not None:
            return RTResult().failure(error)
        assert value is not None

        return RTResult().success(value)

    builtin_functions["run"] = {
        "function": execute_run,
        "param_names": ["file_name"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": True,
        "noug_dir": False
    }

    def execute_example(self, exec_ctx: Context, run: RunFunction, noug_dir: str, work_dir: str):
        """Run code from an example file. Param 'run' is the 'run' function in nougaro.py"""
        # Params :
        # * example_name
        assert exec_ctx.symbol_table is not None
        example_name = exec_ctx.symbol_table.getf("example_name")  # we get the example name
        if example_name is None:
            example_name = String("../example")

        if not isinstance(example_name, String):  # we check if it is a str
            assert example_name.pos_start is not None
            assert example_name.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                example_name.pos_start, example_name.pos_end, "first", "example", "str", example_name,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_example"
            ))

        return_example_value = exec_ctx.symbol_table.getf("return_example_value")
        if return_example_value is None:
            return_example_value = FALSE.copy()

        if not isinstance(return_example_value, Number):
            assert return_example_value.pos_start is not None
            assert return_example_value.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                return_example_value.pos_start, return_example_value.pos_end,
                "second", "example", "number", return_example_value,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_example"
            ))

        return_example_value = return_example_value.is_true()

        file_name = os.path.abspath(noug_dir + "/examples/" + example_name.value + ".noug")

        assert self.pos_start is not None
        assert self.pos_end is not None
        try:  # we try to open the example file
            with open(file_name, 'r+', encoding='UTF-8') as file:
                script = file.read()
                file.close()
        except FileNotFoundError:
            return RTResult().failure(RTFileNotFoundError(
                self.pos_start, self.pos_end,
                file_name,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_example"
            ))
        except Exception as e:
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"failed to load script '{file_name}' due to internal error '{str(e.__class__.__name__)}: {str(e)}'.",
                exec_ctx, origin_file="src.runtime.values.function.builtin_function.BuiltInFunction.execute_example"
            ))

        assert exec_ctx.parent is not None
        # then we execute the file
        value, error = run(
            file_name, script, noug_dir,
            exec_from=f"{exec_ctx.display_name} from {exec_ctx.parent.display_name}",
            actual_context=f"{exec_ctx.parent.display_name}",
            args=self.cli_args,
            work_dir=work_dir
        )

        if error is not None:  # we check for errors
            return RTResult().failure(error)
        assert value is not None

        if return_example_value:
            return RTResult().success(value)
        return RTResult().success(NoneValue(False))

    builtin_functions["example"] = {
        "function": execute_example,
        "param_names": [],
        "optional_params": ["example_name", "return_example_value"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": True,
        "noug_dir": False
    }

    def execute_system_call(self, exec_ctx: Context):
        """System call. e.g. system_call('ls') lists the directory on bash."""
        # Params :
        # * cmd
        assert exec_ctx.symbol_table is not None
        cmd = exec_ctx.symbol_table.getf("cmd")  # we get the command
        if not isinstance(cmd, String):  # we check if it is a string
            assert cmd is not None
            assert cmd.pos_start is not None
            assert cmd.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                cmd.pos_start, cmd.pos_end, "first", "system_call", "str", cmd,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_system_call"
            ))

        try:  # we execute the command
            to_return_value = os_system(str(cmd.value))
            return RTResult().success(String(str(to_return_value)))
        except Exception as e:
            assert self.pos_start is not None
            assert self.pos_end is not None
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"failed to call '{cmd}' due to internal error '{str(e.__class__.__name__)}: {str(e)}'.",
                exec_ctx, origin_file="src.runtime.values.function.builtin_function.BuiltInFunction.execute_system_call"
            ))

    builtin_functions["system_call"] = {
        "function": execute_system_call,
        "param_names": ["cmd"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_lower(self, exec_ctx: Context):
        """Return lower-cased string. e.g. lower('NOUGARO') returns 'nougaro'."""
        # Params :
        # * value
        assert exec_ctx.symbol_table is not None
        value = exec_ctx.symbol_table.getf("value")  # we get the value
        if not isinstance(value, String):  # we check if it is a string
            assert value is not None
            assert value.pos_start is not None
            assert value.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                value.pos_start, value.pos_end, "first", "lower", "str", value,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_lower"
            ))
        return RTResult().success(String(value.value.lower()))  # we return the lower str

    builtin_functions["lower"] = {
        "function": execute_lower,
        "param_names": ["value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_upper(self, exec_ctx: Context):
        """Return upper-cased string. e.g. upper('nougaro') returns 'NOUGARO'."""
        # Params :
        # * value
        assert exec_ctx.symbol_table is not None
        value = exec_ctx.symbol_table.getf("value")  # we get the value
        if not isinstance(value, String):  # we check if it is a string
            assert value is not None
            assert value.pos_start is not None
            assert value.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                value.pos_start, value.pos_end, "first", "upper", "str", value,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_upper"
            ))
        return RTResult().success(String(value.value.upper()))  # we return the upper str

    builtin_functions["upper"] = {
        "function": execute_upper,
        "param_names": ["value"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_nougaro(self, exec_ctx: Context):
        """Open a random song of Claude Nougaro. If argument 'song' is filled, open this song (if in database)."""
        # Optional params :
        # * song
        assert exec_ctx.symbol_table is not None
        song = exec_ctx.symbol_table.getf("song")  # we get the song name
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
            assert song.pos_start is not None
            assert song.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                song.pos_start, song.pos_end, "first", "nougaro", "str", song,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_nougaro"
            ))

        if song.value == "help":  # help message
            return RTResult().success(String(f"The available songs are: {', '.join(list(songs.keys()))}"))

        import webbrowser
        try:
            webbrowser.open(songs[song.value], new=2)  # we open the song in the web browser
            return RTResult().success(NoneValue(False))
        except KeyError:
            assert song.pos_start is not None
            assert song.pos_end is not None
            return RTResult().failure(RunTimeError(
                song.pos_start, song.pos_end,
                f"'{song.value}' is not a song in the actual database. Available songs: "
                f"{', '.join(list(songs.keys()))}",
                exec_ctx, origin_file="src.runtime.values.function.builtin_function.BuiltInFunction.execute_nougaro"
            ))

    builtin_functions["nougaro"] = {
        "function": execute_nougaro,
        "param_names": [],
        "optional_params": ["song"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute___gpl__(self, exec_ctx: Context, noug_dir: str):
        """Open or print the GNU GPL 3.0."""
        # Optional params :
        # * print_in_term

        assert exec_ctx.symbol_table is not None
        print_in_term = exec_ctx.symbol_table.getf("print_in_term")  # we get 'print_in_term' value
        if print_in_term is None:  # if print_in_term is None, we put it false
            print_in_term = FALSE.copy()

        if not isinstance(print_in_term, Number):  # we check if it is a number
            assert print_in_term.pos_start is not None
            assert print_in_term.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                print_in_term.pos_start, print_in_term.pos_end,
                "first", "__gpl__", "number", print_in_term,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute___gpl__"
            ))

        if not os.path.exists(os.path.abspath(noug_dir + "/LICENSE")):  # the GPL3 file is not found
            print("A problem occurred while opening or printing the license.\n"
                  "You can read the license online by following this link :\n"
                  "https://www.gnu.org/licenses/gpl-3.0.txt")
            return RTResult().success(NoneValue(False))

        if print_in_term.is_true():  # we print the GPL3 in the terminal
            with open(os.path.abspath(noug_dir + "/LICENSE"), 'r+') as license_file:
                print(license_file.read())
                license_file.close()
                return RTResult().success(NoneValue(False))
        else:  # we open the GPL3 in the default system app
            # todo: test on macOS and BSD
            # tested on Windows, Linux
            import platform
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(('open', os.path.abspath(noug_dir + "/LICENSE")))
            elif system == 'Windows':  # Windows
                print("Make sure to select a *text editor/reader* (like notepad or n++) in the list that will pop :)")
                os.startfile(os.path.realpath(noug_dir + "/LICENSE"))  # only on Windows # type: ignore
            elif system == "Linux":  # Linux
                subprocess.run(('xdg-open', os.path.abspath(noug_dir + "/LICENSE")))
            elif system == "FreeBSD" or system == "OpenBSD" or system.endswith("BSD"):
                text_editor = input("Enter the command of your text editor (example: vim, emacs, …) ")
                subprocess.run((text_editor, os.path.abspath(noug_dir + "/LICENSE")))
            else:
                print(f"<built-in function __gpl__> said:\n"
                      f"Sorry, your OS is not recognized. (platform.system() is '{system}')\n"
                      f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html\n"
                      f"In your report, please copy this error message.\n"
                      f"To read the license, you can use __gpl__(False) or read it online."
                      f"To read the license online, follow this link:\n"
                      f"https://www.gnu.org/licenses/gpl-3.0.txt")
                print("However, you can enter the command to open your text editor, the argument of the file will be "
                      "automatically added.")
                command = input("Enter the command of your text editor (example: vim, emacs, …): ")
                subprocess.run((command, os.path.abspath(noug_dir + "/LICENSE")))
            return RTResult().success(NoneValue(False))

    builtin_functions["__gpl__"] = {
        "function": execute___gpl__,
        "param_names": [],
        "optional_params": ["print_in_term"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": True
    }

    def execute___is_keyword__(self, exec_ctx: Context):
        """Check if the word is a nougaro keyword."""
        # Params :
        # * word

        # we get the word
        assert exec_ctx.symbol_table is not None
        word = exec_ctx.symbol_table.getf("word")
        if not isinstance(word, String):  # we check if it is a string
            assert word is not None
            assert word.pos_start is not None
            assert word.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                word.pos_start, word.pos_end, "first", "__is_keyword__", "str", word,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute___is_keyword__"
            ))
        result = RTResult()
        # then we return if this is a keyword or not.
        return result.success(TRUE.copy()) if is_keyword(word.value) else result.success(FALSE.copy())

    builtin_functions["__is_keyword__"] = {
        "function": execute___is_keyword__,
        "param_names": ["word"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute___is_valid_token_type__(self, exec_ctx: Context):
        """Check if the type is a nougaro token type."""
        # Params :
        # * type

        # we get the type to check
        assert exec_ctx.symbol_table is not None
        type_ = exec_ctx.symbol_table.getf("type")
        if not isinstance(type_, String):  # we check if it is a string
            assert type_ is not None
            assert type_.pos_start is not None
            assert type_.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                type_.pos_start, type_.pos_end, "first", "__is_valid_token_type__", "str", type_,
                exec_ctx,
                "src.runtime.values.functions.builtin_function.BuiltInFunction.execute___is_valid_token_type__"
            ))
        result = RTResult()
        # then we return if this is a valid tok type or not.
        return result.success(TRUE) if does_tok_type_exist(type_.value) else result.success(FALSE)

    builtin_functions["__is_valid_token_type__"] = {
        "function": execute___is_valid_token_type__,
        "param_names": ["type"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute___test__(self, exec_ctx: Context, run: RunFunction, noug_dir: str, work_dir: str):
        """Execute the test file."""
        # optional params:
        # * return
        assert exec_ctx.symbol_table is not None
        should_i_print_ok = exec_ctx.symbol_table.getf("print_OK")
        should_i_return = exec_ctx.symbol_table.getf("return")
        if should_i_print_ok is None:
            should_i_print_ok = FALSE.copy()
        if should_i_return is None:
            should_i_return = FALSE.copy()
        exec_ctx.symbol_table.set("file_name", String(os.path.abspath(noug_dir + "/tests/test_file.noug")))

        print("Please also run unittests if you want to build nougaro.")

        with open(os.path.abspath(noug_dir + "/config/SHOULD_TEST_PRINT_OK"), "w+") as should_i_print_ok_f:
            should_i_print_ok_f.write(str(int(should_i_print_ok.is_true())))

        if should_i_return.is_true():
            return self.execute_run(exec_ctx, run, noug_dir, work_dir)
        else:
            result = self.execute_run(exec_ctx, run, noug_dir, work_dir)
            if result.error is not None:
                return result
            return RTResult().success(NoneValue(False))

    builtin_functions["__test__"] = {
        "function": execute___test__,
        "param_names": [],
        "optional_params": ["print_OK", "return"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": True,
        "noug_dir": False
    }

    def execute_ord(self, exec_ctx: Context):
        """like python ord"""
        # params:
        # * chr
        assert exec_ctx.symbol_table is not None
        chr_ = exec_ctx.symbol_table.getf("chr")  # we get the char

        if not isinstance(chr_, String):  # we check if it is a string
            assert chr_ is not None
            assert chr_.pos_start is not None
            assert chr_.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                chr_.pos_start, chr_.pos_end, "first", "ord", "str", chr_,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_ord"
            ))

        if len(chr_.value) != 1:
            assert chr_.pos_start is not None
            assert chr_.pos_end is not None
            return RTResult().failure(RTTypeError(
                chr_.pos_start, chr_.pos_end,
                f"ord() expected a character, but string of length {len(chr_.value)} found.",
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_ord"
            ))

        try:
            return RTResult().success(Number(ord(chr_.to_python_str())))
        except Exception as e:
            assert self.pos_start is not None
            assert self.pos_end is not None
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f'Python error: {e.__class__.__name__}: {e}',
                exec_ctx, origin_file="src.runtime.values.functions.builtin_function.BuiltInFunction.execute_ord"
            ))

    builtin_functions["ord"] = {
        "function": execute_ord,
        "param_names": ["chr"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_chr(self, exec_ctx: Context):
        """like python chr"""
        # params:
        # * ord
        assert exec_ctx.symbol_table is not None
        ord_ = exec_ctx.symbol_table.getf("ord")  # we get the char

        assert ord_ is not None
        assert ord_.pos_start is not None
        assert ord_.pos_end is not None
        if not isinstance(ord_, Number):  # we check if it is a string
            return RTResult().failure(RTTypeErrorF(
                ord_.pos_start, ord_.pos_end, "first", "chr", "int", ord_,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_chr"
            ))

        if not isinstance(ord_.value, int):
            return RTResult().failure(RTTypeError(
                ord_.pos_start, ord_.pos_end,
                f"first argument of builtin function 'chr' must be an int.",
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_chr"
            ))

        try:
            return RTResult().success(String(chr(ord_.value)))
        except Exception as e:
            assert self.pos_start is not None
            assert self.pos_end is not None
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f'Python error: {e.__class__.__name__}: {e}',
                exec_ctx, origin_file="src.runtime.values.functions.builtin_function.BuiltInFunction.execute_chr"
            ))

    builtin_functions["chr"] = {
        "function": execute_chr,
        "param_names": ["ord"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute___how_many_lines_of_code__(self, exec_ctx: Context, noug_dir: str):
        """Return the number of lines of code in the Nougaro Interpreter"""
        assert exec_ctx.symbol_table is not None
        total = 0
        all_files: dict[str, int] = {}

        print_values = exec_ctx.symbol_table.getf("print_values")
        print_ = True
        if print_values:
            if isinstance(print_values, Number):
                if print_values.value == FALSE.value:
                    print_ = False
        if print_:
            print("Computing...")

        folders = [os.path.abspath(noug_dir + f) for f in [
            '/',
            '/lib_',
            '/src',
            '/src/errors',
            '/src/lexer',
            '/src/parser',
            *['/src/runtime' + g for g in ['', '/values', '/values/basevalues', '/values/functions', '/values/tools']]
        ]]
        for folder in folders:
            for file_dir in os.listdir(folder):
                is_python_or_noug_file = file_dir.endswith(".py") or file_dir.endswith(".noug")
                if file_dir != "example.noug" and is_python_or_noug_file:
                    with open(f"{folder}/{file_dir}", "r+", encoding="UTF-8") as file:
                        len_ = len(file.readlines())
                        file.close()
                    total += len_
                    if print_:
                        print(f"In file: {folder}/{file_dir}: {len_}")
                    all_files[f"{folder}/{file_dir}"] = len_

        if print_:
            all_files_items: list[tuple[str, int]] = list(all_files.items())
            all_files_sorted: list[tuple[str, int]] = sorted(all_files_items, key=lambda ele: ele[1], reverse=True)
            all_files: dict[str, int] = {key: val for key, val in all_files_sorted}
            top_keys = list(all_files.keys())[:6]
            top_values = [all_files[key] for key in top_keys]
            top_: dict[str, int] = {}
            for i, key in enumerate(top_keys):
                top_[key] = top_values[i]
            print(f"\nTop files:")
            for top_file in top_:
                print(f"{top_file}: {top_[top_file]}")
        return RTResult().success(Number(total))

    builtin_functions["__how_many_lines_of_code__"] = {
        "function": execute___how_many_lines_of_code__,
        "param_names": [],
        "optional_params": ["print_values"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": True
    }

    def execute_round(self, exec_ctx: Context):
        """Like python 'round'"""
        assert exec_ctx.symbol_table is not None
        number = exec_ctx.symbol_table.getf("number")
        n_digits = exec_ctx.symbol_table.getf("n_digits")

        if not isinstance(number, Number):
            assert number is not None
            assert number.pos_start is not None
            assert number.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                number.pos_start, number.pos_end, "first", "round", "number", number,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_round"
            ))

        number_: int | float = number.value
        if n_digits is None:
            return RTResult().success(Number(round(number_)))

        if not (isinstance(n_digits, Number) and isinstance(n_digits.value, int)):
            assert n_digits.pos_start is not None
            assert n_digits.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                n_digits.pos_start, n_digits.pos_end, "second", "round", "int", n_digits,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_round"
            ))

        return RTResult().success(Number(round(number_, n_digits.value)))

    builtin_functions["round"] = {
        "function": execute_round,
        "param_names": ["number"],
        "optional_params": ["n_digits"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }
    
    def execute_sort(self, exec_ctx: Context):
        """Like python’s sort()"""
        assert exec_ctx.symbol_table is not None
        result = RTResult()
        list_ = exec_ctx.symbol_table.getf("list_")
        mode = exec_ctx.symbol_table.getf("mode")
        
        if not isinstance(list_, List):
            assert list_ is not None
            assert list_.pos_start is not None
            assert list_.pos_end is not None
            return result.failure(RTTypeErrorF(
                list_.pos_start, list_.pos_end, "first", "sort", "list", list_,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_sort"
            ))
        if mode is None:
            mode = String("timsort").set_pos(self.pos_start, self.pos_end)
        if not isinstance(mode, String):
            assert mode.pos_start is not None
            assert mode.pos_end is not None
            return result.failure(RTTypeErrorF(
                mode.pos_start, mode.pos_end, "second", "sort", "str", mode,
                exec_ctx, "src.runtime.values.functions.builtin_function.BuiltInFunction.execute_sort"
            ))

        mode_noug = mode
        mode = mode_noug.value
        list_to_sort: list[Value] = list_.elements
        if mode == "timsort":  # default python sort algorithm
            try:
                sorted_ = sorted(list_to_sort, key=lambda val: noug2py(val, False))
            except TypeError as e:
                assert list_.pos_start is not None
                assert list_.pos_end is not None
                return result.failure(RTTypeError(
                    list_.pos_start, list_.pos_end,
                    str(e), exec_ctx,
                    origin_file="src.runtime.values.function.builtin_function.BuiltInFunction.execute_sort"
                ))
        elif mode == "stalin":  # stalin sort
            def get_comparison(
                    list_to_sort_: list[Value], index_: int
            ) -> tuple[Number, None] | tuple[None, RunTimeError]:
                if index_ + 1 < len(list_to_sort_):
                    comp, error_ = list_to_sort_[index_].get_comparison_gt(list_to_sort_[index_ + 1])
                    if error_ is not None:
                        return None, error_
                    else:
                        assert isinstance(comp, Number)
                else:
                    comp = FALSE.copy()
                return comp, None

            for i in range(len(list_to_sort)):
                if i == len(list_to_sort):
                    break

                comparison, error = get_comparison(list_to_sort, i)
                if error is not None:
                    return result.failure(error)
                
                assert comparison is not None

                while i + 1 < len(list_to_sort) and comparison.is_true():
                    list_to_sort.pop(i + 1)
                    comparison, error = get_comparison(list_to_sort, i)
                    if error is not None:
                        return result.failure(error)
                    assert comparison is not None

            sorted_ = list_to_sort  
        elif mode == "sleep":  # sleep sort
            # sleep sort was implemented by Mistera. Please refer to him if you have any questions about it, as I
            # completely don’t have any ideas of how tf asyncio works
            import asyncio

            sorted_: list[Value] = []
            list_to_sort_only_nums: list[int] = []
            for i in list_to_sort:
                assert i.pos_start is not None
                assert i.pos_end is not None
                if not isinstance(i, Number) or not isinstance(i.value, int):
                    return result.failure(RTTypeError(
                        i.pos_start, i.pos_end, 
                        f"sleep mode: expected list of int, but found {i.type_} inside the list.",
                        exec_ctx,
                        origin_file="src.runtime.values.function.builtin_function.BuiltInFunction.execute_sort"
                    ))
                if i.value < 0:
                    return result.failure(RTTypeError(
                        i.pos_start, i.pos_end,
                        f"sleep mode: expected list of positive integers, but found negative integer {i.value} inside "
                        f"the list.",
                        exec_ctx,
                        origin_file="src.runtime.values.function.builtin_function.BuiltInFunction.execute_sort"

                    ))
                list_to_sort_only_nums.append(i.value)

            async def execute_coroutine_list(_list: list[Coroutine[Any, Any, None]]):
                await asyncio.gather(*_list)

            async def wait_and_append(i_: int):
                nonlocal sorted_
                await asyncio.sleep(i_)
                sorted_.append(Number(i_))

            list_of_coroutines = [wait_and_append(i) for i in list_to_sort_only_nums]
            asyncio.run(execute_coroutine_list(list_of_coroutines))
        else:  # mode is none of the above
            assert mode_noug.pos_start is not None
            assert mode_noug.pos_end is not None
            return result.failure(RunTimeError(
                mode_noug.pos_start, mode_noug.pos_end,
                "this mode does not exist. Available modes:\n"
                "\t* 'timsort' (default),\n"
                "\t* 'stalin',"
                "\t* 'sleep'.",
                exec_ctx, origin_file="src.runtime.values.function.builtin_function.BuiltInFunction.execute_sort"
            ))
        
        return result.success(List(sorted_))

    builtin_functions["sort"] = {
        "function": execute_sort,
        "param_names": ["list_"],
        "optional_params": ["mode"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_reverse(self, exec_ctx: Context):
        """Reverses a list, e.g. [1, 2, 3] becomes [3, 2, 1]"""
        assert exec_ctx.symbol_table is not None
        list_or_str = exec_ctx.symbol_table.getf("list_or_str")
        is_right_type = isinstance(list_or_str, List) or isinstance(list_or_str, String)
        assert list_or_str is not None
        if not is_right_type:
            assert list_or_str.pos_start is not None
            assert list_or_str.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                list_or_str.pos_start, list_or_str.pos_end,
                "first", "reverse", "list", list_or_str, exec_ctx,
                origin_file="src.runtime.values.function.builtin_function.BuiltInFunction.execute_reverse",
                or_="str"
            ))

        if isinstance(list_or_str, List):
            list_or_str.elements.reverse()
        elif isinstance(list_or_str, String):
            temp_list = list(list_or_str.value)
            temp_list.reverse()
            list_or_str.value = "".join(temp_list)
        return RTResult().success(list_or_str)

    builtin_functions["reverse"] = {
        "function": execute_reverse,
        "param_names": ["list_or_str"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_startswith(self, exec_ctx: Context):
        """Check if a str starts with some other str"""
        assert exec_ctx.symbol_table is not None
        str_ = exec_ctx.symbol_table.getf("str_")
        if not isinstance(str_, String):
            assert str_ is not None
            assert str_.pos_start is not None
            assert str_.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                str_.pos_start, str_.pos_end,
                "first", "startswith", "str", str_,
                exec_ctx,
                origin_file="src.runtime.values.function.builtin_function.BuiltInFunction.execute_startswith"
            ))

        startswith = exec_ctx.symbol_table.getf("startswith")
        if not isinstance(startswith, String):
            assert startswith is not None
            assert startswith.pos_start is not None
            assert startswith.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                startswith.pos_start, startswith.pos_end,
                "second", "startswith", "str", startswith,
                exec_ctx,
                origin_file="src.runtime.values.function.builtin_function.BuiltInFunction.execute_startswith"
            ))

        return RTResult().success(Number(int(str_.value.startswith(startswith.value))))

    builtin_functions["startswith"] = {
        "function": execute_startswith,
        "param_names": ["str_", "startswith"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_endswith(self, exec_ctx: Context):
        """Check if a str ends with some other str"""
        assert exec_ctx.symbol_table is not None
        str_ = exec_ctx.symbol_table.getf("str_")
        if not isinstance(str_, String):
            assert str_ is not None
            assert str_.pos_start is not None
            assert str_.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                str_.pos_start, str_.pos_end,
                "first", "endswith", "str", str_,
                exec_ctx,
                origin_file="src.runtime.values.function.builtin_function.BuiltInFunction.execute_endswith"
            ))

        endswith = exec_ctx.symbol_table.getf("endswith")
        if not isinstance(endswith, String):
            assert endswith is not None
            assert endswith.pos_start is not None
            assert endswith.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                endswith.pos_start, endswith.pos_end,
                "second", "endswith", "str", endswith,
                exec_ctx,
                origin_file="src.runtime.values.function.builtin_function.BuiltInFunction.execute_endswith"
            ))

        return RTResult().success(Number(int(str_.value.endswith(endswith.value))))

    builtin_functions["endswith"] = {
        "function": execute_endswith,
        "param_names": ["str_", "endswith"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute___python__(self, exec_ctx: Context) -> RTResult:
        """Execute a python line. Same as python’s `eval()`"""
        assert exec_ctx.symbol_table is not None
        source = exec_ctx.symbol_table.getf("source")
        if not isinstance(source, String):
            assert source is not None
            assert source.pos_start is not None
            assert source.pos_end is not None
            return RTResult().failure(RTTypeErrorF(
                source.pos_start, source.pos_end,
                "first", "__python__", "str", source,
                exec_ctx,
                origin_file="src.runtime.values.function.builtin_function.BuiltInFunction.execute___python__"
            ))
        try:
            v = eval(source.value)
        except Exception as e:
            assert source.pos_start is not None
            assert source.pos_end is not None
            return RTResult().failure(PythonError(
                source.pos_start, source.pos_end,
                e,
                exec_ctx,
                origin_file="src.runtime.values.function.builtin_function.BuiltInFunction.execute___python__"
            ))
        return RTResult().success(py2noug(v))

    builtin_functions["__python__"] = {
        "function": execute___python__,
        "param_names": ["source"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    # ==================
