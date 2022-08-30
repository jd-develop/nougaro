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
from typing import Union


# ##########
# NODES
# ##########
class Node:
    pos_start = None
    pos_end = None


# VALUE NODES
class NumberNode(Node):
    """Node for numbers (both int and float). However, the tok type can be TT_INT or TT_FLOAT"""
    def __init__(self, token: Token):
        self.token: Token = token
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'{self.token}'


class StringNode(Node):
    """Node for strings. Tok type can be TT_STRING"""
    def __init__(self, token: Token):
        self.token: Token = token
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'{self.token}'


class ListNode(Node):
    """Node for list. self.element_nodes is a list of nodes. Needs pos_start and pos_end when init."""
    def __init__(self, element_nodes: list[Node], pos_start, pos_end):
        self.element_nodes = element_nodes
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'(list:{str(self.element_nodes)})'


# VAR NODES
class VarAssignNode(Node):
    """Node for variable assign
    example: `var foo += bar`: var_name_token is Token(TT_STRING, 'foo')
                               value_node is VarAccessNode where var_name_tokens_list is [Token(TT_IDENTIFIER, 'bar')]
                               equal is TT_PLUSEQ
    """
    def __init__(self, var_name_token, value_node, equal=TT_EQ):
        self.var_name_token = var_name_token
        self.value_node = value_node
        self.equal = equal

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.value_node.pos_end

    def __repr__(self):
        return f'(var_assign:{self.var_name_token} {self.equal} {self.value_node})'


class VarAccessNode(Node):
    """Node for variable access
    example: `foo`: var_name_tokens_list is [Token(TT_IDENTIFIER, 'foo')]
    example 2: `foo ? bar`: var_name_tokens_list is [Token(TT_IDENTIFIER, 'foo'), Token(TT_IDENTIFIER, 'bar')]
    """
    def __init__(self, var_name_tokens_list: list[Token]):
        self.var_name_tokens_list = var_name_tokens_list

        self.pos_start = self.var_name_tokens_list[0].pos_start
        self.pos_end = self.var_name_tokens_list[-1].pos_end

    def __repr__(self):
        return f'(var_access:{self.var_name_tokens_list})'


class VarDeleteNode(Node):
    """Node for variable delete, such as `del foo` where var_name_token is Token(TT_IDENTIFIER, 'foo')"""
    def __init__(self, var_name_token):
        self.var_name_token = var_name_token

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.var_name_token.pos_end

    def __repr__(self):
        return f'(var_delete:{self.var_name_token})'


# OPERATOR NODES
class BinOpNode(Node):
    """Node for binary operations.
    Examples:
        in the binary op `3 * 4`, left_node is a NumberNode which have this number token: Token(TT_INT, 3)
                                  op_token is Token(TT_MUL)
                                  right_node is a NumberNode which have this number token: Token(TT_INT, 4)
        in the binary op `foo // bar`, left_node is a VarAccessNode which his var_name_tokens_list is\
                                                                                        [Token(TT_IDENTIFIER, 'foo')]
                                       op_token is Token(TT_FLOORDIV)
                                       right_node is a VarAccessNode which his var_name_tokens_list is\
                                                                                        [Token(TT_IDENTIFIER, 'bar')]
    """
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_token}, {self.right_node})'


class BinOpCompNode(Node):
    """Same as BinOpNode for comp operators (>, <, >=, ...)
    nodes_and_tokens_list are the list of all nodes and operator tokens, such as
        [NumberNode, Token(TT_NE), VarAccessNode, Token(TT_GTE), NumberNode, Token(TT_EE), ReadNode]

    Yeah, you can use ReadNodes here x)
    But IDK who makes that, because results of 'read' statement are often put into a variable...
    """
    def __init__(self, nodes_and_tokens_list):
        self.nodes_and_tokens_list: list[Union[Node, Token]] = nodes_and_tokens_list

        self.pos_start = self.nodes_and_tokens_list[0].pos_start
        self.pos_end = self.nodes_and_tokens_list[-1].pos_end

    def __repr__(self):
        return f'[{", ".join([str(x) for x in self.nodes_and_tokens_list])}]'


