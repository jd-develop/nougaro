#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# IMPORTS
# nougaro modules imports
from src.values.functions.base_function import BaseFunction
from src.values.basevalues import NoneValue
from src.runtime_result import RTResult
# built-in python imports
# no imports


class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, should_return_none):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_return_none = should_return_none
        self.type_ = "func"

    def __repr__(self):
        return f'<function {self.name}>'

    def execute(self, args, interpreter_):
        result = RTResult()
        interpreter = interpreter_()
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
