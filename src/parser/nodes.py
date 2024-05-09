#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.lexer.position import Position as _Position
from src.lexer.token import Token as _Token
from src.lexer.token_types import TT as _TT
# built-in python imports
# no imports


# ##########
# NODES
# ##########
class Node:
    pos_start: _Position
    pos_end: _Position
    attr = False


# VALUE NODES
class NumberNode(Node):
    """Node for numbers (both int and float). The tok type can be TT_INT or TT_FLOAT"""
    def __init__(self, token: _Token):
        self.token = token
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'num:{self.token}'


class NumberENumberNode(Node):
    """Node for numbers like 10e2 or 4e-5"""
    def __init__(self, num_token: _Token, exponent_token: _Token):
        self.num_token = num_token
        self.exponent_token = exponent_token

        self.pos_start = num_token.pos_start
        self.pos_end = exponent_token.pos_end

    def __repr__(self):
        return f'numE:({self.num_token})e({self.exponent_token})'


class StringNode(Node):
    """Node for strings. Tok type can be TT_STRING"""
    def __init__(self, token: _Token):
        self.token = token
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'string_node:{self.token}'


class ListNode(Node):
    """Node for list. self.element_nodes is a list of nodes. Needs pos_start and pos_end when init."""
    def __init__(self, element_nodes: list[tuple[Node, bool]], pos_start: _Position, pos_end: _Position):
        self.element_nodes = element_nodes
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'list:{str(self.element_nodes)}'


# VAR NODES
class VarAssignNode(Node):
    """Node for variable assign
    I’m too bored to rewrite examples. TODO: rewrite examples"""
    def __init__(
            self,
            var_names: list[list[_Token | Node]],
            value_nodes: list[Node] | None,
            equal: _Token
    ):
        self.var_names: list[list[_Token | Node]] = var_names
        self.value_nodes = value_nodes
        self.equal = equal

        self.pos_start = self.var_names[0][0].pos_start
        if self.value_nodes is not None:
            self.pos_end = self.value_nodes[-1].pos_end
        else:
            self.pos_end = self.equal.pos_end

    def __repr__(self):
        return f'var_assign:({self.var_names} {self.equal} {self.value_nodes})'


class VarAccessNode(Node):
    """Node for variable access
    attr parameter is True when the var we try to access is an attribute, False if it is a global or local variable
    example: `foo`: var_name_tokens_list is [Token(TT_IDENTIFIER, 'foo')]
    example 2: `foo ? bar`: var_name_tokens_list is [Token(TT_IDENTIFIER, 'foo'), Token(TT_IDENTIFIER, 'bar')]
    """
    def __init__(self, var_name_tokens_list: list[_Token | Node], attr: bool = False):
        self.var_name_tokens_list = var_name_tokens_list
        self.attr = attr

        self.pos_start = self.var_name_tokens_list[0].pos_start
        self.pos_end = self.var_name_tokens_list[-1].pos_end

    def __repr__(self):
        return f'var_access:{self.var_name_tokens_list}' + ('(is attr in var assign)' if self.attr else '')


class VarDeleteNode(Node):
    """Node for variable delete, such as `del foo` where var_name_token is Token(TT_IDENTIFIER, 'foo')"""
    def __init__(self, var_name_token: _Token):
        self.var_name_token = var_name_token
        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.var_name_token.pos_end

    def __repr__(self):
        return f'var_delete:{self.var_name_token}'


