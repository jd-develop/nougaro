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
from src.position import Position
from src.token import Token
from src.token_types import *
from src.constants import DIGITS, LETTERS, LETTERS_DIGITS
from src.errors import *
# built-in python imports
# no imports


# ##########
# LEXER
# ##########
class Lexer:
    """Transforms code into a list of tokens -lexical units-"""
    def __init__(self, file_name: str, text: str):
        self.file_name: str = file_name  # name of the file we're executing
        self.text: str = text  # raw code we have to execute
        self.pos: Position = Position(-1, 0, -1, file_name, text)  # actual position of the lexer
        self.current_char: str = None  # current char
        self.advance()

    def advance(self):
        """advance of 1 char in self.text"""
        self.pos.advance(self.current_char)  # advance in position
        # set the new current char - the next one in the code or None if this is EOF (end of file)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None

    def make_tokens(self):
        """Returns a token list with self.text. Return tok_list, None or [], error."""
        tokens: list[Token] = []

        there_is_a_space_or_a_tab_or_a_comment = False
        while self.current_char is not None:  # None is EOF
            if self.current_char in ' \t':  # tab and space
                there_is_a_space_or_a_tab_or_a_comment = True
                self.advance()
            elif self.current_char == '#':  # for comments
                there_is_a_space_or_a_tab_or_a_comment = True
                self.skip_comment()
            elif self.current_char in ';\n':  # semicolons and new lines
                there_is_a_space_or_a_tab_or_a_comment = False
                tokens.append(Token(TT["NEWLINE"], pos_start=self.pos))
                self.advance()

            elif self.current_char in DIGITS + '.':  # the char is a digit: we generate a number
                there_is_a_space_or_a_tab_or_a_comment = False
                number, error = self.make_number()
                if error is None:  # there is no error
                    tokens.append(number)
                else:  # there is an error, we return it
                    return [], error
            elif self.current_char in LETTERS + '_':  # the char is a letter or an underscore: identifier or keyword
                tok = self.make_identifier()
                if len(tokens) == 0:
                    tokens.append(tok)
                elif there_is_a_space_or_a_tab_or_a_comment:
                    tokens.append(tok)
                # if you think the following code is awful and ugly, you're RIGHT
                elif tokens[-1].type in (TT['INT'], TT['FLOAT']) and \
                        tok.type == TT['IDENTIFIER'] and \
                        (tok.value.startswith('e') or tok.value.startswith('E')) and \
                        tok.value[1:].isdigit() and \
                        self.current_char != '.':
                    tokens.append(Token(TT['E_INFIX'], pos_start=tok.pos_start, pos_end=tok.pos_start.copy().advance()))
                    tokens.append(Token(TT['INT'], int(tok.value[1:]), tok.pos_start.copy().advance().advance(),
                                        tok.pos_end))
                elif tokens[-1].type in (TT['INT'], TT['FLOAT']) and \
                        tok.type == TT['IDENTIFIER'] and \
                        (tok.value.startswith('e') or tok.value.startswith('E')) and \
                        self.current_char == '-':
                    # TODO: (x)e-(y)
                    tokens.append(tok)
                else:
                    tokens.append(tok)
                there_is_a_space_or_a_tab_or_a_comment = False
            elif self.current_char == '"' or self.current_char == "'":  # the char is a quote: str
                there_is_a_space_or_a_tab_or_a_comment = False
                string_, error = self.make_string(self.current_char)
                if error is None:  # there is no error
                    tokens.append(string_)
                else:  # there is an error: we return it
                    return [], error

            # basic math stuff
            elif self.current_char == '+':
                there_is_a_space_or_a_tab_or_a_comment = False
                tokens.append(self.make_plus())
            elif self.current_char == '-':
                there_is_a_space_or_a_tab_or_a_comment = False
                tokens.append(self.make_minus_or_arrow())
            elif self.current_char == '*':
                there_is_a_space_or_a_tab_or_a_comment = False
                tokens.append(self.make_mul())
            elif self.current_char == '/':
                there_is_a_space_or_a_tab_or_a_comment = False
                tokens.append(self.make_div())
            elif self.current_char == '^':
                there_is_a_space_or_a_tab_or_a_comment = False
                token, error = self.make_pow()
                if error is not None:
                    return [], error
                tokens.append(token)
            elif self.current_char == '%':
                there_is_a_space_or_a_tab_or_a_comment = False
                tokens.append(self.make_perc())

            # bitwise operators
            elif self.current_char == "|":
                there_is_a_space_or_a_tab_or_a_comment = False
                token, error = self.make_or()
                if error is not None:
                    return [], error
                tokens.append(token)
            elif self.current_char == "&":
                there_is_a_space_or_a_tab_or_a_comment = False
                token, error = self.make_and()
                if error is not None:
                    return [], error
                tokens.append(token)
            elif self.current_char == "~":
                there_is_a_space_or_a_tab_or_a_comment = False
                tokens.append(Token(TT["BITWISENOT"], pos_start=self.pos))
                self.advance()

            # parentheses and brackets
            elif self.current_char == '(':
                there_is_a_space_or_a_tab_or_a_comment = False
                tokens.append(Token(TT["LPAREN"], pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                there_is_a_space_or_a_tab_or_a_comment = False
                tokens.append(Token(TT["RPAREN"], pos_start=self.pos))
                self.advance()
            elif self.current_char == '[':
                there_is_a_space_or_a_tab_or_a_comment = False
                tokens.append(Token(TT["LSQUARE"], pos_start=self.pos))
                self.advance()
            elif self.current_char == ']':
                there_is_a_space_or_a_tab_or_a_comment = False
                tokens.append(Token(TT["RSQUARE"], pos_start=self.pos))
                self.advance()

            # equals (+=, -=, ... are generated above, in the 'basic math stuff' category)
            elif self.current_char == '!':
                there_is_a_space_or_a_tab_or_a_comment = False
                token, error = self.make_not_equals()
                if error is not None:
                    return [], error
                tokens.append(token)
            elif self.current_char == '=':
                there_is_a_space_or_a_tab_or_a_comment = False
                tokens.append(self.make_equals())
            elif self.current_char == '<':
                there_is_a_space_or_a_tab_or_a_comment = False
                token, error = self.make_less_than()
                if error is not None:
                    return [], error
                tokens.append(token)
            elif self.current_char == '>':
                there_is_a_space_or_a_tab_or_a_comment = False
                token, error = self.make_greater_than()
                if error is not None:
                    return [], error
                tokens.append(token)

            # syntax 'var a = b ? c ? d ? e ? f'
            elif self.current_char == '?':
                there_is_a_space_or_a_tab_or_a_comment = False
                tokens.append(Token(TT["INTERROGATIVE_PNT"], pos_start=self.pos))
                self.advance()

            # comma
            elif self.current_char == ',':
                there_is_a_space_or_a_tab_or_a_comment = False
                tokens.append(Token(TT["COMMA"], pos_start=self.pos))
                self.advance()
            else:
                # illegal char
                pos_start = self.pos.copy()
                char = self.current_char
                return [], IllegalCharError(pos_start, self.pos.advance(), f"'{char}' is an illegal character.",
                                            origin_file="src.lexer.Lexer.make_tokens")

        # append the end of file
        tokens.append(Token(TT["EOF"], pos_start=self.pos))
        return tokens, None

    def make_plus(self):
        """Make + or += """
        token_type = TT["PLUS"]
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':  # +=
            self.advance()
            token_type = TT["PLUSEQ"]

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_minus_or_arrow(self):
        """ Make - , -> or -= """
        token_type = TT["MINUS"]
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '>':  # ->
            self.advance()
            token_type = TT["ARROW"]
        elif self.current_char == '=':  # -=
            self.advance()
            token_type = TT["MINUSEQ"]

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_mul(self):
        """Make * or *= """
        token_type = TT["MUL"]
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':  # *=
            self.advance()
            token_type = TT["MULTEQ"]

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_div(self):
        """Make / , // , /= or //= """
        token_type = TT["DIV"]
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '/':  # //
            self.advance()
            token_type = TT["FLOORDIV"]
            if self.current_char == '=':  # //=
                self.advance()
                token_type = TT["FLOORDIVEQ"]
        elif self.current_char == '=':  # /=
            self.advance()
            token_type = TT["DIVEQ"]

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_pow(self):
        """Make ^ , ^= , ^^ , ^^= , or ^^^=
        OK, so ^ is the power, ^= is power eq
               ^^ is bitwise xor, ^^= is bitwise xor eq
               ^^^ doesn't exist, ^^^= is boolean xor eq
        """
        token_type = TT["POW"]
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':  # ^=
            self.advance()
            token_type = TT["POWEQ"]
        elif self.current_char == '^':  # ^^
            self.advance()
            token_type = TT["BITWISEXOR"]
            if self.current_char == '=':  # ^^=
                self.advance()
                token_type = TT["BITWISEXOREQ"]
            elif self.current_char == '^':  # ^^^
                self.advance()
                if self.current_char != "=":
                    return None, InvalidSyntaxError(pos_start, self.pos, "expected '=' after '^^^'.",
                                                    "src.lexer.Lexer.make_pow")
                token_type = TT["XOREQ"]  # ^^^=
                self.advance()

        return Token(token_type, pos_start=pos_start, pos_end=self.pos), None

    def make_perc(self):
        """Make % or %= """
        token_type = TT["PERC"]
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':  # %=
            self.advance()
            token_type = TT["PERCEQ"]

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_or(self):
        """Make | , |= or ||=
            | is bitwise or, |= is bitwise or eq
            ||= is boolean or eq
        """
        pos_start = self.pos.copy()
        self.advance()
        token_type = TT["BITWISEOR"]

        if self.current_char == '=':  # |=
            token_type = TT["BITWISEOREQ"]
            self.advance()
        elif self.current_char == '|':  # ||
            self.advance()
            if self.current_char != "=":
                return None, InvalidSyntaxError(pos_start, self.pos, "expected '=' after '||'.",
                                                "src.lexer.Lexer.make_or")
            token_type = TT["OREQ"]  # ||=
            self.advance()

        return Token(token_type, pos_start=pos_start, pos_end=self.pos), None

    def make_and(self):
        """Make & , &= or &&=
            & is bitwise and, &= is bitwise and eq
            &&= is boolean and eq
        """
        pos_start = self.pos.copy()
        self.advance()
        token_type = TT["BITWISEAND"]

        if self.current_char == '=':  # &=
            token_type = TT["BITWISEANDEQ"]
            self.advance()
        elif self.current_char == '&':  # &&
            self.advance()
            if self.current_char != "=":
                return None, InvalidSyntaxError(pos_start, self.pos, "expected '=' after '&&'.",
                                                "src.lexer.Lexer.make_and")
            token_type = TT["ANDEQ"]  # &&=
            self.advance()

        return Token(token_type, pos_start=pos_start, pos_end=self.pos), None

    def make_string(self, quote='"'):
        """Make string. We need quote to know where to stop"""
        string_ = ''
        if quote == '"':
            other_quote = "'"
        else:
            other_quote = '"'
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()

        escape_characters = {  # \n is a back line, \t is a tab
            'n': '\n',
            't': '\t'
        }

        # if self.current_char == quote, we have to stop looping because the str is closed
        # if escape_character, the last char is a \, so there is an escape sequence
        # if escape_character but self.current_char != quote, we SHOULD continue looping because \" doesn't close the
        # str
        while self.current_char != quote or escape_character:
            if self.current_char is None:  # EOF: the string was not closed.
                return None, InvalidSyntaxError(
                    pos_start, self.pos,
                    f"{other_quote}{quote}{other_quote} was never closed.",
                    "src.lexer.Lexer.make_string"
                )
            if escape_character:  # if the last char is \, we check for escape sequence
                string_ += escape_characters.get(self.current_char, self.current_char)  # the arg is doubled: if
                #                                                                         self.current_char is not a
                #                                                                         valid escape_sequence, we
                #                                                                         get self.current_char as
                #                                                                         the next char.
                escape_character = False  # there is no more escape char
            elif self.current_char == '\\':  # the next is an escape char
                escape_character = True
            else:  # there is no escape char, we add our char in the str
                string_ += self.current_char
            self.advance()  # we advance

        self.advance()  # we advance after the str
        return Token(TT["STRING"], string_, pos_start, self.pos), None

    def make_identifier(self):
        """Make an identifier or a keyword"""
        id_str = ''  # identifier or keyword as python string
        pos_start = self.pos.copy()

        # while not EOF and current char still in authorized chars in identifier and keywords
        while self.current_char is not None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()

        token_type = TT["KEYWORD"] if id_str in KEYWORDS else TT["IDENTIFIER"]  # KEYWORDS is the keywords list
        return Token(token_type, id_str, pos_start, self.pos)

    def make_number(self):
        """Make number, int or float"""
        num_str = ''
        dot_count = 0  # we can't have more than one dot, so we count them
        pos_start = self.pos.copy()

        if self.current_char == '+':
            self.advance()
        if self.current_char == '-':
            num_str += '-'
            self.advance()

        # if char is still a number or a dot
        while self.current_char is not None and self.current_char in DIGITS + '.' + '_':
            if self.current_char == '.':  # if the char is a dot
                if dot_count == 1:  # if we already encountered a dot
                    return None, InvalidSyntaxError(self.pos, self.pos.copy().advance(),
                                                    "a number can't have more than one dot.",
                                                    "src.lexer.Lexer.make_number")
                dot_count += 1
                num_str += '.'
            elif self.current_char == '_':  # you can write 5_371_281 instead of 5371281
                pass
            else:
                num_str += self.current_char
            self.advance()  # we advance

        if num_str == '.':
            return None, InvalidSyntaxError(
                pos_start, self.pos,
                "no digit in number '.'.",
                "src.lexer.Lexer.make_number"
            )

        if num_str == '':
            return None, InvalidSyntaxError(
                pos_start, self.pos,
                "can not make a number with this expression.",
                "src.lexer.Lexer.make_number"
            )

        # TODO: 0x, 0b, 0o
        # when you have 0b or 0o, it is easy to check if the next int only contains digits between 0 to 1 or 0 to 7
        # however, with 0x, it is more complicated...
        # if num_str == '0':
        #     prefixes = {
        #         "x": TT["0X_PREFIX"],
        #         "o": TT["0O_PREFIX"],
        #         "b": TT["0B_PREFIX"],
        #     }
        #     if self.current_char in prefixes.keys():
        #         token = Token(prefixes[self.current_char], pos_start=pos_start, pos_end=self.pos.copy())
        #         self.advance()
        #         return token, None

        if dot_count == 0:  # if there is no dots, this is an INT, else this is a FLOAT
            return Token(TT["INT"], int(num_str), pos_start, self.pos.copy()), None
        else:
            return Token(TT["FLOAT"], float(num_str), pos_start, self.pos.copy()), None

    def make_not_equals(self):
        """Make != or !>>"""
        # current char is '!'
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':  # !=
            self.advance()
            return Token(TT["NE"], pos_start=pos_start, pos_end=self.pos), None
        elif self.current_char == '>':  # !>
            self.advance()
            if self.current_char != '>':
                return None, InvalidSyntaxError(pos_start, self.pos, "expected '!>>', but got '!>'.",
                                                "src.lexer.Lexer.make_not_equals")
            # !>>
            self.advance()
            return Token(TT["TO_AND_OVERWRITE"], pos_start=pos_start, pos_end=self.pos), None

        self.advance()
        return None, InvalidSyntaxError(pos_start, self.pos, "expected '!=' or '!>>', but got '!'.",
                                        "src.lexer.Lexer.make_not_equals")

    def make_equals(self):
        """Make = , == or ===
        Exemple of use for ===:
            var a = a == b
            var a === b
        """
        token_type = TT["EQ"]
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':  # ==
            self.advance()
            token_type = TT["EE"]
            if self.current_char == '=':  # ===
                self.advance()
                token_type = TT["EEEQ"]

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
        """Make < , <= , <== , <<= """
        token_type = TT["LT"]
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':  # <=
            self.advance()
            token_type = TT["LTE"]
            if self.current_char == '=':  # <==
                self.advance()
                token_type = TT["LTEEQ"]
        elif self.current_char == '<':  # <<
            self.advance()
            if self.current_char == '=':  # <<=
                self.advance()
                token_type = TT["LTEQ"]
            else:
                return None, InvalidSyntaxError(
                    pos_start,
                    self.pos,
                    f"expected '=' after '<<', got '{self.current_char}.",
                    "src.lexer.Lexer.make_less_than"
                )

        return Token(token_type, pos_start=pos_start, pos_end=self.pos), None

    def make_greater_than(self):
        """Make > , >= , >== , >> , >>= """
        token_type = TT["GT"]
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TT["GTE"]
            if self.current_char == '=':
                self.advance()
                token_type = TT["GTEEQ"]
        elif self.current_char == '>':
            self.advance()
            token_type = TT["TO"]
            if self.current_char == '=':
                self.advance()
                token_type = TT["GTEQ"]

        return Token(token_type, pos_start=pos_start, pos_end=self.pos), None

    def skip_comment(self):
        """Skip a comment (until back line or EOF)"""
        # current char is '#'
        self.advance()

        while self.current_char != '\n' and self.current_char is not None:  # None -> EOF
            self.advance()
