#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.lexer.position import Position
from src.runtime.values.basevalues.value import Value
from src.runtime.values.basevalues.basevalues import NoneValue, String, Number
from src.runtime.values.number_constants import TRUE, FALSE
from src.runtime.runtime_result import RTResult
from src.errors.errors import RunTimeError
from src.runtime.context import Context
from src.runtime.symbol_table import SymbolTable
# built-in python imports
# no imports


class BaseFunction(Value):
    """Parent class for all the function classes (Function, BaseBuiltinFunction and its children)"""
    def __init__(self, name: str | None, pos_start: Position, pos_end: Position, call_with_module_context: bool = False):
        super().__init__(pos_start, pos_end)
        self.name: str = name if name is not None else '<function>'
        # (if 'name' is None, we have something like `def()->foo`)
        self.type_ = 'BaseFunction'
        self.call_with_module_context: bool = call_with_module_context
    
    def __repr__(self) -> str:
        return "BaseFunction"

    def to_python_str(self) -> str:
        return repr(self)
    
    def to_str_(self):
        return String(repr(self), self.pos_start, self.pos_end).set_context(self.context), None

    def generate_new_context(self, use_self_context_ctx_table: bool = False):
        """Generates a new context with the right name, the right parent context and the right position"""
        # print(self.context)
        new_context = Context(self.name, self.pos_start, self.context)
        # set the symbol table to the parent one
        if use_self_context_ctx_table:
            assert self.context is not None
            new_context.symbol_table = SymbolTable(self.context.symbol_table)
        elif new_context.parent is None:
            new_context.symbol_table = SymbolTable()
        else:
            new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, param_names: list[str], args: list[Value | tuple[String, Value]], optional_params: list[str] | None = None,
                   should_respect_args_number: bool = True):
        # this function is not overwritten
        """Check if the number of args match with the number of params/optional params"""
        # create a result
        result = RTResult()
        if optional_params is None:  # there is no optional params
            optional_params = []

        # check if there is too much params
        if (len(args) > len(param_names + optional_params)) and should_respect_args_number:
            first_arg = args[len(param_names + optional_params)]
            last_arg = args[-1]
            if isinstance(first_arg, tuple):
                first_arg = first_arg[1]
            if isinstance(last_arg, tuple):
                last_arg = last_arg[1]
            assert self.context is not None
            return result.failure(RunTimeError(
                first_arg.pos_start, last_arg.pos_end,
                f"{len(args) - len(param_names + optional_params)} too many args passed into '{self.name}'.",
                self.context, origin_file="src.values.functions.base_function.BaseFunction.check_args"
            ))

        # check if there is too few params
        if len(args) < len(param_names) and should_respect_args_number:
            assert self.context is not None
            return result.failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"{len(param_names) - len(args)} too few args passed into '{self.name}'.",
                self.context, origin_file="src.values.functions.base_function.BaseFunction.check_args"
            ))
        
        # check names
        found_keyword_arg = False
        populated_params: list[str] = []
        populated_optional_params: list[str] = []
        for i, argument in enumerate(args):
            if found_keyword_arg and isinstance(argument, Value):
                assert self.context is not None
                return result.failure(RunTimeError(
                    argument.pos_start, argument.pos_end,
                    "positional arguments should not be placed after keyword arguments.",
                    self.context, origin_file="src.values.functions.base_funcntion.BaseFunction.check_args"
                ))
            if isinstance(argument, tuple):
                argument_name, argument_value = argument
                if argument_name.value in param_names:
                    if argument_name.value in populated_params:
                        assert self.context is not None
                        return result.failure(RunTimeError(
                            argument_name.pos_start, argument_value.pos_end,
                            f"parameter '{argument_name.value}' is already populated.",
                            self.context, origin_file="src.values.functions.base_funcntion.BaseFunction.check_args"
                        ))
                    populated_params.append(argument_name.value)
                elif argument_name.value in optional_params:
                    if argument_name.value in populated_optional_params:
                        assert self.context is not None
                        return result.failure(RunTimeError(
                            argument_name.pos_start, argument_value.pos_end,
                            f"optional parameter '{argument_name.value}' is already populated.",
                            self.context, origin_file="src.values.functions.base_funcntion.BaseFunction.check_args"
                        ))
                    populated_optional_params.append(argument_name.value)
            elif i < len(param_names):
                populated_params.append(param_names[i])
            else:
                populated_optional_params.append(optional_params[i-len(param_names)])

        if sorted(populated_params) != sorted(param_names):
            first_arg = args[len(param_names + optional_params)]
            last_arg = args[-1]
            if isinstance(first_arg, tuple):
                first_arg = first_arg[1]
            if isinstance(last_arg, tuple):
                last_arg = last_arg[1]
            assert self.context is not None
            return result.failure(RunTimeError(
                first_arg.pos_start, last_arg.pos_end,
                f"too much or too few mendatory arguments were passed into '{self.name}'.",
                self.context, origin_file="src.values.functions.base_function.BaseFunction.check_args"
            ))

        return result.success(NoneValue(self.pos_start, self.pos_end))  # if there is the right number of params

    @staticmethod
    def populate_args(param_names: list[str], args: list[Value | tuple[String, Value]],
                      exec_context: Context, optional_params: list[str] | None = None,
                      should_respect_args_number: bool = True):
        # this function is not overwritten
        """Make the args match to the param names in the symbol table"""
        # We need the context for the symbol table :)
        if optional_params is None:  # there is no optional params
            optional_params = []

        assert exec_context.symbol_table is not None
        if should_respect_args_number:  # the number of args SHOULD be equal to the number of params
            found_keyword_argument = False
            for i in range(len(args)):
                if found_keyword_argument:
                    argument = args[i]
                    assert isinstance(argument, tuple)  # this has been properly checked in check_args
                    arg_name = argument[0].value
                    arg_value = argument[1]
                    arg_value.set_context(exec_context)
                    exec_context.symbol_table.set(arg_name, arg_value)
                elif i < len(param_names):  # the argument is in the non-optional parameters list
                    arg_name = param_names[i]
                    arg_value = args[i]
                    if not isinstance(arg_value, Value):
                        arg_name = arg_value[0].value
                        arg_value = arg_value[1]
                        found_keyword_argument = True
                    arg_value.set_context(exec_context)
                    exec_context.symbol_table.set(arg_name, arg_value)
                else:  # the argument is in the optional parameters list
                    arg_name = optional_params[len(param_names) - i]
                    arg_value = args[i]
                    if not isinstance(arg_value, Value):
                        arg_name = arg_value[0].value
                        arg_value = arg_value[1]
                        found_keyword_argument = True
                    arg_value.set_context(exec_context)
                    exec_context.symbol_table.set(arg_name, arg_value)
        else:  # the number of args may not be equal to the number of params
            found_keyword_argument = False
            for i in range(len(args)):
                if found_keyword_argument:
                    argument = args[i]
                    assert isinstance(argument, tuple)  # this has been properly checked in check_args
                    arg_name = argument[0].value
                    arg_value = argument[1]
                    arg_value.set_context(exec_context)
                    exec_context.symbol_table.set(arg_name, arg_value)
                elif i < len(param_names):  # the argument is in the non-optional parameters list (when this happens ?)
                    arg_name = param_names[i]
                    arg_value = args[i]
                    if not isinstance(arg_value, Value):
                        arg_name = arg_value[0].value
                        arg_value = arg_value[1]
                        found_keyword_argument = True
                    arg_value.set_context(exec_context)
                    exec_context.symbol_table.set(arg_name, arg_value)
                elif (i - len(param_names)) < len(optional_params):
                    # the argument is in the optional parameters list
                    arg_name = optional_params[(i - len(param_names))]
                    arg_value = args[i]
                    if not isinstance(arg_value, Value):
                        arg_name = arg_value[0].value
                        arg_value = arg_value[1]
                        found_keyword_argument = True
                    arg_value.set_context(exec_context)
                    exec_context.symbol_table.set(arg_name, arg_value)
                else:  # the argument is not in the non-optional parameters list, nor in the optional
                    # we don't need to continue to loop: we are at after the last argument that can be matched with
                    # a param. Breaking here may improve performance in some specific contexts
                    break

    def check_and_populate_args(
            self, param_names: list[str], args: list[Value | tuple[String, Value]], exec_context: Context,
            optional_params: list[str] | None = None, should_respect_args_number: bool = True
    ) -> RTResult:
        """self.check_args() then self.populate_args()"""
        # We still need the context for the symbol table
        result = RTResult()
        result.register(self.check_args(param_names, args, optional_params, should_respect_args_number))
        if result.should_return():  # if there is an error
            return result
        self.populate_args(param_names, args, exec_context, optional_params, should_respect_args_number)
        return result.success(NoneValue(self.pos_start, self.pos_end))

    def get_comparison_eq(self, other: Value):
        return FALSE.copy().set_pos(self.pos_start, self.pos_end).set_context(self.context), None

    def get_comparison_ne(self, other: Value):
        return TRUE.copy().set_pos(self.pos_start, self.pos_end).set_context(self.context), None

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
