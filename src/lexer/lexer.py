#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.lexer.position import Position
from src.lexer.token import Token
from src.lexer.token_types import *
from src.constants import DIGITS, IDENTIFIERS_LEGAL_CHARS, LETTERS_DIGITS
from src.errors.errors import *
# built-in python imports
import unicodedata


# ##########
# LEXER
# ##########
class Lexer:
    """Transforms code into a list of tokens (lexical units)"""
    def __init__(self, file_name: str, text: str):
        self.file_name: str = file_name  # name of the file we're executing
        self.text: str = text  # raw code we have to execute
        self.pos: Position = Position(-1, 0, -1, file_name, text)  # actual position of the lexer
        self.current_char: str | None = None
        self.advance()

    def get_char(self, pos):
        return self.text[pos.index] if pos.index < len(self.text) else None

    def advance(self):
        """Advance of 1 char in self.text"""
        self.pos.advance(self.current_char)  # advance in position
        # set the new current char - the next one in the code or None if this is EOF (end of file)
        self.current_char = self.get_char(self.pos)
        # USEFUL to know where tf you are in the file when it throws at you an unclear error
        # if self.pos.index in [7583, 5547]:
        #     print(self.pos.index, self.pos.line_number, self.current_char, self.next_char())

    def next_char(self):
        """Returns the next char without advancing"""
        new_pos = self.pos.copy().advance(self.current_char)
        # get the next char in the code (or None if this is EOF (end of file))
        next_char = self.get_char(new_pos)
        return next_char

    def make_tokens(self) -> tuple[list[Token], None | Error]:
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
            elif self.current_char == '\\' and self.next_char() is not None and self.next_char() in ';\n':
                self.advance()
                self.advance()
            elif self.current_char == "\\":  # and next char is invalid
                return [], InvalidSyntaxError(
                    self.pos.copy(), self.pos.advance(),
                    "expected new line or semicolon after '\\'.",
                    origin_file="src.lexer.lexer.Lexer.make_tokens"
                )
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
            elif self.current_char in IDENTIFIERS_LEGAL_CHARS:  # the char is legal: identifier or keyword
                tok = self.make_identifier()
                try:
                    last_tok_is_number = tokens[-1].type in (TT['INT'], TT['FLOAT'])
                except IndexError:
                    last_tok_is_number = False
                current_tok_is_identifier = tok.type == TT['IDENTIFIER']
                current_tok_is_maybe_e_infix = (
                        last_tok_is_number and current_tok_is_identifier and
                        (tok.value.startswith('e') or tok.value.startswith('E'))
                )
                current_tok_is_positive_e_infix = (
                        current_tok_is_maybe_e_infix and tok.value[1:].isdigit() and self.current_char != "."
                )
                if self.next_char() is not None:
                    current_tok_is_negative_e_infix = (
                        current_tok_is_maybe_e_infix and self.current_char == "-" and self.next_char() in DIGITS
                    )
                else:
                    current_tok_is_negative_e_infix = False

                if len(tokens) == 0:
                    tokens.append(tok)
                elif there_is_a_space_or_a_tab_or_a_comment:
                    tokens.append(tok)
                elif current_tok_is_positive_e_infix:
                    tokens.append(Token(
                        TT['E_INFIX'],
                        pos_start=tok.pos_start,
                        pos_end=tok.pos_start.copy().advance()
                    ))
                    tokens.append(Token(
                        TT['INT'],
                        value=int(tok.value[1:]),
                        pos_start=tok.pos_start.copy().advance().advance(),
                        pos_end=tok.pos_end
                    ))
                elif current_tok_is_negative_e_infix:
                    self.advance()

                    num, error = self.make_number(_0prefixes=False)
                    if error is not None:
                        return [], error

                    num: Token
                    if num.type == TT["FLOAT"]:
                        return [], InvalidSyntaxError(
                            num.pos_start, num.pos_end,
                            "expected int, get float.",
                            origin_file="src.lexer.lexer.Lexer.make_tokens"
                        )
                    else:
                        tokens.append(Token(
                            TT['E_INFIX'],
                            pos_start=tok.pos_start,
                            pos_end=tok.pos_start.copy().advance()
                        ))
                        tokens.append(num.set_value(-1*num.value))
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
                if self.next_char() == "*":
                    there_is_a_space_or_a_tab_or_a_comment = True
                    self.skip_multiline_comment()
                else:
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

            # dollar-print
            elif self.current_char == "$":
                there_is_a_space_or_a_tab_or_a_comment = False
                dollar, id_ = self.make_dollar_print()
                tokens.append(dollar)
                tokens.append(id_)
            else:
                # illegal char
                pos_start = self.pos.copy()
                char = self.current_char
                try:
                    char_name = unicodedata.name(char)
                except ValueError:
                    char_name = "unknown char"
                return [], IllegalCharError(
                    pos_start, self.pos.advance(),
                    f"'{char}' is an illegal character (U+{hex(ord(char))[2:].upper()}, {char_name})",
                    origin_file="src.lexer.lexer.Lexer.make_tokens"
                )

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
                                                    "src.lexer.lexer.Lexer.make_pow")
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
                                                "src.lexer.lexer.Lexer.make_or")
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
                                                "src.lexer.lexer.Lexer.make_and")
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
        unicode_escape_character = False
        unicode_char_name = False
        bracket_expected = False

        unicode_ttl = 0
        unicode_str = ""
        unicode_char_name_str = ""
        unicode_char_name_exp_pos_start = self.pos.copy()

        self.advance()

        escape_characters = {  # \n is a back line, \t is a tab
            'n': '\n',
            't': '\t',
            'x': 'UNICODE2',
            'u': 'UNICODE4',
            'U': 'UNICODE8',
            'N': 'UNICODE_CHAR_NAME'
        }

        # if self.current_char == quote, we have to stop looping because the str is closed
        # if escape_character, the last char is a \, so there is an escape sequence
        # if escape_character but self.current_char != quote, we SHOULD continue looping because \" doesn't close the
        # str
        while self.current_char != quote or escape_character:
            if self.current_char is None:  # EOF: the string was not closed.
                return None, InvalidSyntaxError(
                    pos_start, pos_start.copy().advance(),
                    f"{other_quote}{quote}{other_quote} was never closed.",
                    "src.lexer.lexer.Lexer.make_string"
                )
            if unicode_escape_character:
                unicode_ttl -= 1
                if self.current_char not in "0123456789ABCDEF" + "abcdef":
                    return None, InvalidSyntaxError(
                        pos_start, self.pos,
                        "please provide valid unicode codepoint (in hexadecimal).",
                        origin_file="src.lexer.lexer.Lexer.make_string"
                    )
                unicode_str += self.current_char
                if unicode_ttl == 0:
                    unicode_escape_character = False
                    string_ += chr(int(unicode_str, base=16))
                    unicode_str = ""
            elif unicode_char_name:
                if bracket_expected:
                    if self.current_char != "{":
                        return None, InvalidSyntaxError(
                            unicode_char_name_exp_pos_start, self.pos.copy(),
                            "'{' expected after '\\N'.",
                            origin_file="src.lexer.lexer.Lexer.make_string"
                        )
                    self.advance()
                    bracket_expected = False
                    continue
                if self.current_char == "}":
                    unicode_char_name = False
                    try:
                        character = unicodedata.lookup(unicode_char_name_str)
                    except KeyError as e:
                        return None, InvalidSyntaxError(
                            unicode_char_name_exp_pos_start, self.pos.copy(),
                            str(e).replace('"', ''),  # There are quotes around the error message.
                            origin_file="src.lexer.lexer.Lexer.make_string"
                        )
                    string_ += character
                    self.advance()
                    continue
                unicode_char_name_str += self.current_char
            elif escape_character:  # if the last char is \, we check for escape sequence
                character = escape_characters.get(self.current_char, self.current_char)
                if character == "UNICODE2":
                    unicode_ttl = 2
                    unicode_escape_character = True
                    unicode_str = ""
                elif character == "UNICODE4":
                    unicode_ttl = 4
                    unicode_escape_character = True
                    unicode_str = ""
                elif character == "UNICODE8":
                    unicode_ttl = 8
                    unicode_escape_character = True
                    unicode_str = ""
                elif character == "UNICODE_CHAR_NAME":
                    unicode_char_name = True
                    bracket_expected = True
                    unicode_char_name_str = ""
                    unicode_char_name_exp_pos_start = self.pos.copy()
                else:
                    string_ += character
                # the arg is doubled: if self.current_char is not a valid escape_sequence, we get self.current_char as
                # the next char.
                escape_character = False  # there is no more escape char
            elif self.current_char == '\\':  # the next is an escape char
                escape_character = True
            else:  # there is no escape char, we add our char in the str
                string_ += self.current_char
            self.advance()  # we advance

        if unicode_escape_character:
            if bracket_expected:
                return None, InvalidSyntaxError(
                    unicode_char_name_exp_pos_start, self.pos.copy(),
                    "'{' expected after '\\N'.",
                    origin_file="src.lexer.lexer.Lexer.make_string"
                )
            return None, InvalidSyntaxError(
                pos_start, self.pos,
                f"please provide valid unicode codepoint (missing {unicode_ttl} hexadecimal digits).",
                origin_file="src.lexer.lexer.Lexer.make_string"
            )
        if unicode_char_name:
            return None, InvalidSyntaxError(
                pos_start, self.pos,
                "'\\N{' expression never closed.",
                origin_file="src.lexer.lexer.Lexer.make_string"
            )

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

    def make_number(self, digits=DIGITS + '.', _0prefixes=True, mode="int"):
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
        while self.current_char is not None and self.current_char in digits + '_':
            if self.current_char == '.':  # if the char is a dot
                if dot_count == 1:  # if we already encountered a dot
                    return None, InvalidSyntaxError(self.pos, self.pos.copy().advance(),
                                                    "a number can't have more than one dot.",
                                                    "src.lexer.lexer.Lexer.make_number")
                dot_count += 1
                num_str += '.'
            elif self.current_char == '_':  # you can write 5_371_281 instead of 5371281
                pass
            else:
                num_str += self.current_char
            self.advance()  # we advance

        if isinstance(self.current_char, str) and self.current_char not in digits and self.current_char in "23456789":
            base = {
                "bin": 2,
                "oct": 8
            }
            return None, InvalidSyntaxError(
                self.pos, self.pos.copy().advance(),
                f"invalid digit for base {base[mode]}: {self.current_char}",
                "src.lexer.lexer.Lexer.make_number"
            )

        if num_str == '.':
            return Token(TT["DOT"], pos_start=pos_start, pos_end=self.pos), None

        if num_str == '':
            return None, InvalidSyntaxError(
                pos_start, self.pos,
                "can not make a number with this expression.",
                "src.lexer.lexer.Lexer.make_number"
            )

        if _0prefixes and num_str == '0':
            prefixes: dict[str, tuple[str, str]] = {
                "x": ("012334567898ABCDEF"+"abcdef", "hex"),
                "X": ("012334567898ABCDEF"+"abcdef", "hex"),
                "o": ("01234567", "oct"),
                "O": ("01234567", "oct"),
                "b": ("01", "bin"),
                "B": ("01", "bin"),
            }
            if self.current_char in prefixes.keys():
                prefix = prefixes[self.current_char]
                self.advance()
                num, error = self.make_number(prefix[0], False, prefix[1])
                if error is not None:
                    return None, error
                return num, None

        if mode == 'int':
            if dot_count == 0:  # if there is no dots, this is an INT, else this is a FLOAT
                return Token(TT["INT"], int(num_str), pos_start, self.pos.copy()), None
            else:
                return Token(TT["FLOAT"], float(num_str), pos_start, self.pos.copy()), None
        elif mode == "hex":
            return Token(TT["INT"], int(num_str, 16), pos_start, self.pos.copy()), None
        elif mode == "oct":
            return Token(TT["INT"], int(num_str, 8), pos_start, self.pos.copy()), None
        elif mode == "bin":
            return Token(TT["INT"], int(num_str, 2), pos_start, self.pos.copy()), None
        else:
            raise Exception("The specified mode is incorrect...")

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
                                                "src.lexer.lexer.Lexer.make_not_equals")
            # !>>
            self.advance()
            return Token(TT["TO_AND_OVERWRITE"], pos_start=pos_start, pos_end=self.pos), None

        self.advance()
        return None, InvalidSyntaxError(pos_start, self.pos, "expected '!=' or '!>>', but got '!'.",
                                        "src.lexer.lexer.Lexer.make_not_equals")

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
                    f"expected '=' after '<<', got '{self.current_char}'.",
                    "src.lexer.lexer.Lexer.make_less_than"
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

    def make_dollar_print(self):
        """Make dollar-print syntax"""
        # current char is '$'
        dollar_pos = self.pos.copy()
        self.advance()

        id_pos_start = self.pos.copy()
        identifier = ""
        if self.current_char is not None and self.current_char in IDENTIFIERS_LEGAL_CHARS:
            identifier += self.current_char
            self.advance()

        # while not EOF and current char still in authorized chars in identifier and keywords
        while self.current_char is not None and self.current_char in LETTERS_DIGITS + '_':
            identifier += self.current_char
            self.advance()

        token_type = TT["KEYWORD"] if identifier in KEYWORDS else TT["IDENTIFIER"]  # KEYWORDS is the keywords list
        return Token(TT["DOLLAR"], pos_start=dollar_pos), Token(token_type, identifier, id_pos_start, self.pos)

    def skip_comment(self):
        """Skip a comment (until back line or EOF)"""
        # current char is '#'
        self.advance()

        while self.current_char != '\n' and self.current_char is not None:  # None -> EOF
            self.advance()

    def skip_multiline_comment(self):
        """Skip a multi-line comment (until */ or EOF)"""
        # current char is '/'
        self.advance()
        # current char is '*'
        self.advance()

        # None -> EOF
        while self.current_char is not None and not (self.current_char == "*" and self.next_char() == "/"):
            self.advance()
        if self.current_char == "*":
            self.advance()
            if self.current_char == "/":
                self.advance()
