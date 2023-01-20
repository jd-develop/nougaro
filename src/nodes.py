#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
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
from src.token import Token
from src.token_types import TT
# built-in python imports
# no imports


# ##########
# NODES
# ##########
class Node:
    pos_start = None
    pos_end = None


# VALUE NODES
class NumberNode(Node):
    """Node for numbers (both int and float). The tok type can be TT_INT or TT_FLOAT"""
    def __init__(self, token: Token):
        self.token: Token = token
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'num:{self.token}'


class NumberENumberNode(Node):
    """Node for numbers like 10e2 or 4e-5"""
    def __init__(self, num_token: Token, exponent_token: Token):
        self.num_token = num_token
        self.exponent_token = exponent_token

        self.pos_start = num_token.pos_start
        self.pos_end = exponent_token.pos_end

    def __repr__(self):
        return f'numE:({self.num_token})e({self.exponent_token})'


class StringNode(Node):
    """Node for strings. Tok type can be TT_STRING"""
    def __init__(self, token: Token):
        self.token: Token = token
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'string_node:{self.token}'


class ListNode(Node):
    """Node for list. self.element_nodes is a list of nodes. Needs pos_start and pos_end when init."""
    def __init__(self, element_nodes: list[tuple[Node, bool]], pos_start, pos_end):
        self.element_nodes = element_nodes
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'list:{str(self.element_nodes)}'


# VAR NODES
class VarAssignNode(Node):
    """Node for variable assign
    example: `var foo += bar`: var_name_tokens is [Token(TT_STRING, 'foo')]
                               value_nodes is [VarAccessNode where var_name_tokens_list is [Token(TT_IDENTIFIER, 'bar')]
                                    ]
                               equal is TT_PLUSEQ
    example: `var a, b /= 1, 2`: var_name_tokens is [Token(TT_STRING, 'a'), Token(TT_STRING, 'b')]
                                 value_nodes is [NumberNode, NumberNode] (values of the num tok : 1 and 2
                                 equal is TT_DIVEQ
                                 same as `var a /= 1 ; var b /= 2`
    """
    def __init__(self, var_name_tokens, value_nodes, equal=TT["EQ"]):
        self.var_name_tokens = var_name_tokens
        self.value_nodes = value_nodes
        self.equal = equal

        self.pos_start = self.var_name_tokens[0].pos_start
        self.pos_end = self.value_nodes[-1].pos_end

    def __repr__(self):
        return f'var_assign:({self.var_name_tokens} {self.equal} {self.value_nodes})'


class VarAccessNode(Node):
    """Node for variable access
    attr parameter is True when the var we try to access is an attribute, False if it is a global or local variable
    example: `foo`: var_name_tokens_list is [Token(TT_IDENTIFIER, 'foo')]
    example 2: `foo ? bar`: var_name_tokens_list is [Token(TT_IDENTIFIER, 'foo'), Token(TT_IDENTIFIER, 'bar')]
    """
    def __init__(self, var_name_tokens_list: list[Token], attr: bool = False):
        self.var_name_tokens_list = var_name_tokens_list
        self.attr = attr

        self.pos_start = self.var_name_tokens_list[0].pos_start
        self.pos_end = self.var_name_tokens_list[-1].pos_end

    def __repr__(self):
        return f'var_access:{self.var_name_tokens_list}({self.attr})'


