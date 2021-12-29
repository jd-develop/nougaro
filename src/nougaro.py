#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain
# Actually running with Python 3.9, works with Python 3.10

# IMPORTS
# nougaro modules imports
from src.token_constants import *
from src.strings_with_arrows import *
from src.constants import *
from src.position import *
from src.tokens import *
# built-in python imports
import os
import math


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
            elif self.current_char == '"' or self.current_char == "'":
                tokens.append(self.make_string(self.current_char))
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(self.make_minus_or_arrow())
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(TT_POW, pos_start=self.pos))
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
            elif self.current_char == '|':
                tokens.append(Token(TT_ABS, pos_start=self.pos))
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
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
                self.advance()
            else:
                # illegal char
                pos_start = self.pos.copy()
                char = self.current_char
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "' is an illegal character.")

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        # print(tokens)
        return tokens, None

    def make_string(self, quote='"'):
        string_ = ''
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()

        escape_characters = {
            'n': '\n',
            't': '\t'
        }

        while self.current_char is not None and (self.current_char != quote or escape_character):
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
        return Token(TT_STRING, string_, pos_start, self.pos)

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

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None

        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "expected : '!=' but got : '!'")

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

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)


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
# CONTEXT
# ##########
class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table: SymbolTable = None

    def __repr__(self) -> str:
        repr_str = f'symbol_table: (\n' \
                   f'{self.symbol_table}' \
                   f')\n' \
                   f'parent: (\n' \
                   f'   {self.parent}\n' \
                   f')\n' \
                   f'parent_entry_pos: {self.parent_entry_pos}\n' \
                   f'display_name: {self.display_name}\n' \
                   f'NB: this is __repr__ from nougaro.Context (internal)'
        return repr_str


