#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# IMPORTS
# nougaro modules imports
from src.values.value import Value
from src.runtime_result import RTResult
from src.errors import RunTimeError
from src.context import Context
from src.symbol_table import SymbolTable
# built-in python imports
# no imports


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