class VarDeleteNode(Node):
    """Node for variable delete, such as `del foo` where var_name_token is Token(TT_IDENTIFIER, 'foo')"""
    def __init__(self, var_name_token):
        self.var_name_token = var_name_token

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.var_name_token.pos_end

    def __repr__(self):
        return f'var_delete:{self.var_name_token}'


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
        in the binary op `foo.bar ^ 2`, left_node is this python list: [TT_IDENTIFIER:foo, TT_IDENTIFIER:bar]
                                        op_token is Token(TT_POW)
                                        right_node is a Number node with value INT:2
    """
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node

        if isinstance(self.left_node, list):
            self.pos_start = self.left_node[0].pos_start
        else:
            self.pos_start = self.left_node.pos_start
        if isinstance(self.right_node, list):
            self.pos_end = self.right_node[-1].pos_end
        else:
            self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'bin_op:({self.left_node}, {self.op_token}, {self.right_node})'


class BinOpCompNode(Node):
    """Same as BinOpNode for comp operators (>, <, >=, ...)
    nodes_and_tokens_list are the list of all nodes and operator tokens, such as
        [NumberNode, Token(TT_NE), VarAccessNode, Token(TT_GTE), NumberNode, Token(TT_EE), ReadNode]

    Yeah, you can use ReadNodes here x)
    But IDK who makes that, because results of 'read' statement are often put into a variable...
    """
    def __init__(self, nodes_and_tokens_list):
        self.nodes_and_tokens_list: list[Node | Token | list[Node | Token]] = nodes_and_tokens_list

        if isinstance(self.nodes_and_tokens_list[0], list):
            self.pos_start = self.nodes_and_tokens_list[0][0].pos_start
        else:
            self.pos_start = self.nodes_and_tokens_list[0].pos_start

        if isinstance(self.nodes_and_tokens_list[-1], list):
            self.pos_end = self.nodes_and_tokens_list[-1][-1].pos_end
        else:
            self.pos_end = self.nodes_and_tokens_list[-1].pos_end

    def __repr__(self):
        return f'bin_op_comp:({", ".join([str(x) for x in self.nodes_and_tokens_list])})'


class UnaryOpNode(Node):
    """Node for Unary operator (such as `not 1` or `~12`)
        op_token is the operator token. In these examples, it is respectively Token(TT_KEYWORD, 'not') and\
                                                                                                Token(TT_BITWISENOT)
        node is the node after the operator. In these examples, these are both NumberNode, the first with the number
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
        if isinstance(self.node, list):
            self.pos_end = self.node[-1].pos_end
        else:
            self.pos_end = self.node.pos_end

    def __repr__(self):
        return f'unary_op:({self.op_token}, {self.node})'


# TEST NODES
class IfNode(Node):
    """Node for the 'if' structure. All the cases except the else case are in 'cases'.
    A case is a tuple under this form: (condition, expression if the condition is true)
    condition and expression are both Nodes, and should_return_node is a bool
    An else case is a Node
    """
    def __init__(self, cases: list[tuple[Node, Node]], else_case: Node, debug: bool = False):
        self.cases: list[tuple[Node, Node]] = cases
        self.else_case: Node = else_case

        self.pos_start = self.cases[0][0].pos_start

        if debug:
            print(f"else_case : type {type(self.else_case)}, value " + str(self.else_case))
            print(f"cases[-1][0] : type {type(self.cases[-1][0])}, value " + str(self.cases[-1][0]))
        self.pos_end = (self.else_case or self.cases[-1][0]).pos_end

    def __repr__(self):
        return f'if {self.cases[0][0]} then {self.cases[0][1]} ' \
               f'{" ".join([f"elif {case[0]} then {case[1]}" for case in self.cases[1:]])} ' \
               f'else {self.else_case}'


class AssertNode(Node):
    """Node for the 'assert' structure, such as `assert False, "blah blah blah that is an error message"`
    In this example, assertion is a VarAccessNode (identifier: False), and errmsg is a StringNode.
    errmsg can be None, like in `assert False`.
    """
    def __init__(self, assertion: Node, pos_start, pos_end, errmsg: Node = None):
        self.assertion: Node = assertion
        self.errmsg: Node = errmsg

        self.pos_start = pos_start
        self.pos_end = pos_end

        if self.errmsg is None:
            self.errmsg = StringNode(Token(TT["STRING"], value='',
                                           pos_start=self.pos_start.copy(), pos_end=self.pos_end.copy()))

    def __repr__(self):
        return f'assert:({self.assertion}, {self.errmsg})'


