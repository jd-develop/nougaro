#!/usr/bin/env python3
# coding:utf-8
# this file is part of NOUGARO language, created by Jean Dubois (github.com/jd-develop)
# Public Domain
# Actually running with Python 3.9.7

# IMPORTS
# nougaro modules imports
from token_constants import *
from strings_with_arrows import *
# build in python imports
import string


# ##########
# COLORS
# ##########
def print_in_red(txt): print("\033[91m {}\033[00m".format(txt))


# ##########
# CONSTANTS
# ##########
DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS


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

    def advance(self, current_char=None):
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


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start is not None:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        if pos_end is not None:
            self.pos_end = pos_end

    def __repr__(self) -> str:
        if self.value:
            return f'{self.type}:{self.value}'
        elif self.value == 0:
            return f'{self.type}:{self.value}'
        return f'{self.type}'

    def matches(self, type_, value):
        return self.type == type_ and self.value == value


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
                number, error = self.make_number()
                if error is None:
                    tokens.append(number)
                else:
                    return [], error
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(TT_POW, pos_start=self.pos))
                self.advance()
            elif self.current_char == '=':
                tokens.append(Token(TT_EQ, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            else:
                # illegal char
                pos_start = self.pos.copy()
                char = self.current_char
                return [], IllegalCharError(pos_start, self.pos, char + " is an illegal character. It may happens when "
                                                                        "an non-ASCII letter is used in a identifier.")

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

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
                    pos_start = self.pos.copy()
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


# ##########
# RUNTIME RESULT
# ##########
class RTResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, result):
        if result.error is not None:
            self.error = result.error
        return result.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self


# ##########
# VALUES
# ##########
class Number:
    def __init__(self, value):
        self.value = value
        self.pos_start = None
        self.pos_end = None
        self.context = None
        self.set_pos()
        self.set_context()

    def __repr__(self):
        return str(self.value)

    def set_context(self, context=None):
        self.context = context
        return self

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def added_to(self, other):  # ADDITION
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None

    def subbed_by(self, other):  # SUBTRACTION
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None

    def multiplied_by(self, other):  # MULTIPLICATION
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None

    def dived_by(self, other):  # DIVISION
        if isinstance(other, Number):
            if other.value == 0:
                return None, RunTimeError(
                    other.pos_start, other.pos_end, 'division by zero is not possible.', self.context
                )
            return Number(self.value / other.value).set_context(self.context), None

    def powered_by(self, other):  # POWER
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy


# ##########
# NODES
# ##########
class NumberNode:
    def __init__(self, token):
        self.token = token
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'{self.token}'


class VarAccessNode:
    def __init__(self, var_name_token):
        self.var_name_token = var_name_token

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.var_name_token.pos_end


class VarAssignNode:
    def __init__(self, var_name_token, value_node):
        self.var_name_token = var_name_token
        self.value_node = value_node

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.value_node.pos_end


class BinOpNode:
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_token}, {self.right_node})'


class UnaryOpNode:
    def __init__(self, op_token, node):
        self.op_token = op_token
        self.node = node

        self.pos_start = self.op_token.pos_start
        self.pos_end = self.node.pos_end

    def __repr__(self):
        return f'({self.op_token}, {self.node})'


# ##########
# PARSE RESULT
# ##########
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0

    def register_advancement(self):
        self.advance_count += 1

    def register(self, result):
        self.advance_count += result.advance_count
        if result.error:
            self.error = result.error
        return result.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if self.error is None or self.advance_count == 0:
            self.error = error
        return self


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
        self.current_token = None
        self.advance()

    def parse(self):
        result = self.expr()
        if result.error is None and self.current_token.type != TT_EOF:
            return result.failure(
                InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                   "expected '+', '-', '*' or '/'.")
            )
        return result

    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token

    def atom(self):
        result = ParseResult()
        token = self.current_token

        if token.type in (TT_INT, TT_FLOAT):
            result.register_advancement()
            self.advance()
            return result.success(NumberNode(token))
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

        return result.failure(
            InvalidSyntaxError(token.pos_start, token.pos_end, "expected int, float, identifier, '+', '-' or '('.")
        )

    def power(self):
        return self.bin_op(self.atom, (TT_POW, ), self.factor)

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

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        result = ParseResult()
        if self.current_token.matches(TT_KEYWORD, 'VAR'):
            result.register_advancement()
            self.advance()

            if self.current_token.type != TT_IDENTIFIER:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end, f"expected identifier, "
                                                                              f"but got {self.current_token.type}."
                ))

            var_name = self.current_token
            result.register_advancement()
            self.advance()

            if self.current_token.type != TT_EQ:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end, f"expected '=', "
                                                                              f"but got {self.current_token.type}."
                ))

            result.register_advancement()
            self.advance()
            expr = result.register(self.expr())
            if result.error is not None:
                return result
            return result.success(VarAssignNode(var_name, expr))

        node = result.register(self.bin_op(self.term, (TT_PLUS, TT_MINUS)))

        if result.error is not None:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected 'VAR', int, float, identifier, '+', '-' or '('"
            ))

        return result.success(node)

    def bin_op(self, func_a, ops, func_b=None):
        if func_b is None:
            func_b = func_a
        result = ParseResult()
        left = result.register(func_a())
        if result.error is not None:
            return result

        while self.current_token.type in ops:
            op_token = self.current_token
            result.register_advancement()
            self.advance()
            right = result.register(func_b())
            if result.error:
                return result
            left = BinOpNode(left, op_token, right)
        return result.success(left)


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
        string_line = string_with_arrows(self.pos_start.file_txt, self.pos_start, self.pos_end)
        while string_line[0] in " ":
            # delete spaces at the start of the str.
            # Add chars after the space in the string after the "while string_line[0] in" to delete them.
            string_line = string_line[1:]
        result = f"In file {self.pos_start.file_name}, line {self.pos_start.line_number + 1} : " + '\n \t' + \
            string_line + '\n ' + \
            f'{self.error_name} : {self.details}'
        return result


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "IllegalCharError", details)


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "InvalidSyntaxError", details)


class ExpectedCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "ExpectedCharacterError", details)


class RunTimeError(Error):
    def __init__(self, pos_start, pos_end, details, context, rt_error=True, error_name=""):

        super().__init__(pos_start, pos_end, "RunTimeError" if rt_error else error_name, details)
        self.context = context

    def as_string(self):
        string_line = string_with_arrows(self.pos_start.file_txt, self.pos_start, self.pos_end)
        while string_line[0] in " ":
            # delete spaces at the start of the str.
            # Add chars after the space in the string after the "while string_line[0] in" to delete them.
            string_line = string_line[1:]
        result = self.generate_traceback()
        result += '\n \t' + string_line + '\n ' + f'{self.error_name} : {self.details}'
        return result

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx is not None:
            result = f' In file {pos.file_name}, line {pos.line_number + 1}, in {ctx.display_name} :' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return "Traceback (more recent call last) :\n" + result


class NotDefinedError(RunTimeError):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="NotDefinedError")
        self.context = context


# ##########
# CONTEXT
# ##########
class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None


# ##########
# SYMBOL TABLE
# ##########
class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None

    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent is not None:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]


# ##########
# INTERPRETER
# ##########
class Interpreter:
    # this class have not __init__ method
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    @staticmethod
    def no_visit_method(node, context):
        print(context)
        print(f"NOUGARO INTERNAL ERROR : No visit_{type(node).__name__} method defined.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/redirect1.html")
        raise Exception(f'No visit_{type(node).__name__} method defined.')

    @staticmethod
    def visit_NumberNode(node, context):
        return RTResult().success(Number(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error is not None:
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.error is not None:
            return res

        if node.op_token.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_token.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_token.type == TT_MUL:
            result, error = left.multiplied_by(right)
        elif node.op_token.type == TT_DIV:
            result, error = left.dived_by(right)
        elif node.op_token.type == TT_POW:
            result, error = left.powered_by(right)
        else:
            raise Exception("result is not defined after executing nougaro.Interpreter.visit_BinOpNode (python file) "
                            "because of an invalid token.\n"
                            "Please report this bug at https://jd-develop.github.io/nougaro/redirect1.html")

        if error is not None:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        result = RTResult()
        number = result.register(self.visit(node.node, context))
        if result.error is not None:
            return result

        error = None

        if node.op_token.type == TT_MINUS:
            number, error = number.multiplied_by(Number(-1))

        if error is not None:
            return result.failure(error)
        else:
            return result.success(number.set_pos(node.pos_start, node.pos_end))

    @staticmethod
    def visit_VarAccessNode(node, context):
        result = RTResult()
        var_name = node.var_name_token.value
        value = context.symbol_table.get(var_name)

        if value is None:
            return result.failure(
                NotDefinedError(
                    node.pos_start, node.pos_end, f'{var_name} is not defined', context
                )
            )

        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return result.success(value)

    def visit_VarAssignNode(self, node, context):
        result = RTResult()
        var_name = node.var_name_token.value
        value = result.register(self.visit(node.value_node, context))
        if result.error is not None:
            return result

        context.symbol_table.set(var_name, value)
        return result.success(value)


global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))


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
    if ast.error is not None:
        return None, ast.error

    # run program
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error
