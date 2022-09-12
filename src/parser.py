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
from src.token_types import *
from src.errors import InvalidSyntaxError
from src.parse_result import ParseResult
from src.nodes import *  # src.tokens.Token is imported in src.nodes
# built-in python imports
from typing import Any, Union


# ##########
# PARSER
# ##########
class Parser:
    """ The Parser (transforms Tokens from the Lexer to Nodes for the Interpreter).
        Please see grammar.txt for AST.
    """

    def __init__(self, tokens: list):
        self.tokens: list = tokens  # tokens from the lexer
        self.token_index = -1  # we start at -1, because we advance 2 lines after, so the index will be 0
        self.current_token: Token = None  # Token is imported in src.nodes
        self.advance()

    def parse(self):
        """Parse tokens and return a result that contain a main node"""
        result = self.statements()
        if result.error is not None and self.current_token.type != TT["EOF"]:
            return result.failure(
                InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                   "expected '+', '-', '*', '/', '//', '%', 'and', 'or' or 'xor'.")
            )
        return result

    def advance(self):
        """Advance of 1 token"""
        self.token_index += 1
        self.update_current_token()
        return self.current_token

    def reverse(self, amount: int = 1):
        """Advance of -1 token"""
        # this is just the opposite of self.advance ^^
        self.token_index -= amount
        self.update_current_token()
        return self.current_token

    def update_current_token(self):
        """Update current token after having advanced"""
        if 0 <= self.token_index < len(self.tokens):  # if the index is correct
            self.current_token = self.tokens[self.token_index]  # we update

    # GRAMMARS ATOMS (AST) :

    def statements(self, stop: list[Union[tuple[(str, Any)], str]] = None) -> ParseResult:
        """The returned node in the parse result is ALWAYS a ListNode here."""
        if stop is None:
            stop = [TT["EOF"]]  # token(s) that stops parser in this function
        result = ParseResult()  # we create the result
        statements = []  # list of statements
        pos_start = self.current_token.pos_start.copy()  # pos_start

        while self.current_token.type == TT["NEWLINE"]:  # skip new lines
            result.register_advancement()
            self.advance()

        if self.current_token.type == TT["EOF"]:  # End Of File -> nothing to parse!
            return result.success(NoNode())

        last_token_type = self.current_token.type

        statement = result.register(self.statement())  # we register a statement
        if result.error is not None:  # we check for errors
            return result
        statements.append(statement)  # we append the statement to our list of there is no error

        while True:  # 'break's inside the loop
            newline_count = 0
            while self.current_token.type == TT["NEWLINE"]:  # skip new lines
                result.register_advancement()
                self.advance()
                newline_count += 1

            # we check if we have to stop parsing
            # in stop there can be tok types or tuples like (tok_type, tok_value)
            # I made a HUGE optimisation here: there was a 'for' loop (git blame for date)
            if self.current_token.type in stop or (self.current_token.type, self.current_token.value) in stop:
                break
            else:
                if newline_count == 0:  # there was no new line between the last statement and this one: unexpected
                    # token
                    if last_token_type == TT["IDENTIFIER"] and self.current_token.type in EQUALS:
                        # there was no new line but there is 'id =' (need 'var')
                        return result.failure(
                            InvalidSyntaxError(
                                self.current_token.pos_start, self.current_token.pos_end,
                                "unexpected token. To declare a variable, use 'var' keyword."
                            )
                        )
                    return result.failure(
                        InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end,
                            "unexpected token."
                        )
                    )

            # we replace the last token type
            last_token_type = self.current_token.type

            # we register a statement, check for errors and append the statement if all is OK
            statement = result.register(self.statement())
            if result.error is not None:
                return result
            statements.append(statement)

        return result.success(ListNode(  # we put all the nodes parsed here into a ListNode
            statements,
            pos_start,
            self.current_token.pos_end.copy()
        ))

    def statement(self) -> ParseResult:  # only one statement
        result = ParseResult()
        pos_start = self.current_token.pos_start.copy()

        if self.current_token.matches(TT["KEYWORD"], 'return'):
            result.register_advancement()
            self.advance()

            expr = result.try_register(self.expr())
            if expr is None:
                self.reverse(result.to_reverse_count)
            return result.success(ReturnNode(expr, pos_start, self.current_token.pos_start.copy()))

        if self.current_token.matches(TT["KEYWORD"], 'continue'):
            result.register_advancement()
            self.advance()

            return result.success(ContinueNode(pos_start, self.current_token.pos_start.copy()))

        if self.current_token.matches(TT["KEYWORD"], 'break'):
            result.register_advancement()
            self.advance()

            return result.success(BreakNode(pos_start, self.current_token.pos_start.copy()))

        if self.current_token.matches(TT["KEYWORD"], 'import'):
            result.register_advancement()
            self.advance()

            if self.current_token.type != TT["IDENTIFIER"]:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected identifier after 'import'."
                    )
                )

            identifier = self.current_token

            result.register_advancement()
            self.advance()

            return result.success(ImportNode(identifier, pos_start, self.current_token.pos_start.copy()))

        expr = result.register(self.expr())
        if result.error is not None:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "expected 'var', int, float, identifier, 'if', 'for', 'while', 'def', 'continue', 'break', 'return', "
                "'+', '-', '(', '[', '|' or 'not'."
            ))

        return result.success(expr)

    def expr(self) -> ParseResult:
        result = ParseResult()
        pos_start = self.current_token.pos_start.copy()
        if self.current_token.matches(TT["KEYWORD"], 'var'):
            result.register_advancement()
            self.advance()

            if self.current_token.type != TT["IDENTIFIER"]:
                if self.current_token.type != TT["KEYWORD"]:
                    if self.current_token.type not in TOKENS_TO_QUOTE:
                        error_msg = f"expected identifier, but got {self.current_token.type}."
                    else:
                        error_msg = f"expected identifier, but got '{self.current_token.type}'."
                    return result.failure(
                        InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end, error_msg
                        )
                    )
                else:
                    return result.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "use keyword as identifier is illegal."
                    ))

            var_name = self.current_token
            result.register_advancement()
            self.advance()

            equal = self.current_token
            equals = EQUALS

            if self.current_token.type not in equals:
                if self.current_token.type in [TT["EE"], TT["GT"], TT["LT"], TT["GTE"], TT["LTE"]]:
                    error_msg = f"expected an assignation equal, but got a test equal ('{self.current_token.type}')."
                elif self.current_token.type not in TOKENS_TO_QUOTE:
                    error_msg = f"expected an equal, but got {self.current_token.type}."
                else:
                    error_msg = f"expected an equal, but got '{self.current_token.type}'."
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end, error_msg
                    )
                )

            result.register_advancement()
            self.advance()

            expr = result.register(self.expr())
            if result.error is not None:
                return result
            return result.success(VarAssignNode(var_name, expr, equal))

        if self.current_token.matches(TT["KEYWORD"], 'del'):
            result.register_advancement()
            self.advance()

            if self.current_token.type != TT["IDENTIFIER"]:
                if self.current_token.type != TT["KEYWORD"]:
                    if self.current_token.type not in TOKENS_TO_QUOTE:
                        error_msg = f"expected identifier, but got {self.current_token.type}."
                    else:
                        error_msg = f"expected identifier, but got '{self.current_token.type}'."
                    return result.failure(
                        InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end, error_msg
                        )
                    )
                else:
                    return result.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "use keyword as identifier is illegal."
                    ))

            var_name = self.current_token
            result.register_advancement()
            self.advance()

            if result.error is not None:
                return result
            return result.success(VarDeleteNode(var_name))

        if self.current_token.matches(TT["KEYWORD"], 'write'):
            result.register_advancement()
            self.advance()

            expr_to_write = result.register(self.expr())
            if result.error is not None:
                return result

            if self.current_token.type not in [TT["TO"], TT["TO_AND_OVERWRITE"]]:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "'>>' or '!>>' is missing. The correct syntax is 'write () >> ()'."
                    )
                )
            to_token = self.current_token

            result.register_advancement()
            self.advance()

            file_name_expr = result.register(self.expr())
            if result.error is not None:
                return result

            if self.current_token.type == TT["INT"]:
                line_number = self.current_token.value

                result.register_advancement()
                self.advance()
            else:
                line_number = 'last'

            return result.success(WriteNode(expr_to_write, file_name_expr, to_token, line_number, pos_start,
                                            self.current_token.pos_start.copy()))

        if self.current_token.matches(TT["KEYWORD"], 'read'):
            result.register_advancement()
            self.advance()

            file_name_expr = result.register(self.expr())
            if result.error is not None:
                return result

            identifier = None

            if self.current_token.type == TT["TO"]:
                result.register_advancement()
                self.advance()

                if self.current_token.type != TT["IDENTIFIER"]:
                    return result.failure(
                        InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end,
                            f"expected identifier, got {self.current_token.type}."
                        )
                    )

                identifier = self.current_token

                result.register_advancement()
                self.advance()

            if self.current_token.type == TT["INT"]:
                line_number = self.current_token.value

                result.register_advancement()
                self.advance()
            else:
                line_number = 'all'

            return result.success(ReadNode(file_name_expr, identifier, line_number, pos_start,
                                           self.current_token.pos_start.copy()))

        if self.current_token.matches(TT["KEYWORD"], "assert"):
            result.register_advancement()
            self.advance()

            assertion = result.register(self.expr())
            if result.error is not None:
                return result

            if self.current_token.type == TT["COMMA"]:
                # register an error message to print if the assertion is false.
                # if there is no comma, there is no error message
                result.register_advancement()
                self.advance()

                errmsg = result.register(self.expr())
                if result.error is not None:
                    return result

                return result.success(AssertNode(assertion, pos_start, self.current_token.pos_start.copy(),
                                                 errmsg=errmsg))

            return result.success(AssertNode(assertion, pos_start, self.current_token.pos_start.copy()))

        node = result.register(self.bin_op(self.comp_expr, (
            (TT["KEYWORD"], "and"),
            (TT["KEYWORD"], "or"),
            (TT["KEYWORD"], 'xor'),
            TT["BITWISEAND"],
            TT["BITWISEOR"],
            TT["BITWISEXOR"]
        )))

        if result.error is not None:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "expected 'var', 'del', 'read', 'write', int, float, identifier, 'if', 'for', 'while', 'def', '+', '-',"
                " '(', '[', '|' or 'not'."
            ))

        return result.success(node)

    def comp_expr(self) -> ParseResult:
        result = ParseResult()
        if self.current_token.matches(TT["KEYWORD"], 'not') or self.current_token.type == TT["BITWISENOT"]:
            op_token = self.current_token
            result.register_advancement()
            self.advance()

            node = result.register(self.comp_expr())
            if result.error is not None:
                return result
            return result.success(UnaryOpNode(op_token, node))

        node = result.register(
            self.bin_op(self.arith_expr, (
                TT["EE"],
                TT["NE"],
                TT["LT"],
                TT["GT"],
                TT["LTE"],
                TT["GTE"],
                (TT["KEYWORD"], "in")
            ), left_has_priority=False)
        )
        if result.error is not None:
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     "expected int, float, identifier, '+', '-', '(', '[' or 'not'."))
        return result.success(node)

    def arith_expr(self) -> ParseResult:
        return self.bin_op(self.term, (TT["PLUS"], TT["MINUS"]))

    def term(self) -> ParseResult:
        return self.bin_op(self.factor, (TT["MUL"], TT["DIV"], TT["PERC"], TT["FLOORDIV"]))

    def factor(self) -> ParseResult:
        result = ParseResult()
        token = self.current_token

        if token.type in (TT["PLUS"], TT["MINUS"]):
            result.register_advancement()
            self.advance()
            factor = result.register(self.factor())
            if result.error is not None:
                return result
            return result.success(UnaryOpNode(token, factor))

        return self.power()

    def power(self) -> ParseResult:
        return self.bin_op(self.call, (TT["POW"],), self.factor)  # do not remove the comma after 'TT["POW"]' !!

    def call(self) -> ParseResult:
        result = ParseResult()
        atom = result.register(self.atom())
        if result.error is not None:
            return result

        if self.current_token.type == TT["LPAREN"]:
            call_node = atom

            while self.current_token.type == TT["LPAREN"]:
                result.register_advancement()
                self.advance()
                arg_nodes = []

                if self.current_token.type == TT["RPAREN"]:
                    result.register_advancement()
                    self.advance()
                else:
                    if self.current_token.type == TT["MUL"]:
                        result.register_advancement()
                        self.advance()
                        list_node: ListNode = result.register(self.list_expr())
                        if result.error is not None:
                            return result.failure(
                                InvalidSyntaxError(
                                    self.current_token.pos_start, self.current_token.pos_end,
                                    "expected a list after '*' in call arguments."
                                )
                            )

                        for node in list_node.element_nodes:
                            arg_nodes.append(node)
                    else:
                        arg_nodes.append(result.register(self.expr()))
                        if result.error is not None:
                            return result.failure(
                                InvalidSyntaxError(
                                    self.current_token.pos_start, self.current_token.pos_end,
                                    "expected ')', '*', 'var', 'if', 'for', 'while', 'def', int, float, identifier, '+'"
                                    ", '-', '(', '[' or 'not'."
                                )
                            )

                        while self.current_token.type == TT["COMMA"]:
                            result.register_advancement()
                            self.advance()

                            arg_nodes.append(result.register(self.expr()))
                            if result.error is not None:
                                return result

                    if self.current_token.type != TT["RPAREN"]:
                        return result.failure(
                            InvalidSyntaxError(
                                self.current_token.pos_start, self.current_token.pos_end,
                                "expected ',' or ')'."
                            )
                        )

                    result.register_advancement()
                    self.advance()
                call_node = CallNode(call_node, arg_nodes)

            return result.success(call_node)
        return result.success(atom)

    def atom(self) -> ParseResult:
        result = ParseResult()
        token = self.current_token

        if token.type in (TT["INT"], TT["FLOAT"]):
            result.register_advancement()
            self.advance()
            return result.success(NumberNode(token))
        elif token.type == TT["STRING"]:
            final_string = token.value
            final_token = token.copy()

            result.register_advancement()
            self.advance()

            while self.current_token.type == TT["STRING"]:
                final_string += self.current_token.value

                result.register_advancement()
                self.advance()

            final_token.value = final_string
            return result.success(StringNode(final_token))
        elif token.type == TT["IDENTIFIER"]:
            result.register_advancement()
            self.advance()

            choices = [token]
            while self.current_token.type == TT["INTERROGATIVE_PNT"]:
                result.register_advancement()
                self.advance()
                if self.current_token.type != TT["IDENTIFIER"]:
                    if self.current_token.type in TOKENS_TO_QUOTE:
                        return result.failure(
                            InvalidSyntaxError(
                                self.current_token.pos_start, self.current_token.pos_end,
                                f"expected identifier after '?', but got '{self.current_token.type}'."
                            )
                        )
                    else:
                        return result.failure(
                            InvalidSyntaxError(
                                self.current_token.pos_start, self.current_token.pos_end,
                                f"expected identifier after '?', but got {self.current_token.type}."
                            )
                        )
                choices.append(self.current_token)
                result.register_advancement()
                self.advance()

            return result.success(VarAccessNode(choices))
        elif token.type == TT["LPAREN"]:
            result.register_advancement()
            self.advance()
            expr = result.register(self.expr())
            if result.error is not None:
                return result
            if self.current_token.type == TT["RPAREN"]:
                result.register_advancement()
                self.advance()
                return result.success(expr)
            else:
                return result.failure(
                    InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ')'.")
                )
        elif token.type == TT["LSQUARE"]:
            list_expr = result.register(self.list_expr())
            if result.error is not None:
                return result
            return result.success(list_expr)
        elif token.matches(TT["KEYWORD"], 'if'):
            if_expr = result.register(self.if_expr())
            if result.error is not None:
                return result
            return result.success(if_expr)
        elif token.matches(TT["KEYWORD"], 'for'):
            for_expr = result.register(self.for_expr())
            if result.error is not None:
                return result
            return result.success(for_expr)
        elif token.matches(TT["KEYWORD"], 'while'):
            while_expr = result.register(self.while_expr())
            if result.error is not None:
                return result
            return result.success(while_expr)
        elif token.matches(TT["KEYWORD"], 'do'):
            do_expr = result.register(self.do_expr())
            if result.error is not None:
                return result
            return result.success(do_expr)
        elif token.matches(TT["KEYWORD"], 'def'):
            func_def = result.register(self.func_def())
            if result.error is not None:
                return result
            return result.success(func_def)

        return result.failure(
            InvalidSyntaxError(token.pos_start, token.pos_end, "expected int, float, identifier, 'if', 'for', 'while', "
                                                               "'def', '+', '-', '[' or '('.")
        )

    def list_expr(self) -> ParseResult:
        result = ParseResult()
        element_nodes = []
        pos_start = self.current_token.pos_start.copy()

        if self.current_token.type != TT["LSQUARE"]:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "expected '['."
            ))

        result.register_advancement()
        self.advance()

        if self.current_token.type == TT["RSQUARE"]:
            result.register_advancement()
            self.advance()
        else:
            if self.current_token.type == TT["MUL"]:
                result.register_advancement()
                self.advance()
                list_node: ListNode = result.register(self.list_expr())
                if result.error is not None:
                    return result
                for node in list_node.element_nodes:
                    element_nodes.append(node)
            else:
                element_nodes.append(result.register(self.expr()))
                if result.error is not None:
                    return result.failure(
                        InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end,
                            "expected ']', '*', 'var', 'if', 'for', 'while', 'def', int, float, identifier, '+', '-', "
                            "'(', '[' or 'not'."
                        )
                    )

            while self.current_token.type == TT["COMMA"]:
                result.register_advancement()
                self.advance()

                if self.current_token.type == TT["MUL"]:
                    result.register_advancement()
                    self.advance()
                    list_node: ListNode = result.register(self.list_expr())
                    if result.error is not None:
                        return result
                    for node in list_node.element_nodes:
                        element_nodes.append(node)
                else:
                    element_nodes.append(result.register(self.expr()))
                    if result.error is not None:
                        return result

            if self.current_token.type != TT["RSQUARE"]:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected ',' or ']'."
                    )
                )

            result.register_advancement()
            self.advance()

        return result.success(ListNode(
            element_nodes, pos_start, self.current_token.pos_end.copy()
        ))

    def if_expr(self) -> ParseResult:
        result = ParseResult()
        all_cases = result.register(self.if_expr_cases('if'))
        if result.error is not None:
            return result
        cases, else_cases = all_cases
        return result.success(IfNode(cases, else_cases))

    def if_expr_b(self) -> ParseResult:  # elif
        return self.if_expr_cases("elif")

    def if_expr_c(self) -> ParseResult:  # else
        result = ParseResult()
        else_case = None

        if self.current_token.matches(TT["KEYWORD"], 'else'):
            result.register_advancement()
            self.advance()

            if self.current_token.type == TT["NEWLINE"]:
                result.register_advancement()
                self.advance()

                statements = result.register(self.statements(stop=[(TT["KEYWORD"], 'end')]))
                if result.error is not None:
                    return result
                else_case = (statements, True)

                if self.current_token.matches(TT["KEYWORD"], 'end'):
                    result.register_advancement()
                    self.advance()
                else:
                    return result.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected 'end'."
                    ))
            else:
                expr = result.register(self.statement())
                if result.error is not None:
                    return result
                else_case = (expr, False)

        return result.success(else_case)

    def if_expr_b_or_c(self) -> ParseResult:  # elif elif elif (...) else or just else
        result = ParseResult()
        cases, else_case = [], None

        if self.current_token.matches(TT["KEYWORD"], 'elif'):
            all_cases = result.register(self.if_expr_b())
            if result.error is not None:
                return result
            cases, else_case = all_cases
        else:
            else_case = result.register(self.if_expr_c())
            if result.error is not None:
                return result

        return result.success((cases, else_case))

    def if_expr_cases(self, case_keyword) -> ParseResult:  # how to explain this function ? IDK
        result = ParseResult()
        cases = []
        else_case = None

        if not self.current_token.matches(TT["KEYWORD"], case_keyword):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"expected '{case_keyword}'."
            ))

        result.register_advancement()
        self.advance()

        condition = result.register(self.expr())
        if result.error is not None:
            return result

        if not self.current_token.matches(TT["KEYWORD"], 'then'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end, "expected 'then'."
            ))

        result.register_advancement()
        self.advance()

        if self.current_token.type == TT["NEWLINE"]:
            result.register_advancement()
            self.advance()

            statements = result.register(self.statements(stop=[(TT["KEYWORD"], 'elif'), (TT["KEYWORD"], 'else'),
                                                               (TT["KEYWORD"], 'end')]))
            if result.error is not None:
                return result
            cases.append((condition, statements, True))

            if self.current_token.matches(TT["KEYWORD"], 'end'):
                result.register_advancement()
                self.advance()
            else:
                all_cases = result.register(self.if_expr_b_or_c())
                if result.error is not None:
                    return result
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:  # no newline : single line 'if'
            expr = result.register(self.statement())
            if result.error is not None:
                return result
            cases.append((condition, expr, False))

            all_cases = result.register(self.if_expr_b_or_c())
            if result.error is not None:
                return result
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return result.success((cases, else_case))

    def for_expr(self) -> ParseResult:
        result = ParseResult()
        if not self.current_token.matches(TT["KEYWORD"], 'for'):
            return result.error(InvalidSyntaxError, self.current_token.pos_start, self.current_token.pos_end,
                                "expected 'for'.")

        result.register_advancement()
        self.advance()

        if self.current_token.type != TT["IDENTIFIER"]:
            if self.current_token.type != TT["KEYWORD"]:
                if self.current_token.type not in TOKENS_TO_QUOTE:
                    error_msg = f"expected identifier, but got {self.current_token.type}."
                else:
                    error_msg = f"expected identifier, but got '{self.current_token.type}'."
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end, error_msg
                    )
                )
            else:
                return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                         f"use keyword as identifier is illegal."))

        var_name = self.current_token
        result.register_advancement()
        self.advance()

        if self.current_token.matches(TT["KEYWORD"], 'in'):
            result.register_advancement()
            self.advance()

            list_ = result.register(self.expr())
            if result.error is not None:
                return result

            if not self.current_token.matches(TT["KEYWORD"], 'then'):
                return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                         "expected 'then'."))

            result.register_advancement()
            self.advance()

            if self.current_token.type == TT["NEWLINE"]:
                result.register_advancement()
                self.advance()

                body = result.register(self.statements(stop=[(TT["KEYWORD"], 'end')]))
                if result.error is not None:
                    return result

                if not self.current_token.matches(TT["KEYWORD"], 'end'):
                    return result.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected 'end'."
                    ))

                result.register_advancement()
                self.advance()

                return result.success(ForNodeList(var_name, body, list_, True))

            body = result.register(self.statement())
            if result.error is not None:
                return result

            return result.success(ForNodeList(var_name, body, list_, False))
        elif self.current_token.type != TT["EQ"]:
            if self.current_token.type not in TOKENS_TO_QUOTE:
                error_msg = f"expected 'in' or '=', but got {self.current_token.type}."
            else:
                error_msg = f"expected 'in' or '=', but got '{self.current_token.type}'."
            return result.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end, error_msg
                )
            )

        result.register_advancement()
        self.advance()

        start_value = result.register(self.expr())
        if result.error is not None:
            return result

        if not self.current_token.matches(TT["KEYWORD"], 'to'):
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     f"expected 'to'."))

        result.register_advancement()
        self.advance()

        end_value = result.register(self.expr())
        if result.error is not None:
            return result

        if self.current_token.matches(TT["KEYWORD"], 'step'):
            result.register_advancement()
            self.advance()

            step_value = result.register(self.expr())
            if result.error is not None:
                return result
        else:
            step_value = None

        if not self.current_token.matches(TT["KEYWORD"], 'then'):
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     "expected 'then'."))

        result.register_advancement()
        self.advance()

        if self.current_token.type == TT["NEWLINE"]:
            result.register_advancement()
            self.advance()

            body = result.register(self.statements(stop=[(TT["KEYWORD"], 'end')]))
            if result.error is not None:
                return result

            if not self.current_token.matches(TT["KEYWORD"], 'end'):
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected 'end'."
                ))

            result.register_advancement()
            self.advance()

            return result.success(ForNode(var_name, start_value, end_value, step_value, body, True))

        body = result.register(self.statement())
        if result.error is not None:
            return result

        return result.success(ForNode(var_name, start_value, end_value, step_value, body, False))

    def while_expr(self) -> ParseResult:
        result = ParseResult()

        if not self.current_token.matches(TT["KEYWORD"], 'while'):
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     "expected 'while'."))

        result.register_advancement()
        self.advance()

        condition = result.register(self.expr())
        if result.error is not None:
            return result

        if not self.current_token.matches(TT["KEYWORD"], 'then'):
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     "expected 'then'."))

        result.register_advancement()
        self.advance()

        if self.current_token.type == TT["NEWLINE"]:
            result.register_advancement()
            self.advance()

            body = result.register(self.statements(stop=[(TT["KEYWORD"], 'end')]))
            if result.error is not None:
                return result

            if not self.current_token.matches(TT["KEYWORD"], 'end'):
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected 'end'."
                ))

            result.register_advancement()
            self.advance()

            return result.success(WhileNode(condition, body, True))

        body = result.register(self.statement())
        if result.error is not None:
            return result

        return result.success(WhileNode(condition, body, False))

    def do_expr(self) -> ParseResult:
        result = ParseResult()

        if not self.current_token.matches(TT["KEYWORD"], 'do'):
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     "expected 'do'."))

        result.register_advancement()
        self.advance()

        if self.current_token.type == TT["NEWLINE"]:
            result.register_advancement()
            self.advance()

            body = result.register(self.statements(stop=[(TT["KEYWORD"], 'then')]))
            if result.error is not None:
                return result

            should_return_none = True
        else:
            body = result.register(self.statement())
            if result.error is not None:
                return result

            should_return_none = False

        if not self.current_token.matches(TT["KEYWORD"], 'then'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "expected 'then'."
            ))

        result.register_advancement()
        self.advance()

        if not self.current_token.matches(TT["KEYWORD"], 'loop'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "expected 'loop'."
            ))

        result.register_advancement()
        self.advance()

        if not self.current_token.matches(TT["KEYWORD"], 'while'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "expected 'while'."
            ))

        result.register_advancement()
        self.advance()

        condition = result.register(self.expr())
        if result.error is not None:
            return result

        return result.success(DoWhileNode(body, condition, should_return_none))

    def func_def(self) -> ParseResult:
        result = ParseResult()

        if not self.current_token.matches(TT["KEYWORD"], 'def'):
            return result.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected 'def'."
                )
            )

        result.register_advancement()
        self.advance()

        if self.current_token.type == TT["IDENTIFIER"]:
            var_name_token = self.current_token
            result.register_advancement()
            self.advance()
            if self.current_token.type != TT["LPAREN"]:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected '('."
                    )
                )
        else:
            var_name_token = None
            if self.current_token.type != TT["LPAREN"]:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected identifier or '('."
                    )
                )

        result.register_advancement()
        self.advance()
        param_names_tokens = []

        if self.current_token.type == TT["IDENTIFIER"]:
            param_names_tokens.append(self.current_token)
            result.register_advancement()
            self.advance()

            while self.current_token.type == TT["COMMA"]:
                result.register_advancement()
                self.advance()

                if self.current_token.type != TT["IDENTIFIER"]:
                    if self.current_token.type != TT["KEYWORD"]:
                        if self.current_token.type not in TOKENS_TO_QUOTE:
                            error_msg = f"expected identifier after comma, but got {self.current_token.type}."
                        else:
                            error_msg = f"expected identifier after comma, but got '{self.current_token.type}'."
                        return result.failure(
                            InvalidSyntaxError(
                                self.current_token.pos_start, self.current_token.pos_end, error_msg
                            )
                        )
                    else:
                        return result.failure(
                            InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                               f"expected identifier after coma. "
                                               f"NB : use keyword as identifier is illegal.")
                        )

                param_names_tokens.append(self.current_token)
                result.register_advancement()
                self.advance()

            if self.current_token.type != TT["RPAREN"]:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected ',' or ')'."
                    )
                )
        else:
            if self.current_token.type != TT["RPAREN"]:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected identifier or ')'."
                    )
                )

        result.register_advancement()
        self.advance()

        if self.current_token.type == TT["ARROW"]:
            result.register_advancement()
            self.advance()

            body = result.register(self.expr())
            if result.error is not None:
                return result

            return result.success(FuncDefNode(
                var_name_token,
                param_names_tokens,
                body,
                True
            ))

        if self.current_token.type != TT["NEWLINE"]:
            return result.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected '->' or new line."
                )
            )

        result.register_advancement()
        self.advance()

        body = result.register(self.statements(stop=[(TT["KEYWORD"], 'end')]))
        if result.error is not None:
            return result

        if not self.current_token.matches(TT["KEYWORD"], 'end'):
            return result.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected 'end'."
                )
            )

        result.register_advancement()
        self.advance()

        return result.success(FuncDefNode(
            var_name_token,
            param_names_tokens,
            body,
            False
        ))

    def bin_op(self, func_a, ops, func_b=None, left_has_priority: bool = True) -> ParseResult:
        # param left_has_priority is used to know if we have to parse (for exemple) 3==3==3 into
        # ((int:3, ==, int:3), ==, int:3) or (int:3, ==, int:3, ==, int:3)
        if func_b is None:
            func_b = func_a
        result = ParseResult()
        left = result.register(func_a())
        if result.error is not None:
            return result

        if left_has_priority:
            while self.current_token.type in ops or (self.current_token.type, self.current_token.value) in ops:
                op_token = self.current_token
                result.register_advancement()
                self.advance()
                right = result.register(func_b())
                if result.error is not None:
                    return result
                left = BinOpNode(left, op_token, right)
            return result.success(left)
        else:
            nodes_and_tokens_list = [left]
            while self.current_token.type in ops or (self.current_token.type, self.current_token.value) in ops:
                op_token = self.current_token
                result.register_advancement()
                self.advance()
                right = result.register(func_b())
                if result.error is not None:
                    return result
                nodes_and_tokens_list.append(op_token)
                nodes_and_tokens_list.append(right)
            return result.success(BinOpCompNode(nodes_and_tokens_list))
