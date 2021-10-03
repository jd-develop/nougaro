#!/usr/bin/env python3
# coding:utf-8
# this file is part of NOUGARO language, created by Jean Dubois (github.com/jd-develop)
# Public Domain
# Actually running with Python 3.9.7
from strings_with_arrows import *


# ##########
# COLORS
# ##########
def print_in_red(txt): print("\033[91m {}\033[00m".format(txt))


# ##########
# CONSTANTS
# ##########
DIGITS = '0123456789'


# ##########
# ERRORS
# ##########
class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f"In file {self.pos_start.file_name}, line {self.pos_start.line_number + 1} : " + \
            string_with_arrows(self.pos_start.file_txt, self.pos_start, self.pos_end) + '\n' + \
                 f'{self.error_name} : {self.details}'
        return result


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "IllegalCharError", details)


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "InvalidSyntaxError", details)


# ##########
# POSITION
# ##########
class Position:
    def __init__(self, index, line_number, colon, file_name, file_txt):
        self.index = index
        self.line_number = line_number
        self.colon = colon
        self.file_name = file_name
        self.file_txt = file_txt

    def advance(self, current_char):
        self.index += 1
        self.colon += 1

        if current_char == '\n':
            self.line_number += 1
            self.colon = 0

        return self

    def copy(self):
        return Position(self.index, self.line_number, self.colon, self.file_name, self.file_txt)


# ##########
# TOKENS
# ##########
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'  # +
TT_MINUS = 'MINUS'  # -
TT_MUL = 'MUL'  # *
TT_DIV = 'DIV'  # /
TT_RPAREN = 'RPAREN'  # )
TT_LPAREN = 'LPAREN'  # (


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self) -> str:
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'


# ##########
# LEXER
# ##########
class Lexer:
    def __init__(self, file_name, text):
        self.file_name = file_name
        self.text = text
        self.pos = Position(-1, 0, -1, file_name, text)
        self.current_char = None
        self.advance()

    def advance(self):  # advance of 1 char in self.text
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char is not None:
            if self.current_char in ' \t':  # tab and space
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            else:
                # illegal char
                pos_start = self.pos.copy()
                char = self.current_char
                return [], IllegalCharError(pos_start, self.pos, char + " is an illegal character.")

        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0

        while self.current_char is not None and self.current_char in DIGITS + '.':  # if char is still a number or a dot
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))


# ##########
# NODES
# ##########
class NumberNode:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'{self.token}'


class BinOpNode:
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_token}, {self.right_node})'


# ##########
# PARSER
# ##########
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.current_token = None
        self.advance()

    def parse(self):
        res = self.expr()
        return res

    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token

    def factor(self):
        token = self.current_token

        if token.type in (TT_INT, TT_FLOAT):
            self.advance()
            return NumberNode(token)

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def bin_op(self, func, ops):
        left = func()

        while self.current_token.type in ops:
            op_token = self.current_token
            self.advance()
            right = func()
            left = BinOpNode(left, op_token, right)
        return left


# ##########
# RUN
# ##########
def run(file_name, text):
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()
    if error is not None:
        return None, error

    # abstract syntax tree
    parser = Parser(tokens)
    ast = parser.parse()

    return ast, error
