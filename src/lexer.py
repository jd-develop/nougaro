#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# IMPORTS
# nougaro modules imports
from src.position import Position
from src.tokens import Token
from src.token_constants import *
from src.constants import DIGITS, LETTERS, LETTERS_DIGITS
from src.errors import *
# built-in python imports
# no imports


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
            elif self.current_char == '#':  # for comments
                self.skip_comment()
            elif self.current_char in ';\n':  # semicolons and new lines
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
                self.advance()

            elif self.current_char in DIGITS:
                number, error = self.make_number()
                if error is None:
                    tokens.append(number)
                else:
                    return [], error
            elif self.current_char in LETTERS + '_':
                tokens.append(self.make_identifier())
            elif self.current_char == '"' or self.current_char == "'":
                string_, error = self.make_string(self.current_char)
                if error is None:
                    tokens.append(string_)
                else:
                    return [], error

            elif self.current_char == '+':
                tokens.append(self.make_plus())
            elif self.current_char == '-':
                tokens.append(self.make_minus_or_arrow())
            elif self.current_char == '*':
                tokens.append(self.make_mul())
            elif self.current_char == '/':
                tokens.append(self.make_div())
            elif self.current_char == '^':
                token, error = self.make_pow()
                if error is not None:
                    return [], error
                tokens.append(token)
            elif self.current_char == '%':
                tokens.append(self.make_perc())
            elif self.current_char == "|":
                token, error = self.make_or()
                if error is not None:
                    return [], error
                tokens.append(token)
            elif self.current_char == "&":
                token, error = self.make_and()
                if error is not None:
                    return [], error
                tokens.append(token)
            elif self.current_char == "~":
                tokens.append(Token(TT_BITWISENOT, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(TT_LSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(TT_RSQUARE, pos_start=self.pos))
                self.advance()

            elif self.current_char == '!':
                token, error = self.make_not_equals()
                if error is not None:
                    return [], error
                tokens.append(token)
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
            elif self.current_char == '?':
                tokens.append(Token(TT_INTERROGATIVE_PNT, pos_start=self.pos))
                self.advance()

            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
                self.advance()
            else:
                # illegal char
                pos_start = self.pos.copy()
                char = self.current_char
                return [], IllegalCharError(pos_start, self.pos.advance(), f"'{char}' is an illegal character.")

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_plus(self):
        token_type = TT_PLUS
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TT_PLUSEQ

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_minus(self):
        token_type = TT_MINUS
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TT_MINUSEQ

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_mul(self):
        token_type = TT_MUL
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TT_MULTEQ

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_div(self):
        token_type = TT_DIV
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '/':
            self.advance()
            token_type = TT_FLOORDIV
            if self.current_char == '=':
                self.advance()
                token_type = TT_FLOORDIVEQ
        elif self.current_char == '=':
            self.advance()
            token_type = TT_DIVEQ

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_pow(self):
        token_type = TT_POW
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':  # ^=
            self.advance()
            token_type = TT_POWEQ
        elif self.current_char == '^':  # ^^
            self.advance()
            token_type = TT_BITWISEXOR
            if self.current_char == '=':  # ^^=
                self.advance()
                token_type = TT_BITWISEXOREQ
            elif self.current_char == '^':  # ^^^
                self.advance()
                if self.current_char != "=":  # ^^^=
                    return None, InvalidSyntaxError(pos_start, self.pos, "expected '=' after '^^^'.")
                token_type = TT_XOREQ
                self.advance()

        return Token(token_type, pos_start=pos_start, pos_end=self.pos), None

    def make_perc(self):
        token_type = TT_PERC
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TT_PERCEQ

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_or(self):
        pos_start = self.pos.copy()
        self.advance()
        token_type = TT_BITWISEOR

        if self.current_char == '=':
            token_type = TT_BITWISEOREQ
            self.advance()
        elif self.current_char == '|':
            self.advance()
            if self.current_char != "=":
                return None, InvalidSyntaxError(pos_start, self.pos, "expected '=' after '||'.")
            token_type = TT_OREQ
            self.advance()

        return Token(token_type, pos_start=pos_start, pos_end=self.pos), None

    def make_and(self):
        pos_start = self.pos.copy()
        self.advance()
        token_type = TT_BITWISEAND

        if self.current_char == '=':
            token_type = TT_BITWISEANDEQ
            self.advance()
        elif self.current_char == '&':
            self.advance()
            if self.current_char != "=":
                return None, InvalidSyntaxError(pos_start, self.pos, "expected '=' after '&&'.")
            token_type = TT_ANDEQ
            self.advance()

        return Token(token_type, pos_start=pos_start, pos_end=self.pos), None

    def make_string(self, quote='"'):
        string_ = ''
        if quote == '"':
            other_quote = "'"
        else:
            other_quote = '"'
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()

        escape_characters = {
            'n': '\n',
            't': '\t'
        }

        while self.current_char != quote or escape_character:
            if self.current_char is None:
                return None, InvalidSyntaxError(
                    pos_start, self.pos,
                    f"{other_quote}{quote}{other_quote} was never closed."
                )
            if escape_character:
                string_ += escape_characters.get(self.current_char, self.current_char)
                escape_character = False
            else:
                if self.current_char == '\\':
                    escape_character = True
                else:
                    string_ += self.current_char
            self.advance()

        self.advance()
        return Token(TT_STRING, string_, pos_start, self.pos), None

    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()

        token_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(token_type, id_str, pos_start, self.pos)

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char in DIGITS + '.':  # if char is still a number or a dot
            if self.current_char == '.':
                if dot_count == 1:
                    return None, InvalidSyntaxError(pos_start, self.pos, "a number can't have more than one dot.")
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos.copy()), None
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos.copy()), None

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None

        self.advance()
        return None, InvalidSyntaxError(pos_start, self.pos, "expected '!=', but got '!'.")

    def make_equals(self):
        token_type = TT_EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TT_EE

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
        token_type = TT_LT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TT_LTE

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
        token_type = TT_GT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TT_GTE

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_minus_or_arrow(self):
        token_type = TT_MINUS
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '>':
            self.advance()
            token_type = TT_ARROW
        elif self.current_char == '=':
            self.advance()
            token_type = TT_MINUSEQ

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def skip_comment(self):
        self.advance()

        while self.current_char != '\n' and self.current_char is not None and self.current_char != ';':  # None -> EOF
            self.advance()
