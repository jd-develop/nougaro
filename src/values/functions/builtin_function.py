#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# IMPORTS
# nougaro modules imports
from src.values.functions.base_function import BaseFunction
from src.context import Context
from src.values.basevalues import *
from src.values.specific_values.number import *
from src.misc import CustomBuiltInFuncMethod
from src.errors import RTFileNotFoundError, RTTypeError
# built-in python imports
from os import system as os_system, name as os_name
import random


class BaseBuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)
        self.type_ = 'built-in func'

    def __repr__(self):
        return f'<built-in function {self.name}>'

    def execute(self, args, interpreter_, run, exec_from: str = "<invalid>"):
        return RTResult().success(NoneValue(False))

    def no_visit_method(self, exec_context: Context):
        print(exec_context)
        print(f"NOUGARO INTERNAL ERROR : No execute_{self.name} method defined in "
              f"src.values.functions.builtin_function.BaseBuiltInFunction.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/redirect1.html with all informations "
              f"above.")
        raise Exception(f'No execute_{self.name} method defined in '
                        f'src.values.functions.builtin_function.BaseBuiltInFunction.')

    def copy(self):
        copy = BaseBuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy


class BuiltInFunction(BaseBuiltInFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args, interpreter_, run, exec_from: str = "<invalid>"):
        result = RTResult()
        exec_context = self.generate_new_context()
        exec_context.symbol_table.set("__exec_from__", String(exec_from))
        exec_context.symbol_table.set("__actual_context__", String(self.name))

        method_name = f'execute_{self.name}'
        method: CustomBuiltInFuncMethod = getattr(self, method_name, self.no_visit_method)

        result.register(self.check_and_populate_args(method.arg_names, args, exec_context,
                                                     optional_args=method.optional_args,
                                                     should_respect_args_number=method.should_respect_args_number))
        if result.should_return():
            return result

        if method_name == 'execute_run':
            return_value = result.register(self.execute_run(exec_context, run))
            if result.should_return():
                return result
            return result.success(return_value)

        try:
            return_value = result.register(method(exec_context))
        except TypeError:
            try:
                return_value = result.register(method())
            except TypeError:  # it only executes when coding
                return_value = result.register(method(exec_context))
        if result.should_return():
            return result
        return result.success(return_value)

    def no_visit_method(self, exec_context: Context):
        print(exec_context)
        print(f"NOUGARO INTERNAL ERROR : No execute_{self.name} method defined in "
              f"src.values.functions.builtin_function.BuiltInFunction.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/redirect1.html with all informations "
              f"above.")
        raise Exception(f'No execute_{self.name} method defined in '
                        f'src.values.functions.builtin_function.BuiltInFunction.')

    def copy(self):
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
        result = RTResult()
        return result.success(NoneValue(False))

    execute_void.arg_names = []
    execute_void.optional_args = []
    execute_void.should_respect_args_number = False

    def execute_print(self, exec_context: Context):
        """Print 'value'"""
        # Optional params:
        # * value
        value = exec_context.symbol_table.get('value')
        if value is not None:
            try:
                print(value.to_str())
            except Exception:
                print(str(value))
        else:
            print()
        return RTResult().success(NoneValue(False))

    execute_print.arg_names = []
    execute_print.optional_args = ["value"]
    execute_print.should_respect_args_number = True

    def execute_print_ret(self, exec_context: Context):
        """Print 'value' and returns 'value'"""
        # Optional params:
        # * value
        value = exec_context.symbol_table.get('value')
        if value is not None:
            try:
                print(value.to_str())
                return RTResult().success(String(value.to_str()))
            except Exception:
                print(str(value))
                return RTResult().success(String(str(value)))
        else:
            print()
            return RTResult().success(String(''))

    execute_print_ret.arg_names = []
    execute_print_ret.optional_args = ['value']
    execute_print_ret.should_respect_args_number = True

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
    execute_input.should_respect_args_number = True

    def execute_input_int(self, exec_context: Context):
        """Basic input (int). Repeat while entered value is not an int."""
        # Optional params:
        # * text_to_display
        text_to_display = exec_context.symbol_table.get('text_to_display')
        while True:
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
                print(f"'{text}' must be an integer. Try again :")
        return RTResult().success(Number(number))

    execute_input_int.arg_names = []
    execute_input_int.optional_args = ['text_to_display']
    execute_input_int.should_respect_args_number = True

    def execute_input_num(self, exec_context: Context):
        """Basic input (int or float). Repeat while entered value is not a num."""
        # Optional params:
        # * text_to_display
        text_to_display = exec_context.symbol_table.get('text_to_display')
        while True:
            if text_to_display is None:
                text = input()
            elif isinstance(text_to_display, String) or isinstance(text_to_display, Number):
                text = input(text_to_display.value)
            else:
                text = input()

            try:
                number = float(text)
                break
            except ValueError:
                print(f"'{text}' must be an number. Try again :")
        return RTResult().success(Number(number))

    execute_input_num.arg_names = []
    execute_input_num.optional_args = ['text_to_display']
    execute_input_num.should_respect_args_number = True

    def execute_clear(self):
        """Clear the screen"""
        # No params.
        os_system('cls' if (os_name.lower() == "nt" or os_name.lower().startswith("windows")) else 'clear')
        return RTResult().success(NoneValue(False))

    execute_clear.arg_names = []
    execute_clear.optional_args = []
    execute_clear.should_respect_args_number = False

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
        return RTResult().success(TRUE if is_int else FALSE)

    execute_is_int.arg_names = ['value']
    execute_is_int.optional_args = []
    execute_is_int.should_respect_args_number = True

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
        return RTResult().success(TRUE if is_float else FALSE)

    execute_is_float.arg_names = ['value']
    execute_is_float.optional_args = []
    execute_is_float.should_respect_args_number = True

    def execute_is_num(self, exec_context: Context):
        """Check if 'value' is an int or a float"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        is_number = isinstance(value, Number)
        return RTResult().success(TRUE if is_number else FALSE)

    execute_is_num.arg_names = ['value']
    execute_is_num.optional_args = []
    execute_is_num.should_respect_args_number = True

    def execute_is_list(self, exec_context: Context):
        """Check if 'value' is a List"""
        # Params:
        # * value
        is_list = isinstance(exec_context.symbol_table.get('value'), List)
        return RTResult().success(TRUE if is_list else FALSE)

    execute_is_list.arg_names = ['value']
    execute_is_list.optional_args = []
    execute_is_list.should_respect_args_number = True

    def execute_is_str(self, exec_context: Context):
        """Check if 'value' is a String"""
        # Params:
        # * value
        is_str = isinstance(exec_context.symbol_table.get('value'), String)
        return RTResult().success(TRUE if is_str else FALSE)

    execute_is_str.arg_names = ['value']
    execute_is_str.optional_args = []
    execute_is_str.should_respect_args_number = True

    def execute_is_func(self, exec_context: Context):
        """Check if 'value' is a BaseFunction"""
        # Params:
        # * value
        is_func = isinstance(exec_context.symbol_table.get('value'), BaseFunction)
        return RTResult().success(TRUE if is_func else FALSE)

    execute_is_func.arg_names = ['value']
    execute_is_func.optional_args = []
    execute_is_func.should_respect_args_number = True

    def execute_is_none(self, exec_context: Context):
        """Check if 'value' is a NoneValue"""
        # Params:
        # * value
        is_none = isinstance(exec_context.symbol_table.get('value'), NoneValue)
        return RTResult().success(TRUE if is_none else FALSE)

    execute_is_none.arg_names = ['value']
    execute_is_none.optional_args = []
    execute_is_none.should_respect_args_number = True

    def execute_append(self, exec_context: Context):
        """Append 'value' to 'list'"""
        # Params:
        # * list
        # * value
        list_ = exec_context.symbol_table.get('list')
        value = exec_context.symbol_table.get('value')

        if not isinstance(list_, List):
            return RTResult().failure(RTTypeError(
                list_.pos_start, list_.pos_end,
                "first argument of built-in function 'append' must be a list.",
                exec_context
            ))

        list_.elements.append(value)
        return RTResult().success(list_)

    execute_append.arg_names = ['list', 'value']
    execute_append.optional_args = []
    execute_append.should_respect_args_number = True

    def execute_pop(self, exec_context: Context):
        """Remove element at 'index' from 'list'"""
        # Params:
        # * list
        # * index
        list_ = exec_context.symbol_table.get('list')
        index = exec_context.symbol_table.get('index')

        if not isinstance(list_, List):
            return RTResult().failure(RTTypeError(
                list_.pos_start, list_.pos_end,
                "first argument of built-in function 'pop' must be a list.",
                exec_context
            ))

        if not isinstance(index, Number):
            return RTResult().failure(RTTypeError(
                index.pos_start, index.pos_end,
                "second argument of built-in function 'pop' must be a number.",
                exec_context
            ))

        try:
            list_.elements.pop(index.value)
        except Exception:
            return RTResult().failure(RTIndexError(
                list_.pos_start, index.pos_end,
                f'pop index {index.value} out of range.',
                self.context
            ))
        return RTResult().success(list_)

    execute_pop.arg_names = ['list', 'index']
    execute_pop.optional_args = []
    execute_pop.should_respect_args_number = True

    def execute_insert(self, exec_context: Context):
        """Remove element at 'index' from 'list'"""
        # Params:
        # * list
        # * index
        list_ = exec_context.symbol_table.get('list')
        value = exec_context.symbol_table.get('value')
        index = exec_context.symbol_table.get('index')

        if not isinstance(list_, List):
            return RTResult().failure(RTTypeError(
                list_.pos_start, list_.pos_end,
                "first argument of built-in function 'insert' must be a list.",
                exec_context
            ))

        if index is None:
            index = Number(len(list_.elements))

        if not isinstance(index, Number):
            return RTResult().failure(RTTypeError(
                index.pos_start, index.pos_end,
                "third argument of built-in function 'insert' must be a number.",
                exec_context
            ))

        list_.elements.insert(index.value, value)
        return RTResult().success(list_)

    execute_insert.arg_names = ['list', 'value']
    execute_insert.optional_args = ['index']
    execute_insert.should_respect_args_number = True

    def execute_extend(self, exec_context: Context):
        """Extend list 'list1' with the elements of 'list2'"""
        # Params:
        # * list1
        # * list2
        # Optional params:
        # * delete_duplicates
        list1 = exec_context.symbol_table.get('list1')
        list2 = exec_context.symbol_table.get('list2')
        delete_duplicates = exec_context.symbol_table.get('delete_duplicates')

        if not isinstance(list1, List):
            return RTResult().failure(RTTypeError(
                list1.pos_start, list1.pos_end,
                "first argument of built-in function 'extend' must be a list.",
                exec_context
            ))

        if not isinstance(list2, List):
            return RTResult().failure(RTTypeError(
                list2.pos_start, list2.pos_end,
                "second argument of built-in function 'extend' must be a list.",
                exec_context
            ))

        if delete_duplicates is not None:
            if not isinstance(delete_duplicates, Number):
                return RTResult().failure(RTTypeError(
                    list2.pos_start, list2.pos_end,
                    "third argument of built-in function 'extend' must be a number.",
                    exec_context
                ))
            if delete_duplicates.value != FALSE.value:
                list1_e = list1.elements
                list2_e = list2.elements
                final_list = list1_e
                for e in list2_e:
                    can_append = True
                    for e1 in list1_e:
                        equal, error = e.get_comparison_eq(e1)
                        if error is not None:
                            continue
                        if equal is not None:
                            if equal.value == TRUE.value:
                                can_append = False
                    if can_append:
                        final_list.append(e)
                return RTResult().success(List(final_list))

        list1.elements.extend(list2.elements)
        return RTResult().success(list1)

    execute_extend.arg_names = ['list1', 'list2']
    execute_extend.optional_args = ['delete_duplicates']
    execute_extend.should_respect_args_number = True

    def execute_get(self, exec_context: Context):
        # Params:
        # * list
        # * index
        list_ = exec_context.symbol_table.get('list')
        index_ = exec_context.symbol_table.get('index')

        if not isinstance(list_, List):
            return RTResult().failure(
                RTTypeError(
                    list_.pos_start, list_.pos_end,
                    "first argument of built-in function 'get' must be a list.",
                    exec_context
                )
            )

        if not isinstance(index_, Number):
            return RTResult().failure(
                RTTypeError(
                    index_.pos_start, index_.pos_end,
                    "second argument of built-in function 'get' must be an int.",
                    exec_context
                )
            )

        try:
            return RTResult().success(list_[index_.value])
        except Exception:
            return RTResult().failure(RTIndexError(
                list_.pos_start, index_.pos_end,
                f'list index {index_.value} out of range.',
                exec_context
            ))

    execute_get.arg_names = ['list', 'index']
    execute_get.optional_args = []
    execute_get.should_respect_args_number = True

    def execute_replace(self, exec_context: Context):
        """Replace an element in a list by another"""
        # Params:
        # * list
        # * index
        # * value
        list_ = exec_context.symbol_table.get("list")
        index_ = exec_context.symbol_table.get('index')
        value = exec_context.symbol_table.get('value')

        if not isinstance(list_, List):
            return RTResult().failure(
                RTTypeError(
                    list_.pos_start, list_.pos_end,
                    "first argument of built-in function 'get' must be a list.",
                    exec_context
                )
            )

        if not isinstance(index_, Number):
            return RTResult().failure(
                RTTypeError(
                    index_.pos_start, index_.pos_end,
                    "second argument of built-in function 'get' must be an int.",
                    exec_context
                )
            )

        try:
            list_.elements[index_.value] = value
        except IndexError:
            return RTResult().failure(RTIndexError(
                list_.pos_start, index_.pos_end,
                f'list index {index_.value} out of range.',
                exec_context
            ))

        return RTResult().success(list_)

    execute_replace.arg_names = ['list', 'index', 'value']
    execute_replace.optional_args = []
    execute_replace.should_respect_args_number = True

    def execute_max(self, exec_context: Context):
        """Calculates the max value of a list"""
        # Params:
        # * value
        # Optional params:
        # * ignore_not_num (default False)
        list_ = exec_context.symbol_table.get('list')
        if not isinstance(list_, List):
            return RTResult().failure(
                RTTypeError(
                    list_.pos_start, list_.pos_end,
                    "first argument of builtin function 'max' must be a list.",
                    exec_context
                )
            )
        ignore_not_num = exec_context.symbol_table.get('ignore_not_num')
        if ignore_not_num is None:
            ignore_not_num = FALSE.set_pos(list_.pos_end, self.pos_end)
        if not isinstance(ignore_not_num, Number):
            return RTResult().failure(
                RTTypeError(
                    ignore_not_num.pos_start, ignore_not_num.pos_end,
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
                if ignore_not_num.value == FALSE.value:
                    return RTResult().failure(
                        RTTypeError(
                            list_.pos_start, list_.pos_end,
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
                if ignore_not_num.value == FALSE.value:
                    return RTResult().failure(
                        RTTypeError(
                            self.pos_start, self.pos_end,
                            "first argument of builtin function 'max' must be a list containing only numbers. "
                            "You can execute the function with True as the second argument to avoid this error.",
                            exec_context
                        )
                    )
        return RTResult().success(max_)

    execute_max.arg_names = ['list']
    execute_max.optional_args = ['ignore_not_num']
    execute_max.should_respect_args_number = True

    def execute_min(self, exec_context: Context):
        """Calculates the min value of a list"""
        # Params:
        # * value
        # Optional params:
        # * ignore_not_num (default False)
        list_ = exec_context.symbol_table.get('list')
        if not isinstance(list_, List):
            return RTResult().failure(
                RTTypeError(
                    list_.pos_start, list_.pos_end,
                    "first argument of builtin function 'min' must be a list.",
                    exec_context
                )
            )
        ignore_not_num = exec_context.symbol_table.get('ignore_not_num')
        if ignore_not_num is None:
            ignore_not_num = FALSE.set_pos(list_.pos_end, self.pos_end)
        if not isinstance(ignore_not_num, Number):
            return RTResult().failure(
                RTTypeError(
                    ignore_not_num.pos_start, ignore_not_num.pos_end,
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
                if ignore_not_num.value == FALSE.value:
                    return RTResult().failure(
                        RTTypeError(
                            list_.pos_start, list_.pos_end,
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
                if ignore_not_num.value == FALSE.value:
                    return RTResult().failure(
                        RTTypeError(
                            self.pos_start, self.pos_end,
                            "first argument of builtin function 'min' must be a list containing only numbers. "
                            "You can execute the function with True as the second argument to avoid this error.",
                            exec_context
                        )
                    )
        return RTResult().success(min_)

    execute_min.arg_names = ['list']
    execute_min.optional_args = ['ignore_not_num']
    execute_min.should_respect_args_number = True

    def execute_split(self, exec_context: Context):
        """Splits a str into a list."""
        # Optional params:
        # * char
        str_ = exec_context.symbol_table.get('str')
        char = exec_context.symbol_table.get('char')
        if not isinstance(str_, String):
            return RTResult().failure(
                RTTypeError(
                    self.pos_start, self.pos_end,
                    "first argument of builtin function 'split' must be a str.",
                    exec_context
                )
            )
        if char is None or isinstance(char, NoneValue):
            char = String(' ')
        if not isinstance(char, String):
            return RTResult().failure(
                RTTypeError(
                    self.pos_start, self.pos_end,
                    "second argument of builtin function 'split' must be a str or None.",
                    exec_context
                )
            )
        split_res = str_.value.split(char.value)
        new_list = []
        for e in split_res:
            new_list.append(String(e))
        final_list = List(new_list)

        return RTResult().success(final_list)

    execute_split.arg_names = ['str']
    execute_split.optional_args = ['char']
    execute_split.should_respect_args_number = True

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
    execute_exit.should_respect_args_number = True

    def execute_type(self, exec_context: Context):
        """Get the type of 'value'"""
        # Params :
        # * value
        value_to_get_type = exec_context.symbol_table.get('value')
        return RTResult().success(String(value_to_get_type.type_))

    execute_type.arg_names = ['value']
    execute_type.optional_args = []
    execute_type.should_respect_args_number = True

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
    execute_str.should_respect_args_number = True

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
    execute_int.should_respect_args_number = True

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
    execute_float.should_respect_args_number = True

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
    execute_list.should_respect_args_number = True

    def execute_len(self, exec_ctx: Context):
        """Returns the length of a list"""
        # Params :
        # * list
        list_ = exec_ctx.symbol_table.get('list')

        if not isinstance(list_, List):
            return RTResult().failure(RTTypeError(
                list_.pos_start, list_.pos_end,
                "first argument of built-in function 'len' must be a list.",
                exec_ctx
            ))

        return RTResult().success(Number(len(list_.elements)))

    execute_len.arg_names = ['list']
    execute_len.optional_args = []
    execute_len.should_respect_args_number = True

    def execute_rickroll(self):
        """Hum... You haven't seen anything. Close the doc please. Right now."""
        # no params
        import webbrowser
        webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ", new=2)
        return RTResult().success(String("I think you've been rickrolled..."))

    execute_rickroll.arg_names = []
    execute_rickroll.optional_args = []
    execute_rickroll.should_respect_args_number = False

    def execute_run(self, exec_ctx: Context, run):
        """Run code from another file. Param 'run' is the 'run' function in nougaro.py"""
        # Params :
        # * file_name
        file_name = exec_ctx.symbol_table.get("file_name")

        if not isinstance(file_name, String):
            return RTResult().failure(RTTypeError(
                file_name.pos_start, file_name.pos_end,
                "first argument of built-in function 'run' must be a str.",
                exec_ctx
            ))

        file_name = file_name.value

        try:
            with open(file_name, 'r', encoding='UTF-8') as file:
                script = file.read()
        except FileNotFoundError:
            return RTResult().failure(RTFileNotFoundError(
                self.pos_start, self.pos_end,
                file_name,
                exec_ctx
            ))
        except Exception as e:
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"failed to load script '{file_name}' due to internal error '{str(e.__class__.__name__)}: {str(e)}'.",
                exec_ctx
            ))

        value, error = run(file_name, script, exec_from=f"{exec_ctx.display_name} from {exec_ctx.parent.display_name}",
                           actual_context=f"{exec_ctx.parent.display_name}")

        if error is not None:
            return RTResult().failure(error)

        return RTResult().success(NoneValue(False))

    execute_run.arg_names = ["file_name"]
    execute_run.optional_args = []
    execute_run.should_respect_args_number = True

    def execute_system_call(self, exec_ctx: Context):
        """System call. e.g. system_call('ls') lists the directory on bash."""
        # Params :
        # * cmd
        cmd = exec_ctx.symbol_table.get("cmd")
        if not isinstance(cmd, String):
            return RTResult().failure(RTTypeError(
                cmd.pos_start, cmd.pos_end,
                f"first argument of builtin function 'system_call' must be a str.",
                exec_ctx
            ))
        try:
            to_return_value = os_system(str(cmd.value))
            return RTResult().success(String(to_return_value))
        except Exception as e:
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"failed to call '{cmd}' due to internal error '{str(e.__class__.__name__)}: {str(e)}'.",
                exec_ctx
            ))

    execute_system_call.arg_names = ["cmd"]
    execute_system_call.optional_args = []
    execute_system_call.should_respect_args_number = True

    def execute_lower(self, exec_ctx: Context):
        """Return lower-cased string. e.g. lower('NOUGARO') returns 'nougaro'."""
        # Params :
        # * value
        value = exec_ctx.symbol_table.get("value")
        if not isinstance(value, String):
            return RTResult().failure(RTTypeError(
                value.pos_start, value.pos_end,
                f"first argument of builtin function 'lower' must be a str.",
                exec_ctx
            ))
        return RTResult().success(String(value.value.lower()))

    execute_lower.arg_names = ["value"]
    execute_lower.optional_args = []
    execute_lower.should_respect_args_number = True

    def execute_upper(self, exec_ctx: Context):
        """Return upper-cased string. e.g. upper('nougaro') returns 'NOUGARO'."""
        # Params :
        # * value
        value = exec_ctx.symbol_table.get("value")
        if not isinstance(value, String):
            return RTResult().failure(RTTypeError(
                value.pos_start, value.pos_end,
                f"first argument of builtin function 'upper' must be a str.",
                exec_ctx
            ))
        return RTResult().success(String(value.value.upper()))

    execute_upper.arg_names = ["value"]
    execute_upper.optional_args = []
    execute_upper.should_respect_args_number = True

    def execute_nougaro(self, exec_ctx: Context):
        """Open a random song of Claude Nougaro. If argument 'song' is filled, open this song (if in database)."""
        # Params :
        # * song
        song = exec_ctx.symbol_table.get("song")
        songs = {
            "Toulouse": "https://www.youtube.com/watch?v=wehrXJTA3vI",
            "Armstrong": "https://www.youtube.com/watch?v=Dkqsh0kkjFw",
            "Bidonville": "https://www.youtube.com/watch?v=sh6jpbxjFKY",
            "Tu verras": "https://www.youtube.com/watch?v=rK3r-AqlNjU",
        }  # PR if you want to add more songs :)
        if song is None:
            import webbrowser
            song = random.choice(list(songs.keys()))
            webbrowser.open(songs[song], new=2)
            return RTResult().success(String(song))
        if not isinstance(song, String):
            return RTResult().failure(RTTypeError(
                song.pos_start, song.pos_end,
                f"first argument of builtin function 'nougaro' must be a str.",
                exec_ctx
            ))

        if song.value == "help":
            return RTResult().success(String(f"The available songs are: {', '.join(list(songs.keys()))}"))

        import webbrowser
        try:
            webbrowser.open(songs[song.value], new=2)
            return RTResult().success(NoneValue(False))
        except KeyError:
            return RTResult().failure(RunTimeError(
                song.pos_start, song.pos_end,
                f"'{song.value}' is not a song in the actual database. Available songs: "
                f"{', '.join(list(songs.keys()))}",
                exec_ctx
            ))

    execute_nougaro.arg_names = []
    execute_nougaro.optional_args = ["song"]
    execute_nougaro.should_respect_args_number = True

    # ==================
