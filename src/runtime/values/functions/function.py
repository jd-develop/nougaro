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
from src.lexer.position import Position, DEFAULT_POSITION
from src.parser.nodes import Node
from src.runtime.values.functions.base_function import BaseFunction
from src.runtime.values.basevalues.value import Value
from src.runtime.values.basevalues.basevalues import NoneValue, String, List, Number
from src.runtime.runtime_result import RTResult
from src.runtime.context import Context
from src.misc import nice_str_from_idk, RunFunction
# built-in python imports
# no imports
# special typing imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.runtime.interpreter import Interpreter


class Function(BaseFunction):
    def __init__(self, name: str | None, body_node: Node, param_names: list[str], should_auto_return: bool,
                 pos_start: Position, pos_end: Position, call_with_module_context: bool = False,
                 optional_params: list[tuple[str, Value | None]] | None = None):
        super().__init__(name, pos_start, pos_end, call_with_module_context)
        self.body_node = body_node
        self.param_names = param_names
        self.optional_params = optional_params
        self.should_auto_return = should_auto_return

    def __repr__(self):
        return f'<function {self.name}>'

    def is_eq(self, other: Value):
        if not isinstance(other, Function):
            return False
        is_eq = self.param_names == other.param_names and self.should_auto_return == other.should_auto_return and \
                self.optional_params == other.optional_params
        are_nodes_eq = self.body_node == other.body_node
        return is_eq and are_nodes_eq

    def get_comparison_eq(self, other: Value):
        return Number(self.is_eq(other), self.pos_start, other.pos_end), None

    def get_comparison_ne(self, other: Value):
        return Number(not self.is_eq(other), self.pos_start, other.pos_end), None

    def to_python_str(self):
        return self.__repr__()

    def execute(self, args: list[Value], interpreter_: type[Interpreter], run: RunFunction,
                noug_dir: str, lexer_metas: dict[str, str | bool], exec_from: str = "<invalid>",
                use_context: Context | None = None, cli_args: list[String] | None = None,
                work_dir: str | None = None):
        if work_dir is None:
            work_dir = noug_dir
        # execute the function
        # create the result
        result = RTResult()
        if cli_args is None:
            cli_args = []

        # create an interpreter to run the code inside the function
        interpreter = interpreter_(run, noug_dir, cli_args, work_dir, lexer_metas)

        if use_context is not None:
            self.context = use_context
        # generate the context and update symbol table
        exec_context = self.generate_new_context(True)
        assert exec_context.symbol_table is not None
        exec_context.symbol_table.set(
            "__exec_from__", String(exec_from, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy())
        )
        exec_context.symbol_table.set(
            "__actual_context__", String(self.name, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy())
        )

        cli_args_value: list[Value] = list(map(nice_str_from_idk, cli_args))
        exec_context.symbol_table.set("__args__", List(cli_args_value, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()))
        # print(self.context)

        # populate argument and check for errors
        result.register(self.check_and_populate_args(self.param_names, args, exec_context, self.optional_params))
        if result.should_return():
            return result

        # run the body node with the interpreter and check for errors
        value = result.register(interpreter.visit(self.body_node, exec_context, methods_instead_of_funcs=False))
        if result.should_return() and result.function_return_value is None:
            return result

        if self.should_auto_return:  # syntax `def foo()->bar`
            return_value = value
        elif result.function_return_value is not None:  # value after the `return` statement
            return_value = result.function_return_value
        else:
            return_value = NoneValue(self.pos_start, self.pos_end, False)

        if return_value is None:
            return_value = NoneValue(self.pos_start, self.pos_end, False)
        return result.success(return_value)

    def copy(self):
        """Return a copy of self"""
        copy = Function(
            self.name,
            self.body_node,
            self.param_names,
            self.should_auto_return,
            self.pos_start,
            self.pos_end,
            self.call_with_module_context,
            self.optional_params
        )
        copy.module_context = self.module_context
        copy.set_context(self.context)
        copy.attributes = self.attributes.copy()
        return copy


class Method(Function):
    """Parent class for methods (functions in classes)"""
    def __init__(self, name: str | None, body_node: Node, param_names: list[str], should_auto_return: bool,
                 pos_start: Position, pos_end: Position, call_with_module_context: bool = False,
                 optional_params: list[tuple[str, Value | None]] | None = None):
        super().__init__(
            name, body_node, param_names, should_auto_return, pos_start, pos_end, call_with_module_context,
            optional_params=optional_params
        )
        self.type_ = "method"
        self.object_: Value | None = None

    def __repr__(self):
        return f'<method {self.name}>'

    def copy(self):
        """Return a copy of self"""
        copy = Method(
            self.name, self.body_node, self.param_names, self.should_auto_return,
            self.pos_start, self.pos_end, self.call_with_module_context,
            optional_params=self.optional_params)
        copy.object_ = self.object_
        copy.module_context = self.module_context
        copy.set_context(self.context)
        copy.attributes = self.attributes.copy()
        return copy

    def is_eq(self, other: Value):
        if not isinstance(other, Method):
            return False
        is_eq = self.param_names == other.param_names and self.should_auto_return == other.should_auto_return and \
                self.optional_params == other.optional_params
        are_nodes_eq = self.body_node == other.body_node
        return is_eq and are_nodes_eq
