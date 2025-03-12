#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2025  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.lexer.position import Position
from src.lexer.token import Token
from src.lexer.token_types import TT, KEYWORDS
from src.constants import LETTERS, DIGITS, IDENTIFIERS_LEGAL_CHARS
from src.errors.errors import InvalidSyntaxError, IllegalCharError, Error
import src.conffiles
# built-in python imports
import unicodedata


# ##########
# LEXER
# ##########
class Lexer:
    """Transforms code into a list of tokens (lexical units)"""
    def __init__(self, file_name: str, text: str, previous_metas: dict[str, str | bool] | None = None):
        self.file_name: str = file_name  # name of the file we're executing
        self.text = text  # raw code we have to execute
        self.pos = Position(-1, 0, -1, file_name, text)  # actual position of the lexer
        self.current_char: str | None = None
        if previous_metas is not None:
            self.metas = previous_metas
        else:
            self.metas: dict[str, str | bool] = {}
        debug = src.conffiles.access_data("debug")
        assert debug is not None
        self.debug = bool(int(debug))
        self.advance()

    def get_char(self, pos: Position):
        return self.text[pos.index] if pos.index < len(self.text) else None

    def advance(self):
        """Advance of 1 char in self.text, and return the new char"""
        self.pos.advance(self.current_char)  # advance in position
        # set the new current char - the next one in the code or None if this is EOF (end of file)
        self.current_char = self.get_char(self.pos)

        # if you want to know where tf you are in the file when it throws at you an unclear error,
        # uncomment these lines and change the right values:
        # if self.pos.index in [7583, 5547]:
        #     print(self.pos.index, self.pos.line_number, self.current_char, self.next_char())

        return self.current_char

    def next_char(self, n_next_chars: int = 1):
        """Returns the next char without advancing"""
        new_pos = self.pos.copy().advance(self.current_char)

        if n_next_chars != 1:
            next_char = self.get_char(new_pos)
            if next_char is not None:
                chars_to_return = next_char
            else:
                chars_to_return = ""

            for _ in range(n_next_chars-1):
                new_pos.advance(self.get_char(new_pos))
                next_char = self.get_char(new_pos)
                if next_char is not None:
                    chars_to_return += next_char
            return chars_to_return

        # get the next char in the code (or None if this is EOF (end of file))
        next_char = self.get_char(new_pos)
        return next_char

    def is_empty_file(self, tokens: list[Token]):
        """Returns if the given list of tokens corresponds to an empty file or not."""
        if len(tokens) == 0:
            return True
        if all([token.type == TT["NEWLINE"] for token in tokens]):
            return True
        return False

    def make_tokens(self) -> tuple[list[Token], None | Error]:
        """Returns a token list with self.text. Return tok_list, None or [], error."""
        tokens: list[Token] = []

        there_is_a_space_or_a_tab_or_a_comment = False
        while self.current_char is not None:  # None is EOF
            next_char = self.next_char()

            maybe_meta = self.next_char(6) == "@meta " and self.current_char in "%-@$"

            if self.current_char in ' \t\N{NBSP}\N{NNBSP}':  # tab and space
                there_is_a_space_or_a_tab_or_a_comment = True
                self.advance()
            elif self.current_char == '#':  # for comments
                if self.next_char(6) == "@meta ":
                    self.advance()
                    is_empty_file = self.is_empty_file(tokens)
                    self.make_meta(is_empty_file, True)
                there_is_a_space_or_a_tab_or_a_comment = True
                self.skip_comment()
            elif self.current_char == '\\' and next_char is not None and next_char in ';\n':
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

            elif self.current_char == "@" or maybe_meta:  # metas
                if maybe_meta:
                    self.advance()
                is_empty_file = self.is_empty_file(tokens)
                none_or_error = self.make_meta(is_empty_file)
                if none_or_error is not None:
                    return [], none_or_error

            elif self.current_char in DIGITS + '.':  # the char is a digit: we generate a number
                there_is_a_space_or_a_tab_or_a_comment = False
                number_with_error = self.make_number()
                if number_with_error[1] is None:  # there is no error
                    tokens.append(number_with_error[0])
                else:  # there is an error, we return it
                    return [], number_with_error[1]
            elif self.current_char in IDENTIFIERS_LEGAL_CHARS:  # the char is legal: identifier or keyword
                tok = self.make_identifier()
                assert tok.value is None or isinstance(tok.value, str)
                try:
                    last_tok_is_number = tokens[-1].type in (TT['INT'], TT['FLOAT'])
                except IndexError:
                    last_tok_is_number = False
                current_tok_is_identifier = tok.type == TT['IDENTIFIER']

                if not last_tok_is_number or not current_tok_is_identifier:
                    tokens.append(tok)
                    there_is_a_space_or_a_tab_or_a_comment = False
                    continue

                current_tok_is_maybe_e_infix: bool = (
                    tok.value is not None and last_tok_is_number and current_tok_is_identifier and
                    (tok.value.startswith('e') or tok.value.startswith('E'))
                )
                if not current_tok_is_maybe_e_infix:
                    tokens.append(tok)
                    there_is_a_space_or_a_tab_or_a_comment = False
                    continue

                tokens_to_append, error = self.make_e_infix(tok, len(tokens), there_is_a_space_or_a_tab_or_a_comment)
                if error is not None:
                    return [], error
                assert tokens_to_append is not None
                tokens.extend(tokens_to_append)

                there_is_a_space_or_a_tab_or_a_comment = False
            elif self.current_char in "'\"«":  # the char is a quote: str
                there_is_a_space_or_a_tab_or_a_comment = False
                string_, error = self.make_string(self.current_char)
                if error is None and string_ is not None:  # there is no error
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
                if error is not None or token is None:
                    return [], error
                tokens.append(token)
            elif self.current_char == '%':
                there_is_a_space_or_a_tab_or_a_comment = False
                tokens.append(self.make_perc())

            # bitwise operators
            elif self.current_char == "|":
                there_is_a_space_or_a_tab_or_a_comment = False
                token, error = self.make_or()
                if error is not None or token is None:
                    return [], error
                tokens.append(token)
            elif self.current_char == "&":
                there_is_a_space_or_a_tab_or_a_comment = False
                token, error = self.make_and()
                if error is not None or token is None:
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
                if error is not None or token is None:
                    return [], error
                tokens.append(token)
            elif self.current_char == '=':
                there_is_a_space_or_a_tab_or_a_comment = False
                tokens.append(self.make_equals())
            elif self.current_char == '<':
                there_is_a_space_or_a_tab_or_a_comment = False
                token, error = self.make_less_than()
                if error is not None or token is None:
                    return [], error
                tokens.append(token)
            elif self.current_char == '>':
                there_is_a_space_or_a_tab_or_a_comment = False
                token, error = self.make_greater_than()
                if error is not None:
                    return [], error
                assert token is not None
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
            # colon
            elif self.current_char == ":":
                there_is_a_space_or_a_tab_or_a_comment = False
                tokens.append(Token(TT["COLON"], pos_start=self.pos))
                self.advance()

            # dollar-print
            elif self.current_char == "$":
                there_is_a_space_or_a_tab_or_a_comment = False
                dollar = self.make_dollar_print()
                tokens.append(dollar)
            else:
                # illegal char
                pos_start = self.pos.copy()
                char = self.current_char

                if char == "»":
                    return [], InvalidSyntaxError(
                        pos_start, self.pos.advance(),
                        f'"«" was never opened.',
                        origin_file="src.lexer.lexer.Lexer.make_tokens"
                    )

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

    def make_meta(self, is_empty_file: bool, dont_panic_on_errors: bool = False) -> None | Error:
        """Make meta. dont_panic_on_errors is set when meta prefix is #@, for instance."""
        pos_start = self.pos.copy()
        if not is_empty_file:
            if dont_panic_on_errors: return
            return InvalidSyntaxError(
                self.pos.copy(), self.pos.advance(),
                "expected metas to be at the beginning of a file.",
                "src.lexer.lexer.Lexer.make_tokens"
            )
        current_char = self.advance()
        for c in "meta":
            if not current_char == c:
                if dont_panic_on_errors: return
                return InvalidSyntaxError(
                    pos_start, self.pos.advance(),
                    "expected keyword `meta`.",
                    "src.lexer.lexer.Lexer.make_tokens"
                )
            current_char = self.advance()

        if current_char is not None and current_char not in " \N{NBSP}\N{NNBSP}\t":
            if dont_panic_on_errors: return
            return InvalidSyntaxError(
                self.pos.copy(), self.pos.advance(),
                "expected whitespace.",
                "src.lexer.lexer.Lexer.make_tokens"
            )
        current_char = self.advance()

        meta_name = ""
        while current_char is not None and current_char in LETTERS:
            meta_name += current_char
            current_char = self.advance()

        meta_argument = ""
        if current_char is not None and current_char in " \N{NBSP}\N{NNBSP}\t":
            current_char = self.advance()
            while current_char is not None and current_char in LETTERS:
                meta_argument += current_char
                current_char = self.advance()

        if current_char is not None and current_char in " \N{NBSP}\N{NNBSP}\t":
            current_char = self.advance()

        if current_char is not None and current_char not in ";\n":
            if dont_panic_on_errors: return
            return InvalidSyntaxError(
                self.pos.copy(), self.pos.advance(),
                "expected newline.",
                "src.lexer.lexer.Lexer.make_tokens"
            )

        if meta_name == "":
            if dont_panic_on_errors: return
            return InvalidSyntaxError(
                pos_start, self.pos.copy(),
                "expected a meta name.",
                "src.lexer.lexer.Lexer.make_tokens"
            )

        self.advance()

        if self.debug:
            print(f"[META] {meta_name=} {meta_argument=}")
        if meta_argument == "":
            self.metas[meta_name] = True
        else:
            self.metas[meta_name] = meta_argument

    def make_plus(self):
        """Make + or += or ++ """
        token_type = TT["PLUS"]
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':  # +=
            self.advance()
            token_type = TT["PLUSEQ"]
        elif self.current_char == "+":  # ++
            self.advance()
            token_type = TT["INCREMENT"]

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_minus_or_arrow(self):
        """ Make - , ->, -= or -- """
        token_type = TT["MINUS"]
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '>':  # ->
            self.advance()
            token_type = TT["ARROW"]
        elif self.current_char == '=':  # -=
            self.advance()
            token_type = TT["MINUSEQ"]
        elif self.current_char == '-':  # --
            self.advance()
            token_type = TT["DECREMENT"]

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
            token_type = TT["FLOORDIV"]
            new_char = self.advance()
            if new_char == '=':  # //=
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
            token_type = TT["BITWISEXOR"]
            new_char = self.advance()
            if new_char == '=':  # ^^=
                self.advance()
                token_type = TT["BITWISEXOREQ"]
            elif self.current_char == '^':  # ^^^
                newest_char = self.advance()
                if newest_char != "=":
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
        legacy_abs = self.metas.get("legacyAbs")
        if legacy_abs:
            token_type = TT["LEGACYABS"]
        else:
            token_type = TT["BITWISEOR"]

        if self.current_char == '=':  # |=
            token_type = TT["BITWISEOREQ"]
            self.advance()
        elif self.current_char == '|':  # ||
            new_char = self.advance()
            if new_char != "=":
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
            new_char = self.advance()
            if new_char != "=":
                return None, InvalidSyntaxError(pos_start, self.pos, "expected '=' after '&&'.",
                                                "src.lexer.lexer.Lexer.make_and")
            token_type = TT["ANDEQ"]  # &&=
            self.advance()

        return Token(token_type, pos_start=pos_start, pos_end=self.pos), None

    def make_string(self, quote: str = '"'):
        """Make string. We need quote to know where to stop"""
        string_ = ''
        if quote == '"':
            other_quote = "'"
            closing_quote = '"'
        elif quote == "'":
            other_quote = '"'
            closing_quote = "'"
        else:
            other_quote = '"'
            closing_quote = "»"
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
        if quote == "«" and self.metas.get("nbspBetweenFrenchGuillemets") is not None:
            assert self.current_char is not None
            if self.current_char not in "\N{NBSP}\N{NNBSP}":
                return None, InvalidSyntaxError(
                    pos_start, self.pos.copy(),
                    "expected no break space or narrow no break space after '«', because nbspBetweenFrenchGuillemets "
                    "meta is enabled.",
                    "src.lexer.lexer.Lexer.make_string"
                )
            self.advance()

        escape_characters = {  # \n is a back line, \t is a tab
            'n': '\n',
            't': '\t',
            'x': 'UNICODE2',
            'u': 'UNICODE4',
            'U': 'UNICODE8',
            'N': 'UNICODE_CHAR_NAME'
        }

        # if self.current_char == closing_quote, we have to stop looping because the str is closed
        # if escape_character, the last char is a \, so there is an escape sequence
        # if escape_character but self.current_char != closing_quote, we SHOULD continue looping because \" doesn't
        # close the str
        def current_char_is_closing_quote():
            if closing_quote == "»" and self.metas.get("nbspBetweenFrenchGuillemets") is not None:
                if self.current_char is None:
                    return False
                return self.current_char in "\N{NBSP}\N{NNBSP}" and self.next_char() == closing_quote
            return self.current_char == closing_quote
        while not current_char_is_closing_quote() or escape_character:
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
        if self.metas.get("nbspBetweenFrenchGuillemets") is not None and closing_quote == "»":
            self.advance()

        self.advance()  # we advance after the str
        return Token(TT["STRING"], pos_start, self.pos, string_), None

    def make_identifier(self):
        """Make an identifier or a keyword"""
        id_str = ''  # identifier or keyword as python string
        pos_start = self.pos.copy()

        # while not EOF and current char still in authorized chars in identifier and keywords
        while self.current_char is not None and self.current_char in IDENTIFIERS_LEGAL_CHARS + DIGITS:
            id_str += self.current_char
            self.advance()

        token_type = TT["KEYWORD"] if id_str in KEYWORDS else TT["IDENTIFIER"]  # KEYWORDS is the keywords list
        return Token(token_type, pos_start, self.pos, id_str)

    def make_number(
            self,
            digits: str = DIGITS + '.',
            _0prefixes: bool = True,
            mode: str = "int"
    ) -> tuple[Token, None] | tuple[None, Error]:
        """Make number, int or float. mode corresponds to the base:
           `int` for base 10, `oct` for base 8, `bin` for base 2 and
           `hex` for base 16"""
        num_str = ''
        dot_count = 0  # we can't have more than one dot, so we count them
        last_was_dot = False
        last_was_underscore = False
        pos_start = self.pos.copy()

        if self.current_char == '+':
            self.advance()
        if self.current_char == '-':
            num_str += '-'
            self.advance()
        if self.current_char == "_":
            return None, InvalidSyntaxError(
                pos_start, self.pos.copy(),
                "trailing underscore at the start of the literal is not allowed.",
                "src.lexer.lexer.Lexer.make_number"
            )

        # if char is still a number or a dot
        while self.current_char is not None and self.current_char in digits + '_':
            if self.current_char == '.':  # if the char is a dot
                last_was_dot = True
                if last_was_underscore:
                    return None, InvalidSyntaxError(self.pos, self.pos.copy().advance(),
                                                    "invalid decimal literal",
                                                    "src.lexer.lexer.Lexer.make_number")
                if dot_count == 1:  # if we already encountered a dot
                    return None, InvalidSyntaxError(self.pos, self.pos.copy().advance(),
                                                    "a number can't have more than one dot.",
                                                    "src.lexer.lexer.Lexer.make_number")
                dot_count += 1
                num_str += '.'
            elif self.current_char == '_':  # you can write 5_371_281 instead of 5371281
                last_was_underscore = True
                if last_was_dot:
                    break
            else:
                last_was_underscore = last_was_dot = False
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
            if self.current_char in prefixes.keys() and self.current_char is not None:
                prefix = prefixes[self.current_char]
                self.advance()
                number_with_error = self.make_number(prefix[0], False, prefix[1])
                if number_with_error[1] is not None:
                    return None, number_with_error[1]
                return number_with_error[0], None

        if last_was_underscore:
            return None, InvalidSyntaxError(
                pos_start, self.pos.copy(),
                "trailing underscore is not allowed.",
                "src.lexer.lexer.Lexer.make_number"
            )

        if mode == 'int':
            if dot_count == 0:  # if there is no dots, this is an INT, else this is a FLOAT
                return Token(TT["INT"], pos_start, self.pos.copy(), int(num_str)), None
            else:
                return Token(TT["FLOAT"], pos_start, self.pos.copy(), float(num_str)), None
        elif mode == "hex":
            return Token(TT["INT"], pos_start, self.pos.copy(), int(num_str, 16)), None
        elif mode == "oct":
            return Token(TT["INT"], pos_start, self.pos.copy(), int(num_str, 8)), None
        elif mode == "bin":
            return Token(TT["INT"], pos_start, self.pos.copy(), int(num_str, 2)), None
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
            new_char = self.advance()
            if new_char == '=':  # <<=
                self.advance()
                token_type = TT["LTEQ"]
            else:
                current_char_user_friendly = f"'{new_char}'"
                if new_char is None:
                    current_char_user_friendly = "(end of file)"
                return None, InvalidSyntaxError(
                    pos_start,
                    self.pos,
                    f"expected '=' after '<<', got {current_char_user_friendly}.",
                    "src.lexer.lexer.Lexer.make_less_than"
                )
        elif self.current_char == "d" and self.next_char(7) == "efault>":  # <default>
            for _ in range(8):
                self.advance()
            token_type = TT["DEFAULT"]

        return Token(token_type, pos_start=pos_start, pos_end=self.pos), None

    def make_greater_than(self) -> tuple[Token, None] | tuple[None, Error]:
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
            new_char = self.advance()
            token_type = TT["TO"]
            if new_char == '=':
                self.advance()
                token_type = TT["GTEQ"]

        return Token(token_type, pos_start=pos_start, pos_end=self.pos), None

    def make_dollar_print(self):
        """Make dollar-print syntax"""
        # current char is '$'
        dollar_pos = self.pos.copy()
        self.advance()
        return Token(TT["DOLLAR"], pos_start=dollar_pos)

    def make_e_infix(
            self,
            tok: Token, 
            len_tokens: int,
            there_is_a_space_or_a_tab_or_a_comment: bool
    ) -> tuple[list[Token], None] | tuple[None, Error]:
        assert tok.value is None or isinstance(tok.value, str)

        token_enswith_digit = (
            tok.value is not None and tok.value[1:] != "" and
            set(tok.value[1:]) <= set(DIGITS + "_") and not tok.value[1:].startswith("_")
        )
        current_tok_is_unsigned_e_infix = (
            token_enswith_digit and self.current_char != "."
        )
        next_char = self.next_char()

        current_tok_is_negative_e_infix = False
        if next_char is not None and tok.value in ["e", "E"]:
            current_tok_is_negative_e_infix = (
                self.current_char == "-" and next_char in DIGITS
            )

        current_tok_is_positive_e_infix = False
        if next_char is not None and tok.value in ["e", "E"]:
            current_tok_is_positive_e_infix = (
                self.current_char == "+" and next_char in DIGITS
            )

        if len_tokens == 0:
            return [tok], None
        elif there_is_a_space_or_a_tab_or_a_comment:
            return [tok], None
        elif current_tok_is_unsigned_e_infix and tok.value is not None:
            return [Token(
                TT['E_INFIX'],
                pos_start=tok.pos_start,
                pos_end=tok.pos_start.copy().advance()
            ), Token(
                TT['INT'],
                value=int(tok.value[1:]),
                pos_start=tok.pos_start.copy().advance().advance(),
                pos_end=tok.pos_end
            )], None
        elif current_tok_is_negative_e_infix or current_tok_is_positive_e_infix:
            self.advance()

            num, error = self.make_number(_0prefixes=False)
            if error is not None:
                return None, error
            assert num is not None

            assert isinstance(num.value, int) or isinstance(num.value, float)
            if num.type == TT["FLOAT"]:
                return None, InvalidSyntaxError(
                    num.pos_start, num.pos_end,
                    "expected int, got float.",
                    origin_file="src.lexer.lexer.Lexer.make_e_infix"
                )
            list_to_return: list[Token] = []
            list_to_return.append(Token(
                TT['E_INFIX'],
                pos_start=tok.pos_start,
                pos_end=tok.pos_start.copy().advance()
            ))
            if current_tok_is_negative_e_infix:
                list_to_return.append(num.set_value(-1*num.value))
            else:
                list_to_return.append(num.set_value(num.value))
            return list_to_return, None
        else:
            return [tok], None

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

        opened_nested_comments = 0

        # None -> EOF
        while self.current_char is not None:
            if (self.current_char == "*" and self.next_char() == "/"):
                if opened_nested_comments == 0:
                    break
                self.advance()
                self.advance()
                opened_nested_comments -= 1
            elif (self.current_char == "/" and self.next_char() == "*"):
                self.advance()
                self.advance()
                opened_nested_comments += 1
            else:
                self.advance()
        if self.current_char == "*":
            new_char = self.advance()
            if new_char == "/":
                self.advance()