class UnaryOpNode(Node):
    """Node for Unary operator (such as `not 1` or `~12`)
        op_token is the operator token. In the examples below, it is respectively Token(TT_KEYWORD, 'not') and\
                                                                                                Token(TT_BITWISENOT)
        node is the node after the operator. In the examples below, these are both NumberNode, the first with the number
                                             tok Token(TT_INT, 1) and the second with Token(TT_INT, 12)


        I write this doc in a plane between Stockholm and Amsterdam. I have a connexion in Amsterdam where I take
        another plane to Toulouse, where I live. Stockholm is a beautiful city. If you have the opportunity to visit it,
        I recommend you to visit some museums such as the Vasa museum or the Nobel Prize Museum. Take your time too to
        visit the old town, on the island of Gamla Stan.
        In the Arlanda Airport I bought a book written by Stephen Hawking, "Brief Answers to the Big Questions". I read
        it in English because there was no book in French in the bookshop. Au moins je m'améliore en anglais, mais c'est
        compliqué...
    """
    def __init__(self, op_token, node):
        self.op_token = op_token
        self.node = node

        self.pos_start = self.op_token.pos_start
        self.pos_end = self.node.pos_end

    def __repr__(self):
        return f'({self.op_token}, {self.node})'


# TEST NODES
class IfNode(Node):
    """Node for the 'if' structure. All the cases except the else case are in 'cases'.
    A case is a tuple under this form: (condition, expression if the condition is true, should_return_none)
    condition and expression are both Nodes, and should_return_node is a bool
    A else case is a tuple under this form: (expression: Node, should_return_none: bool)
    """
    def __init__(self, cases, else_case):
        self.cases: list[tuple[Node, Node, bool]] = cases
        self.else_case: tuple[Node, bool] = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end


class AssertNode(Node):
    """Node for the 'assert' structure, such as `assert False, "blah blah blah that is an error message"`
    In the example below, assertion is a VarAccessNode (identifier: False), and errmsg is a StringNode.
    errmsg can be None, like in `assert False`.
    """
    def __init__(self, assertion: Node, pos_start, pos_end, errmsg: Node = None):
        self.assertion: Node = assertion
        self.errmsg: Node = errmsg

        self.pos_start = pos_start
        self.pos_end = pos_end

        if self.errmsg is None:
            self.errmsg = StringNode(Token(TT_STRING, value='',
                                           pos_start=self.pos_start.copy(), pos_end=self.pos_end.copy()))


# LOOP NODES
class ForNode(Node):
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


class ForNodeList(Node):
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


class WhileNode(Node):
    def __init__(self, condition_node, body_node, should_return_none: bool):
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_none = should_return_none

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f'(while:{self.condition_node} then:{self.body_node})'


class DoWhileNode(Node):
    def __init__(self, body_node, condition_node, should_return_none: bool):
        self.body_node = body_node
        self.condition_node = condition_node
        self.should_return_none = should_return_none

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f'(do:{self.body_node} then do while:{self.condition_node})'


class BreakNode(Node):
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return '(break)'


class ContinueNode(Node):
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return '(continue)'


# FUNCTION NODES
class FuncDefNode(Node):
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


class CallNode(Node):
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


class ReturnNode(Node):
    def __init__(self, node_to_return, pos_start, pos_end):
        self.node_to_return = node_to_return

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'(return:{self.node_to_return})'


# MODULE NODES
class ImportNode(Node):
    def __init__(self, identifier, pos_start, pos_end):
        self.identifier = identifier

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'(import:{self.identifier})'


# FILE NODES
class WriteNode(Node):
    def __init__(self, expr_to_write, file_name_expr, to_token, line_number, pos_start, pos_end):
        self.expr_to_write = expr_to_write
        self.file_name_expr = file_name_expr
        self.to_token = to_token
        self.line_number = line_number

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'(write:{self.expr_to_write}{self.to_token.type}{self.file_name_expr} at line {self.line_number})'


class ReadNode(Node):
    def __init__(self, file_name_expr, identifier, line_number, pos_start, pos_end):
        self.file_name_expr = file_name_expr
        self.identifier = identifier
        self.line_number = line_number

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'(read:{self.file_name_expr}>>{self.identifier} at line {self.line_number})'


# SPECIAL NODES
class NoNode(Node):
    ...
