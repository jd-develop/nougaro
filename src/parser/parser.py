#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2025  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.lexer.token_types import TT, TOKENS_NOT_TO_QUOTE, EQUALS
from src.errors.errors import InvalidSyntaxError, Error
from src.parser.parse_result import ParseResult
from src.lexer.token import Token
from src.parser.nodes import *
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

    def __init__(self, tokens: list[Token], metas: dict[str, str | bool] | None = None):
        if metas is None:
            metas = dict()
        self.tokens = tokens  # tokens from the lexer
        self.metas = metas  # metas from the parser
        self.token_index = -1  # we start at -1, because we advance 2 lines after, so the index will be 0
        self.current_token: Token | None = None  # Token is imported in src.nodes
        self.advance()
        self.then_s: list[tuple[Position, Position]] = []  # pos start then pos end

    def parse(self):
        """Parse tokens and return a result that contain a main node"""
        result = self.statements()
        return result

    def advance(self):
        """Advance of 1 token"""
        self.token_index += 1
        self.update_current_token()
        return self.current_token

    def next_token(self):
        """Return the next token, or the current one if EOF"""
        if 0 <= self.token_index + 1 < len(self.tokens):
            return self.tokens[self.token_index + 1]
        else:
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

    def advance_and_check_for(
            self,
            result: ParseResult,
            errmsg: str,
            tok_type: str,
            tok_value: str | None = None,
            origin_file: str = "advance_and_check_for",
            pos_start: Position | None = None,
            pos_end: Position | None = None,
            del_a_then: bool = False
    ):
        """Advance, then run `self.check_for`."""
        result.register_advancement()
        self.advance()

        return self.check_for(result, errmsg, tok_type, tok_value, origin_file, pos_start, pos_end, del_a_then)

    def check_for_and_advance(
            self,
            result: ParseResult,
            errmsg: str,
            tok_type: str,
            tok_value: str | None = None,
            origin_file: str = "advance_and_check_for",
            pos_start: Position | None = None,
            pos_end: Position | None = None,
            del_a_then: bool = False
    ):
        """Run `self.check_for`, then advance."""
        result = self.check_for(result, errmsg, tok_type, tok_value, origin_file, pos_start, pos_end, del_a_then)

        result.register_advancement()
        self.advance()

        return result

    def advance_check_for_and_advance(
            self,
            result: ParseResult,
            errmsg: str,
            tok_type: str,
            tok_value: str | None = None,
            origin_file: str = "advance_and_check_for",
            pos_start: Position | None = None,
            pos_end: Position | None = None,
            del_a_then: bool = False
    ):
        """Advance, then run `self.check_for`, and then advance."""
        result.register_advancement()
        self.advance()

        result = self.check_for(result, errmsg, tok_type, tok_value, origin_file, pos_start, pos_end, del_a_then)

        result.register_advancement()
        self.advance()
        return result

    def check_for(
            self,
            result: ParseResult,
            errmsg: str,
            tok_type: str | list[str],
            tok_value: str | None = None,
            origin_file: str = "check_for",
            pos_start: Position | None = None,
            pos_end: Position | None = None,
            del_a_then: bool = False
    ):
        """Check for a token of type tok_type, eventually with value tok_value. Returns the result.

        * `errmsg` is the error message that should be used if the token is not found. Note that the returned error
          is InvalidSyntaxError. Any occurence of the substring "%toktype%" is replaced by the current token’s type.
        * if `tok_type` is a str, it checks for TT[tok_type]. If it is a list, it checks if the type of the current
          token is in the list. Note that the values in the list need to be values of the TT dict, not the keys.
        * `tok_value`, if given, is used in the .matches() method. It can not be a list.
        * `origin_file` is used in the debug `origin_file` argument of the error. It is the name of the parser’s
          method. For instance, "atom" (converted to "src.parser.parser.Parser.atom")
        * `pos_start` and `pos_end` are the positions for the InvalidSyntaxError. By default (if not given or None),
          pos_start and pos_end are those of the current token.
        * `del_a_then`, if set to True, deletes the last element of the self.thens list.
        """
        assert self.current_token is not None
        if pos_start is None:
            pos_start = self.current_token.pos_start
        if pos_end is None:
            pos_end = self.current_token.pos_end
        if tok_value is None:
            if isinstance(tok_type, str):
                condition = self.current_token.type != TT[tok_type]
            else:
                condition = self.current_token.type not in tok_type
            if condition:
                if self.current_token.type in TOKENS_NOT_TO_QUOTE:
                    current_tok_type = self.current_token.type
                else:
                    current_tok_type = f"'{self.current_token.type}'"
                return result.failure(InvalidSyntaxError(
                    pos_start, pos_end,
                    errmsg.replace("%toktype%", current_tok_type),
                    f"src.parser.parser.Parser.{origin_file}"
                ))
        else:
            if isinstance(tok_type, list):
                raise ValueError("please don’t use tok type lists AND tok values.")
            if not self.current_token.matches(TT[tok_type], tok_value):
                if self.current_token.type in TOKENS_NOT_TO_QUOTE:
                    current_tok_type = self.current_token.type
                else:
                    current_tok_type = f"'{self.current_token.type}'"
                return result.failure(InvalidSyntaxError(
                    pos_start, pos_end,
                    errmsg.replace("%toktype%", current_tok_type),
                    f"src.parser.parser.Parser.{origin_file}"
                ))
        if del_a_then:
            del self.then_s[-1]
        return result


    # GRAMMARS ATOMS (AST) :

    def statements(self, stop: list[tuple[Any, str] | str] | None = None) -> ParseResult:
        """
        statements : NEWLINE* statement (NEWLINE+ statement)* NEWLINE

        The returned node in the parse result is ALWAYS a ListNode here.
        If stop is not specified or None, stop is [TT["EOF"]]"""
        assert self.current_token is not None
        if stop is None:
            stop = [TT["EOF"]]  # token(s) that stops parser in this function
        result = ParseResult()  # we create the result
        statements: list[tuple[Node, bool]] = []  # list of statements
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
        assert statement is not None
        assert not isinstance(statement, list)

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
            # I made a HUGE optimization here: there was a 'for' loop (git blame for date)
            if self.current_token.type in stop or (self.current_token.type, self.current_token.value) in stop:
                break
            if newline_count == 0:  # there was no new line between the last statement and this one: unexpected
                if self.current_token.type in TOKENS_NOT_TO_QUOTE:
                    quote = ""
                else:
                    quote = "'"
                # token
                last_tok_is_identifier = last_token_type == TT["IDENTIFIER"]
                current_tok_is_equal = self.current_token.type in \
                    EQUALS + [TT["INCREMENT"], TT["DECREMENT"]]
                missing_var_error_message = False
                if last_tok_is_identifier and current_tok_is_equal:
                    # there was no new line but there is 'id =' (need 'var')
                    missing_var_error_message = True
                elif last_token_type == TT["IDENTIFIER"] and self.current_token.type == TT["COMMA"]:
                    result.register_advancement()
                    self.advance()
                    missing_var = True
                    while self.current_token.type == TT["IDENTIFIER"]:
                        result.register_advancement()
                        self.advance()
                        if self.current_token.type in EQUALS:
                            break  # missing_var is already True
                        if not (self.current_token.type == TT["COMMA"] or self.current_token.type in EQUALS):
                            missing_var = False
                            break
                        result.register_advancement()
                        self.advance()
                    if missing_var and self.current_token.type in EQUALS:
                        # there was no new line but there is 'id1, id2, ... =' (need 'var')
                        missing_var_error_message = True
                error_msg = f"unexpected token: {quote}{self.current_token}{quote}."
                if missing_var_error_message:
                    error_msg += " To declare or update a variable, use 'var' "\
                                 "keyword."
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    error_msg,
                    "src.parser.parser.Parser.statements"
                ))

            if self.current_token.type == TT["EOF"] and len(self.then_s) != 0:
                return result.failure(InvalidSyntaxError(
                    self.then_s[-1][0], self.then_s[-1][1],
                    "expected 'end' to close a statement, surely this one.",
                    "src.parser.parser.Parser.statements"
                ))

            # we replace the last token type
            last_token_type = self.current_token.type

            # we register a statement, check for errors and append the statement if all is OK
            # statement
            statement = result.register(self.statement())
            if result.error is not None:
                return result
            assert statement is not None
            assert not isinstance(statement, list)

            statements.append((statement, False))

        return result.success(ListNode(  # we put all the nodes parsed here into a ListNode
            statements,
            pos_start,
            self.current_token.pos_end.copy()
        ))

    def statement(self) -> ParseResult:  # only one statement
        """
        statement     : KEYWORD:RETURN expr?
                      : KEYWORD:IMPORT IDENTIFIER (DOT IDENTIFIER)?* (KEYWORD:AS IDENTIFIER)?
                      : KEYWORD:EXPORT expr AS IDENTIFIER
                      : KEYWORD:EXPORT IDENTIFIER (KEYWORD:AS IDENTIFIER)?
                      : KEYWORD:CONTINUE (COLON IDENTIFIER)?
                      : KEYWORD:BREAK (COLON IDENTIFIER)? (KEYWORD:AND KEYWORD:RETURN expr)?
                      : expr
        """
        # we create the result and get the pos start from the current token
        result = ParseResult()
        assert self.current_token is not None
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
            # assert expr is not None
            assert not isinstance(expr, list)

            return result.success(ReturnNode(expr, pos_start, self.current_token.pos_start.copy()))

        # KEYWORD:IMPORT IDENTIFIER
        if self.current_token.matches(TT["KEYWORD"], 'import'):
            result = self.advance_and_check_for(result, "expected identifier after 'import'.",
                                                "IDENTIFIER", origin_file="statement")
            if result.error is not None:
                return result

            identifiers = [self.current_token]
            result.register_advancement()
            self.advance()

            while self.current_token.type == TT["DOT"]:
                result = self.advance_and_check_for(result, "expected identifier after 'import'.",
                                                    "IDENTIFIER", origin_file="statement")
                if result.error is not None:
                    return result

                identifiers.append(self.current_token)
                result.register_advancement()
                self.advance()

            as_identifier = None
            if self.current_token.matches(TT["KEYWORD"], "as"):
                result = self.advance_and_check_for(result, "expected identifier after 'as'.",
                                                    "IDENTIFIER", origin_file="statement")
                if result.error is not None:
                    return result

                as_identifier = self.current_token
                result.register_advancement()
                self.advance()

            return result.success(ImportNode(
                identifiers, pos_start, self.current_token.pos_start.copy(), as_identifier
            ))

        if self.current_token.matches(TT["KEYWORD"], 'export'):
            # we advance
            result.register_advancement()
            self.advance()

            is_identifier = self.current_token.type == TT["IDENTIFIER"]
            next_tok = self.next_token()
            assert next_tok is not None
            next_is_as_or_newline = next_tok.matches(TT["KEYWORD"], 'as') or next_tok.type in [TT["NEWLINE"], TT["EOF"]]
            if is_identifier and next_is_as_or_newline:
                expr_or_identifier = self.current_token
                as_required = False
                result.register_advancement()
                self.advance()
            else:
                # we register an expr
                expr_or_identifier = result.register(self.expr())
                if result.error is not None:
                    return result
                assert expr_or_identifier is not None
                as_required = True

            current_tok_is_as = self.current_token.matches(TT["KEYWORD"], "as")
            if as_required and not current_tok_is_as:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected keyword 'as'.",
                    "src.parser.parser.Parser.statement"
                ))
            if current_tok_is_as:
                result = self.advance_and_check_for(result, "expected identifier after 'as'.",
                                                    "IDENTIFIER", origin_file="statement")
                if result.error is not None:
                    return result

                as_identifier = self.current_token
                result.register_advancement()
                self.advance()
            else:
                as_identifier = None
            assert not isinstance(expr_or_identifier, list)

            return result.success(
                ExportNode(expr_or_identifier, as_identifier, pos_start, self.current_token.pos_start.copy())
            )

        # KEYWORD:CONTINUE
        if self.current_token.matches(TT["KEYWORD"], 'continue'):
            result.register_advancement()
            self.advance()

            label = None
            if self.current_token.type == TT["COLON"]:
                result = self.advance_and_check_for(
                    result, "expected label identifier after ':'.", "IDENTIFIER",
                    origin_file="statement"
                )
                if result.error is not None:
                    return result
                label = self.current_token.value
                assert isinstance(label, str)
                result.register_advancement()
                self.advance()

            return result.success(ContinueNode(pos_start, self.current_token.pos_start.copy(), label))

        # KEYWORD:BREAK
        if self.current_token.matches(TT["KEYWORD"], 'break'):
            result.register_advancement()
            self.advance()

            label = None
            if self.current_token.type == TT["COLON"]:
                result = self.advance_and_check_for(
                    result, "expected label identifier after ':'.", "IDENTIFIER",
                    origin_file="statement"
                )
                if result.error is not None:
                    return result
                label = self.current_token.value
                assert isinstance(label, str)
                result.register_advancement()
                self.advance()

            expr_to_return = None
            if self.current_token.matches(TT["KEYWORD"], "and"):
                result = self.advance_check_for_and_advance(
                    result, "expected keyword “return” after “and”.", "KEYWORD",
                    "return", "statement"
                )
                if result.error is not None:
                    return result
                expr_to_return = result.register(self.expr())
                if result.error is not None:
                    return result

            return result.success(
                BreakNode(pos_start, self.current_token.pos_start.copy(), expr_to_return, label)
            )

        # expr
        expr = result.register(self.expr())
        if result.error is not None:
            return result
        assert expr is not None

        return result.success(expr)

    def expr(self) -> ParseResult:
        """
        expr    : var_assign
                : KEYWORD:DEL IDENTIFIER
                : KEYWORD:WRITE expr (TO|TO_AND_OVERWRITE) expr INT?
                : KEYWORD:READ expr (TO IDENTIFIER)? INT?
                : KEYWORD:ASSERT expr (COMMA expr)?
                : comp_expr ((KEYWORD:AND|KEYWORD:OR|KEYWORD:XOR|BITWISEAND|BITWISEOR|BITWISEXOR) comp_expr)*
        """
        # we create the result and the pos start
        result = ParseResult()
        assert self.current_token is not None
        pos_start = self.current_token.pos_start.copy()

        # var_assign
        if self.current_token.matches(TT["KEYWORD"], 'var'):
            var_assign_node = result.register(self.var_assign())
            if result.error is not None:
                return result
            assert var_assign_node is not None

            return result.success(var_assign_node)

        # KEYWORD:DEL IDENTIFIER
        if self.current_token.matches(TT["KEYWORD"], 'del'):
            return self.var_delete()

        # KEYWORD:WRITE expr (TO|TO_AND_OVERWRITE) expr INT?
        if self.current_token.matches(TT["KEYWORD"], 'write'):
            return self.write_expr(pos_start)

        # KEYWORD:READ expr (TO IDENTIFIER)? INT?
        if self.current_token.matches(TT["KEYWORD"], 'read'):
            return self.read_expr(pos_start)

        # KEYWORD:ASSERT expr (COMMA expr)?
        if self.current_token.matches(TT["KEYWORD"], "assert"):
            return self.assert_expr(pos_start)

        if self.current_token.matches(TT["KEYWORD"], "end"):
            if len(self.then_s) == 0:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "didn't expect 'end', because there is nothing to close.",
                    "src.parser.parser.Parser.expr"
                ))

        # comp_expr ((KEYWORD:AND|KEYWORD:OR|KEYWORD:XOR|BITWISEAND|BITWISEOR|BITWISEXOR) comp_expr)*
        node = result.register(self.bin_op(self.comp_expr,
            (
                (TT["KEYWORD"], "and"),
                (TT["KEYWORD"], "or"),
                (TT["KEYWORD"], 'xor'),
                TT["BITWISEAND"],
                TT["BITWISEOR"],
                TT["BITWISEXOR"]
            )
        ))

        if result.error is not None:
            return result
        assert node is not None
        return result.success(node)

    def var_delete(self) -> ParseResult:
        # todo: accept attributes
        result = ParseResult()
        result.register_advancement()
        self.advance()
        assert self.current_token is not None

        # if the current tok is not an identifier, return an error
        if self.current_token.type != TT["IDENTIFIER"]:
            if self.current_token.type == TT["KEYWORD"]:
                error_msg = "using a keyword as idendifier is illegal."
            elif self.current_token.type in TOKENS_NOT_TO_QUOTE:
                error_msg = f"expected identifier, but got {self.current_token.type}."
            else:
                error_msg = f"expected identifier, but got '{self.current_token.type}'."
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end, error_msg,
                "src.parser.parser.Parser.var_delete"
            ))

        # we assign the identifier to a variable then we advance
        var_name = self.current_token
        result.register_advancement()
        self.advance()

        if result.error is not None:
            return result
        return result.success(VarDeleteNode(var_name))

    def write_expr(self, pos_start: Position) -> ParseResult:
        result = ParseResult()
        result.register_advancement()
        self.advance()
        assert self.current_token is not None

        # we check for an expr
        expr_to_write = result.register(self.expr())
        if result.error is not None:
            return result
        assert expr_to_write is not None

        # (TO|TO_AND_OVERWRITE)
        result = self.check_for(
            result,
            "'>>' or '!>>' is missing. The correct syntax is 'write <expr> >> <expr>' or "
            "'write <expr> !>> <expr>' to override.",
            [TT["TO"], TT["TO_AND_OVERWRITE"]], None, "write_expr"
        )
        if result.error is not None:
            return result
        to_token = self.current_token

        result.register_advancement()
        self.advance()

        # we check for an expr
        file_name_expr = result.register(self.expr())
        if result.error is not None:
            return result
        assert file_name_expr is not None

        # We check if there is an 'int' token. If not, we will return the default value
        if self.current_token.type == TT["INT"]:
            line_number = self.current_token.value
            assert isinstance(line_number, int)

            result.register_advancement()
            self.advance()
        else:
            line_number = 'last'
        assert not isinstance(expr_to_write, list)
        assert not isinstance(file_name_expr, list)

        return result.success(WriteNode(
            expr_to_write, file_name_expr, to_token, line_number,
            pos_start, self.current_token.pos_start.copy()
        ))

    def read_expr(self, pos_start: Position) -> ParseResult:
        result = ParseResult()
        assert self.current_token is not None
        result.register_advancement()
        self.advance()

        # we check for an expr
        file_name_expr = result.register(self.expr())
        if result.error is not None:
            return result
        assert file_name_expr is not None

        identifier = None

        # (TO IDENTIFIER)?
        if self.current_token.type == TT["TO"]:
            result = self.advance_and_check_for(
                result, f"expected identifier, got {self.current_token.type}.",
                "IDENTIFIER", None, "read_expr"
            )
            if result.error is not None:
                return result

            identifier = self.current_token
            result.register_advancement()
            self.advance()

        # INT?
        if self.current_token.type == TT["INT"]:
            line_number = self.current_token.value
            assert isinstance(line_number, int)

            result.register_advancement()
            self.advance()
        else:
            line_number = 'all'
        assert not isinstance(file_name_expr, list)

        return result.success(ReadNode(
            file_name_expr, identifier, line_number,
            pos_start, self.current_token.pos_start.copy()
        ))

    def assert_expr(self, pos_start: Position) -> ParseResult:
        result = ParseResult()
        result.register_advancement()
        self.advance()
        assert self.current_token is not None

        # we check for expr
        assertion = result.register(self.expr())
        if result.error is not None:
            return result
        assert assertion is not None

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

            assert not isinstance(assertion, list)
            assert not isinstance(errmsg, list)

            return result.success(AssertNode(
                assertion, pos_start, self.current_token.pos_start.copy(),
                errmsg=errmsg
            ))
        assert not isinstance(assertion, list)

        return result.success(AssertNode(assertion, pos_start, self.current_token.pos_start.copy()))

    def var_assign(self) -> ParseResult:
        """
        var_assign : KEYWORD:VAR assign_id (COMMA assign_id)?* assign_eq assign_expr
                   : KEYWORD:VAR assign_id (INCREMENT|DECREMENT)
        """
        result = ParseResult()
        assert self.current_token is not None
        pos_start = self.current_token.pos_start.copy()

        result = self.check_for_and_advance(
            result, "expected 'var' keyboard.", "KEYWORD", "var", "var_assign"
        )

        if result.error is not None:
            return result
        all_names_list: list[list[Node | Token]] = []

        while self.current_token.type not in EQUALS:
            # if current token is not identifier we have to register expr
            result = self.check_for(result, "expected identifier.", "IDENTIFIER", None, "var_assign")
            if result.error is not None:
                return result

            current_name_nodes_and_tokens_list, error = self.assign_identifier()
            if error is not None:
                return result.failure(error)
            assert current_name_nodes_and_tokens_list is not None

            all_names_list.append(current_name_nodes_and_tokens_list)
            if self.current_token.type != TT["COMMA"]:
                break
            else:
                result.register_advancement()
                self.advance()

        if len(all_names_list) == 0:
            return result.failure(InvalidSyntaxError(
                pos_start, self.current_token.pos_start,
                "expected at least one identifier.",
                origin_file="src.parser.parser.Parser.var_assign"
            ))

        equal = self.current_token
        if equal.type in [TT["INCREMENT"], TT["DECREMENT"]]:
            result.register_advancement()
            self.advance()
            return result.success(VarAssignNode(all_names_list, None, equal))
        elif equal.type not in EQUALS:
            if self.current_token.type in [TT["EE"], TT["GT"], TT["LT"], TT["GTE"], TT["LTE"], TT["NE"]]:
                error_msg = f"expected an assignation equal, but got a test equal ('{self.current_token.type}')."
            elif self.current_token.type in TOKENS_NOT_TO_QUOTE:
                error_msg = f"expected an equal, but got {self.current_token.type}."
            else:
                error_msg = f"expected an equal, but got '{self.current_token.type}'."
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end, error_msg,
                "src.parser.parser.Parser.expr"
            ))
        result.register_advancement()
        self.advance()

        # expr (COMMA expr)?*
        # we register an expr
        first_node = result.register(self.expr())
        if result.error is not None:
            return result
        assert first_node is not None
        assert not isinstance(first_node, list)
        expressions = [first_node]

        while self.current_token.type == TT["COMMA"]:  # (COMMA expr)?*
            result.register_advancement()
            self.advance()
            node = result.register(self.expr())
            if result.error is not None:
                return result
            assert node is not None
            assert not isinstance(node, list)
            expressions.append(node)

        return result.success(VarAssignNode(all_names_list, expressions, equal))

    def assign_identifier(self) -> tuple[list[Node | Token], None] | tuple[None, Error]:
        """
        assign_id  : (IDENTIFIER (LPAREN NEWLINE?* (MUL? expr (COMMA NEWLINE?* MUL? expr)?*)? NEWLINE?* RPAREN)?* DOT)?* IDENTIFIER
        """
        result = ParseResult()
        current_name_nodes_and_tokens_list: list[Node | Token] = []

        identifier_expected = False
        is_attr = False
        assert self.current_token is not None
        while self.current_token.type == TT["IDENTIFIER"]:
            identifier_expected = False
            identifier = self.current_token
            result.register_advancement()
            self.advance()

            call_node = identifier
            call_node_node = VarAccessNode([identifier], is_attr)
            is_call = self.current_token.type == TT["LPAREN"]

            while self.current_token.type == TT["LPAREN"]:
                result.register_advancement()
                self.advance()
                arg_nodes: list[tuple[Node, bool]] = []

                cur_tok = self.current_token
                while cur_tok is not None and cur_tok.type == TT["NEWLINE"]:
                    result.register_advancement()
                    cur_tok = self.advance()

                comma_expected = False
                mul = False
                # we check for the closing paren.
                if self.current_token.type == TT["RPAREN"]:
                    pos_end = self.current_token.pos_end.copy()
                    result.register_advancement()
                    self.advance()
                    call_node_node = CallNode(call_node_node, arg_nodes, pos_end)
                    continue

                # (MUL? expr (COMMA MUL? expr)?*)?
                if self.current_token.type == TT["MUL"]:  # MUL?
                    mul = True
                    # we advance
                    result.register_advancement()
                    self.advance()
                # expr
                expr_node = result.register(self.expr())
                if result.error is not None:
                    return None, result.error
                assert expr_node is not None
                assert not isinstance(expr_node, list)

                arg_nodes.append((expr_node, mul))
                while self.current_token.type == TT["COMMA"]:  # (COMMA MUL? expr)?*
                    mul = False
                    # we advance
                    result.register_advancement()
                    self.advance()

                    cur_tok = self.current_token
                    while cur_tok is not None and cur_tok.type == TT["NEWLINE"]:
                        result.register_advancement()
                        cur_tok = self.advance()

                    if self.current_token.type == TT["MUL"]:  # MUL?
                        mul = True
                        # we advance
                        result.register_advancement()
                        self.advance()
                    # expr
                    # we register an expr then check for an error
                    expr_node = result.register(self.expr())
                    if result.error is not None:
                        # type ignore is required because type checking strict is DUMB
                        return None, result.error  # type: ignore
                    assert expr_node is not None
                    assert not isinstance(expr_node, list)

                    arg_nodes.append((expr_node, mul))

                cur_tok = self.current_token
                while cur_tok is not None and cur_tok.type == TT["NEWLINE"]:
                    result.register_advancement()
                    cur_tok = self.advance()

                pos_end = self.current_token.pos_end.copy()
                result = self.check_for_and_advance(
                    result, "expected ',' or ')'." if comma_expected else "expected ')'.",
                    "RPAREN", None, "assign_identifier"
                )
                if result.error is not None:
                    return None, result.error
                call_node_node = CallNode(call_node_node, arg_nodes, pos_end)

            if is_call:
                call_node = call_node_node

            if self.current_token.type == TT["DOT"]:
                is_attr = True
                current_name_nodes_and_tokens_list.append(call_node)  # call_node can be identifier token
                result.register_advancement()
                self.advance()
                identifier_expected = True
            elif is_call:
                return None, InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected dot.",
                    origin_file="src.parser.parser.Parser.assign_identifier"
                )
            else:
                current_name_nodes_and_tokens_list.append(call_node)
                break

        if identifier_expected:
            return None, InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "expected identifier after dot.",
                origin_file="src.parser.parser.Parser.assign_identifier"
            )
        return current_name_nodes_and_tokens_list, None

    def comp_expr(self) -> ParseResult:
        """
        comp_expr  : (KEYWORD:NOT|BITWISENOT) comp_expr
                   : arith_expr ((EE|LT|GT|LTE|GTE|KEYWORD:IN) arith_expr)*
        """
        # we create a result
        result = ParseResult()
        assert self.current_token is not None

        # (KEYWORD:NOT|BITWISENOT) comp_expr
        is_not_keyword = self.current_token.matches(TT["KEYWORD"], 'not')
        is_bitwise_not = self.current_token.type == TT["BITWISENOT"]
        if is_not_keyword or is_bitwise_not:
            op_token = self.current_token
            result.register_advancement()
            self.advance()

            # we check for comp_expr
            node = result.register(self.comp_expr())
            if result.error is not None:
                return result
            assert node is not None
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
        assert node is not None
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

        assert token is not None
        # (PLUS|MINUS) factor
        if token.type in (TT["PLUS"], TT["MINUS"]):
            result.register_advancement()
            self.advance()

            # we check for factor
            factor = result.register(self.factor())
            if result.error is not None:
                return result
            assert factor is not None
            return result.success(UnaryOpNode(token, factor))
        elif token.type == TT["LEGACYABS"]:
            pos = (token.pos_start, token.pos_end)
            result.register_advancement()
            self.advance()

            # we check for factor
            factor = result.register(self.factor())
            if result.error is not None:
                return result
            assert factor is not None

            result = self.check_for_and_advance(
                result,
                "this '|' (absolute value) was never closed, or an invalid expression was given.",
                "LEGACYABS", None, "factor", *pos
            )

            return result.success(AbsNode(factor))

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
        assert value is not None
        assert not isinstance(value, list)

        values_list: list[Node] = [value]

        assert self.current_token is not None
        while self.current_token.type == TT["DOT"]:
            result.register_advancement()
            self.advance()
            value = result.register(self.call())
            if result.error is not None:
                return result
            assert value is not None
            assert not isinstance(value, list)

            values_list.append(value)

        return self.bin_op(values_list, (TT["POW"],), self.factor)  # do not remove the comma after 'TT["POW"]' !!

    def call(self) -> ParseResult:
        """
        call       : atom (LPAREN NEWLINE?* (MUL? expr (COMMA NEWLINE?* MUL? expr)?*)? NEWLINE?* RPAREN)?*
        """
        result = ParseResult()

        # we check for atom
        atom = result.register(self.atom())
        if result.error is not None:
            return result
        assert atom is not None

        assert self.current_token is not None
        # (LPAREN NEWLINE?* (MUL? expr (COMMA NEWLINE?* MUL? expr)?*)? NEWLINE?* RPAREN)?*
        if self.current_token.type != TT["LPAREN"]:
            # not a function
            return result.success(atom)

        call_node = atom
        # the '*' at the end of the grammar rule
        # in fact, if we have a()(), we call a, then we call its result. All of that is in one single grammar rule.
        while self.current_token.type == TT["LPAREN"]:
            result.register_advancement()
            self.advance()
            arg_nodes: list[tuple[Node, bool]] = []

            cur_tok = self.current_token
            while cur_tok is not None and self.current_token.type == TT["NEWLINE"]:
                result.register_advancement()
                cur_tok = self.advance()

            comma_expected = False
            mul = False
            # we check for the closing paren.
            if self.current_token.type == TT["RPAREN"]:
                pos_end = self.current_token.pos_end.copy()
                result.register_advancement()
                self.advance()

                assert not isinstance(call_node, list)
                call_node = CallNode(call_node, arg_nodes, pos_end)
                continue

            # (MUL? expr (COMMA MUL? expr)?*)?
            if self.current_token.type == TT["MUL"]:  # MUL?
                mul = True
                # we advance
                result.register_advancement()
                self.advance()

            # expr
            expr_ = result.register(self.expr())
            if result.error is not None:
                return result
            assert expr_ is not None
            assert not isinstance(expr_, list)

            expr_and_mul = (expr_, mul)
            arg_nodes.append(expr_and_mul)
            while self.current_token.type == TT["COMMA"]:  # (COMMA MUL? expr)?*
                mul = False
                # we advance
                result.register_advancement()
                self.advance()

                cur_tok = self.current_token
                while cur_tok is not None and self.current_token.type == TT["NEWLINE"]:
                    result.register_advancement()
                    cur_tok = self.advance()

                if self.current_token.type == TT["MUL"]:  # MUL?
                    mul = True
                    # we advance
                    result.register_advancement()
                    self.advance()
                # expr
                # we register an expr then check for an error
                expr_ = result.register(self.expr())
                if result.error is not None:
                    return result
                assert expr_ is not None
                assert not isinstance(expr_, list)
                expr_and_mul = (expr_, mul)

                arg_nodes.append(expr_and_mul)

            cur_tok = self.current_token
            while cur_tok is not None and self.current_token.type == TT["NEWLINE"]:
                result.register_advancement()
                cur_tok = self.advance()

            pos_end = self.current_token.pos_end.copy()
            result = self.check_for_and_advance(
                result, "expected ',' or ')'." if comma_expected else "expected ')'.",
                "RPAREN", None, "call"
            )
            if result.error is not None:
                return result
            assert not isinstance(call_node, list)

            call_node = CallNode(call_node, arg_nodes, pos_end)

        return result.success(call_node)

    def atom(self) -> ParseResult:
        """
        atom  : (INT|FLOAT)(E_INFIX INT)?|(STRING (STRING NEWLINE?*)?*)
              : (IDENTIFIER (INTERROGATIVE_PNT IDENTIFIER|expr)?*)
              : LPAREN NEWLINE?* expr NEWLINE?* RPAREN
              : DOLLAR IDENTIFIER
              : list_expr
              : if_expr
              : for_expr
              : while_expr
              : do_expr
              : loop_expr
              : func_def
              : <default>
        """
        # we create the result
        result = ParseResult()
        assert self.current_token is not None
        token = self.current_token

        # (INT|FLOAT)(E_INFIX INT)?
        if token.type in (TT["INT"], TT["FLOAT"]):
            expr = result.register(self.int_or_float(token))
        # STRING (STRING)?*
        elif token.type == TT["STRING"]:
            expr = result.register(self.string_expr(token))
        # IDENTIFIER (INTERROGATIVE_PNT IDENTIFIER|expr)?*
        elif token.type == TT["IDENTIFIER"]:
            expr = result.register(self.identifier_and_interrogative_point(token))
        # LPAREN expr RPAREN
        elif token.type == TT["LPAREN"]:
            expr = result.register(self.paren_expr())
        elif token.type == TT["DOLLAR"]:
            expr = result.register(self.dollar_print_expr(token))
        # list_expr
        elif token.type == TT["LSQUARE"]:
            expr = result.register(self.list_expr())
        # if_expr
        elif token.matches(TT["KEYWORD"], 'if'):
            expr = result.register(self.if_expr())
        # for_expr
        elif token.matches(TT["KEYWORD"], 'for'):
            expr = result.register(self.for_expr())
        # while_expr
        elif token.matches(TT["KEYWORD"], 'while'):
            expr = result.register(self.while_expr())
        # do_expr
        elif token.matches(TT["KEYWORD"], 'do'):
            expr = result.register(self.do_expr())
        elif token.matches(TT["KEYWORD"], 'loop'):
            expr = result.register(self.loop_expr())
        # func_def
        elif token.matches(TT["KEYWORD"], 'def'):
            expr = result.register(self.func_def())
        # class_def
        elif token.matches(TT["KEYWORD"], 'class'):
            expr = result.register(self.class_def())
        elif token.matches(TT["KEYWORD"], "else"):
            return result.failure(InvalidSyntaxError(
                token.pos_start, token.pos_end,
                "expected valid expression. Maybe you forgot to close an 'end'?",
                "src.parser.parser.Parser.atom"
            ))
        elif token.type == TT["DEFAULT"]:
            expr = DefaultNode(self.current_token.pos_start, self.current_token.pos_end)
            result.register_advancement()
            self.advance()
        else:
            return result.failure(InvalidSyntaxError(
                token.pos_start, token.pos_end,
                "expected valid expression.",
                "src.parser.parser.Parser.atom"
            ))
        if result.error is not None:
            return result
        assert expr is not None
        return result.success(expr)

    def int_or_float(self, token: Token) -> ParseResult:
        result = ParseResult()
        # we advance
        result.register_advancement()
        self.advance()
        assert self.current_token is not None

        # (E_INFIX INT)?
        if self.current_token.type == TT["E_INFIX"]:
            # INT
            self.advance_and_check_for(
                result, f"expected integer, got %toktype%.", "INT", None, "int_or_float"
            )
            if result.error is not None:
                return result
            exp_token = self.current_token

            # we advance
            result.register_advancement()
            self.advance()
            return result.success(NumberENumberNode(token, exp_token))

        # we return a NumberNode
        return result.success(NumberNode(token))

    def string_expr(self, token: Token) -> ParseResult:
        result = ParseResult()
        assert isinstance(token.value, str)
        # to_return_str is a python str. As we go along the (STRING)?*, we add these to our to_return_str
        to_return_str = token.value  # actually just STRING, not (STRING)?* yet.
        to_return_tok = token.copy()
        assert self.current_token is not None

        # we advance
        result.register_advancement()
        self.advance()

        # (STRING NEWLINE?*)?*
        while self.current_token.type == TT["STRING"]:
            assert isinstance(self.current_token.value, str)
            to_return_str += self.current_token.value

            result.register_advancement()
            self.advance()

            while self.current_token.type == TT["NEWLINE"]:
                next_ = self.next_token()
                if next_ is None:
                    break
                if next_.type not in (TT["NEWLINE"], TT["STRING"]):
                    break
                result.register_advancement()
                self.advance()

        to_return_tok.value = to_return_str
        return result.success(StringNode(to_return_tok))

    def identifier_and_interrogative_point(self, token: Token) -> ParseResult:
        result = ParseResult()
        # the identifier is in the token in 'token'
        # we advance
        result.register_advancement()
        self.advance()
        assert self.current_token is not None

        # IDENTIFIER
        # choices represent all the identifiers in atoms such as 'foo ? bar ? foo_ ? bar_'
        choices: list[Node | Token] = [token]
        # (INTERROGATIVE_PNT IDENTIFIER)?*
        while self.current_token.type == TT["INTERROGATIVE_PNT"]:
            # we advance
            result.register_advancement()
            self.advance()

            value = self.current_token
            # we check for identifier
            if self.current_token.type != TT["IDENTIFIER"]:
                # eventually, the user could use a value instead of an identifier
                value = result.register(self.expr())
                if result.error is not None:
                    return result
                assert value is not None
                # append the token to our list
                assert not isinstance(value, list)

                choices.append(value)
                break  # the expr is the final value we want to parse
                #        E.g.: `identifier ? identifier ? expr ? whatever` : we don't want the `? whatever`

            # append the token to our list
            choices.append(value)
            # we advance
            result.register_advancement()
            self.advance()

        return result.success(VarAccessNode(choices))

    def paren_expr(self) -> ParseResult:
        result = ParseResult()

        # we advance
        result.register_advancement()
        self.advance()

        while self.current_token is not None and self.current_token.type == TT["NEWLINE"]:
            result.register_advancement()
            self.advance()

        # we register an expr
        expr = result.register(self.expr())
        if result.error is not None:  # we check for any error
            return result
        assert expr is not None

        while self.current_token is not None and self.current_token.type == TT["NEWLINE"]:
            result.register_advancement()
            self.advance()

        # we check for right parenthesis
        result = self.check_for_and_advance(result, "expected ')'.", "RPAREN", None, "paren_expr")
        if result.error is not None:
            return result

        return result.success(expr)

    def dollar_print_expr(self, token: Token) -> ParseResult:
        result = ParseResult()
        result.register_advancement()
        self.advance()

        if self.current_token is not None and self.current_token.type == TT["IDENTIFIER"]:
            identifier = self.current_token
            assert identifier is not None
            result.register_advancement()
            self.advance()
        else:
            identifier = Token(TT["IDENTIFIER"], token.pos_start, token.pos_end, "")

        return result.success(DollarPrintNode(identifier, token.pos_start, identifier.pos_end.copy()))

    def list_expr(self) -> ParseResult:
        """
        list_expr  : LSQUARE NEWLINE?* (MUL? expr (COMMA NEWLINE?* MUL? expr)?*)? NEWLINE?* RSQUARE
        """
        # we create the result
        result = ParseResult()
        # the python list that will contain the nougaro list's elements
        element_nodes: list[tuple[Node, bool]] = []
        # we copy the current token pos start
        assert self.current_token is not None
        pos_start = self.current_token.pos_start.copy()
        first_tok_pos_end = self.current_token.pos_end.copy()

        mul = False

        result = self.check_for_and_advance(result, "expected '['.", "LSQUARE", None, "list_expr")
        if result.error is not None:
            return result

        cur_tok = self.current_token
        while cur_tok is not None and self.current_token.type == TT["NEWLINE"]:
            result.register_advancement()
            cur_tok = self.advance()

        if self.current_token.type == TT["RSQUARE"]:  # ] : we close the list
            pos_end = self.current_token.pos_end.copy()
            result.register_advancement()
            self.advance()
            return result.success(ListNode(
                element_nodes, pos_start, pos_end
            ))

        # there are elements
        # MUL? expr (COMMA NEWLINE?* MUL? expr)?*
        if self.current_token.type == TT["MUL"]:  # MUL?
            mul = True
            # we advance
            result.register_advancement()
            self.advance()
        # expr
        # we register an expr then check for an error
        expr_ = result.register(self.expr())
        if result.error is not None:
            return result
        assert expr_ is not None
        assert not isinstance(expr_, list)
        expr_and_mul = (expr_, mul)

        element_nodes.append(expr_and_mul)

        while self.current_token.type == TT["COMMA"]:  # (COMMA NEWLINE?* MUL? expr)?*
            mul = False
            # we advance
            result.register_advancement()
            self.advance()

            cur_tok = self.current_token
            while cur_tok is not None and self.current_token.type == TT["NEWLINE"]:
                result.register_advancement()
                cur_tok = self.advance()

            if self.current_token.type == TT["MUL"]:  # MUL?
                mul = True
                # we advance
                result.register_advancement()
                self.advance()
            # expr
            # we register an expr then check for an error
            expr_ = result.register(self.expr())
            if result.error is not None:
                return result
            assert expr_ is not None
            assert not isinstance(expr_, list)
            expr_and_mul = (expr_, mul)

            element_nodes.append(expr_and_mul)

        cur_tok = self.current_token
        while cur_tok is not None and self.current_token.type == TT["NEWLINE"]:
            result.register_advancement()
            cur_tok = self.advance()

        pos_end = self.current_token.pos_end.copy()
        result = self.check_for_and_advance(
                result, "'[' was never closed.", "RSQUARE", None, "list_expr", pos_start, first_tok_pos_end
        )
        if result.error is not None:
            return result
        return result.success(ListNode(
            element_nodes, pos_start, pos_end
        ))

    def if_expr(self) -> ParseResult:
        """
        if_expr : KEYWORD:IF expr KEYWORD:THEN
                  ((statement if_expr_b|if_expr_c?)
                  | (NEWLINE statements KEYWORD:END|if_expr_b|if_expr_c))
        """
        result = ParseResult()
        # we register our if expr using a super cool function
        cases, else_case, error = self.if_expr_cases('if')
        if error is not None:
            return result.failure(error)
        assert cases is not None
        return result.success(IfNode(cases, else_case))

    def if_expr_b(self):  # elif
        """
        if_expr_b : KEYWORD:ELIF expr KEYWORD:THEN
                    ((statement if_expr_b|if_expr_c?)
                    | (NEWLINE statements KEYWORD:END|if_expr_b|if_expr_c))
        """
        return self.if_expr_cases("elif")

    def if_expr_c(self) -> tuple[Node | None, None] | tuple[None, Error]:  # else
        """
        if_expr_c : KEYWORD:ELSE
                    (statement
                    | (NEWLINE statements KEYWORD:END))
        """
        result = ParseResult()
        # as we know so far, there is no 'else' structure
        else_case = None
        assert self.current_token is not None

        # now we know there is a 'else' keyword
        if self.current_token.matches(TT["KEYWORD"], 'else'):
            else_tok_pos = (self.current_token.pos_start.copy(), self.current_token.pos_end.copy())
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
                    return None, result.error
                assert statements is not None
                else_case = statements

                # this happen when EOF after 'else'
                result = self.check_for_and_advance(result, "expected 'end' to close this 'else'.", "KEYWORD",
                                                    "end", "if_expr_c", *else_tok_pos, True)
                if result.error is not None:
                    return None, result.error
            else:  # there is no newline: statement
                expr = result.register(self.statement())
                if result.error is not None:
                    return None, result.error
                else_case = expr
        assert not isinstance(else_case, list)

        return else_case, None

    def if_expr_b_or_c(self) -> tuple[list[tuple[Node, Node]] | None, Node | None, Error | None]:
        """Return a elif cases list (condition, body), an else body, and eventually an error."""
        # cases are all the 'elif' cases and else_case is None so far.
        cases, else_case = [], None
        assert self.current_token is not None

        # KEYWORD:ELIF statement
        if self.current_token.matches(TT["KEYWORD"], 'elif'):
            cases, else_case, error = self.if_expr_b()
            if error is not None:
                return None, None, error
        else:  # KEYWORD:ELSE statement
            else_case, error = self.if_expr_c()
            if error is not None:
                return None, None, error

        return cases, else_case, None

    def if_expr_cases(
            self, case_keyword: str
    ) -> tuple[list[tuple[Node, Node]], Node | None, None] | tuple[None, None, Error]:
        """Return a cases list (condition, body), an else body, and eventually an error."""
        result = ParseResult()
        cases: list[tuple[Node, Node]] = []
        else_case = None
        assert self.current_token is not None

        result = self.check_for_and_advance(result, f"expected '{case_keyword}'.", "KEYWORD",
                                            case_keyword, "if_expr_cases")
        if result.error is not None:
            return None, None, result.error

        # condition expr
        condition = result.register(self.expr())
        if result.error is not None:
            return None, None, result.error  # type: ignore
        assert condition is not None

        # then keyword
        result = self.check_for(result, "expected 'then'.", "KEYWORD", "then", "if_expr_cases")
        if result.error is not None:
            return None, None, result.error
        then_tok = self.current_token.copy()

        result.register_advancement()
        self.advance()

        # NEWLINE statements (if_expr_b|if_expr_c?)*? KEYWORD:END
        if self.current_token.type == TT["NEWLINE"]:
            self.then_s.append((then_tok.pos_start, then_tok.pos_end))
            result.register_advancement()
            self.advance()

            # statements that end at any 'elif', 'else' or 'end'
            statements = result.register(self.statements(stop=[
                (TT["KEYWORD"], 'elif'), (TT["KEYWORD"], 'else'), (TT["KEYWORD"], 'end')
            ]))
            if result.error is not None:
                return None, None, result.error  # type: ignore
            assert statements is not None
            assert not isinstance(condition, list)
            assert not isinstance(statements, list)

            cases.append((condition, statements))

            if self.current_token.matches(TT["KEYWORD"], 'end'):
                del self.then_s[-1]
                result.register_advancement()
                self.advance()
            else:
                elif_cases, else_case, error = self.if_expr_b_or_c()  # elif or else
                if error is not None:
                    return None, None, error
                assert elif_cases is not None
                cases.extend(elif_cases)
        else:  # no newline : single line 'if'
            # expr
            expr = result.register(self.statement())
            if result.error is not None:
                return None, None, result.error  # type: ignore
            assert expr is not None
            assert not isinstance(condition, list)
            assert not isinstance(expr, list)
            cases.append((condition, expr))

            # (if_expr_b|if_expr_c?)*?
            elif_cases, else_case, error = self.if_expr_b_or_c()  # elif or else
            if error is not None:
                return None, None, error
            assert elif_cases is not None
            cases.extend(elif_cases)
        return cases, else_case, None

    def for_expr(self) -> ParseResult:
        """
        for_expr      : KEYWORD:FOR (COLON IDENTIFIER)?
                        IDENTIFIER EQ expr KEYWORD:TO expr (KEYWORD:STEP expr)? KEYWORD:THEN
                        statement | (NEWLINE statements KEYWORD:END)
                      : KEYWORD:FOR (COLON IDENTIFIER)?
                        IDENTIFIER KEYWORD:IN expr KEYWORD:THEN
                        statement | (NEWLINE statements KEYWORD:END)
        """
        result = ParseResult()
        assert self.current_token is not None
        result = self.check_for(result, "expected 'for'.", "KEYWORD", "for", "for_expr")
        if result.error is not None:
            return result
        for_tok = self.current_token.copy()

        result.register_advancement()
        self.advance()

        label = None
        if self.current_token.type == TT["COLON"]:
            result = self.advance_and_check_for(
                result, "expected label identifier after ':'.", "IDENTIFIER",
                origin_file="for_expr"
            )
            if result.error is not None:
                return result
            label = self.current_token.value
            assert isinstance(label, str)
            result.register_advancement()
            self.advance()

        if self.current_token.type != TT["IDENTIFIER"]:
            if self.current_token.type == TT["KEYWORD"]:
                error_msg = "using keyword as identifier is illegal."
            elif self.current_token.type in TOKENS_NOT_TO_QUOTE:
                error_msg = f"expected identifier, but got {self.current_token.type}."
            else:
                error_msg = f"expected identifier, but got '{self.current_token.type}'."
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end, error_msg,
                "src.parser.parser.Parser.for_expr"
            ))

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
            assert iterable_ is not None

            # KEYWORD:THEN
            result = self.check_for(result, "expected 'then'.", "KEYWORD", "then", "for_expr")
            if result.error is not None:
                return result
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

                result = self.check_for_and_advance(
                    result, "this 'for' was never closed (by 'end').",
                    "KEYWORD", "end", "for_expr", for_tok.pos_start, for_tok.pos_end,
                    del_a_then=True
                )
            else:
                # statement
                body = result.register(self.statement())

            if result.error is not None:
                return result
            assert body is not None
            assert not isinstance(body, list)
            assert not isinstance(iterable_, list)

            return result.success(ForNodeList(var_name, body, iterable_, label))

        # EQ expr KEYWORD:TO expr (KEYWORD:STEP expr)? KEYWORD:THEN statement | (NEWLINE statements KEYWORD:END)
        result = self.check_for_and_advance(result, "expected 'in' or '=', but got %toktype%.", "EQ",
                                            None, "for_expr")
        if result.error is not None:
            return result
        # expr
        start_value = result.register(self.expr())
        if result.error is not None:
            return result
        assert start_value is not None

        # KEYWORD:TO
        result = self.check_for_and_advance(result, "expected 'to'.", "KEYWORD",
                                            "to", "for_expr")
        if result.error is not None:
            return result

        # expr
        end_value = result.register(self.expr())
        if result.error is not None:
            return result
        assert end_value is not None

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
        result = self.check_for(result, "expected 'then'.", "KEYWORD", "then", "for_expr")
        if result.error is not None:
            return result
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
            result = self.check_for_and_advance(
                result, "this 'for' was never closed (by 'end').", "KEYWORD", "end",
                "for_expr", for_tok.pos_start, for_tok.pos_end, del_a_then=True
            )
        else:
            # statement
            body = result.register(self.statement())

        if result.error is not None:
            return result
        assert body is not None
        assert not isinstance(start_value, list)
        assert not isinstance(end_value, list)
        assert not isinstance(step_value, list)
        assert not isinstance(body, list)

        return result.success(ForNode(var_name, start_value, end_value, step_value, body, label))

    def while_expr(self) -> ParseResult:
        """
        while_expr    : KEYWORD:WHILE (COLON IDENTIFIER)?
                        expr KEYWORD:THEN
                        statement | (NEWLINE statements KEYWORD:END)
        """
        result = ParseResult()
        assert self.current_token is not None

        # KEYWORD:WHILE expr KEYWORD:THEN statement | (NEWLINE statements KEYWORD:END)
        result = self.check_for_and_advance(result, "expected 'while'.", "KEYWORD", "while", "while_expr")
        if result.error is not None:
            return result

        label = None
        if self.current_token.type == TT["COLON"]:
            result = self.advance_and_check_for(
                result, "expected label identifier after ':'.", "IDENTIFIER",
                origin_file="while_expr"
            )
            if result.error is not None:
                return result
            label = self.current_token.value
            assert isinstance(label, str)
            result.register_advancement()
            self.advance()

        # expr
        condition = result.register(self.expr())
        if result.error is not None:
            return result
        assert condition is not None

        # KEYWORD:THEN
        result = self.check_for(result, "expected 'then'.", "KEYWORD", "then", "while_expr")
        if result.error is not None:
            return result
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
            result = self.check_for_and_advance(
                result, "expected 'end'.", "KEYWORD", "end", "while_expr", del_a_then=True
            )
        else:
            # statement
            body = result.register(self.statement())

        if result.error is not None:
            return result
        assert body is not None
        assert not isinstance(body, list)
        assert not isinstance(condition, list)

        return result.success(WhileNode(condition, body, label))

    def do_expr(self) -> ParseResult:
        """
        do_expr: KEYWORD:DO (COLON IDENTIFIER)?
                 (statement | (NEWLINE statements)) KEYWORD:THEN KEYWORD:LOOP KEYWORD:WHILE expr
        """
        result = ParseResult()
        assert self.current_token is not None

        result = self.check_for_and_advance(result, "expected 'do'.", "KEYWORD", "do", "do_expr")
        if result.error is not None:
            return result

        label = None
        if self.current_token.type == TT["COLON"]:
            result = self.advance_and_check_for(
                result, "expected label identifier after ':'.", "IDENTIFIER",
                origin_file="do_expr"
            )
            if result.error is not None:
                return result
            label = self.current_token.value
            assert isinstance(label, str)
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
            assert body is not None
        else:
            # statement
            body = result.register(self.statement())
            if result.error is not None:
                return result
            assert body is not None

        # KEYWORD:THEN KEYWORD:LOOP KEYWORD:WHILE
        for expected_token in ["then", "loop", "while"]:
            result = self.check_for_and_advance(result, f"expected '{expected_token}'.", "KEYWORD", expected_token, "do_expr")

        # expr
        condition = result.register(self.expr())
        if result.error is not None:
            return result
        assert condition is not None
        assert not isinstance(body, list)
        assert not isinstance(condition, list)

        return result.success(DoWhileNode(body, condition, label))

    def loop_expr(self) -> ParseResult:
        """
            loop_expr     : KEYWORD:LOOP (COLON IDENTIFIER)?
                            statement | (NEWLINE statements KEYWORD:END)
        """
        result = ParseResult()
        assert self.current_token is not None

        loop_tok = self.current_token
        result = self.check_for_and_advance(result, "expected 'loop'.", "KEYWORD", "loop", "loop_expr")
        if result.error is not None:
            return result

        label = None
        if self.current_token.type == TT["COLON"]:
            result = self.advance_and_check_for(
                result, "expected label identifier after ':'.", "IDENTIFIER",
                origin_file="loop_expr"
            )
            if result.error is not None:
                return result
            label = self.current_token.value
            assert isinstance(label, str)
            result.register_advancement()
            self.advance()

        # NEWLINE statements KEYWORD:END
        if self.current_token.type == TT["NEWLINE"]:
            self.then_s.append((loop_tok.pos_start, loop_tok.pos_end))
            result.register_advancement()
            self.advance()

            # statements
            body = result.register(self.statements(stop=[(TT["KEYWORD"], 'end')]))
            if result.error is not None:
                return result

            # KEYWORD:END
            result = self.check_for_and_advance(
                result, "expected 'end'.", "KEYWORD", "end", "loop_expr", del_a_then=True
            )
        else:
            # statement
            body = result.register(self.statement())

        if result.error is not None:
            return result
        assert body is not None
        assert not isinstance(body, list)

        return result.success(LoopNode(loop_tok.pos_start, body, label))

    def func_def(self) -> ParseResult:
        """
            func_def      : KEYWORD:DEF IDENTIFIER? func_def_args optional_func_def_args?
                            (ARROW expr)|(NEWLINE statements KEYWORD:END)
        """
        result = ParseResult()
        assert self.current_token is not None

        def_tok = self.current_token.copy()
        result = self.check_for_and_advance(result, "expected 'def'.", "KEYWORD", None, "func_def")

        # IDENTIFIER?
        if self.current_token.type == TT["IDENTIFIER"]:
            var_name_token = self.current_token
            result.register_advancement()
            self.advance()

            errmsg = "expected '('."
        else:
            var_name_token = None
            errmsg = "expeted identifier or '('."

        # LPAREN
        result = self.check_for_and_advance(result, errmsg, "LPAREN", None, "func_def")

        cur_tok = self.current_token
        while cur_tok is not None and cur_tok.type == TT["NEWLINE"]:
            result.register_advancement()
            cur_tok = self.advance()

        param_names_tokens: list[Token] = []

        # (IDENTIFIER (COMMA NEWLINE?* IDENTIFIER)*)?
        errmsg = "expected identifier or ')'."
        if self.current_token.type == TT["IDENTIFIER"]:
            errmsg = "expected ',' or ')'."
            param_names_tokens.append(self.current_token)
            result.register_advancement()
            self.advance()

            # (COMMA NEWLINE?* IDENTIFIER)*?
            while self.current_token.type == TT["COMMA"]:
                result.register_advancement()
                self.advance()

                cur_tok = self.current_token
                while cur_tok is not None and cur_tok.type == TT["NEWLINE"]:
                    result.register_advancement()
                    cur_tok = self.advance()

                # IDENTIFIER
                if self.current_token.type != TT["IDENTIFIER"]:
                    if self.current_token.type == TT["KEYWORD"]:
                        error_msg = "expected identifier after comma. NB: usage of keyword as identifier is illegal."
                    elif self.current_token.type in TOKENS_NOT_TO_QUOTE:
                        error_msg = f"expected identifier after comma, but got {self.current_token.type}."
                    else:
                        error_msg = f"expected identifier after comma, but got '{self.current_token.type}'."
                    return result.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end, error_msg,
                        "src.parser.parser.Parser.func_def"
                    ))

                param_names_tokens.append(self.current_token)
                result.register_advancement()
                self.advance()

        cur_tok = self.current_token
        while cur_tok is not None and cur_tok.type == TT["NEWLINE"]:
            result.register_advancement()
            cur_tok = self.advance()

        result = self.check_for_and_advance(result, errmsg, "RPAREN", None, "func_def")
        if result.error is not None:
            return result

        optional_params: list[tuple[Token, Node]] = []
        # optional_func_def_args?
        # LPAREN
        if self.current_token.type == TT["LPAREN"]:
            result.register_advancement()
            self.advance()

            cur_tok = self.current_token
            while cur_tok is not None and cur_tok.type == TT["NEWLINE"]:
                result.register_advancement()
                cur_tok = self.advance()

            result = self.check_for(
                result, "expected identifier after '('", "IDENTIFIER", origin_file="func_def"
            )

            identifier = self.current_token
            result = self.advance_check_for_and_advance(
                result, "expected '=' after identifier", "EQ", origin_file="func_def"
            )
            if result.error is not None:
                return result
            node = result.register(self.expr())
            if result.error is not None:
                return result
            assert node is not None
            assert not isinstance(node, list)
            optional_params.append((identifier, node))

            # (COMMA NEWLINE?* IDENTIFIER EQ expr)*?
            while self.current_token.type == TT["COMMA"]:
                result.register_advancement()
                self.advance()

                cur_tok = self.current_token
                while cur_tok is not None and cur_tok.type == TT["NEWLINE"]:
                    result.register_advancement()
                    cur_tok = self.advance()

                # IDENTIFIER
                if self.current_token.type != TT["IDENTIFIER"]:
                    if self.current_token.type == TT["KEYWORD"]:
                        error_msg = "expected identifier after comma. NB: usage of keyword as identifier is illegal."
                    elif self.current_token.type in TOKENS_NOT_TO_QUOTE:
                        error_msg = f"expected identifier after comma, but got {self.current_token.type}."
                    else:
                        error_msg = f"expected identifier after comma, but got '{self.current_token.type}'."
                    return result.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end, error_msg,
                        "src.parser.parser.Parser.func_def"
                    ))

                identifier = self.current_token
                result = self.advance_check_for_and_advance(
                    result, "expected '=' after identifier", "EQ", origin_file="func_def"
                )
                if result.error is not None:
                    return result
                node = result.register(self.expr())
                if result.error is not None:
                    return result
                assert node is not None
                assert not isinstance(node, list)
                optional_params.append((identifier, node))

            cur_tok = self.current_token
            while cur_tok is not None and cur_tok.type == TT["NEWLINE"]:
                result.register_advancement()
                cur_tok = self.advance()

            result = self.check_for_and_advance(
                result, "expected ',' or ')'.", "RPAREN", None, "func_def"
            )
            if result.error is not None:
                return result

        # ARROW expr
        if self.current_token.type == TT["ARROW"]:
            result.register_advancement()
            self.advance()

            # expr
            body = result.register(self.expr())
            if result.error is not None:
                return result
            assert body is not None
            assert not isinstance(body, list)

            return result.success(FuncDefNode(
                var_name_token,
                param_names_tokens,
                body,
                should_auto_return=True,
                optional_params=optional_params
            ))

        result = self.check_for_and_advance(result, "expected '->' or new line.", "NEWLINE", None, "func_def")

        self.then_s.append((def_tok.pos_start, def_tok.pos_end))

        # statements
        body = result.register(self.statements(stop=[(TT["KEYWORD"], 'end')]))
        if result.error is not None:
            return result
        assert body is not None

        # KEYWORD:END
        self.check_for_and_advance(result, "expected 'end'.", "KEYWORD", "end",
                                   "func_def", del_a_then=True)
        if result.error is not None:
            return result
        assert not isinstance(body, list)

        return result.success(FuncDefNode(
            var_name_token,
            param_names_tokens,
            body,
            False,
            optional_params
        ))

    def class_def(self) -> ParseResult:
        """
            KEYWORD:CLASS IDENTIFIER?
            (LPAREN NEWLINE?* IDENTIFIER? NEWLINE?* RPAREN)?
            (ARROW expr)
          | (NEWLINE statements KEYWORD:END)
        """
        result = ParseResult()
        assert self.current_token is not None

        class_tok = self.current_token.copy()
        pos_start = class_tok.pos_start.copy()
        result = self.check_for_and_advance(result, "expected 'class'", "KEYWORD", "class", "class_def")

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

            cur_tok = self.current_token
            while cur_tok is not None and self.current_token.type == TT["NEWLINE"]:
                result.register_advancement()
                cur_tok = self.advance()

            # IDENTIFIER?
            if self.current_token.type == TT["IDENTIFIER"]:
                parent_var_name_tok = self.current_token
                result.register_advancement()
                self.advance()
            else:
                parent_var_name_tok = None

            cur_tok = self.current_token
            while cur_tok is not None and self.current_token.type == TT["NEWLINE"]:
                result.register_advancement()
                cur_tok = self.advance()

            # RPAREN
            result = self.check_for_and_advance(result, "expected ')'.", "RPAREN", None, "class_def")
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
            assert body is not None
            assert not isinstance(body, list)

            return result.success(ClassNode(
                var_name_token,
                parent_var_name_tok,
                body,
                True,
                pos_start
            ))

        # NEWLINE statements KEYWORD:END
        result = self.check_for_and_advance(result, "expected '->' or new line.", "NEWLINE", None, "class_def")

        self.then_s.append((class_tok.pos_start, class_tok.pos_end))

        # statements
        body = result.register(self.statements(stop=[(TT["KEYWORD"], 'end')]))
        if result.error is not None:
            return result
        assert body is not None

        # KEYWORD:END
        result = self.check_for_and_advance(result, "expected 'end'.", "KEYWORD", "end", "class_def", del_a_then=True)
        assert not isinstance(body, list)

        return result.success(ClassNode(
            var_name_token,
            parent_var_name_tok,
            body,
            False,
            pos_start
        ))

    def bin_op(
            self,
            func_a: Callable[..., ParseResult] | list[Node],
            ops: Iterable[str | tuple[str, Any]],
            func_b: Callable[..., ParseResult] | list[Node] | None = None,
            left_has_priority: bool = True
    ) -> ParseResult:
        """Binary operator such as 1+1 or 3==2
        Can return BinOpCompNode, BinOpNode, any node, or list."""
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
            assert left is not None
        else:
            left = func_a  # func_a is a list: this is the left operand
        assert func_b is not None

        assert self.current_token is not None

        if left_has_priority:
            while self.current_token.type in ops or (self.current_token.type, self.current_token.value) in ops:
                op_token = self.current_token  # operator token
                result.register_advancement()  # we advance
                self.advance()
                if not isinstance(func_b, list):  # we check if func_b is a list or a function
                    right: Node | None | list[Node] = result.register(func_b())
                    if result.error is not None:
                        return result
                    assert right is not None
                else:
                    right: Node | None | list[Node] = func_b  # it is a list
                left = BinOpNode(left, op_token, right)  # we update our left, and we loop to the next operand
            return result.success(left)
        else:
            nodes_and_tokens_list: list[Node | Token | list[Node]] = [left]
            while self.current_token.type in ops or (self.current_token.type, self.current_token.value) in ops:
                # check comments above
                op_token = self.current_token
                result.register_advancement()
                self.advance()
                if not isinstance(func_b, list):
                    right: Node | None | list[Node] = result.register(func_b())
                    if result.error is not None:
                        return result
                    assert right is not None
                else:
                    right: Node | None | list[Node] = func_b
                # we add our operator and operand to our list
                nodes_and_tokens_list.append(op_token)
                nodes_and_tokens_list.append(right)
            # this is a messy bugfix tbh
            if len(nodes_and_tokens_list) == 1 and isinstance(nodes_and_tokens_list[0], Node):
                return result.success(nodes_and_tokens_list[0])
            if len(nodes_and_tokens_list) == 1 and isinstance(nodes_and_tokens_list[0], list):
                if len(nodes_and_tokens_list[0]) == 1:
                    return result.success(nodes_and_tokens_list[0][0])
            return result.success(BinOpCompNode(nodes_and_tokens_list))