# LOOP NODES
class ForNode(Node):
    """Node for 'for a = b to c (step d) then' structure.
    In this example :
        var_name_tok is Token(TT_IDENTIFIER, 'a')
        start_value_node is a VarAccessNode (identifier: b)
        end_value_node is a VarAccessNode (identifier: c)
        step_value_node is None or a VarAccessNode (identifier: d)
        body_node is the node after the 'then'
    """
    def __init__(
            self,
            var_name_token: Token,
            start_value_node: Node,
            end_value_node: Node,
            step_value_node: Node,
            body_node: Node,
    ):
        # by default step_value_node is None
        self.var_name_token: Token = var_name_token
        self.start_value_node: Node = start_value_node
        self.end_value_node: Node = end_value_node
        self.step_value_node: Node = step_value_node
        self.body_node: Node = body_node

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f"for:({self.var_name_token} = {self.start_value_node} to {self.end_value_node} step " \
               f"{self.step_value_node} then {self.body_node})"


class ForNodeList(Node):
    """Node for 'for a in b then' structure, where b is a list/iterable.
    In this example :
        var_name_tok is Token(TT_IDENTIFIER, 'a')
        body_node is the node after the 'then'
        list_node is a VarAccessNode (identifier: b)
    """
    def __init__(self, var_name_token: Token, body_node: Node, list_node: Node | ListNode):
        # if list = [1, 2, 3]
        # for var in list is same as for var = 1 to 3 (step 1)

        self.var_name_token: Token = var_name_token
        self.body_node = body_node
        self.list_node = list_node

        # Position
        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f"for:({self.var_name_token} in {self.list_node} then {self.body_node})"


class WhileNode(Node):
    """Node for 'while' structure.
    Example: while True then foo()
    Here, condition_node is a VarAccessNode (identifier: True)
          body_node is a CallNode (identifier: foo, no args)*
    """
    def __init__(self, condition_node: Node, body_node: Node):
        self.condition_node: Node = condition_node
        self.body_node: Node = body_node

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f'while:({self.condition_node} then:{self.body_node})'


class DoWhileNode(Node):
    """Node for 'do then loop while' structure.
    Example: do foo() then loop while True
    Here, body_node is a CallNode (identifier: foo, no args)
          condition_node is a VarAccessNode (identifier: True)
    """
    def __init__(self, body_node, condition_node):
        self.body_node = body_node
        self.condition_node = condition_node

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f'do:({self.body_node} then loop while:{self.condition_node})'


class BreakNode(Node):
    """Node for `break` statement"""
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return 'break'


class ContinueNode(Node):
    """Node for `continue` statement"""
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return 'continue'


# FUNCTION NODES
class FuncDefNode(Node):
    """Node for function definition.
    Example: `def a(bar) -> foo(bar)`
        Here, var_name_token is Token(TT_IDENTIFIER, 'a')
              param_names_tokens is [Token(TT_IDENTIFIER, 'bar')]
              body_node is CallNode (identifier: foo, args: bar)
    should_auto_return is bool (it happens in one-line functions)
    If, in the function definition, the name is not defined (like in `def()->void()`), var_name_token is None
    """
    def __init__(self, var_name_token: Token, param_names_tokens: list[Token], body_node: Node,
                 should_auto_return: bool):
        self.var_name_token: Token = var_name_token
        self.param_names_tokens: list[Token] = param_names_tokens
        self.body_node: Node = body_node
        self.should_auto_return: bool = should_auto_return

        if self.var_name_token is not None:  # a name is given: we take its pos_start as our pos_start
            self.pos_start = self.var_name_token.pos_start
        elif len(self.param_names_tokens) > 0:  # there is no name given, but there is parameters. We take the first's
            #                                     pos_start as our pos_start.
            self.pos_start = self.param_names_tokens[0].pos_start
        else:  # there is no name nor parameters given, we take the body's pos_start as our pos_start.
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f'def:{self.var_name_token}({self.param_names_tokens})->{self.body_node}'