# OPERATOR NODES
class BinOpNode(Node):
    """Node for binary operations.
    Todo: rewrite examples
    """
    def __init__(self, left_node: Node | list[Node], op_token: _Token, right_node: Node | list[Node]):
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
    def __init__(self, nodes_and_tokens_list: list[Node | _Token | list[Node]]):
        self.nodes_and_tokens_list = nodes_and_tokens_list

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
    """
    def __init__(self, op_token: _Token, node: Node | list[Node]):
        self.op_token = op_token
        self.node = node

        self.pos_start = self.op_token.pos_start
        if isinstance(self.node, list):
            self.pos_end = self.node[-1].pos_end
        else:
            self.pos_end = self.node.pos_end

    def __repr__(self):
        return f'unary_op:({self.op_token}, {self.node})'
    

class AbsNode(Node):
    """Node for the legacy absolute value syntax (|-12|)"""
    def __init__(self, node_to_abs: Node | list[Node]):
        self.node_to_abs = node_to_abs

        if isinstance(self.node_to_abs, list):
            self.pos_start = self.node_to_abs[0].pos_start
            self.pos_end = self.node_to_abs[-1].pos_end
        else:
            self.pos_start = self.node_to_abs.pos_start
            self.pos_end = self.node_to_abs.pos_end

    def __repr__(self):
        return f'abs:({self.node_to_abs})'


# TEST NODES
class IfNode(Node):
    """Node for the 'if' structure. All the cases except the else case are in 'cases'.
    A case is a tuple under this form: (condition, expression if the condition is true)
    condition and expression are both Nodes, and should_return_node is a bool
    An else case is a Node
    """
    def __init__(self, cases: list[tuple[Node, Node]], else_case: Node | None, debug: bool = False):
        self.cases: list[tuple[Node, Node]] = cases
        self.else_case: Node | None = else_case

        self.pos_start = self.cases[0][0].pos_start

        if debug:
            print(f"else_case: type {type(self.else_case)}, value " + str(self.else_case))
            print(f"cases[-1][0]: type {type(self.cases[-1][0])}, value " + str(self.cases[-1][0]))
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
    def __init__(self, assertion: Node, pos_start: _Position, pos_end: _Position, errmsg: Node | None = None):
        self.assertion = assertion
        self.errmsg = errmsg
        if self.errmsg is None:
            self.errmsg = StringNode(_Token(
                _TT["STRING"],
                value='',
                pos_start=pos_start.copy(),
                pos_end=pos_end.copy()
            ))

        self.pos_start = pos_start
        self.pos_end = pos_end

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
            var_name_token: _Token,
            start_value_node: Node,
            end_value_node: Node,
            step_value_node: Node | None,
            body_node: Node,
            label: str | None = None
    ):
        # by default step_value_node is None
        self.var_name_token = var_name_token
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.label = label

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        label = f":{self.label}" if self.label is not None else ""
        return f"for{label} {self.var_name_token} = {self.start_value_node} to {self.end_value_node} step " \
               f"{self.step_value_node} then {self.body_node}"


class ForNodeList(Node):
    """Node for 'for a in b then' structure, where b is a list/iterable.
    In this example :
        var_name_tok is Token(TT_IDENTIFIER, 'a')
        body_node is the node after the 'then'
        list_node is a VarAccessNode (identifier: b)
    """
    def __init__(self, var_name_token: _Token, body_node: Node, list_node: Node | ListNode,
                 label: str | None = None):
        # if list = [1, 2, 3]
        # for var in list is same as for var = 1 to 3 (step 1)

        self.var_name_token: _Token = var_name_token
        self.body_node = body_node
        self.list_node = list_node
        self.label = label

        # Position
        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        label = f":{self.label}" if self.label is not None else ""
        return f"for{label} {self.var_name_token} in {self.list_node} then {self.body_node}"


class WhileNode(Node):
    """Node for 'while' structure.
    Example: while True then foo()
    Here, condition_node is a VarAccessNode (identifier: True)
          body_node is a CallNode (identifier: foo, no args)*
    """
    def __init__(self, condition_node: Node, body_node: Node, label: str | None = None):
        self.condition_node: Node = condition_node
        self.body_node: Node = body_node
        self.label = label

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        label = f":{self.label}" if self.label is not None else ""
        return f'while{label} {self.condition_node} then {self.body_node}'


class DoWhileNode(Node):
    """Node for 'do then loop while' structure.
    Example: do foo() then loop while True
    Here, body_node is a CallNode (identifier: foo, no args)
          condition_node is a VarAccessNode (identifier: True)
    """
    def __init__(self, body_node: Node, condition_node: Node, label: str | None = None):
        self.body_node = body_node
        self.condition_node = condition_node
        self.label = label

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        label = f":{self.label}" if self.label is not None else ""
        return f"do{label} {self.body_node} then loop while {self.condition_node}"


class BreakNode(Node):
    """Node for `break` statement"""
    def __init__(self, pos_start: _Position, pos_end: _Position,
                 node_to_return: Node | list[Node] | None = None,
                 label: str | None = None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.node_to_return = node_to_return
        self.label = label

    def __repr__(self):
        if self.label is not None:
            repr_ = f"break:{self.label}"
        else:
            repr_ = "break"
        if self.node_to_return is not None:
            return f"{repr_} and return {self.node_to_return}"
        return repr_


class ContinueNode(Node):
    """Node for `continue` statement"""
    def __init__(self, pos_start: _Position, pos_end: _Position, label: str | None = None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.label = label

    def __repr__(self):
        if self.label is not None:
            return f"continue:{self.label}"
        return "continue"


# FUNCTION NODES
class FuncDefNode(Node):
    """Node for function definition.
    Example: `def a(bar) -> foo(bar)`
        Here, var_name_token is Token(TT_IDENTIFIER, 'a')
              param_names_tokens is [Token(TT_IDENTIFIER, 'bar')]
              body_node is CallNode (identifier: foo, args: bar)
    should_auto_return is bool (it happens in one-line functions)
    If, in the function definition, the name is not defined (like in `def()->void()`), var_name_token is None

    Optional params are under the form (name, default value)
    """
    def __init__(self, var_name_token: _Token | None, param_names_tokens: list[_Token], body_node: Node,
                 should_auto_return: bool, optional_params: list[tuple[_Token, Node]] = []):
        self.var_name_token = var_name_token
        self.param_names_tokens = param_names_tokens
        self.optional_params = optional_params
        self.body_node = body_node
        self.should_auto_return = should_auto_return

        if self.var_name_token is not None:  # a name is given: we take its pos_start as our pos_start
            self.pos_start = self.var_name_token.pos_start
        elif len(self.param_names_tokens) > 0:  # there is no name given, but there is parameters. We take the first's
            #                                     pos_start as our pos_start.
            self.pos_start = self.param_names_tokens[0].pos_start
        else:  # there is no name nor parameters given, we take the body's pos_start as our pos_start.
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f'def:{self.var_name_token}({self.param_names_tokens}, {self.optional_params})->{self.body_node}'


class ClassNode(Node):
    """Node for class statement.
    Example: `class B(A) -> foo(bar)`
        Here, var_name_token is Token(TT_IDENTIFIER, 'B')
              parent_var_name_token is Token(TT_IDENTIFIER, 'A')
              body_node is CallNode (identifier: foo, args: bar)
    should_auto_return is bool (it happens in one-line functions)
    If, in the function definition, the name is not defined (like in `def()->void()`), var_name_token is None
    """
    def __init__(self, var_name_token: _Token | None, parent_var_name_token: _Token | None, body_node: Node,
                 should_auto_return: bool):
        self.var_name_token = var_name_token
        self.parent_var_name_token = parent_var_name_token
        self.body_node = body_node
        self.should_auto_return = should_auto_return

        if self.var_name_token is not None:  # a name is given: we take its pos_start as our pos_start
            self.pos_start = self.var_name_token.pos_start
        elif self.parent_var_name_token is not None:  # there is no name given, but there is a parent given.
            self.pos_start = self.parent_var_name_token.pos_start
        else:  # there is no name nor parameters given, we take the body's pos_start as our pos_start.
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        if self.parent_var_name_token is not None:
            return f'class:{self.var_name_token}({self.parent_var_name_token})->{self.body_node}'
        else:
            return f'class:{self.var_name_token}->{self.body_node}'


class CallNode(Node):
    """Node for call structure (like `foo(bar, 1)`)
    Here: node_to_call is a VarAccessNode (identifier: foo)
          arg_nodes is [VarAccessNode (identifier: bar), NumberNode (num: 1)]
    If there is no arguments given, arg_nodes is empty.
    """
    def __init__(self, node_to_call: Node, arg_nodes: list[tuple[Node, bool]], keyword_arg_nodes: list[tuple[_Token, Node, bool]] = []):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes
        self.keyword_arg_nodes = keyword_arg_nodes

        self.pos_start = self.node_to_call.pos_start

        if len(keyword_arg_nodes) > 0:
            self.pos_end = self.keyword_arg_nodes[-1][1].pos_end
        elif len(self.arg_nodes) > 0:  # if there are arguments, we take the last one's pos_end as our pos_end.
            self.pos_end = self.arg_nodes[-1][0].pos_end
        else:  # if there is no parameter, we take the node_to_call's pos_end as our pos_end.
            self.pos_end = self.node_to_call.pos_end

    def __repr__(self):
        return f'call:{self.node_to_call}({self.arg_nodes}, {self.keyword_arg_nodes})'


class ReturnNode(Node):
    """Node for `return` structure.
    node_to_return is the node after the 'return' keyword. It may be None
    """
    def __init__(self, node_to_return: Node | None, pos_start: _Position, pos_end: _Position):
        self.node_to_return: Node | None = node_to_return

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'return:({self.node_to_return})'


# MODULE NODES
class ImportNode(Node):
    """Node for `import` structure.
    identifier is the name of the module to import. It is a token. Example: Token(TT_IDENTIFIER, 'math')
    """
    def __init__(self, identifiers: list[_Token], pos_start: _Position, pos_end: _Position,
                 as_identifier: _Token | None = None):
        self.identifiers: list[_Token] = identifiers
        self.as_identifier: _Token | None = as_identifier

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        names = [str(identifier) for identifier in self.identifiers]
        if self.as_identifier is None:
            return f"import:{'.'.join(names)}"
        return f'import:{".".join(names)}:as:{self.as_identifier}'


class ExportNode(Node):
    """Node for `export` structure.
    identifier is the name of the module to import. It is a token. Example: Token(TT_IDENTIFIER, 'lorem_ipsum')
    """
    def __init__(self, expr_or_identifier: Node | _Token, as_identifier: _Token | None,
                 pos_start: _Position, pos_end: _Position):
        self.expr_or_identifier: Node | _Token = expr_or_identifier
        self.as_identifier: _Token | None = as_identifier

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        if self.as_identifier is None:
            return f"export:{self.expr_or_identifier}"
        else:
            return f"export:{self.expr_or_identifier}:as:{self.as_identifier}"


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
    def __init__(self, expr_to_write: Node, file_name_expr: Node, to_token: _Token, line_number: str | int,
                 pos_start: _Position, pos_end: _Position):
        self.expr_to_write: Node = expr_to_write
        self.file_name_expr: Node = file_name_expr
        self.to_token = to_token
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
    def __init__(self, file_name_expr: Node, identifier: _Token | None, line_number: int | str,
                 pos_start: _Position, pos_end: _Position):
        self.file_name_expr: Node = file_name_expr
        self.identifier: _Token | None = identifier
        self.line_number: int | str = line_number

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'read:({self.file_name_expr}>>{self.identifier} at line {self.line_number})'


# MISC
class DollarPrintNode(Node):
    """$identifier"""
    def __init__(self, identifier: _Token, pos_start: _Position, pos_end: _Position):
        self.identifier = identifier

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'${self.identifier}'


# SPECIAL NODES
class NoNode(Node):
    """If the file to execute is empty or filled by back lines, this node is the only node of the node list."""
    def __repr__(self):
        return "NoNode"
