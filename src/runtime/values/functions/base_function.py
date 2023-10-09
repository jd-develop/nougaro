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
from src.runtime.values.number_constants import TRUE, FALSE
from src.runtime.runtime_result import RTResult
from src.errors.errors import RunTimeError
from src.runtime.context import Context
from src.runtime.symbol_table import SymbolTable
# built-in python imports
# no imports


class BaseFunction(Value):
    """Parent class for all the function classes (Function, BaseBuiltinFunction and its children)"""
    def __init__(self, name, call_with_module_context=False):
        super().__init__()
        self.name = name if name is not None else '<function>'  # if 'name' is None, we have something like `def()->foo`
        self.type_ = 'BaseFunction'
        self.call_with_module_context: bool = call_with_module_context

    def generate_new_context(self, use_self_context_ctx_table: bool = False):
        """Generates a new context with the right name, the right parent context and the right position"""
        # print(self.context)
        new_context = Context(self.name, self.context, self.pos_start)
        # set the symbol table to the parent one
        if use_self_context_ctx_table:
            new_context.symbol_table = SymbolTable(self.context.symbol_table)
        elif new_context.parent is None:
            new_context.symbol_table = SymbolTable()
        else:
            new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, param_names, args, optional_params: list = None, should_respect_args_number: bool = True):
        """Check if the number of args match with the number of params/optional params"""
        # create a result
        result = RTResult()
        if optional_params is None:  # there is no optional params
            optional_params = []

        # check if there is too much params
        if (len(args) > len(param_names + optional_params)) and should_respect_args_number:
            return result.failure(
                RunTimeError(
                    args[len(param_names + optional_params)].pos_start, args[-1].pos_end,
                    f"{len(args) - len(param_names + optional_params)} too many args passed into '{self.name}'.",
                    self.context, origin_file="src.values.functions.base_function.BaseFunction.check_args()"
                )
            )

        # check if there is too few params
        if len(args) < len(param_names) and should_respect_args_number:
            return result.failure(
                RunTimeError(
                    self.pos_start, self.pos_end,
                    f"{len(param_names) - len(args)} too few args passed into '{self.name}'.",
                    self.context, origin_file="src.values.functions.base_function.BaseFunction.check_args()"
                )
            )

        return result.success(None)  # if there is the right number of params

    @staticmethod
    def populate_args(param_names: list[str], args, exec_context: Context, optional_params: list[str] = None,
                      should_respect_args_number: bool = True):
        """Make the args match to the param names in the symbol table"""
        # We need the context for the symbol table :)
        if optional_params is None:  # there is no optional params
            optional_params = []

        if should_respect_args_number:  # the number of args SHOULD be equal to the number of params
            for i in range(len(args)):
                if i < len(param_names):  # the argument is in the non-optional parameters list
                    arg_name = param_names[i]
                    arg_value = args[i]
                    arg_value.set_context(exec_context)
                    exec_context.symbol_table.set(arg_name, arg_value)
                else:  # the argument is in the optional parameters list
                    arg_name = optional_params[len(param_names) - i]
                    arg_value = args[i]
                    arg_value.set_context(exec_context)
                    exec_context.symbol_table.set(arg_name, arg_value)
        else:  # the number of args may not be equal to the number of params
            for i in range(len(args)):
                if i < len(param_names):  # the argument is in the non-optional parameters list (when this happens ?)
                    arg_name = param_names[i]
                    arg_value = args[i]
                    arg_value.set_context(exec_context)
                    exec_context.symbol_table.set(arg_name, arg_value)
                elif (i - len(param_names) + 1) < len(optional_params):
                    # the argument is in the optional parameters list

                    # don't ask anything about the above condition. I don't understand how it works, but it works
                    # if someone can explain me clearly why we put a +1, mail me: jd-dev@laposte.net
                    # - Jean Dubois
                    arg_name = optional_params[(i - len(param_names))]
                    arg_value = args[i]
                    arg_value.set_context(exec_context)
                    exec_context.symbol_table.set(arg_name, arg_value)
                else:  # the argument is not in the non-optional parameters list, nor in the optional
                    # we don't need to continue to loop : we are at after the last argument that can be matched with
                    # a param. Breaking here may improve performance in some specific contexts
                    break

    def check_and_populate_args(self, param_names, args, exec_context: Context, optional_params: list = None,
                                should_respect_args_number: bool = True):
        """self.check_args() then self.populate_args()"""
        # We still need the context for the symbol table ;)
        result = RTResult()
        result.register(self.check_args(param_names, args, optional_params, should_respect_args_number))
        if result.should_return():  # if there is an error
            return result
        self.populate_args(param_names, args, exec_context, optional_params, should_respect_args_number)
        return result.success(None)

    def get_comparison_eq(self, other):
        return FALSE.copy().set_context(self.context), None

    def get_comparison_ne(self, other):
        return TRUE.copy().set_context(self.context), None

    def get_comparison_gte(self, other):
        return FALSE.copy().set_context(self.context), None

    def get_comparison_lte(self, other):
        return FALSE.copy().set_context(self.context), None
