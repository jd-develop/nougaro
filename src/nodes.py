#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# IMPORTS
# nougaro modules imports
from src.tokens import Token
from src.token_constants import TT_EQ
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
        return f'{str(self.element_nodes)}'


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
    def __init__(self, var_name_token):
        self.var_name_token = var_name_token

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.var_name_token.pos_end


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
    def __init__(self, var_name_token: Token, arg_name_tokens: list[Token], body_node, should_auto_return):
        self.var_name_token = var_name_token
        self.arg_name_tokens = arg_name_tokens
        self.body_node = body_node
        self.should_auto_return = should_auto_return

        if self.var_name_token is not None:
            self.pos_start = self.var_name_token.pos_start
        elif len(self.arg_name_tokens) > 0:
            self.pos_start = self.arg_name_tokens[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f'(funcdef:{self.var_name_token} args:{self.arg_name_tokens})'


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
        return f'(call:{self.node_to_call})'


class ReturnNode:
    def __init__(self, node_to_return, pos_start, pos_end):
        self.node_to_return = node_to_return

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'(return:{self.node_to_return})'


# SOME MATH NODES
class AbsNode:
    def __init__(self, node_to_abs):
        self.node_to_abs = node_to_abs

        self.pos_start = self.node_to_abs.pos_start
        self.pos_end = self.node_to_abs.pos_end

    def __repr__(self):
        return f'|{self.node_to_abs}|'


# SPECIAL NODES
class NoNode:
    pass
