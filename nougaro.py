#!/usr/bin/env python3
# coding:utf-8
# this file is part of NOUGARO language, created by Jean Dubois (github.com/jd-develop)
# Public Domain
# Actually running with Python 3.9.7

# ##########
# CONSTANTS
# ##########
DIGITS = '0123456789'


# ##########
# ERRORS
# ##########
class Error:
    def __init__(self, error_name, details):
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        return result


class IllegalCharError(Error):
    def __init__(self, details):
        super().__init__("IllegalCharError", details)


# ##########
# POSITION
# ##########
class Position:
    def __init__(self, index, line_number, colon):
        self.index = index
        self.line_number = line_number
        self.colon = colon


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
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.current_char = None
        self.advance()

    def advance(self):  # advance of 1 char in self.text
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

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
                # return some error
                char = self.current_char
                return [], IllegalCharError(char + " is an illegal character.")

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
# RUN
# ##########
def run(text):
    lexer = Lexer(text)
    tokens, error = lexer.make_tokens()

    return tokens, error