# ##########
# SYMBOL TABLE
# ##########
class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def __repr__(self) -> str:
        return f'   symbols: {self.symbols}\n' \
               f'   parent: (\n' \
               f'       {self.parent}\n' \
               f'   )'

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
# VALUES
# ##########
class Value:
    def __init__(self):
        self.pos_start = self.pos_end = self.context = None
        self.set_pos()
        self.set_context()
        self.type_ = "BaseValue"

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context: Context = None):
        self.context = context
        return self

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multiplied_by(self, other):
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        return None, self.illegal_operation(other)

    def powered_by(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_ne(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gte(self, other):
        return None, self.illegal_operation(other)

    def and_(self, other):
        return None, self.illegal_operation(other)

    def or_(self, other):
        return None, self.illegal_operation(other)

    def not_(self):
        return None, self.illegal_operation()

    def excl_or(self, other):
        """ Exclusive or """
        return None, self.illegal_operation(other)

    def execute(self, args):
        return RTResult().failure(self.illegal_operation())

    def abs_(self):
        return RTResult().failure(self.illegal_operation())

    def to_str_(self):
        return None, RTResult().failure(self.illegal_operation())

    def to_int_(self):
        return None, RTResult().failure(self.illegal_operation())

    def to_float_(self):
        return None, RTResult().failure(self.illegal_operation())

    def to_list_(self):
        return None, RTResult().failure(self.illegal_operation())

    def copy(self):
        print(self.context)
        print('NOUGARO INTERNAL ERROR : No copy method defined in Value.copy().\n'
              'Please report this bug at https://jd-develop.github.io/nougaro/redirect1.html with the information below'
              )
        raise Exception('No copy method defined in Value.copy().')

    @staticmethod
    def is_true():
        return False

    def illegal_operation(self, other=None):
        if other is None:
            return RunTimeError(
                self.pos_start, self.pos_end, f'illegal operation with {self.type_}.', self.context
            )
        return RunTimeError(
            self.pos_start, other.pos_end, f'illegal operation between {self.type_} and {other.type_}.', self.context
        )


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.type_ = "str"

    def __repr__(self):
        return f'"{self.value}"'

    def to_str(self):
        return self.value

    def added_to(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def multiplied_by(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def is_true(self):
        return len(self.value) > 0

    def to_str_(self):
        return self, None

    def to_int_(self):
        try:
            return Number(int(float(self.value))).set_context(self.context), None
        except ValueError:
            return None, RTResult().failure(RunTimeError(self.pos_start, self.pos_end,
                                                         f"str {self.value} can not be converted to int.",
                                                         self.context))

    def to_float_(self):
        try:
            return Number(float(self.value)).set_context(self.context), None
        except ValueError:
            return None, RTResult().failure(RunTimeError(self.pos_start, self.pos_end,
                                                         f"str {self.value} can not be converted to int.",
                                                         self.context))

    def to_list_(self):
        list_ = []
        for element in list(self.value):
            list_.append(String(element).set_context(self.context))
        return List(list_).set_context(self.context), None

    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy


class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        if isinstance(self.value, int):
            self.type_ = 'int'
        elif isinstance(self.value, float):
            self.type_ = 'float'

    def __repr__(self):
        return str(self.value)

    def added_to(self, other):  # ADDITION
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def subbed_by(self, other):  # SUBTRACTION
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def multiplied_by(self, other):  # MULTIPLICATION
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def dived_by(self, other):  # DIVISION
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTArithmeticError(
                    other.pos_start, other.pos_end, 'division by zero is not possible.', self.context
                )
            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def powered_by(self, other):  # POWER
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def and_(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def or_(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def excl_or(self, other):
        """ Exclusive or """
        if isinstance(other, Number):
            return Number(int(self.value ^ other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def not_(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def is_true(self):
        return self.value != 0

    def abs_(self):
        return Number(abs(self.value))

    def to_str_(self):
        return String(str(self.value)).set_context(self.context), None

    def to_int_(self):
        return Number(int(self.value)).set_context(self.context), None

    def to_float_(self):
        return Number(float(self.value)).set_context(self.context), None

    def to_list_(self):
        list_ = []
        for element in self.to_str_()[0].to_list_()[0]:
            list_.append(element.to_int_()[0])
        return List(list_).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy


Number.NULL = Number(0)
Number.FALSE = Number(0)
Number.TRUE = Number(1)
Number.MATH_PI = Number(math.pi)
Number.MATH_E = Number(math.e)
Number.MATH_SQRT_PI = Number(math.sqrt(math.pi))


class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements
        self.type_ = 'list'

    def __repr__(self):
        return f'[{", ".join([str(x) for x in self.elements])}]'

    def __getitem__(self, item):
        return self.elements.__getitem__(item)

    def added_to(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None

    def subbed_by(self, other):
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except Exception:
                return None, RTIndexError(
                    other.pos_start, other.pos_end,
                    f'pop index {other.value} out of range.',
                    self.context
                )
        else:
            return None, self.illegal_operation(other)

    def multiplied_by(self, other):
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, self.illegal_operation(other)

    def dived_by(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except Exception:
                return None, RTIndexError(
                    other.pos_start, other.pos_end,
                    f'list index {other.value} out of range.',
                    self.context
                )
        else:
            return None, self.illegal_operation(other)

    def to_str_(self):
        return String(str(self.elements)).set_context(self.context), None

    def to_list_(self):
        return self, None

    def copy(self):
        copy = List(self.elements)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy


class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name if name is not None else '<function>'
        self.type_ = 'BaseFunction'

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        result = RTResult()

        if len(args) > len(arg_names):
            return result.failure(
                RunTimeError(
                    self.pos_start, self.pos_end,
                    f"{len(args) - len(arg_names)} too many args passed into '{self.name}'",
                    self.context
                )
            )

        if len(args) < len(arg_names):
            return result.failure(
                RunTimeError(
                    self.pos_start, self.pos_end,
                    f"{len(arg_names) - len(args)} too few args passed into '{self.name}'",
                    self.context
                )
            )

        return result.success(None)

    @staticmethod
    def populate_args(arg_names, args, exec_context: Context):
        # We need the context for the symbol table :)
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_context)
            exec_context.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_context: Context):
        # We still need the context for the symbol table ;)
        result = RTResult()
        result.register(self.check_args(arg_names, args))
        if result.error is not None:
            return result
        self.populate_args(arg_names, args, exec_context)
        return result.success(None)


class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.type_ = "func"

    def __repr__(self):
        return f'<function {self.name}>'

    def execute(self, args):
        result = RTResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()

        result.register(self.check_and_populate_args(self.arg_names, args, exec_context))
        if result.error is not None:
            return result

        value = result.register(interpreter.visit(self.body_node, exec_context))
        if result.error is not None:
            return result
        return result.success(value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy


class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)
        self.type_ = 'built-in func'

    def __repr__(self):
        return f'<built-in function {self.name}>'

    def execute(self, args):
        result = RTResult()
        exec_context = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        result.register(self.check_and_populate_args(method.arg_names, args, exec_context))
        if result.error is not None:
            return result

        try:
            return_value = result.register(method(exec_context))
        except TypeError:
            try:
                return_value = result.register(method())
            except TypeError:  # it only executes when coding
                return_value = result.register(method(exec_context))
        if result.error is not None:
            return result
        return result.success(return_value)

    def no_visit_method(self, exec_context: Context):
        print(exec_context)
        print(f"NOUGARO INTERNAL ERROR : No execute_{self.name} method defined in nougaro.BuildInFunction.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/redirect1.html with informations above.")
        raise Exception(f'No execute_{self.name} method defined in nougaro.BuildInFunction.')

    # ==================
    # BUILD IN FUNCTIONS
    # ==================

    def execute_print(self, exec_context: Context):
        """Print 'value'"""
        # Params:
        # * value
        try:
            print(exec_context.symbol_table.get('value').to_str())
        except Exception:
            print(str(exec_context.symbol_table.get('value')))
        return RTResult().success(Number.NULL)
    execute_print.arg_names = ["value"]

    def execute_print_ret(self, exec_context: Context):
        """Print 'value' in a returned str"""
        # Params:
        # * value
        return RTResult().success(String(str(exec_context.symbol_table.get('value'))))
    execute_print_ret.arg_names = ["value"]

    def execute_input(self):
        """Basic input (str)"""
        # No params.
        text = input()
        return RTResult().success(String(text))
    execute_input.arg_names = []

    def execute_input_int(self):
        """Basic input (int). Repeat while entered value is not an int."""
        # No params.
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f'{text} must be an integer. Try again :')
        return RTResult().success(Number(number))
    execute_input_int.arg_names = []

    def execute_clear(self):
        """Clear the screen"""
        # No params.
        os.system('cls' if (os.name == "nt" or os.name == "Windows") else 'clear')
        return RTResult().success(Number.NULL)
    execute_clear.arg_names = []

    def execute_is_number(self, exec_context: Context):
        """Check if 'value' is a Number"""
        # Params:
        # * value
        is_number = isinstance(exec_context.symbol_table.get('value'), Number)
        return RTResult().success(Number.TRUE if is_number else Number.FALSE)
    execute_is_number.arg_names = ['value']

    def execute_is_list(self, exec_context: Context):
        """Check if 'value' is a List"""
        # Params:
        # * value
        is_number = isinstance(exec_context.symbol_table.get('value'), List)
        return RTResult().success(Number.TRUE if is_number else Number.FALSE)
    execute_is_list.arg_names = ['value']

    def execute_is_string(self, exec_context: Context):
        """Check if 'value' is a String"""
        # Params:
        # * value
        is_number = isinstance(exec_context.symbol_table.get('value'), String)
        return RTResult().success(Number.TRUE if is_number else Number.FALSE)
    execute_is_string.arg_names = ['value']

    def execute_is_function(self, exec_context: Context):
        """Check if 'value' is a BaseFunction"""
        # Params:
        # * value
        is_number = isinstance(exec_context.symbol_table.get('value'), BaseFunction)
        return RTResult().success(Number.TRUE if is_number else Number.FALSE)
    execute_is_function.arg_names = ['value']

    def execute_append(self, exec_context: Context):
        """Append 'value' to 'list'"""
        # Params:
        # * list
        # * value
        list_ = exec_context.symbol_table.get('list')
        value = exec_context.symbol_table.get('value')

        if not isinstance(list_, List):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'append' must be a list.",
                exec_context
            ))

        list_.elements.append(value)
        return RTResult().success(list_)
    execute_append.arg_names = ['list', 'value']

    def execute_pop(self, exec_context: Context):
        """Remove element at 'index' from 'list'"""
        # Params:
        # * list
        # * index
        list_ = exec_context.symbol_table.get('list')
        index = exec_context.symbol_table.get('index')

        if not isinstance(list_, List):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'pop' must be a list.",
                exec_context
            ))

        if not isinstance(index, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "second argument of built-in function 'pop' must be a number.",
                exec_context
            ))

        try:
            list_.elements.pop(index.value)
        except Exception:
            return RTResult().failure(RTIndexError(
                self.pos_start, self.pos_end,
                f'pop index {index.value} out of range.',
                self.context
            ))
        return RTResult().success(list_)
    execute_pop.arg_names = ['list', 'index']

    def execute_extend(self, exec_context: Context):
        """Extend list 'list1' with the elements of 'list2'"""
        # Params:
        # * list1
        # * list2
        list1 = exec_context.symbol_table.get('list1')
        list2 = exec_context.symbol_table.get('list2')

        if not isinstance(list1, List):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'extend' must be a list.",
                exec_context
            ))

        if not isinstance(list2, List):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "second argument of built-in function 'extend' must be a list.",
                exec_context
            ))

        list1.elements.extend(list2.elements)
        return RTResult().success(list1)
    execute_extend.arg_names = ['list1', 'list2']

    def execute_get(self, exec_context: Context):
        # Params:
        # * list
        # * index
        list_ = exec_context.symbol_table.get('list')
        index_ = exec_context.symbol_table.get('index')

        if not isinstance(list_, List):
            return RTResult().failure(
                RunTimeError(
                    self.pos_start, self.pos_end,
                    "first argument of built-in function 'get' must be a list.",
                    exec_context
                )
            )

        if not isinstance(index_, Number):
            return RTResult().failure(
                RunTimeError(
                    self.pos_start, self.pos_end,
                    "second argument of built-in function 'get' must be an int.",
                    exec_context
                )
            )
        index_ = index_.value

        try:
            return RTResult().success(list_[index_])
        except Exception:
            return RTResult().failure(RTIndexError(
                self.pos_start, self.pos_end,
                f'index {index_} out of range.',
                self.context
            ))
    execute_get.arg_names = ['list', 'index']

    def execute_sqrt(self, exec_context: Context):
        """Calculates square root of 'value'"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'sqrt' must be a number.",
                exec_context
            ))

        if not value.value >= 0:
            return RTResult().failure(RTArithmeticError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'sqrt' must be greater than (or equal to) 0.",
                exec_context
            ))

        sqrt = math.sqrt(value.value)
        return RTResult().success(Number(sqrt))
    execute_sqrt.arg_names = ['value']

    def execute_degrees(self, exec_context: Context):
        """Converts 'value' (radians) to degrees"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'degrees' must be a number (angle in radians).",
                exec_context
            ))
        degrees = math.degrees(value.value)
        return RTResult().success(Number(degrees))
    execute_degrees.arg_names = ['value']

    def execute_radians(self, exec_context: Context):
        """Converts 'value' (degrees) to radians"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'radians' must be a number (angle in degrees).",
                exec_context
            ))
        radians = math.radians(value.value)
        return RTResult().success(Number(radians))
    execute_radians.arg_names = ['value']

    def execute_sin(self, exec_context: Context):
        """Calculates sin('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'sin' must be a number (angle in radians).",
                exec_context
            ))
        sin = math.sin(value.value)
        return RTResult().success(Number(sin))
    execute_sin.arg_names = ['value']

    def execute_cos(self, exec_context: Context):
        """Calculates cos('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'cos' must be a number (angle in radians).",
                exec_context
            ))
        cos = math.cos(value.value)
        return RTResult().success(Number(cos))
    execute_cos.arg_names = ['value']

    def execute_tan(self, exec_context: Context):
        """Calculates tan('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'tan' must be a number (angle in radians).",
                exec_context
            ))
        tan = math.tan(value.value)
        return RTResult().success(Number(tan))
    execute_tan.arg_names = ['value']

    def execute_asin(self, exec_context: Context):
        """Calculates asin('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'asin' must be a number.",
                exec_context
            ))
        try:
            asin = math.asin(value.value)
        except ValueError:
            return RTResult().failure(RTArithmeticError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'asin' must be a number between -1 and 1.",
                exec_context
            ))
        return RTResult().success(Number(asin))
    execute_asin.arg_names = ['value']

    def execute_acos(self, exec_context: Context):
        """Calculates acos('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'acos' must be a number.",
                exec_context
            ))
        try:
            acos = math.acos(value.value)
        except ValueError:
            return RTResult().failure(RTArithmeticError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'acos' must be a number between -1 and 1.",
                exec_context
            ))
        return RTResult().success(Number(acos))
    execute_acos.arg_names = ['value']

    def execute_atan(self, exec_context: Context):
        """Calculates atan('value')"""
        # Params:
        # * value
        value = exec_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                "first argument of built-in function 'atan' must be a number.",
                exec_context
            ))
        atan = math.atan(value.value)
        return RTResult().success(Number(atan))
    execute_atan.arg_names = ['value']

    def execute_exit(self):
        """Stops the Nougaro Interpreter"""
        # No params.
        exit()
    execute_exit.arg_names = []

    def execute_type(self, exec_context: Context):
        """Stops the Nougaro Interpreter"""
        # Params :
        # * value
        value_to_get_type = exec_context.symbol_table.get('value')
        return RTResult().success(String(value_to_get_type.type_))
    execute_type.arg_names = ['value']

    def execute_str(self, exec_context: Context):
        """Python 'str()'"""
        # Params :
        # * value
        result = RTResult()
        value = exec_context.symbol_table.get('value')
        str_value, error = value.to_str_()
        if error is not None:
            return error

        return result.success(str_value)
    execute_str.arg_names = ['value']

    def execute_int(self, exec_context: Context):
        """Python 'int()'"""
        # Params :
        # * value
        result = RTResult()
        value = exec_context.symbol_table.get('value')
        int_value, error = value.to_int_()
        if error is not None:
            return error

        return result.success(int_value)
    execute_int.arg_names = ['value']

    def execute_float(self, exec_context: Context):
        """Python 'float()'"""
        # Params :
        # * value
        result = RTResult()
        value = exec_context.symbol_table.get('value')
        float_value, error = value.to_float_()
        if error is not None:
            return error

        return result.success(float_value)
    execute_float.arg_names = ['value']

    def execute_list(self, exec_context: Context):
        """Python 'list()'"""
        # Params :
        # * value
        result = RTResult()
        value = exec_context.symbol_table.get('value')
        list_value, error = value.to_list_()
        if error is not None:
            return error

        return result.success(list_value)
    execute_list.arg_names = ['value']

    # ==================

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy


