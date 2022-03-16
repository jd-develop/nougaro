#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# IMPORTS
# nougaro modules imports
from src.token_constants import *
from src.errors import InvalidSyntaxError
from src.parse_result import ParseResult
from src.nodes import *  # src.tokens.Token is imported in src.nodes
# built-in python imports
# no imports


# ##########
# PARSER
# ##########
class Parser:
    """
        Please see grammar.txt for operation priority.
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.current_token: Token = None  # Token is imported in src.nodes
        self.advance()

    def parse(self):
        result = self.statements()
        if result.error is not None and self.current_token.type != TT_EOF:
            return result.failure(
                InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                   "expected '+', '-', '*', '/', '//', '%', 'and', 'or' or 'xor'.")
            )
        return result

    def advance(self):
        self.token_index += 1
        self.update_current_token()
        return self.current_token

    def reverse(self, amount: int = 1):
        # this is just the opposite of self.advance ^^
        self.token_index -= amount
        self.update_current_token()
        return self.current_token

    def update_current_token(self):
        if 0 <= self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]

    # GRAMMARS ATOMS (AST) :

    def statements(self):
        result = ParseResult()
        statements = []
        pos_start = self.current_token.pos_start.copy()

        while self.current_token.type == TT_NEWLINE:
            result.register_advancement()
            self.advance()

        if self.current_token.type == TT_EOF:
            return result.success(NoNode())

        statement = result.register(self.statement())
        if result.error is not None:
            return result
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.current_token.type == TT_NEWLINE:
                result.register_advancement()
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False

            if not more_statements:
                break
            statement = result.try_register(self.statement())
            if statement is None:
                self.reverse(result.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)

        return result.success(ListNode(
            statements,
            pos_start,
            self.current_token.pos_end.copy()
        ))

    def statement(self):
        result = ParseResult()
        pos_start = self.current_token.pos_start.copy()

        if self.current_token.matches(TT_KEYWORD, 'return'):
            result.register_advancement()
            self.advance()

            expr = result.try_register(self.expr())
            if expr is None:
                self.reverse(result.to_reverse_count)
            return result.success(ReturnNode(expr, pos_start, self.current_token.pos_start.copy()))

        if self.current_token.matches(TT_KEYWORD, 'continue'):
            result.register_advancement()
            self.advance()

            return result.success(ContinueNode(pos_start, self.current_token.pos_start.copy()))

        if self.current_token.matches(TT_KEYWORD, 'break'):
            result.register_advancement()
            self.advance()

            return result.success(BreakNode(pos_start, self.current_token.pos_start.copy()))

        expr = result.register(self.expr())
        if result.error is not None:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "expected 'var', int, float, identifier, 'if', 'for', 'while', 'def', 'continue', 'break', 'return', "
                "'+', '-', '(', '[', '|' or 'not'."
            ))

        return result.success(expr)

    def expr(self):
        result = ParseResult()
        if self.current_token.matches(TT_KEYWORD, 'var'):
            result.register_advancement()
            self.advance()

            if self.current_token.type != TT_IDENTIFIER:
                if self.current_token.type != TT_KEYWORD:
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
            equals = [TT_EQ, TT_PLUSEQ, TT_MINUSEQ, TT_MULTEQ, TT_DIVEQ, TT_POWEQ, TT_FLOORDIVEQ, TT_PERCEQ]

            if self.current_token.type not in equals:
                if self.current_token.type not in TOKENS_TO_QUOTE:
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

        if self.current_token.matches(TT_KEYWORD, 'del'):
            result.register_advancement()
            self.advance()

            if self.current_token.type != TT_IDENTIFIER:
                if self.current_token.type != TT_KEYWORD:
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

        node = result.register(self.bin_op(self.comp_expr, (
            (TT_KEYWORD, "and"), (TT_KEYWORD, "or"), (TT_KEYWORD, 'xor'))))

        if result.error is not None:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "expected 'var', int, float, identifier, 'if', 'for', 'while', 'def', '+', '-', '(', '[', '|' or 'not'."
            ))

        return result.success(node)

    def comp_expr(self):
        result = ParseResult()
        if self.current_token.matches(TT_KEYWORD, 'not'):
            op_token = self.current_token
            result.register_advancement()
            self.advance()

            node = result.register(self.comp_expr())
            if result.error is not None:
                return result
            return result.success(UnaryOpNode(op_token, node))

        node = result.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE,
                                                             (TT_KEYWORD, "in")),
                                           left_has_priority=False))
        if result.error is not None:
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     "expected int, float, identifier, '+', '-', '(', '[' or 'not'."))
        return result.success(node)

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV, TT_PERC, TT_FLOORDIV))

    def factor(self):
        result = ParseResult()
        token = self.current_token

        if token.type in (TT_PLUS, TT_MINUS):
            result.register_advancement()
            self.advance()
            factor = result.register(self.factor())
            if result.error is not None:
                return result
            return result.success(UnaryOpNode(token, factor))

        return self.power()

    def power(self):
        return self.bin_op(self.call, (TT_POW,), self.factor)

    def call(self):
        result = ParseResult()
        abs_ = result.register(self.abs_())
        if result.error is not None:
            return result

        if self.current_token.type == TT_LPAREN:
            call_node = abs_

            while self.current_token.type == TT_LPAREN:
                result.register_advancement()
                self.advance()
                arg_nodes = []

                if self.current_token.type == TT_RPAREN:
                    result.register_advancement()
                    self.advance()
                else:
                    arg_nodes.append(result.register(self.expr()))
                    if result.error is not None:
                        return result.failure(
                            InvalidSyntaxError(
                                self.current_token.pos_start, self.current_token.pos_end,
                                "expected ')', 'var', 'if', 'for', 'while', 'def', int, float, identifier, '+', '-', "
                                "'(', '[' or 'not'."
                            )
                        )

                    while self.current_token.type == TT_COMMA:
                        result.register_advancement()
                        self.advance()

                        arg_nodes.append(result.register(self.expr()))
                        if result.error is not None:
                            return result

                    if self.current_token.type != TT_RPAREN:
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
        return result.success(abs_)

    def abs_(self):
        result = ParseResult()

        if self.current_token.type == TT_ABS:
            result.register_advancement()
            self.advance()
            expr = result.register(self.expr())
            if result.error is not None:
                return result
            if self.current_token.type != TT_ABS:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected '|'."
                    )
                )
            result.register_advancement()
            self.advance()
            return result.success(AbsNode(expr))
        else:
            atom = result.register(self.atom())
            if result.error is not None:
                return result
            return result.success(atom)

    def atom(self):
        result = ParseResult()
        token = self.current_token

        if token.type in (TT_INT, TT_FLOAT):
            result.register_advancement()
            self.advance()
            return result.success(NumberNode(token))
        elif token.type == TT_STRING:
            result.register_advancement()
            self.advance()
            return result.success(StringNode(token))
        elif token.type == TT_IDENTIFIER:
            result.register_advancement()
            self.advance()
            return result.success(VarAccessNode(token))
        elif token.type == TT_LPAREN:
            result.register_advancement()
            self.advance()
            expr = result.register(self.expr())
            if result.error is not None:
                return result
            if self.current_token.type == TT_RPAREN:
                result.register_advancement()
                self.advance()
                return result.success(expr)
            else:
                return result.failure(
                    InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "expected ')'.")
                )
        elif token.type == TT_LSQUARE:
            list_expr = result.register(self.list_expr())
            if result.error is not None:
                return result
            return result.success(list_expr)
        elif token.matches(TT_KEYWORD, 'if'):
            if_expr = result.register(self.if_expr())
            if result.error is not None:
                return result
            return result.success(if_expr)
        elif token.matches(TT_KEYWORD, 'for'):
            for_expr = result.register(self.for_expr())
            if result.error is not None:
                return result
            return result.success(for_expr)
        elif token.matches(TT_KEYWORD, 'while'):
            while_expr = result.register(self.while_expr())
            if result.error is not None:
                return result
            return result.success(while_expr)
        elif token.matches(TT_KEYWORD, 'def'):
            func_def = result.register(self.func_def())
            if result.error is not None:
                return result
            return result.success(func_def)

        return result.failure(
            InvalidSyntaxError(token.pos_start, token.pos_end, "expected int, float, identifier, 'if', 'for', 'while', "
                                                               "'def', '+', '-', '[' or '('.")
        )

    def list_expr(self):
        result = ParseResult()
        element_nodes = []
        pos_start = self.current_token.pos_start.copy()

        if self.current_token.type != TT_LSQUARE:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "expected '['."
            ))

        result.register_advancement()
        self.advance()

        if self.current_token.type == TT_RSQUARE:
            result.register_advancement()
            self.advance()
        else:
            element_nodes.append(result.register(self.expr()))
            if result.error is not None:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected ']', 'var', 'if', 'for', 'while', 'def', int, float, identifier, '+', '-', '(', "
                        "'[' or 'not'."
                    )
                )

            while self.current_token.type == TT_COMMA:
                result.register_advancement()
                self.advance()

                element_nodes.append(result.register(self.expr()))
                if result.error is not None:
                    return result

            if self.current_token.type != TT_RSQUARE:
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

    def if_expr(self):
        result = ParseResult()
        all_cases = result.register(self.if_expr_cases('if'))
        if result.error is not None:
            return result
        cases, else_cases = all_cases
        return result.success(IfNode(cases, else_cases))

    def if_expr_b(self):
        return self.if_expr_cases("elif")

    def if_expr_c(self):
        result = ParseResult()
        else_case = None

        if self.current_token.matches(TT_KEYWORD, 'else'):
            result.register_advancement()
            self.advance()

            if self.current_token.type == TT_NEWLINE:
                result.register_advancement()
                self.advance()

                statements = result.register(self.statements())
                if result.error is not None:
                    return result
                else_case = (statements, True)

                if self.current_token.matches(TT_KEYWORD, 'end'):
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

    def if_expr_b_or_c(self):
        result = ParseResult()
        cases, else_case = [], None

        if self.current_token.matches(TT_KEYWORD, 'elif'):
            all_cases = result.register(self.if_expr_b())
            if result.error is not None:
                return result
            cases, else_case = all_cases
        else:
            else_case = result.register(self.if_expr_c())
            if result.error is not None:
                return result

        return result.success((cases, else_case))

    def if_expr_cases(self, case_keyword):
        result = ParseResult()
        cases = []
        else_case = None

        if not self.current_token.matches(TT_KEYWORD, case_keyword):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"expected '{case_keyword}'."
            ))

        result.register_advancement()
        self.advance()

        condition = result.register(self.expr())
        if result.error is not None:
            return result

        if not self.current_token.matches(TT_KEYWORD, 'then'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end, "expected 'then'."
            ))

        result.register_advancement()
        self.advance()

        if self.current_token.type == TT_NEWLINE:
            result.register_advancement()
            self.advance()

            statements = result.register(self.statements())
            if result.error is not None:
                return result
            cases.append((condition, statements, True))

            if self.current_token.matches(TT_KEYWORD, 'end'):
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

    def for_expr(self):
        result = ParseResult()
        if not self.current_token.matches(TT_KEYWORD, 'for'):
            return result.error(InvalidSyntaxError, self.current_token.pos_start, self.current_token.pos_end,
                                "expected 'for'.")

        result.register_advancement()
        self.advance()

        if self.current_token.type != TT_IDENTIFIER:
            if self.current_token.type != TT_KEYWORD:
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

        if self.current_token.matches(TT_KEYWORD, 'in'):
            result.register_advancement()
            self.advance()

            list_ = result.register(self.expr())
            if result.error is not None:
                return result

            if not self.current_token.matches(TT_KEYWORD, 'then'):
                return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                         "expected 'then'."))

            result.register_advancement()
            self.advance()

            if self.current_token.type == TT_NEWLINE:
                result.register_advancement()
                self.advance()

                body = result.register(self.statements())
                if result.error is not None:
                    return result

                if not self.current_token.matches(TT_KEYWORD, 'end'):
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
        elif self.current_token.type != TT_EQ:
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

        if not self.current_token.matches(TT_KEYWORD, 'to'):
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     f"expected 'to'."))

        result.register_advancement()
        self.advance()

        end_value = result.register(self.expr())
        if result.error is not None:
            return result

        if self.current_token.matches(TT_KEYWORD, 'step'):
            result.register_advancement()
            self.advance()

            step_value = result.register(self.expr())
            if result.error is not None:
                return result
        else:
            step_value = None

        if not self.current_token.matches(TT_KEYWORD, 'then'):
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     "expected 'then'."))

        result.register_advancement()
        self.advance()

        if self.current_token.type == TT_NEWLINE:
            result.register_advancement()
            self.advance()

            body = result.register(self.statements())
            if result.error is not None:
                return result

            if not self.current_token.matches(TT_KEYWORD, 'end'):
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected 'end'."
                ))

            result.register_advancement()
            self.advance()

            return result.success(ForNode(var_name, start_value, end_value, step_value, body, True))

        body = result.register(self.expr())
        if result.error is not None:
            return result

        return result.success(ForNode(var_name, start_value, end_value, step_value, body, False))

    def while_expr(self):
        result = ParseResult()

        if not self.current_token.matches(TT_KEYWORD, 'while'):
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     "expected 'while'."))

        result.register_advancement()
        self.advance()

        condition = result.register(self.expr())
        if result.error is not None:
            return result

        if not self.current_token.matches(TT_KEYWORD, 'then'):
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     "expected 'then'."))

        result.register_advancement()
        self.advance()

        if self.current_token.type == TT_NEWLINE:
            result.register_advancement()
            self.advance()

            body = result.register(self.statements())
            if result.error is not None:
                return result

            if not self.current_token.matches(TT_KEYWORD, 'end'):
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

    def func_def(self):
        result = ParseResult()

        if not self.current_token.matches(TT_KEYWORD, 'def'):
            return result.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected 'def'."
                )
            )

        result.register_advancement()
        self.advance()

        if self.current_token.type == TT_IDENTIFIER:
            var_name_token = self.current_token
            result.register_advancement()
            self.advance()
            if self.current_token.type != TT_LPAREN:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected '('."
                    )
                )
        else:
            var_name_token = None
            if self.current_token.type != TT_LPAREN:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected identifier or '('."
                    )
                )

        result.register_advancement()
        self.advance()
        arg_name_tokens = []

        if self.current_token.type == TT_IDENTIFIER:
            arg_name_tokens.append(self.current_token)
            result.register_advancement()
            self.advance()

            while self.current_token.type == TT_COMMA:
                result.register_advancement()
                self.advance()

                if self.current_token.type != TT_IDENTIFIER:
                    if self.current_token.type != TT_KEYWORD:
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

                arg_name_tokens.append(self.current_token)
                result.register_advancement()
                self.advance()

            if self.current_token.type != TT_RPAREN:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected ',' or ')'."
                    )
                )
        else:
            if self.current_token.type != TT_RPAREN:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected identifier or ')'."
                    )
                )

        result.register_advancement()
        self.advance()

        if self.current_token.type == TT_ARROW:
            result.register_advancement()
            self.advance()

            body = result.register(self.expr())
            if result.error is not None:
                return result

            return result.success(FuncDefNode(
                var_name_token,
                arg_name_tokens,
                body,
                True
            ))

        if self.current_token.type != TT_NEWLINE:
            return result.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected '->' or new line."
                )
            )

        result.register_advancement()
        self.advance()

        body = result.register(self.statements())
        if result.error is not None:
            return result

        if not self.current_token.matches(TT_KEYWORD, 'end'):
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
            arg_name_tokens,
            body,
            False
        ))

    def bin_op(self, func_a, ops, func_b=None, left_has_priority: bool = True):
        # param left_has_priority is used to know if we have to write (for exemple) ((int:3, ==, int:3), ==, int:3)
        # or (int:3, ==, int:3, ==, int:3)
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
