#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.parser.nodes import Node
from src.runtime.values.functions.base_function import BaseFunction
from src.runtime.values.basevalues.basevalues import NoneValue, String, List
from src.runtime.runtime_result import RTResult
from src.runtime.context import Context
from src.misc import nice_str_from_idk
# built-in python imports
# no imports


class Function(BaseFunction):
    def __init__(self, name: str, body_node: Node, param_names: str, should_auto_return: bool, call_with_module_context: bool = False):
        super().__init__(name, call_with_module_context)
        self.body_node = body_node
        self.param_names = param_names
        self.should_auto_return = should_auto_return
        self.type_ = "func"

    def __repr__(self):
        return f'<function {self.name}>'

    def execute(self, args, interpreter_, run, noug_dir, exec_from: str = "<invalid>",
                use_context: Context | None = None, cli_args=None, work_dir: str = None):
        if work_dir is None:
            work_dir = noug_dir
        # execute the function
        # create the result
        result = RTResult()

        # create an interpreter to run the code inside the function
        interpreter = interpreter_(run, noug_dir, cli_args, work_dir)

        if use_context is not None:
            self.context = use_context
        # generate the context and update symbol table
        exec_context = self.generate_new_context(True)
        exec_context.symbol_table.set("__exec_from__", String(exec_from))
        exec_context.symbol_table.set("__actual_context__", String(self.name))
        if cli_args is None:
            exec_context.symbol_table.set("__args__", List([]))
        else:
            cli_args = list(map(nice_str_from_idk, cli_args))
            exec_context.symbol_table.set("__args__", List(cli_args))
        # print(self.context)

        # populate argument and check for errors
        result.register(self.check_and_populate_args(self.param_names, args, exec_context))
        if result.should_return():
            return result

        # run the body node with the interpreter and check for errors
        value = result.register(interpreter.visit(self.body_node, exec_context, methods_instead_of_funcs=False))
        if result.should_return() and result.function_return_value is None:
            return result

        # I took a moment to understand the following line, so I put a long comment to explain it
        # * should_auto_return is for the syntax `def foo()->bar`
        # * function_return_value is the value after the `return` statement.
        # So, here:
        # * if this is a one-line function: return_value is the value inside the function
        # * if this is a multi-line function with a `return` statement, we have `None or (value) or (NoneValue)`: Python
        #   takes the value
        # * if this is a multi-line function without a `return` statement, we have `None or None or (NoneValue)`: Python
        #   takes the NoneValue
        return_value = (value if self.should_auto_return else None) or result.function_return_value or NoneValue(False)
        return result.success(return_value)

    def copy(self):
        """Return a copy of self"""
        copy = Function(self.name, self.body_node, self.param_names, self.should_auto_return,
                        self.call_with_module_context)
        copy.module_context = self.module_context
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.attributes = self.attributes.copy()
        return copy


class Method(Function):
    """Parent class for methods (functions in classes)"""
    def __init__(self, name, body_node, param_names, should_auto_return,
                 call_with_module_context: bool = False):
        super().__init__(name, body_node, param_names, should_auto_return, call_with_module_context)
        self.type_ = "method"
        self.object_ = None

    def __repr__(self):
        return f'<method {self.name}>'

    def copy(self):
        """Return a copy of self"""
        copy = Method(self.name, self.body_node, self.param_names, self.should_auto_return,
                      self.call_with_module_context)
        copy.object_ = self.object_
        copy.module_context = self.module_context
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.attributes = self.attributes.copy()
        return copy