BuiltInFunction.PRINT = BuiltInFunction('print')
BuiltInFunction.PRINT_RET = BuiltInFunction('print_ret')
BuiltInFunction.INPUT = BuiltInFunction('input')
BuiltInFunction.INPUT_INT = BuiltInFunction('input_int')
BuiltInFunction.CLEAR = BuiltInFunction('clear')

BuiltInFunction.IS_NUMBER = BuiltInFunction('is_number')
BuiltInFunction.IS_STRING = BuiltInFunction('is_string')
BuiltInFunction.IS_LIST = BuiltInFunction('is_list')
BuiltInFunction.IS_FUNCTION = BuiltInFunction('is_function')
BuiltInFunction.TYPE = BuiltInFunction('type')
BuiltInFunction.INT = BuiltInFunction('int')
BuiltInFunction.FLOAT = BuiltInFunction('float')
BuiltInFunction.STR = BuiltInFunction('str')
BuiltInFunction.LIST = BuiltInFunction('list')

BuiltInFunction.APPEND = BuiltInFunction('append')
BuiltInFunction.POP = BuiltInFunction('pop')
BuiltInFunction.EXTEND = BuiltInFunction('extend')
BuiltInFunction.GET = BuiltInFunction('get')

# Maths
BuiltInFunction.SQRT = BuiltInFunction('sqrt')
BuiltInFunction.RADIANS = BuiltInFunction('radians')
BuiltInFunction.DEGREES = BuiltInFunction('degrees')
BuiltInFunction.SIN = BuiltInFunction('sin')
BuiltInFunction.COS = BuiltInFunction('cos')
BuiltInFunction.TAN = BuiltInFunction('tan')
BuiltInFunction.ASIN = BuiltInFunction('asin')
BuiltInFunction.ACOS = BuiltInFunction('acos')
BuiltInFunction.ATAN = BuiltInFunction('atan')

