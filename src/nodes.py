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
from src.tokens import Token
from src.token_constants import TT_EQ, TT_STRING
# built-in python imports
# no imports


# ##########
# NODES
# ##########

# VALUE NODES
class NumberNode:
    def __init__(self, token):
        self.token = token
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'{self.token}'


class StringNode:
    def __init__(self, token):
        self.token = token
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'{self.token}'


class ListNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'(list:{str(self.element_nodes)})'


# VAR NODES
class VarAssignNode:
    def __init__(self, var_name_token, value_node, equal=TT_EQ):
        self.var_name_token = var_name_token
        self.value_node = value_node
        self.equal = equal

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.value_node.pos_end

    def __repr__(self):
        return f'(var_assign:{self.var_name_token} {self.equal} {self.value_node})'


class VarAccessNode:
    def __init__(self, var_name_tokens_list: list[Token]):
        self.var_name_tokens_list = var_name_tokens_list

        self.pos_start = self.var_name_tokens_list[0].pos_start
        self.pos_end = self.var_name_tokens_list[-1].pos_end

    def __repr__(self):
        return f'(var_access:{self.var_name_tokens_list})'


class VarDeleteNode:
    def __init__(self, var_name_token):
        self.var_name_token = var_name_token

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.var_name_token.pos_end

    def __repr__(self):
        return f'(var_delete:{self.var_name_token})'


# OPERATOR NODES
class BinOpNode:
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_token}, {self.right_node})'


class BinOpCompNode:
    def __init__(self, nodes_and_tokens_list):
        self.nodes_and_tokens_list = nodes_and_tokens_list

        self.pos_start = self.nodes_and_tokens_list[0].pos_start
        self.pos_end = self.nodes_and_tokens_list[-1].pos_end

    def __repr__(self):
        return f'[{", ".join([str(x) for x in self.nodes_and_tokens_list])}]'


class UnaryOpNode:
    def __init__(self, op_token, node):
        self.op_token = op_token
        self.node = node

        self.pos_start = self.op_token.pos_start
        self.pos_end = self.node.pos_end

    def __repr__(self):
        return f'({self.op_token}, {self.node})'


# TEST NODES
class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end


class AssertNode:
    def __init__(self, assertion, pos_start, pos_end, errmsg=None):
        self.assertion = assertion
        self.errmsg = errmsg

        self.pos_start = pos_start
        self.pos_end = pos_end

        if self.errmsg is None:
            self.errmsg = StringNode(Token(TT_STRING, value='',
                                           pos_start=self.pos_start.copy(), pos_end=self.pos_end.copy()))


# LOOP NODES
class ForNode:
    def __init__(self, var_name_token, start_value_node, end_value_node, step_value_node, body_node,
                 should_return_none: bool):
        # by default step_value_node is None
        self.var_name_token: Token = var_name_token
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.should_return_none = should_return_none

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.body_node.pos_end


class ForNodeList:
    def __init__(self, var_name_token, body_node, list_node: ListNode, should_return_none: bool):
        # if list = [1, 2, 3]
        # for var in list == for var = 1 to 3 (step 1)

        self.var_name_token: Token = var_name_token
        self.body_node = body_node
        self.list_node = list_node
        self.should_return_none = should_return_none

        # Position
        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.body_node.pos_end


class WhileNode:
    def __init__(self, condition_node, body_node, should_return_none: bool):
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_none = should_return_none

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f'(while:{self.condition_node} then:{self.body_node})'


class DoWhileNode:
    def __init__(self, body_node, condition_node, should_return_none: bool):
        self.body_node = body_node
        self.condition_node = condition_node
        self.should_return_none = should_return_none

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f'(do:{self.body_node} then do while:{self.condition_node})'


class BreakNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return '(break)'


class ContinueNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return '(continue)'


# FUNCTION NODES
class FuncDefNode:
    def __init__(self, var_name_token: Token, param_names_tokens: list[Token], body_node, should_auto_return):
        self.var_name_token = var_name_token
        self.param_names_tokens = param_names_tokens
        self.body_node = body_node
        self.should_auto_return = should_auto_return

        if self.var_name_token is not None:
            self.pos_start = self.var_name_token.pos_start
        elif len(self.param_names_tokens) > 0:
            self.pos_start = self.param_names_tokens[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f'(funcdef:{self.var_name_token} args:{self.param_names_tokens})'


class CallNode:
    def __init__(self, node_to_call, arg_nodes: list):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = self.node_to_call.pos_start

        if len(self.arg_nodes) > 0:
            self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end

    def __repr__(self):
        return f'(call:{self.node_to_call}, arg_nodes:{self.arg_nodes})'


class ReturnNode:
    def __init__(self, node_to_return, pos_start, pos_end):
        self.node_to_return = node_to_return

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'(return:{self.node_to_return})'


# MODULE NODES
class ImportNode:
    def __init__(self, identifier, pos_start, pos_end):
        self.identifier = identifier

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'(import:{self.identifier})'


# FILE NODES
class WriteNode:
    def __init__(self, expr_to_write, file_name_expr, to_token, line_number, pos_start, pos_end):
        self.expr_to_write = expr_to_write
        self.file_name_expr = file_name_expr
        self.to_token = to_token
        self.line_number = line_number

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'(write:{self.expr_to_write}{self.to_token.type}{self.file_name_expr} at line {self.line_number})'


class ReadNode:
    def __init__(self, file_name_expr, identifier, line_number, pos_start, pos_end):
        self.file_name_expr = file_name_expr
        self.identifier = identifier
        self.line_number = line_number

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'(read:{self.file_name_expr}>>{self.identifier} at line {self.line_number})'


# SPECIAL NODES
class NoNode:
    pass
