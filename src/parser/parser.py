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
from src.lexer.token_types import *
from src.errors.errors import InvalidSyntaxError
from src.parser.parse_result import ParseResult
from src.parser.nodes import *  # src.tokens.Token is imported in src.nodes
from src.lexer.position import Position
# built-in python imports
from typing import Any, Iterable, Callable


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
        self.current_token: Token | None = None  # Token is imported in src.nodes
        self.advance()
        self.then_s: list[tuple[Position, Position]] = []  # pos start then pos end

    def parse(self):
        """Parse tokens and return a result that contain a main node"""
        result = self.statements()
        if result.error is not None and self.current_token.type != TT["EOF"]:
            return result.failure(
                InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                   "expected '+', '-', '*', '/', '//', '%', 'and', 'or' or 'xor'.",
                                   "src.parser.Parser.parse")
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

    def statements(self, stop: list[tuple[Any, str] | str] = None) -> ParseResult:
        """
        statements : NEWLINE* statement (NEWLINE+ statement)* NEWLINE

        The returned node in the parse result is ALWAYS a ListNode here."""
        if stop is None:
            stop = [TT["EOF"]]  # token(s) that stops parser in this function
        result = ParseResult()  # we create the result
        statements = []  # list of statements
        pos_start = self.current_token.pos_start.copy()  # pos_start

        # NEWLINE*
        while self.current_token.type == TT["NEWLINE"]:  # skip new lines
            result.register_advancement()
            self.advance()

        if self.current_token.type == TT["EOF"]:  # End Of File -> nothing to parse!
            return result.success(NoNode())

        last_token_type = self.current_token.type

        # statement
        statement = result.register(self.statement())  # we register a statement
        if result.error is not None:  # we check for errors
            return result
        statements.append((statement, False))  # we append the statement to our list of there is no error

        # (NEWLINE+ statement)*
        while True:  # 'break' inside the loop
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
                                "unexpected token. To declare a variable, use 'var' keyword.",
                                "src.parser.Parser.statements"
                            )
                        )
                    if last_token_type == TT["IDENTIFIER"] and self.current_token.type == TT["COMMA"]:
                        result.register_advancement()
                        self.advance()
                        missing_var = True
                        while self.current_token.type == TT["IDENTIFIER"]:
                            result.register_advancement()
                            self.advance()
                            if self.current_token.type in EQUALS:
                                break  # missing_var is already True
                            if self.current_token.type != TT["COMMA"] and self.current_token.type not in EQUALS:
                                missing_var = False
                                break
                            result.register_advancement()
                            self.advance()
                        if missing_var and self.current_token.type in EQUALS:
                            # there was no new line but there is 'id1, id2, ... =' (need 'var')
                            return result.failure(
                                InvalidSyntaxError(
                                    self.current_token.pos_start, self.current_token.pos_end,
                                    "unexpected token. To declare a variable, use 'var' keyword.",
                                    "src.parser.Parser.statements"
                                )
                            )
                    return result.failure(
                        InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end,
                            f"unexpected token: {self.current_token}.",
                            "src.parser.Parser.statements"
                        )
                    )

            if self.current_token.type == TT["EOF"]:
                if len(self.then_s) != 0:
                    return result.failure(
                        InvalidSyntaxError(
                            self.then_s[-1][0], self.then_s[-1][1],
                            "'end' expected to close a statement, surely this one.",
                            "src.parser.Parser.statements"
                        )
                    )

            # we replace the last token type
            last_token_type = self.current_token.type

            # we register a statement, check for errors and append the statement if all is OK
            # statement
            statement = result.register(self.statement())
            if result.error is not None:
                return result
            statements.append((statement, False))

        return result.success(ListNode(  # we put all the nodes parsed here into a ListNode
            statements,
            pos_start,
            self.current_token.pos_end.copy()
        ))

    def statement(self) -> ParseResult:  # only one statement
        """
        statement  : KEYWORD:RETURN expr?
                   : KEYWORD:IMPORT IDENTIFIER
                   : KEYWORD:EXPORT IDENTIFIER
                   : KEYWORD:CONTINUE
                   : KEYWORD:BREAK
                   : expr
        """
        # we create the result and get the pos start from the current token
        result = ParseResult()
        pos_start = self.current_token.pos_start.copy()

        # we check for tokens

        # KEYWORD:RETURN expr?
        if self.current_token.matches(TT["KEYWORD"], 'return'):
            result.register_advancement()
            self.advance()

            # expr?
            expr = result.try_register(self.expr())  # we try to register an expression
            if expr is None:  # there is no expr : we reverse
                self.reverse(result.to_reverse_count)
            return result.success(ReturnNode(expr, pos_start, self.current_token.pos_start.copy()))

        # KEYWORD:IMPORT IDENTIFIER
        if self.current_token.matches(TT["KEYWORD"], 'import'):
            # we advance
            result.register_advancement()
            self.advance()

            # we check for identifier
            if self.current_token.type != TT["IDENTIFIER"]:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected identifier after 'import'.",
                        "src.parser.Parser.statement"
                    )
                )

            identifier = self.current_token

            result.register_advancement()
            self.advance()

            return result.success(ImportNode(identifier, pos_start, self.current_token.pos_start.copy()))

        if self.current_token.matches(TT["KEYWORD"], 'export'):
            # we advance
            result.register_advancement()
            self.advance()

            # we check for identifier
            if self.current_token.type != TT["IDENTIFIER"]:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected identifier after 'export'.",
                        "src.parser.Parser.statement"
                    )
                )

            identifier = self.current_token

            result.register_advancement()
            self.advance()

            return result.success(ExportNode(identifier, pos_start, self.current_token.pos_start.copy()))

        # KEYWORD:CONTINUE
        if self.current_token.matches(TT["KEYWORD"], 'continue'):
            result.register_advancement()
            self.advance()

            return result.success(ContinueNode(pos_start, self.current_token.pos_start.copy()))

        # KEYWORD:BREAK
        if self.current_token.matches(TT["KEYWORD"], 'break'):
            result.register_advancement()
            self.advance()

            return result.success(BreakNode(pos_start, self.current_token.pos_start.copy()))

        # expr
        expr = result.register(self.expr())
        if result.error is not None:
            return result

        return result.success(expr)

    def expr(self) -> ParseResult:
        """
        expr    : KEYWORD:VAR IDENTIFIER (COMMA IDENTIFIER)?* (EQ|PLUSEQ|MINUSEQ|MULTEQ|DIVEQ|POWEQ|FLOORDIVEQ|PERCEQ|
                    OREQ|ANDEQ|XOREQ|BITWISEANDEQ|BITWISEOREQ|BITWISEXOREQ|EEEQ|GTEQ|GTEEQ|LTEQ|LTEEQ) expr
                    (COMMA expr)?*
                : KEYWORD:DEL IDENTIFIER
                : KEYWORD:WRITE expr (TO|TO_AND_OVERWRITE) expr INT?
                : KEYWORD:READ expr (TO IDENTIFIER)? INT?
                : KEYWORD:ASSERT expr (COMMA expr)?
                : comp_expr ((KEYWORD:AND|KEYWORD:OR|KEYWORD:XOR|BITWISEAND|BITWISEOR|BITWISEXOR) comp_expr)*
        """
        # we create the result and the pos start
        result = ParseResult()
        pos_start = self.current_token.pos_start.copy()

        # KEYWORD:VAR IDENTIFIER (COMMA IDENTIFIER)?* (EQ|...) expr (COMMA expr)?)
        if self.current_token.matches(TT["KEYWORD"], 'var'):
            result.register_advancement()
            self.advance()
            var_names = []

            # we check for identifier
            if self.current_token.type != TT["IDENTIFIER"]:
                if self.current_token.type != TT["KEYWORD"]:
                    if self.current_token.type not in TOKENS_TO_QUOTE:
                        error_msg = f"expected identifier, but got {self.current_token.type}."
                    else:
                        error_msg = f"expected identifier, but got '{self.current_token.type}'."
                    return result.failure(
                        InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end, error_msg,
                            "src.parser.Parser.expr"
                        )
                    )
                else:
                    return result.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "use keyword as identifier is illegal.", "src.parser.Parser.expr"
                    ))

            # IDENTIFIER (COMMA IDENTIFIER)?*
            while self.current_token.type == TT["IDENTIFIER"]:
                var_names.append(self.current_token)

                result.register_advancement()
                self.advance()
                if self.current_token.type != TT["COMMA"]:  # (COMMA IDENTIFIER)?*
                    break

                # there is a comma: next token should be identifier
                result.register_advancement()
                self.advance()
                if self.current_token.type != TT["IDENTIFIER"]:  # return an error.
                    if self.current_token.type != TT["KEYWORD"]:
                        if self.current_token.type not in TOKENS_TO_QUOTE:
                            error_msg = f"expected identifier, but got {self.current_token.type}."
                        else:
                            error_msg = f"expected identifier, but got '{self.current_token.type}'."
                        return result.failure(
                            InvalidSyntaxError(
                                self.current_token.pos_start, self.current_token.pos_end, error_msg,
                                "src.parser.Parser.expr"
                            )
                        )
                    else:
                        return result.failure(InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end,
                            "use keyword as identifier is illegal.", "src.parser.Parser.expr"
                        ))

            # EQUALS is stored in src/token_types.py
            equal = self.current_token
            equals = EQUALS

            # we check if the token is in equal
            if self.current_token.type not in equals:
                if self.current_token.type in [TT["EE"], TT["GT"], TT["LT"], TT["GTE"], TT["LTE"], TT["NE"]]:
                    error_msg = f"expected an assignation equal, but got a test equal ('{self.current_token.type}')."
                elif self.current_token.type not in TOKENS_TO_QUOTE:
                    error_msg = f"expected an equal, but got {self.current_token.type}."
                else:
                    error_msg = f"expected an equal, but got '{self.current_token.type}'."
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end, error_msg, "src.parser.Parser.expr"
                    )
                )

            # we advance
            result.register_advancement()
            self.advance()

            # we register an expr
            expressions = [result.register(self.expr())]
            if result.error is not None:
                return result

            while self.current_token.type == TT["COMMA"]:  # (COMMA expr)?*
                result.register_advancement()
                self.advance()
                expressions.append(result.register(self.expr()))
                if result.error is not None:
                    return result

            return result.success(VarAssignNode(var_names, expressions, equal))

        # KEYWORD:DEL IDENTIFIER
        if self.current_token.matches(TT["KEYWORD"], 'del'):
            result.register_advancement()
            self.advance()

            # if the current tok is not an identifier, return an error
            if self.current_token.type != TT["IDENTIFIER"]:
                if self.current_token.type != TT["KEYWORD"]:
                    if self.current_token.type not in TOKENS_TO_QUOTE:
                        error_msg = f"expected identifier, but got {self.current_token.type}."
                    else:
                        error_msg = f"expected identifier, but got '{self.current_token.type}'."
                    return result.failure(
                        InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end, error_msg,
                            "src.parser.Parser.expr"
                        )
                    )
                else:
                    return result.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "use keyword as identifier is illegal.", "src.parser.Parser.expr"
                    ))

            # we assign the identifier to a variable then we advance
            var_name = self.current_token
            result.register_advancement()
            self.advance()

            if result.error is not None:
                return result
            return result.success(VarDeleteNode(var_name))

        # KEYWORD:WRITE expr (TO|TO_AND_OVERWRITE) expr INT?
        if self.current_token.matches(TT["KEYWORD"], 'write'):
            result.register_advancement()
            self.advance()

            # we check for an expr
            expr_to_write = result.register(self.expr())
            if result.error is not None:
                return result

            # (TO|TO_AND_OVERWRITE)
            if self.current_token.type not in [TT["TO"], TT["TO_AND_OVERWRITE"]]:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "'>>' or '!>>' is missing. The correct syntax is 'write () (!)>> ()'.", "src.parser.Parser.expr"
                    )
                )
            to_token = self.current_token

            result.register_advancement()
            self.advance()

            # we check for an expr
            file_name_expr = result.register(self.expr())
            if result.error is not None:
                return result

            # We check if there is an 'int' token. If not, we will return the default value
            if self.current_token.type == TT["INT"]:
                line_number = self.current_token.value

                result.register_advancement()
                self.advance()
            else:
                line_number = 'last'

            return result.success(WriteNode(expr_to_write, file_name_expr, to_token, line_number, pos_start,
                                            self.current_token.pos_start.copy()))

        # KEYWORD:READ expr (TO IDENTIFIER)? INT?
        if self.current_token.matches(TT["KEYWORD"], 'read'):
            result.register_advancement()
            self.advance()

            # we check for an expr
            file_name_expr = result.register(self.expr())
            if result.error is not None:
                return result

            identifier = None

            # (TO IDENTIFIER)?
            if self.current_token.type == TT["TO"]:
                result.register_advancement()
                self.advance()

                # we check for an identifier
                if self.current_token.type != TT["IDENTIFIER"]:
                    return result.failure(
                        InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end,
                            f"expected identifier, got {self.current_token.type}.", "src.parser.Parser.expr"
                        )
                    )

                identifier = self.current_token

                result.register_advancement()
                self.advance()

            # INT?
            if self.current_token.type == TT["INT"]:
                line_number = self.current_token.value

                result.register_advancement()
                self.advance()
            else:
                line_number = 'all'

            return result.success(ReadNode(file_name_expr, identifier, line_number, pos_start,
                                           self.current_token.pos_start.copy()))

        # KEYWORD:ASSERT expr (COMMA expr)?
        if self.current_token.matches(TT["KEYWORD"], "assert"):
            result.register_advancement()
            self.advance()

            # we check for expr
            assertion = result.register(self.expr())
            if result.error is not None:
                return result

            # we check for comma
            if self.current_token.type == TT["COMMA"]:
                # register an error message to print if the assertion is false.
                # if there is no comma, there is no error message
                result.register_advancement()
                self.advance()

                # we check for an expr
                errmsg = result.register(self.expr())
                if result.error is not None:
                    return result

                return result.success(AssertNode(assertion, pos_start, self.current_token.pos_start.copy(),
                                                 errmsg=errmsg))

            return result.success(AssertNode(assertion, pos_start, self.current_token.pos_start.copy()))

        if self.current_token.matches(TT["KEYWORD"], "end"):
            if len(self.then_s) == 0:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "didn't expect 'end', because there is nothing to close.",
                        "src.parser.Parser.expr"
                    )
                )

        # comp_expr ((KEYWORD:AND|KEYWORD:OR|KEYWORD:XOR|BITWISEAND|BITWISEOR|BITWISEXOR) comp_expr)*
        node = result.register(self.bin_op(self.comp_expr, (
            (TT["KEYWORD"], "and"),
            (TT["KEYWORD"], "or"),
            (TT["KEYWORD"], 'xor'),
            TT["BITWISEAND"],
            TT["BITWISEOR"],
            TT["BITWISEXOR"]
        )))

        if result.error is not None:
            return result

        return result.success(node)

    def comp_expr(self) -> ParseResult:
        """
        comp_expr  : (KEYWORD:NOT|BITWISENOT) comp_expr
                   : arith_expr ((EE|LT|GT|LTE|GTE|KEYWORD:IN) arith_expr)*
        """
        # we create a result
        result = ParseResult()

        # (KEYWORD:NOT|BITWISENOT) comp_expr
        if self.current_token.matches(TT["KEYWORD"], 'not') or self.current_token.type == TT["BITWISENOT"]:
            op_token = self.current_token
            result.register_advancement()
            self.advance()

            # we check for comp_expr
            node = result.register(self.comp_expr())
            if result.error is not None:
                return result
            return result.success(UnaryOpNode(op_token, node))

        # arith_expr ((EE|LT|GT|LTE|GTE|KEYWORD:IN) arith_expr)*
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
            return result
        return result.success(node)

    def arith_expr(self) -> ParseResult:
        """
        arith_expr : term ((PLUS|MINUS) term)*
        """
        # term ((PLUS|MINUS) term)*
        return self.bin_op(self.term, (TT["PLUS"], TT["MINUS"]))

    def term(self) -> ParseResult:
        """
        term       : factor ((MUL|DIV|PERC|FLOORDIV) factor)*
        """
        # factor ((MUL|DIV|PERC|FLOORDIV) factor)*
        return self.bin_op(self.factor, (TT["MUL"], TT["DIV"], TT["PERC"], TT["FLOORDIV"]))

    def factor(self) -> ParseResult:
        """
        factor     : (PLUS|MINUS) factor
                   : power
        """
        result = ParseResult()
        token = self.current_token

        # (PLUS|MINUS) factor
        if token.type in (TT["PLUS"], TT["MINUS"]):
            result.register_advancement()
            self.advance()

            # we check for factor
            factor = result.register(self.factor())
            if result.error is not None:
                return result
            return result.success(UnaryOpNode(token, factor))

        # power
        return self.power()

    def power(self) -> ParseResult:
        """
        power      : call (DOT call)?* (POW factor)*
        """
        # call (DOT call)?*
        result = ParseResult()
        value = result.register(self.call())
        if result.error is not None:
            return result
        values_list = [value]

        while self.current_token.type == TT["DOT"]:
            result.register_advancement()
            self.advance()
            value = result.register(self.call())
            if result.error is not None:
                return result
            values_list.append(value)

        return self.bin_op(values_list, (TT["POW"],), self.factor)  # do not remove the comma after 'TT["POW"]' !!

    def call(self) -> ParseResult:
        """
        call       : atom (LPAREN (MUL? expr (COMMA MUL? expr)?*)? RPAREN)?*
        """
        result = ParseResult()

        # we check for atom
        atom = result.register(self.atom())
        if result.error is not None:
            return result

        # (LPAREN (MUL? expr (COMMA MUL? expr)?*)? RPAREN)?*
        if self.current_token.type == TT["LPAREN"]:
            call_node = atom

            # the '*' at the end of the grammar rule
            # in fact, if we have a()(), we call a, then we call its result. All of that is in one single grammar rule.
            while self.current_token.type == TT["LPAREN"]:
                result.register_advancement()
                self.advance()
                arg_nodes = []

                comma_expected = False
                mul = False
                # we check for the closing paren.
                if self.current_token.type == TT["RPAREN"]:
                    result.register_advancement()
                    self.advance()
                else:  # (MUL? expr (COMMA MUL? expr)?*)?
                    if self.current_token.type == TT["MUL"]:  # MUL?
                        mul = True
                        # we advance
                        result.register_advancement()
                        self.advance()
                    # expr
                    arg_nodes.append(
                        (
                            result.register(self.expr()),
                            mul
                        )
                    )
                    if result.error is not None:
                        return result
                    while self.current_token.type == TT["COMMA"]:  # (COMMA MUL? expr)?*
                        mul = False
                        # we advance
                        result.register_advancement()
                        self.advance()

                        if self.current_token.type == TT["MUL"]:  # MUL?
                            mul = True
                            # we advance
                            result.register_advancement()
                            self.advance()
                        # expr
                        # we register an expr then check for an error
                        arg_nodes.append(
                            (
                                result.register(self.expr()),
                                mul
                            )
                        )
                        if result.error is not None:
                            return result

                    if self.current_token.type != TT["RPAREN"]:  # there is no paren (it is expected)
                        return result.failure(
                            InvalidSyntaxError(
                                self.current_token.pos_start, self.current_token.pos_end,
                                "expected ',' or ')'." if comma_expected else "expected ')'.", "src.parser.Parser.call"
                            )
                        )

                    result.register_advancement()
                    self.advance()
                call_node = CallNode(call_node, arg_nodes)

            return result.success(call_node)
        return result.success(atom)

    def atom(self) -> ParseResult:
        """
        atom  : (INT|FLOAT)(E_INFIX INT)?|(STRING (STRING)?*)|(IDENTIFIER (INTERROGATIVE_PNT IDENTIFIER|expr)?*)
              : LPAREN expr RPAREN
              : list_expr
              : if_expr
              : for_expr
              : while_expr
              : do_expr
              : func_def
        """
        # we create the result
        result = ParseResult()
        token = self.current_token

        # (INT|FLOAT)(E_INFIX INT)?
        if token.type in (TT["INT"], TT["FLOAT"]):
            # we advance
            result.register_advancement()
            self.advance()

            # (E_INFIX INT)?
            if self.current_token.type == TT["E_INFIX"]:
                # we advance
                result.register_advancement()
                self.advance()

                # INT
                if self.current_token.type != TT["INT"]:
                    return result.failure(
                        InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end,
                            f"expected an int here, but got {self.current_token.type}.",
                            "src.parser.Parser.atom"
                        )
                    )
                exp_token = self.current_token

                # we advance
                result.register_advancement()
                self.advance()
                return result.success(NumberENumberNode(token, exp_token))

            # we return a NumberNode
            return result.success(NumberNode(token))

        # STRING (STRING)?*
        elif token.type == TT["STRING"]:
            # this is a useless comment ^^
            # to_return_str is a python str. As we go along the (STRING)?*, we add these to our to_return_str
            to_return_str = token.value  # actually just STRING, not (STRING)?* yet.
            to_return_tok = token.copy()

            # we advance
            result.register_advancement()
            self.advance()

            # (STRING)?*
            while self.current_token.type == TT["STRING"]:
                to_return_str += self.current_token.value

                result.register_advancement()
                self.advance()

            to_return_tok.value = to_return_str
            return result.success(StringNode(to_return_tok))

        # IDENTIFIER (INTERROGATIVE_PNT IDENTIFIER|expr)?*
        elif token.type == TT["IDENTIFIER"]:
            # the identifier is in the token in 'token'
            # we advance
            result.register_advancement()
            self.advance()

            # IDENTIFIER
            # choices represent all the identifiers in atoms such as 'foo ? bar ? foo_ ? bar_'
            choices = [token]
            # (INTERROGATIVE_PNT IDENTIFIER)?*
            while self.current_token.type == TT["INTERROGATIVE_PNT"]:
                # we advance
                result.register_advancement()
                self.advance()

                value = self.current_token
                # we check for identifier
                if self.current_token.type != TT["IDENTIFIER"]:
                    value = result.register(self.expr())  # eventually, the user could use a value instead of an
                    #                                       identifier
                    if result.error is not None:
                        return result
                    # append the token to our list
                    choices.append(value)
                    break  # the expr is the final value we want to parse
                    #        E.g.: `identifier ? identifier ? expr ? whatever` : we don't want the `? whatever`

                # append the token to our list
                choices.append(value)
                # we advance
                result.register_advancement()
                self.advance()

            return result.success(VarAccessNode(choices))

        # LPAREN expr RPAREN
        elif token.type == TT["LPAREN"]:
            # we advance
            result.register_advancement()
            self.advance()
            # we register an expr
            expr = result.register(self.expr())
            if result.error is not None:  # we check for any error
                return result
            # we check for right parenthesis
            if self.current_token.type == TT["RPAREN"]:
                # we advance and then return our expr
                result.register_advancement()
                self.advance()

                return result.success(expr)
            else:  # we return an error message
                return result.failure(
                    InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ')'.",
                                       "src.parser.Parser.atom")
                )

        # list_expr
        elif token.type == TT["LSQUARE"]:
            list_expr = result.register(self.list_expr())
            if result.error is not None:  # we check for error
                return result
            return result.success(list_expr)
        # if_expr
        elif token.matches(TT["KEYWORD"], 'if'):
            if_expr = result.register(self.if_expr())
            if result.error is not None:  # We check for errors
                return result
            return result.success(if_expr)
        # for_expr
        elif token.matches(TT["KEYWORD"], 'for'):
            for_expr = result.register(self.for_expr())
            if result.error is not None:  # We check for errors
                return result
            return result.success(for_expr)
        # while_expr
        elif token.matches(TT["KEYWORD"], 'while'):
            while_expr = result.register(self.while_expr())
            if result.error is not None:  # We check for errors
                return result
            return result.success(while_expr)
        # do_expr
        elif token.matches(TT["KEYWORD"], 'do'):
            do_expr = result.register(self.do_expr())
            if result.error is not None:  # We check for errors
                return result
            return result.success(do_expr)
        # func_def
        elif token.matches(TT["KEYWORD"], 'def'):
            func_def = result.register(self.func_def())
            if result.error is not None:  # We check for errors
                return result
            return result.success(func_def)
        # class_def
        elif token.matches(TT["KEYWORD"], 'class'):
            class_def = result.register(self.class_def())
            if result.error is not None:  # We check for errors
                return result
            return result.success(class_def)

        if self.current_token.matches(TT["KEYWORD"], "else"):
            return result.failure(
                InvalidSyntaxError(token.pos_start, token.pos_end,
                                   "expected valid expression. Maybe you forgot to close an 'end'?",
                                   "src.parser.Parser.atom")
            )

        return result.failure(
            InvalidSyntaxError(token.pos_start, token.pos_end, "expected valid expression.",
                               "src.parser.Parser.atom")
        )

    def list_expr(self) -> ParseResult:
        """
        list_expr  : LSQUARE (MUL? expr (COMMA MUL? expr)?*)? RSQUARE
        """
        # we create the result
        result = ParseResult()
        # the python list that will contain the nougaro list's elements
        element_nodes = []
        # we copy the current token pos start
        pos_start = self.current_token.pos_start.copy()
        first_tok_pos_end = self.current_token.pos_end.copy()

        mul = False

        if self.current_token.type != TT["LSQUARE"]:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "expected '['.", "src.parser.Parser.list_expr"
            ))

        # we advance
        result.register_advancement()
        self.advance()

        if self.current_token.type == TT["RSQUARE"]:  # ] : we close the list
            result.register_advancement()
            self.advance()
        else:  # there are elements
            # MUL? expr (COMMA MUL? expr)?*
            if self.current_token.type == TT["MUL"]:  # MUL?
                mul = True
                # we advance
                result.register_advancement()
                self.advance()
            # expr
            # we register an expr then check for an error
            element_nodes.append(
                (
                    result.register(self.expr()),
                    mul
                )
            )
            if result.error is not None:
                return result

            while self.current_token.type == TT["COMMA"]:  # (COMMA MUL? expr)?*
                mul = False
                # we advance
                result.register_advancement()
                self.advance()

                if self.current_token.type == TT["MUL"]:  # MUL?
                    mul = True
                    # we advance
                    result.register_advancement()
                    self.advance()
                # expr
                # we register an expr then check for an error
                element_nodes.append(
                    (
                        result.register(self.expr()),
                        mul
                    )
                )
                if result.error is not None:
                    return result

            if self.current_token.type != TT["RSQUARE"]:  # there is no ']' to close the list
                return result.failure(
                    InvalidSyntaxError(
                        pos_start, first_tok_pos_end,
                        "'[' was never closed.",
                        "src.parser.Parser.list_expr"
                    )
                )

            # we advance
            result.register_advancement()
            self.advance()

        return result.success(ListNode(
            element_nodes, pos_start, self.current_token.pos_end.copy()
        ))

    def if_expr(self) -> ParseResult:
        """
        if_expr : KEYWORD:IF expr KEYWORD:THEN
                  ((statement if_expr_b|if_expr_c?)
                  | (NEWLINE statements KEYWORD:END|if_expr_b|if_expr_c))
        """
        result = ParseResult()
        # we register our if expr using a super cool function
        all_cases = result.register(self.if_expr_cases('if'))
        if result.error is not None:
            return result
        # we unpack the values. cases are 'if' and 'elif's, else_cases is 'else'
        cases, else_case = all_cases
        return result.success(IfNode(cases, else_case))

    def if_expr_b(self) -> ParseResult:  # elif
        """
        if_expr_b : KEYWORD:ELIF expr KEYWORD:THEN
                    ((statement if_expr_b|if_expr_c?)
                    | (NEWLINE statements KEYWORD:END|if_expr_b|if_expr_c))
        """
        return self.if_expr_cases("elif")

    def if_expr_c(self) -> ParseResult:  # else
        """
        if_expr_c : KEYWORD:ELSE
                    (statement
                    | (NEWLINE statements KEYWORD:END))
        """
        result = ParseResult()
        # as we know so far, there is no 'else' structure
        else_case = None

        # now we know there is a 'else' keyword
        if self.current_token.matches(TT["KEYWORD"], 'else'):
            else_tok_pos = [self.current_token.pos_start.copy(), self.current_token.pos_end.copy()]
            # we advance
            result.register_advancement()
            self.advance()

            # (NEWLINE statements KEYWORD:END)
            if self.current_token.type == TT["NEWLINE"]:
                # we advance
                result.register_advancement()
                self.advance()

                # we register our statements, and we stop at an 'end' keyword.
                statements = result.register(self.statements(stop=[(TT["KEYWORD"], 'end')]))
                if result.error is not None:
                    return result
                else_case = statements

                if self.current_token.matches(TT["KEYWORD"], 'end'):
                    del self.then_s[-1]
                    # we advance
                    result.register_advancement()
                    self.advance()
                else:
                    # it happens only in one case:
                    # if condition then
                    #   expr
                    # else
                    # (EOF)
                    return result.failure(InvalidSyntaxError(
                        *else_tok_pos,
                        "expected 'end' to close this 'else'.",
                        "src.parser.Parser.if_expr_c"
                    ))
            else:  # there is no newline: statement
                expr = result.register(self.statement())
                if result.error is not None:
                    return result
                else_case = expr

        return result.success(else_case)

    def if_expr_b_or_c(self) -> ParseResult:  # elif elif elif (...) else or just else
        result = ParseResult()
        # cases are all the 'elif' cases and else_case is None so far.
        cases, else_case = [], None

        # KEYWORD:ELIF statement
        if self.current_token.matches(TT["KEYWORD"], 'elif'):
            all_cases = result.register(self.if_expr_b())
            if result.error is not None:
                return result
            cases, else_case = all_cases
        else:  # KEYWORD:ELSE statement
            else_case = result.register(self.if_expr_c())
            if result.error is not None:
                return result

        return result.success((cases, else_case))

    def if_expr_cases(self, case_keyword) -> ParseResult:
        result = ParseResult()
        cases = []
        else_case = None

        if not self.current_token.matches(TT["KEYWORD"], case_keyword):  # there is no 'elif' nor 'else'
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"expected '{case_keyword}'.",
                "src.parser.Parser.if_expr_cases"
            ))

        result.register_advancement()
        self.advance()

        # condition expr
        condition = result.register(self.expr())
        if result.error is not None:
            return result

        # then keyword
        if not self.current_token.matches(TT["KEYWORD"], 'then'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end, "expected 'then'.",
                "src.parser.Parser.if_expr_cases"
            ))
        then_tok = self.current_token.copy()

        result.register_advancement()
        self.advance()

        # NEWLINE statements (if_expr_b|if_expr_c?)*? KEYWORD:END
        if self.current_token.type == TT["NEWLINE"]:
            self.then_s.append((then_tok.pos_start, then_tok.pos_end))
            result.register_advancement()
            self.advance()

            # statements that end at any 'elif', 'else' or 'end'
            statements = result.register(self.statements(stop=[(TT["KEYWORD"], 'elif'), (TT["KEYWORD"], 'else'),
                                                               (TT["KEYWORD"], 'end')]))
            if result.error is not None:
                return result
            cases.append((condition, statements))

            if self.current_token.matches(TT["KEYWORD"], 'end'):
                del self.then_s[-1]
                result.register_advancement()
                self.advance()
            else:
                all_cases = result.register(self.if_expr_b_or_c())  # elif or else
                if result.error is not None:
                    return result
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:  # no newline : single line 'if'
            # expr
            expr = result.register(self.statement())
            if result.error is not None:
                return result
            cases.append((condition, expr))

            # (if_expr_b|if_expr_c?)*?
            all_cases = result.register(self.if_expr_b_or_c())
            if result.error is not None:
                return result
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return result.success((cases, else_case))

    def for_expr(self) -> ParseResult:
        """
        for_expr   : KEYWORD:FOR IDENTIFIER EQ expr KEYWORD:TO expr (KEYWORD:STEP expr)? KEYWORD:THEN
                     statement | (NEWLINE statements KEYWORD:END)
                   : KEYWORD:FOR IDENTIFIER KEYWORD:IN expr KEYWORD:THEN
                     statement | (NEWLINE statements KEYWORD:END)
        """
        result = ParseResult()
        if not self.current_token.matches(TT["KEYWORD"], 'for'):
            return result.error(InvalidSyntaxError, self.current_token.pos_start, self.current_token.pos_end,
                                "expected 'for'.",
                                "src.parser.Parser.for_expr")
        for_tok = self.current_token.copy()

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
                        self.current_token.pos_start, self.current_token.pos_end, error_msg,
                        "src.parser.Parser.for_expr"
                    )
                )
            else:
                return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                         f"use keyword as identifier is illegal.",
                                                         "src.parser.Parser.for_expr"))

        # IDENTIFIER
        var_name = self.current_token
        result.register_advancement()
        self.advance()

        # KEYWORD:IN expr KEYWORD:THEN statement | (NEWLINE statements KEYWORD:END)
        if self.current_token.matches(TT["KEYWORD"], 'in'):
            result.register_advancement()
            self.advance()

            # expr
            iterable_ = result.register(self.expr())
            if result.error is not None:
                return result

            # KEYWORD:THEN
            if not self.current_token.matches(TT["KEYWORD"], 'then'):
                return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                         "expected 'then'.",
                                                         "src.parser.Parser.for_expr"))
            then_tok = self.current_token.copy()

            result.register_advancement()
            self.advance()

            # NEWLINE statements KEYWORD:END
            if self.current_token.type == TT["NEWLINE"]:
                self.then_s.append((then_tok.pos_start, then_tok.pos_end))
                result.register_advancement()
                self.advance()

                # statements
                body = result.register(self.statements(stop=[(TT["KEYWORD"], 'end')]))
                if result.error is not None:
                    return result

                if not self.current_token.matches(TT["KEYWORD"], 'end'):
                    return result.failure(InvalidSyntaxError(
                        for_tok.pos_start, for_tok.pos_end,
                        "this 'for' was never closed (by 'end').",
                        "src.parser.Parser.for_expr"
                    ))
                del self.then_s[-1]

                result.register_advancement()
                self.advance()

                return result.success(ForNodeList(var_name, body, iterable_))

            # statement
            body = result.register(self.statement())
            if result.error is not None:
                return result

            return result.success(ForNodeList(var_name, body, iterable_))
        elif self.current_token.type != TT["EQ"]:
            if self.current_token.type not in TOKENS_TO_QUOTE:
                error_msg = f"expected 'in' or '=', but got {self.current_token.type}."
            else:
                error_msg = f"expected 'in' or '=', but got '{self.current_token.type}'."
            return result.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end, error_msg, "src.parser.Parser.for_expr"
                )
            )

        # EQ expr KEYWORD:TO expr (KEYWORD:STEP expr)? KEYWORD:THEN statement | (NEWLINE statements KEYWORD:END)
        result.register_advancement()
        self.advance()

        # expr
        start_value = result.register(self.expr())
        if result.error is not None:
            return result

        # KEYWORD:TO
        if not self.current_token.matches(TT["KEYWORD"], 'to'):
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     f"expected 'to'.", "src.parser.Parser.for_expr"))

        result.register_advancement()
        self.advance()

        # expr
        end_value = result.register(self.expr())
        if result.error is not None:
            return result

        # (KEYWORD:STEP expr)?
        if self.current_token.matches(TT["KEYWORD"], 'step'):
            result.register_advancement()
            self.advance()

            # expr
            step_value = result.register(self.expr())
            if result.error is not None:
                return result
        else:
            step_value = None

        # KEYWORD:THEN
        if not self.current_token.matches(TT["KEYWORD"], 'then'):
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     "expected 'then'.", "src.parser.Parser.for_expr"))
        then_tok = self.current_token.copy()

        result.register_advancement()
        self.advance()

        # NEWLINE statements KEYWORD:END
        if self.current_token.type == TT["NEWLINE"]:
            self.then_s.append((then_tok.pos_start, then_tok.pos_end))
            result.register_advancement()
            self.advance()

            # statements
            body = result.register(self.statements(stop=[(TT["KEYWORD"], 'end')]))

            # KEYWORD:END
            if not self.current_token.matches(TT["KEYWORD"], 'end'):
                return result.failure(InvalidSyntaxError(
                    for_tok.pos_start, for_tok.pos_end,
                    "this 'for' was never closed (by 'end').", "src.parser.Parser.for_expr"
                ))
            del self.then_s[-1]

            if result.error is not None:
                return result

            result.register_advancement()
            self.advance()

            return result.success(ForNode(var_name, start_value, end_value, step_value, body))

        # statement
        body = result.register(self.statement())
        if result.error is not None:
            return result

        return result.success(ForNode(var_name, start_value, end_value, step_value, body))

    def while_expr(self) -> ParseResult:
        result = ParseResult()

        # KEYWORD:WHILE expr KEYWORD:THEN statement | (NEWLINE statements KEYWORD:END)
        if not self.current_token.matches(TT["KEYWORD"], 'while'):
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     "expected 'while'.", "src.parser.Parser.while_expr"))

        result.register_advancement()
        self.advance()

        # expr
        condition = result.register(self.expr())
        if result.error is not None:
            return result

        # KEYWORD:THEN
        if not self.current_token.matches(TT["KEYWORD"], 'then'):
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     "expected 'then'.", "src.parser.Parser.while_expr"))
        then_tok = self.current_token.copy()

        result.register_advancement()
        self.advance()

        # NEWLINE statements KEYWORD:END
        if self.current_token.type == TT["NEWLINE"]:
            self.then_s.append((then_tok.pos_start, then_tok.pos_end))
            result.register_advancement()
            self.advance()

            # statements
            body = result.register(self.statements(stop=[(TT["KEYWORD"], 'end')]))
            if result.error is not None:
                return result

            # KEYWORD:END
            if not self.current_token.matches(TT["KEYWORD"], 'end'):
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected 'end'.", "src.parser.Parser.while_expr"
                ))
            del self.then_s[-1]

            result.register_advancement()
            self.advance()

            return result.success(WhileNode(condition, body))

        # statement
        body = result.register(self.statement())
        if result.error is not None:
            return result

        return result.success(WhileNode(condition, body))

    def do_expr(self) -> ParseResult:
        """
        KEYWORD:DO (statement | (NEWLINE statements NEWLINE)) KEYWORD:THEN KEYWORD:LOOP KEYWORD:WHILE expr
        """
        result = ParseResult()

        if not self.current_token.matches(TT["KEYWORD"], 'do'):
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     "expected 'do'.", "src.parser.Parser.do_expr"))

        result.register_advancement()
        self.advance()

        # NEWLINE statements NEWLINE
        if self.current_token.type == TT["NEWLINE"]:
            result.register_advancement()
            self.advance()

            # statements
            body = result.register(self.statements(stop=[(TT["KEYWORD"], 'then')]))
            if result.error is not None:
                return result
        else:
            # statement
            body = result.register(self.statement())
            if result.error is not None:
                return result

        # KEYWORD:THEN
        if not self.current_token.matches(TT["KEYWORD"], 'then'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "expected 'then'.", "src.parser.Parser.do_expr"
            ))

        result.register_advancement()
        self.advance()

        # KEYWORD:LOOP
        if not self.current_token.matches(TT["KEYWORD"], 'loop'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "expected 'loop'.", "src.parser.Parser.do_expr"
            ))

        result.register_advancement()
        self.advance()

        # KEYWORD:WHILE
        if not self.current_token.matches(TT["KEYWORD"], 'while'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "expected 'while'.", "src.parser.Parser.do_expr"
            ))

        result.register_advancement()
        self.advance()

        # expr
        condition = result.register(self.expr())
        if result.error is not None:
            return result

        return result.success(DoWhileNode(body, condition))

    def func_def(self) -> ParseResult:
        """
            KEYWORD:DEF IDENTIFIER?
            LPAREN (IDENTIFIER (COMMA IDENTIFIER)*)? RPAREN
            (ARROW expr)
            | (NEWLINE statements KEYWORD:END)
        """
        result = ParseResult()

        if not self.current_token.matches(TT["KEYWORD"], 'def'):
            return result.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected 'def'.", "src.parser.Parser.func_def"
                )
            )
        def_tok = self.current_token.copy()

        result.register_advancement()
        self.advance()

        # IDENTIFIER?
        if self.current_token.type == TT["IDENTIFIER"]:
            var_name_token = self.current_token
            result.register_advancement()
            self.advance()

            # LPAREN
            if self.current_token.type != TT["LPAREN"]:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected '('.", "src.parser.Parser.func_def"
                    )
                )
        else:
            var_name_token = None
            # LPAREN
            if self.current_token.type != TT["LPAREN"]:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected identifier or '('.", "src.parser.Parser.func_def"
                    )
                )

        result.register_advancement()
        self.advance()
        param_names_tokens = []

        # (IDENTIFIER (COMMA IDENTIFIER)*)?
        if self.current_token.type == TT["IDENTIFIER"]:
            param_names_tokens.append(self.current_token)
            result.register_advancement()
            self.advance()

            # (COMMA IDENTIFIER)?
            while self.current_token.type == TT["COMMA"]:
                result.register_advancement()
                self.advance()

                # IDENTIFIER
                if self.current_token.type != TT["IDENTIFIER"]:
                    if self.current_token.type != TT["KEYWORD"]:
                        if self.current_token.type not in TOKENS_TO_QUOTE:
                            error_msg = f"expected identifier after comma, but got {self.current_token.type}."
                        else:
                            error_msg = f"expected identifier after comma, but got '{self.current_token.type}'."
                        return result.failure(
                            InvalidSyntaxError(
                                self.current_token.pos_start, self.current_token.pos_end, error_msg,
                                "src.parser.Parser.func_def"
                            )
                        )
                    else:
                        return result.failure(
                            InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                               f"expected identifier after coma. "
                                               f"NB : use keyword as identifier is illegal.",
                                               "src.parser.Parser.func_def")
                        )

                param_names_tokens.append(self.current_token)
                result.register_advancement()
                self.advance()

            # RPAREN
            if self.current_token.type != TT["RPAREN"]:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected ',' or ')'.", "src.parser.Parser.func_def"
                    )
                )
        else:
            # RPAREN
            if self.current_token.type != TT["RPAREN"]:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected identifier or ')'.", "src.parser.Parser.func_def"
                    )
                )

        result.register_advancement()
        self.advance()

        # ARROW expr
        if self.current_token.type == TT["ARROW"]:
            result.register_advancement()
            self.advance()

            # expr
            body = result.register(self.expr())
            if result.error is not None:
                return result

            return result.success(FuncDefNode(
                var_name_token,
                param_names_tokens,
                body,
                should_auto_return=True
            ))

        # NEWLINE statements KEYWORD:END
        if self.current_token.type != TT["NEWLINE"]:
            return result.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected '->' or new line.", "src.parser.Parser.func_def"
                )
            )

        result.register_advancement()
        self.advance()

        self.then_s.append((def_tok.pos_start, def_tok.pos_end))

        # statements
        body = result.register(self.statements(stop=[(TT["KEYWORD"], 'end')]))
        if result.error is not None:
            return result

        # KEYWORD:END
        if not self.current_token.matches(TT["KEYWORD"], 'end'):
            return result.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected 'end'.", "src.parser.Parser.func_def"
                )
            )
        del self.then_s[-1]

        result.register_advancement()
        self.advance()

        return result.success(FuncDefNode(
            var_name_token,
            param_names_tokens,
            body,
            False
        ))

    def class_def(self) -> ParseResult:
        """
            KEYWORD:CLASS IDENTIFIER?
            (LPAREN IDENTIFIER? RPAREN)?
            (ARROW expr)
          | (NEWLINE statements KEYWORD:END)
        """
        result = ParseResult()

        if not self.current_token.matches(TT["KEYWORD"], 'class'):
            return result.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected 'class'.", "src.parser.Parser.class_def"
                )
            )
        class_tok = self.current_token.copy()

        result.register_advancement()
        self.advance()

        # IDENTIFIER?
        if self.current_token.type == TT["IDENTIFIER"]:
            var_name_token = self.current_token
            result.register_advancement()
            self.advance()
        else:
            var_name_token = None

        # (LPAREN IDENTIFIER? RPAREN)?
        # LPAREN
        if self.current_token.type == TT["LPAREN"]:
            result.register_advancement()
            self.advance()

            # IDENTIFIER?
            if self.current_token.type == TT["IDENTIFIER"]:
                parent_var_name_tok = self.current_token
                result.register_advancement()
                self.advance()
            else:
                parent_var_name_tok = None

            # RPAREN
            if self.current_token.type != TT["RPAREN"]:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected ')'.", "src.parser.Parser.class_def"
                    )
                )

            result.register_advancement()
            self.advance()
        else:
            parent_var_name_tok = None

        # ARROW expr
        if self.current_token.type == TT["ARROW"]:
            result.register_advancement()
            self.advance()

            # expr
            body = result.register(self.expr())
            if result.error is not None:
                return result

            return result.success(ClassNode(
                var_name_token,
                parent_var_name_tok,
                body,
                should_auto_return=True
            ))

        # NEWLINE statements KEYWORD:END
        if self.current_token.type != TT["NEWLINE"]:
            return result.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected '->' or new line.", "src.parser.Parser.func_def"
                )
            )

        result.register_advancement()
        self.advance()

        self.then_s.append((class_tok.pos_start, class_tok.pos_end))

        # statements
        body = result.register(self.statements(stop=[(TT["KEYWORD"], 'end')]))
        if result.error is not None:
            return result

        # KEYWORD:END
        if not self.current_token.matches(TT["KEYWORD"], 'end'):
            return result.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected 'end'.", "src.parser.Parser.func_def"
                )
            )
        del self.then_s[-1]

        result.register_advancement()
        self.advance()

        return result.success(ClassNode(
            var_name_token,
            parent_var_name_tok,
            body,
            should_auto_return=False
        ))

    def bin_op(
            self,
            func_a: Callable | list[Node],
            ops: Iterable[str | tuple[str, Any]],
            func_b: Callable | list[Node] = None,
            left_has_priority: bool = True
    ) -> ParseResult:
        """Binary operator such as 1+1 or 3==2"""
        # if any func is a list, like [foo, bar()], the func is foo.bar()
        # param left_has_priority is used to know if we have to parse (for exemple) 3==3==3 into
        # ((int:3, ==, int:3), ==, int:3) (True) or (int:3, ==, int:3, ==, int:3) (False)
        # ops is possible ops in a list
        result = ParseResult()
        if not isinstance(func_a, list):  # we check if the value 'a' is a list or a function
            if func_b is None:  # func_b is None
                func_b = func_a
            left = result.register(func_a())  # we register func_a as the left operand
            if result.error is not None:
                return result
        else:
            left = func_a  # func_a is a list : this is the left operand

        if left_has_priority:
            while self.current_token.type in ops or (self.current_token.type, self.current_token.value) in ops:
                op_token = self.current_token  # operator token
                result.register_advancement()  # we advance
                self.advance()
                if not isinstance(func_b, list):  # we check if func_b is a list or a function
                    right = result.register(func_b())
                    if result.error is not None:
                        return result
                else:
                    right = func_b  # it is a list
                left = BinOpNode(left, op_token, right)  # we update our left, and we loop to the next operand
            return result.success(left)
        else:
            nodes_and_tokens_list = [left]
            while self.current_token.type in ops or (self.current_token.type, self.current_token.value) in ops:
                # check comments above
                op_token = self.current_token
                result.register_advancement()
                self.advance()
                if not isinstance(func_b, list):
                    right = result.register(func_b())
                    if result.error is not None:
                        return result
                else:
                    right = func_b
                # we add our operator and operand to our list
                nodes_and_tokens_list.append(op_token)
                nodes_and_tokens_list.append(right)
            return result.success(BinOpCompNode(nodes_and_tokens_list))