BuiltInFunction.EXIT = BuiltInFunction('exit')


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


class StringNode:
    def __init__(self, token):
        self.token = token
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'{self.token}'


class ListNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'{str(self.element_nodes)}'


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


class IfNode:
    def __init__(self, cases, else_case):
        # by default else_case is None in Parser.if_expr()
        self.cases = cases
        self.else_case = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1][0]).pos_end


class ForNode:
    def __init__(self, var_name_token, start_value_node, end_value_node, step_value_node, body_node):
        # by default step_value_node is None
        self.var_name_token: Token = var_name_token
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.body_node.pos_end


class WhileNode:
    def __init__(self, condition_node, body_node):
        self.condition_node = condition_node
        self.body_node = body_node

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end


class FuncDefNode:
    def __init__(self, var_name_token: Token, arg_name_tokens: list[Token], body_node):
        self.var_name_token = var_name_token
        self.arg_name_tokens = arg_name_tokens
        self.body_node = body_node

        if self.var_name_token is not None:
            self.pos_start = self.var_name_token.pos_start
        elif len(self.arg_name_tokens) > 0:
            self.pos_start = self.arg_name_tokens[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end


class CallNode:
    def __init__(self, node_to_call, arg_nodes: list):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = self.node_to_call.pos_start

        if len(self.arg_nodes) > 0:
            self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end


class AbsNode:
    def __init__(self, node_to_abs):
        self.node_to_abs = node_to_abs

        self.pos_start = self.node_to_abs.pos_start
        self.pos_end = self.node_to_abs.pos_end


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
        self.current_token: Token = None
        self.advance()

    def parse(self):
        result = self.expr()
        if result.error is None and self.current_token.type != TT_EOF:
            return result.failure(
                InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                   "expected '+', '-', '*', '/', 'and', 'or' or 'xor'.")
            )
        return result

    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token

    # GRAMMARS ATOMS :

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

            if self.current_token.type != TT_EQ:
                if self.current_token.type not in TOKENS_TO_QUOTE:
                    error_msg = f"expected '=', but got {self.current_token.type}."
                else:
                    error_msg = f"expected '=', but got '{self.current_token.type}'."
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
            return result.success(VarAssignNode(var_name, expr))

        node = result.register(self.bin_op(self.comp_expr, (
            (TT_KEYWORD, "and"), (TT_KEYWORD, "or"), (TT_KEYWORD, 'xor'))))

        if result.error is not None:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "expected 'var', int, float, identifier, 'if', 'for', 'while', 'def' '+', '-', '(', '[', '|' or 'not'"
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

        node = result.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))
        if result.error is not None:
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     "expected int, float, identifier, '+', '-', '(', '[' or 'not'."))
        return result.success(node)

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

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
                            "expected ')', 'var', 'if', 'for', 'while', 'def', int, float, identifier, '+', '-', '(', "
                            "'[' or 'not'."
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

            return result.success(CallNode(abs_, arg_nodes))
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
                        "'[' or 'not'"
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
                        "expected ',' or ']'"
                    )
                )

            result.register_advancement()
            self.advance()

        return result.success(ListNode(
            element_nodes, pos_start, self.current_token.pos_end.copy()
        ))

    def if_expr(self):
        result = ParseResult()
        cases = []
        else_case = None

        if not self.current_token.matches(TT_KEYWORD, 'if'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end, "expected 'if'"
            ))

        result.register_advancement()
        self.advance()

        condition = result.register(self.expr())
        if result.error is not None:
            return result

        if not self.current_token.matches(TT_KEYWORD, 'then'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end, "expected 'then'"
            ))

        result.register_advancement()
        self.advance()

        expr = result.register(self.expr())
        if result.error is not None:
            return result
        cases.append((condition, expr))

        while self.current_token.matches(TT_KEYWORD, 'elif'):
            result.register_advancement()
            self.advance()

            condition = result.register(self.expr())
            if result.error is not None:
                return result

            if not self.current_token.matches(TT_KEYWORD, 'then'):
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end, "expected 'then'"
                ))

            result.register_advancement()
            self.advance()

            expr = result.register(self.expr())
            if result.error is not None:
                return result
            cases.append((condition, expr))

        if self.current_token.matches(TT_KEYWORD, 'else'):
            result.register_advancement()
            self.advance()

            else_case = result.register(self.expr())
            if result.error is not None:
                return result

        return result.success(IfNode(cases, else_case))

    def for_expr(self):
        result = ParseResult()
        if not self.current_token.matches(TT_KEYWORD, 'for'):
            return result.error(InvalidSyntaxError, self.current_token.pos_start, self.current_token.pos_end,
                                "expected 'for'")

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

        if self.current_token.type != TT_EQ:
            if self.current_token.type not in TOKENS_TO_QUOTE:
                error_msg = f"expected '=', but got {self.current_token.type}."
            else:
                error_msg = f"expected '=', but got '{self.current_token.type}'."
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
                                                     "expected 'then'"))

        result.register_advancement()
        self.advance()

        body = result.register(self.expr())
        if result.error is not None:
            return result

        return result.success(ForNode(var_name, start_value, end_value, step_value, body))

    def while_expr(self):
        result = ParseResult()

        if not self.current_token.matches(TT_KEYWORD, 'while'):
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     "expected 'while'"))

        result.register_advancement()
        self.advance()

        condition = result.register(self.expr())
        if result.error is not None:
            return result

        if not self.current_token.matches(TT_KEYWORD, 'then'):
            return result.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,
                                                     "expected 'then'"))

        result.register_advancement()
        self.advance()

        body = result.register(self.expr())
        if result.error is not None:
            return result

        return result.success(WhileNode(condition, body))

    def func_def(self):
        result = ParseResult()

        if not self.current_token.matches(TT_KEYWORD, 'def'):
            return result.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected 'def'"
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
                        "expected '('"
                    )
                )
        else:
            var_name_token = None
            if self.current_token.type != TT_LPAREN:
                return result.failure(
                    InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "expected identifier or '('"
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

        if self.current_token.type != TT_ARROW:
            return result.failure(
                InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "expected '->'."
                )
            )

        result.register_advancement()
        self.advance()
        node_to_return = result.register(self.expr())
        if result.error is not None:
            return result

        return result.success(FuncDefNode(
            var_name_token,
            arg_name_tokens,
            node_to_return
        ))

    def bin_op(self, func_a, ops, func_b=None):
        if func_b is None:
            func_b = func_a
        result = ParseResult()
        left = result.register(func_a())
        if result.error is not None:
            return result

        while self.current_token.type in ops or (self.current_token.type, self.current_token.value) in ops:
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
    def __init__(self, pos_start, pos_end, details, context: Context, rt_error: bool = True, error_name: str = ""):

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
            result = f' In file {pos.file_name}, line {pos.line_number + 1}, in {ctx.display_name} :\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return "Traceback (more recent call last) :\n" + result