class CallNode(Node):
    """Node for call structure (like `foo(bar, 1)`)
    Here: node_to_call is a VarAccessNode (identifier: foo)
          arg_nodes is [VarAccessNode (identifier: bar), NumberNode (num: 1)]
    If there is no arguments given, arg_nodes is empty.
    """
    def __init__(self, node_to_call: Node, arg_nodes: list):
        self.node_to_call: Node = node_to_call
        self.arg_nodes: list[tuple[Node, bool]] = arg_nodes

        self.pos_start = self.node_to_call.pos_start

        if len(self.arg_nodes) > 0:  # if there are arguments, we take the last one's pos_end as our pos_end.
            self.pos_end = self.arg_nodes[-1][0].pos_end
        else:  # if there is no parameter, we take the node_to_call's pos_end as our pos_end.
            self.pos_end = self.node_to_call.pos_end

    def __repr__(self):
        return f'call:{self.node_to_call}({self.arg_nodes})'


class ReturnNode(Node):
    """Node for `return` structure.
    node_to_return is the node after the 'return' keyword. It may be None
    """
    def __init__(self, node_to_return: Node, pos_start, pos_end):
        self.node_to_return: Node = node_to_return

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'return:({self.node_to_return})'


# MODULE NODES
class ImportNode(Node):
    """Node for `import` structure.
    identifier is the name of the module to import. It is a token. Example: Token(TT_IDENTIFIER, 'math')
    """
    def __init__(self, identifier: Token, pos_start, pos_end):
        self.identifier: Token = identifier

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'import:({self.identifier})'


class ExportNode(Node):
    """Node for `export` structure.
    identifier is the name of the module to import. It is a token. Example: Token(TT_IDENTIFIER, 'lorem_ipsum')
    """
    def __init__(self, identifier: Token, pos_start, pos_end):
        self.identifier: Token = identifier

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'export:({self.identifier})'


# FILE NODES
class WriteNode(Node):
    """Node for `write` structure.
    Example: `write "some text" >> "path/to/file.ext" 6`
        Here, expr_to_write is a StingNode (value: "some text")
              file_name_expr is a StringNode (value: "path/to/file.ext")
              to_token is Token(TT_TO)
              line_number is a python int (value: 6)
    Example: `write text !>> path`
        Here, expr_to_write is a VarAccessNode (identifier: text)
              file_name_expr is a VarAccessNode (identifier: path)
              to_token is Token(TT_TO_AND_OVERWRITE)
              line_number is a python str (value: "last")

    Note that when interpreting, if to_token type is TT_TO_AND_OVERWRITE, it overwrites one line if a line number is
        given, and all the file if it isn't the case.
    """
    def __init__(self, expr_to_write: Node, file_name_expr: Node, to_token: Token, line_number: str | int,
                 pos_start, pos_end):
        self.expr_to_write: Node = expr_to_write
        self.file_name_expr: Node = file_name_expr
        self.to_token: Token = to_token
        self.line_number: str | int = line_number

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'write:({self.expr_to_write}{self.to_token.type}{self.file_name_expr} at line {self.line_number})'


class ReadNode(Node):
    """Node for `read` structure.
    Example: `read path`
        Here, file_name_expr is a VarAccessNode (identifier: path)
              identifier is None
              line_number is Python str "all"
    Example: `read "path/to/file" >> foo
        Here, file_name_expr is a StringNode (value: "path/to/file")
              identifier is Token(TT_IDENTIFIER, 'foo')
              line_number is Python str "all"
    Example: `read "path/to/file" 6`
        Here, file_name_expr is a StringNode (value: "path/to/file")
              identifier is None
              line_number is Python int 6
    Example: `read path >> foo 6`
        Here, file_name_expr is a VarAccessNode (identifier: path)
              identifier is Token(TT_IDENTIFIER, 'foo')
              line_number is Python int 6

    """
    def __init__(self, file_name_expr: Node, identifier: Token, line_number: int | str, pos_start, pos_end):
        self.file_name_expr: Node = file_name_expr
        self.identifier: Token = identifier
        self.line_number: int | str = line_number

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'read:({self.file_name_expr}>>{self.identifier} at line {self.line_number})'


# SPECIAL NODES
class NoNode(Node):
    """If the file to execute is empty or filled by back lines, this node is the only node of the node list."""
    def __repr__(self):
        return "NoNode"