class RTIndexError(RunTimeError):
    def __init__(self, pos_start, pos_end, details, context: Context):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="IndexError")
        self.context = context


class RTArithmeticError(RunTimeError):
    def __init__(self, pos_start, pos_end, details, context: Context):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="ArithmeticError")
        self.context = context


class NotDefinedError(RunTimeError):
    def __init__(self, pos_start, pos_end, details, context: Context):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="NotDefinedError")
        self.context = context


# ##########
# INTERPRETER
# ##########
class Interpreter:
    # this class does not have __init__ method
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    @staticmethod
    def no_visit_method(node, context: Context):
        print(context)
        print(f"NOUGARO INTERNAL ERROR : No visit_{type(node).__name__} method defined in nougaro.Interpreter.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/redirect1.html with informations above.")
        raise Exception(f'No visit_{type(node).__name__} method defined in nougaro.Interpreter.')

    @staticmethod
    def visit_NumberNode(node: NumberNode, context: Context):
        return RTResult().success(Number(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    @staticmethod
    def visit_StringNode(node: StringNode, context: Context):
        return RTResult().success(
            String(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_ListNode(self, node: ListNode, context: Context):
        result = RTResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(result.register(self.visit(element_node, context)))
            if result.error is not None:
                return result

        return result.success(List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_BinOpNode(self, node: BinOpNode, context: Context):
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
        elif node.op_token.type == TT_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_token.type == TT_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_token.type == TT_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_token.type == TT_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_token.type == TT_LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_token.type == TT_GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_token.matches(TT_KEYWORD, 'and'):
            result, error = left.and_(right)
        elif node.op_token.matches(TT_KEYWORD, 'or'):
            result, error = left.or_(right)
        elif node.op_token.matches(TT_KEYWORD, 'xor'):
            result, error = left.excl_or(right)
        else:
            print(context)
            print("NOUGARO INTERNAL ERROR : Result is not defined after executing nougaro.Interpreter.visit_BinOpNode "
                  "because of an invalid token.\n"
                  "Please report this bug at https://jd-develop.github.io/nougaro/redirect1.html with the information "
                  "below")
            raise Exception("Result is not defined after executing nougaro.Interpreter.visit_BinOpNode")

        if error is not None:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node: UnaryOpNode, context: Context):
        result = RTResult()
        number = result.register(self.visit(node.node, context))
        if result.error is not None:
            return result

        error = None

        if node.op_token.type == TT_MINUS:
            number, error = number.multiplied_by(Number(-1))
        elif node.op_token.matches(TT_KEYWORD, 'not'):
            number, error = number.not_()

        if error is not None:
            return result.failure(error)
        else:
            return result.success(number.set_pos(node.pos_start, node.pos_end))

    @staticmethod
    def visit_VarAccessNode(node: VarAccessNode, context: Context):
        result = RTResult()
        var_name = node.var_name_token.value
        value = context.symbol_table.get(var_name)

        if value is None:
            return result.failure(
                NotDefinedError(
                    node.pos_start, node.pos_end, f'{var_name} is not defined.', context
                )
            )

        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return result.success(value)

    def visit_VarAssignNode(self, node: VarAssignNode, context: Context):
        result = RTResult()
        var_name = node.var_name_token.value
        value = result.register(self.visit(node.value_node, context))
        if result.error is not None:
            return result

        if var_name not in VARS_CANNOT_MODIFY:
            context.symbol_table.set(var_name, value)
        else:
            return result.failure(RunTimeError(node.pos_start, node.pos_end,
                                               f"can not create a variable with builtin name '{var_name}'.",
                                               value.context))
        return result.success(value)

    def visit_IfNode(self, node: IfNode, context: Context):
        result = RTResult()
        for condition, expr in node.cases:
            condition_value = result.register(self.visit(condition, context))
            if result.error is not None:
                return result

            if condition_value.is_true():
                expr_value = result.register(self.visit(expr, context))
                if result.error is not None:
                    return result
                return result.success(expr_value)

        if node.else_case is not None:
            else_value = result.register(self.visit(node.else_case, context))
            if result.error is not None:
                return result
            return result.success(else_value)

        return result.success(None)

    def visit_ForNode(self, node: ForNode, context: Context):
        result = RTResult()
        elements = []

        start_value = result.register(self.visit(node.start_value_node, context))
        if result.error is not None:
            return result

        end_value = result.register(self.visit(node.end_value_node, context))
        if result.error is not None:
            return result

        if node.step_value_node is not None:
            step_value = result.register(self.visit(node.step_value_node, context))
            if result.error is not None:
                return result
        else:
            step_value = Number(1)

        i = start_value.value
        condition = (lambda: i < end_value.value) if step_value.value >= 0 else (lambda: i > end_value.value)

        while condition():
            context.symbol_table.set(node.var_name_token.value, Number(i))
            i += step_value.value

            elements.append(result.register(self.visit(node.body_node, context)))
            if result.error is not None:
                return result

        return result.success(List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_WhileNode(self, node: WhileNode, context: Context):
        result = RTResult()
        elements = []

        while True:
            condition = result.register(self.visit(node.condition_node, context))
            if result.error is not None:
                return result

            if not condition.is_true():
                break

            elements.append(result.register(self.visit(node.body_node, context)))
            if result.error is not None:
                return result

        return result.success(List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

    @staticmethod
    def visit_FuncDefNode(node: FuncDefNode, context: Context):
        result = RTResult()
        func_name = node.var_name_token.value if node.var_name_token is not None else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_tokens]
        func_value = Function(func_name, body_node, arg_names).set_context(context).set_pos(node.pos_start,
                                                                                            node.pos_end)

        if node.var_name_token is not None:
            if func_name not in VARS_CANNOT_MODIFY:
                context.symbol_table.set(func_name, func_value)
            else:
                return result.failure(RunTimeError(node.pos_start, node.pos_end,
                                                   f"can not create a function with builtin name '{func_name}'.",
                                                   context))

        return result.success(func_value)

    def visit_CallNode(self, node: CallNode, context: Context):
        result = RTResult()
        args = []

        value_to_call = result.register(self.visit(node.node_to_call, context))
        if result.error is not None:
            return result
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        if isinstance(value_to_call, BaseFunction):
            # call the function
            for arg_node in node.arg_nodes:
                args.append(result.register(self.visit(arg_node, context)))
                if result.error is not None:
                    return result

            return_value = result.register(value_to_call.execute(args))
            if result.error is not None:
                return result
            return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
            return result.success(return_value)

        elif isinstance(value_to_call, List):
            # get the element at the index given
            if len(node.arg_nodes) == 1:
                index = result.register(self.visit(node.arg_nodes[0], context))
                if isinstance(index, Number):
                    index = index.value
                    try:
                        return_value = value_to_call[index]
                        return result.success(return_value)
                    except Exception:
                        return result.failure(
                            RTIndexError(
                                node.arg_nodes[0].pos_start, node.arg_nodes[0].pos_end,
                                f'list index {index} out of range.',
                                context
                            )
                        )
                else:
                    return result.failure(RunTimeError(
                        node.pos_start, node.pos_end,
                        f"indexes must be integers, not {index.type_}.",
                        context
                    ))
            elif len(node.arg_nodes) > 1:
                return_value = []
                for arg_node in node.arg_nodes:
                    index = result.register(self.visit(arg_node, context))
                    if isinstance(index, Number):
                        index = index.value
                        try:
                            return_value.append(value_to_call[index])
                        except Exception:
                            return result.failure(
                                RTIndexError(
                                    arg_node.pos_start, arg_node.pos_end,
                                    f'list index {index} out of range.',
                                    context
                                )
                            )
                    else:
                        return result.failure(RunTimeError(
                            arg_node.pos_start, arg_node.pos_end,
                            f"indexes must be integers, not {index.type_}.",
                            context
                        ))
                return result.success(List(return_value).set_context(context).set_pos(node.pos_start, node.pos_end))
            else:
                return result.failure(RunTimeError(
                    node.pos_start, node.pos_end,
                    f"please give at least one index.",
                    context
                ))
        else:
            return result.failure(RunTimeError(
                node.pos_start, node.pos_end,
                f"{value_to_call.type_} is not callable.",
                context
            ))

    def visit_AbsNode(self, node: AbsNode, context: Context):
        result = RTResult()

        value_to_abs = result.register(self.visit(node.node_to_abs, context))
        if result.error is not None:
            return result
        value_to_abs = value_to_abs.copy().set_pos(node.pos_start, node.pos_end)

        if not isinstance(value_to_abs, Number):
            return result.failure(RunTimeError(
                node.pos_start, node.pos_end,
                f"expected int or float, but found {value_to_abs.type_}.",
                context
            ))

        return_value = value_to_abs.abs_()
        return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return result.success(return_value)


# ##########
# SYMBOL TABLE
# ##########
global_symbol_table = SymbolTable()
# Constants
global_symbol_table.set("null", Number.NULL)
global_symbol_table.set("True", Number.TRUE)
global_symbol_table.set("False", Number.FALSE)
# MATHS
global_symbol_table.set("math_pi", Number.MATH_PI)
global_symbol_table.set("math_e", Number.MATH_E)
global_symbol_table.set("sqrt_pi", Number.MATH_SQRT_PI)
# Built-in functions
global_symbol_table.set("print", BuiltInFunction.PRINT)
global_symbol_table.set("print_ret", BuiltInFunction.PRINT_RET)
global_symbol_table.set("input", BuiltInFunction.INPUT)
global_symbol_table.set("input_int", BuiltInFunction.INPUT_INT)
global_symbol_table.set("clear", BuiltInFunction.CLEAR)

global_symbol_table.set("is_num", BuiltInFunction.IS_NUMBER)
global_symbol_table.set("is_str", BuiltInFunction.IS_STRING)
global_symbol_table.set("is_list", BuiltInFunction.IS_LIST)
global_symbol_table.set("is_func", BuiltInFunction.IS_FUNCTION)
global_symbol_table.set("type", BuiltInFunction.TYPE)
global_symbol_table.set("str", BuiltInFunction.STR)
global_symbol_table.set("list", BuiltInFunction.LIST)
global_symbol_table.set("int", BuiltInFunction.INT)
global_symbol_table.set("float", BuiltInFunction.FLOAT)

global_symbol_table.set("append", BuiltInFunction.APPEND)
global_symbol_table.set("pop", BuiltInFunction.POP)
global_symbol_table.set("extend", BuiltInFunction.EXTEND)
global_symbol_table.set("get", BuiltInFunction.GET)
# Mathematical functions
global_symbol_table.set("sqrt", BuiltInFunction.SQRT)
global_symbol_table.set("radians", BuiltInFunction.RADIANS)
global_symbol_table.set("degrees", BuiltInFunction.DEGREES)
global_symbol_table.set("sin", BuiltInFunction.SIN)
global_symbol_table.set("cos", BuiltInFunction.COS)
global_symbol_table.set("tan", BuiltInFunction.TAN)
global_symbol_table.set("asin", BuiltInFunction.ASIN)
global_symbol_table.set("acos", BuiltInFunction.ACOS)
global_symbol_table.set("atan", BuiltInFunction.ATAN)
# Hum...
global_symbol_table.set("answerToTheLifeTheUniverseAndEverything", Number(42))
global_symbol_table.set("numberOfHornsOnAnUnicorn", Number(1))
global_symbol_table.set("theLoneliestNumber", Number(1))

global_symbol_table.set("exit", BuiltInFunction.EXIT)


# ##########
# RUN
# ##########
def run(file_name, text, version: str = "not defined"):
    global_symbol_table.set("noug_version", String(version))
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
