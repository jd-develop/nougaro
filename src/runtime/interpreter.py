#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.runtime.values.basevalues.basevalues import Number, String, List, NoneValue, Value, Module, Constructor
from src.runtime.values.basevalues.basevalues import Object
from src.runtime.values.number_constants import FALSE, TRUE
from src.runtime.values.functions.function import Function, Method
from src.runtime.values.functions.base_function import BaseFunction
from src.parser.nodes import *
from src.errors.errors import RunTimeError, RTNotDefinedError, RTTypeError, RTAttributeError, InvalidSyntaxError
from src.errors.errors import RTAssertionError, RTIndexError, RTFileNotFoundError
from src.lexer.token_types import TT, TOKENS_NOT_TO_QUOTE
from src.lexer.token import Token
from src.runtime.runtime_result import RTResult
from src.runtime.context import Context
from src.misc import clear_screen, RunFunction
from src.runtime.symbol_table import SymbolTable
from src.lexer.position import Position
import src.conffiles
# built-in python imports
from inspect import signature
import os.path
import importlib
import pprint

_ORIGIN_FILE = "src.runtime.interpreter.Interpreter"


# ##########
# INTERPRETER
# ##########
# noinspection PyPep8Naming
class Interpreter:
    def __init__(self, run: RunFunction, noug_dir_: str, args: list[String], work_dir: str):
        debug = src.conffiles.access_data("debug")
        if debug is None:
            debug = 0
        self.debug = bool(int(debug))
        self.run = run
        self.noug_dir = noug_dir_
        self.args = args
        self.work_dir: str = work_dir
        self._methods = None
        self.init_methods()
        assert self._methods is not None
        assert self.work_dir is not None, ("please report this bug on "
                                           "https://github.com/jd-develop/nougaro/issues/new/choose")
        
    def init_methods(self):
        self._methods = {
            "AbsNode": self.visit_AbsNode,
            "AssertNode": self.visit_AssertNode,
            "BinOpCompNode": self.visit_BinOpCompNode,
            "BinOpNode": self.visit_BinOpNode,
            "BreakNode": self.visit_BreakNode,
            "CallNode": self.visit_CallNode,
            "ClassNode": self.visit_ClassNode,
            "ContinueNode": self.visit_ContinueNode,
            "DoWhileNode": self.visit_DoWhileNode,
            "DollarPrintNode": self.visit_DollarPrintNode,
            "ExportNode": self.visit_ExportNode,
            "ForNode": self.visit_ForNode,
            "ForNodeList": self.visit_ForNodeList,
            "FuncDefNode": self.visit_FuncDefNode,
            "IfNode": self.visit_IfNode,
            "ImportNode": self.visit_ImportNode,
            "ListNode": self.visit_ListNode,
            "NoNode": self.visit_NoNode,
            "NumberENumberNode": self.visit_NumberENumberNode,
            "NumberNode": self.visit_NumberNode,
            "ReadNode": self.visit_ReadNode,
            "ReturnNode": self.visit_ReturnNode,
            "StringNode": self.visit_StringNode,
            "UnaryOpNode": self.visit_UnaryOpNode,
            "VarAccessNode": self.visit_VarAccessNode,
            "VarAssignNode": self.visit_VarAssignNode,
            "VarDeleteNode": self.visit_VarDeleteNode,
            "WhileNode": self.visit_WhileNode,
            "WriteNode": self.visit_WriteNode,
        }

    @staticmethod
    def update_symbol_table(ctx: Context):
        assert ctx.symbol_table is not None
        symbols_copy: dict[str, Value] = ctx.symbol_table.symbols.copy()
        if '__symbol_table__' in symbols_copy.keys():
            del symbols_copy['__symbol_table__']
        ctx.symbol_table.set('__symbol_table__', String(pprint.pformat(symbols_copy)))

    def visit(self, node: Node, ctx: Context, methods_instead_of_funcs: bool, other_ctx: Context | None = None,
              main_visit: bool = False) -> RTResult:
        """Visit a node."""
        method_name = f'{type(node).__name__}'
        assert self._methods is not None
        method = self._methods.get(method_name, self.no_visit_method)
        if other_ctx is None:
            other_ctx = ctx.copy()

        PARAMETERS = signature(method).parameters
        match len(PARAMETERS):
            case 0:  # def method(self) is 1 param, def staticmethod() is 0 param
                result = method()  # type: ignore
            case 1:  # def method(self) is 1 param, def staticmethod() is 0 param
                result = method(node)  # type: ignore
            case 3:
                result = method(node, ctx, methods_instead_of_funcs=methods_instead_of_funcs)  # type: ignore
            case 4:
                result = method(node, ctx, other_ctx, methods_instead_of_funcs=methods_instead_of_funcs)  # type: ignore
            case _:
                result = method(node, ctx)  # type: ignore
        if main_visit:
            if result.loop_should_break:
                assert result.break_or_continue_pos is not None
                return result.failure(RunTimeError(
                    result.break_or_continue_pos[0], result.break_or_continue_pos[1],
                    "'break' outside of a loop.", ctx,
                    origin_file=f"{_ORIGIN_FILE}.visit"
                ))
            if result.loop_should_continue:
                assert result.break_or_continue_pos is not None
                return result.failure(RunTimeError(
                    result.break_or_continue_pos[0], result.break_or_continue_pos[1],
                    "'continue' outside of a loop.", ctx,
                    origin_file=f"{_ORIGIN_FILE}.visit"
                ))
            if result.function_return_value is not None:
                assert result.return_pos is not None
                return result.failure(RunTimeError(
                    result.return_pos[0], result.return_pos[1],
                    "'return' outside of a function.", ctx,
                    origin_file=f"{_ORIGIN_FILE}.visit"
                ))
        return result

    def _undefined(
            self,
            pos_start: Position,
            pos_end: Position,
            var_name: str,
            ctx: Context,
            result: RTResult,
            origin_file: str = f"{_ORIGIN_FILE}._undefined",
            edit: bool = False
    ) -> RTResult:
        """Returns a RTNotDefinedError with a proper message.
        Note: `edit` parameter is used when the user wants to edit an undefined variable"""
        assert ctx.symbol_table is not None
        close_match_in_symbol_table = ctx.symbol_table.best_match(var_name)
        IS_NOUGARO_LIB = os.path.exists(os.path.abspath(self.noug_dir + f"/lib_/{var_name}.noug"))
        IS_PYTHON_LIB = os.path.exists(os.path.abspath(self.noug_dir + f"/lib_/{var_name}_.py"))
        if edit:
            err_msg = f"name '{var_name}' is not defined or is not editable in current scope."
        else:
            err_msg = f"name '{var_name}' is not defined."

        if IS_NOUGARO_LIB or IS_PYTHON_LIB:
            if ctx.symbol_table.exists(f'__{var_name}__'):
                # e.g. user entered `var foo += 1` instead of `var __foo__ += 1`
                return result.failure(RTNotDefinedError(
                    pos_start, pos_end,
                    f"{err_msg} Maybe you forgot to import it? Or maybe you did mean '__{var_name}__'?",
                    ctx, origin_file + " (is lib and __var_name__ exists)"
                ))
            elif close_match_in_symbol_table is not None:
                return result.failure(RTNotDefinedError(
                    pos_start, pos_end,
                    f"{err_msg} Maybe you forgot to import it? Or maybe you did mean '{close_match_in_symbol_table}'?",
                    ctx, origin_file + " (is lib and close match in symbol table)"
                ))
            return result.failure(RTNotDefinedError(
                pos_start, pos_end,
                f"{err_msg} Maybe you forgot to import it?",
                ctx, origin_file + " (is lib and no other match)"
            ))
        elif ctx.symbol_table.exists(f'__{var_name}__'):
            # e.g. user entered `var foo += 1` instead of `var __foo__ += 1`
            return result.failure(RTNotDefinedError(
                pos_start, pos_end,
                f"{err_msg} Did you mean '__{var_name}__'?",
                ctx, origin_file + " (is NOT lib and __var_name__ exists)"
            ))
        elif close_match_in_symbol_table is not None:
            return result.failure(RTNotDefinedError(
                pos_start, pos_end,
                f"{err_msg} Did you mean '{close_match_in_symbol_table}'?",
                ctx, origin_file + " (is NOT lib and close match in symbol table)"
            ))
        else:
            return result.failure(RTNotDefinedError(
                pos_start, pos_end,
                err_msg,
                ctx, origin_file + " (is NOT lib and no other match)"
            ))

    def _visit_value_that_can_have_attributes(
            self, node_or_list: Node | list[Node], result: RTResult, context: Context,
            methods_instead_of_funcs: bool
    ) -> RTResult | Value:
        """If node_or_list is Node, visit is and return it. If it is a list, visit the value and its attributes."""
        if not isinstance(node_or_list, list):
            value = result.register(self.visit(node_or_list, context, methods_instead_of_funcs))
            if result.should_return() or value is None:  # check for errors
                return result
        else:  # attributes
            value = result.register(self.visit(node_or_list[0], context, methods_instead_of_funcs))
            if result.should_return() or value is None:  # check for errors
                return result
            if len(node_or_list) != 1:
                for node_ in node_or_list[1:]:
                    new_ctx = Context(display_name=value.__repr__(), parent=context)
                    new_ctx.symbol_table = SymbolTable()
                    new_ctx.symbol_table.set_whole_table(value.attributes)
                    new_ctx.symbol_table.parent = context.symbol_table

                    if not (isinstance(node_, VarAccessNode) or isinstance(node_, CallNode)):
                        assert node_.pos_start is not None
                        assert node_.pos_end is not None
                        return result.failure(RunTimeError(
                            node_.pos_start, node_.pos_end,
                            f"unexpected node: {node_.__class__.__name__}.",
                            context,
                            origin_file=f"{_ORIGIN_FILE}._visit_value_that_can_have_attributes"
                        ))

                    node_.attr = True
                    attr_ = result.register(self.visit(node_, new_ctx, methods_instead_of_funcs, other_ctx=context))
                    if result.should_return() or attr_ is None:
                        return result
                    value = attr_
        return value

    @staticmethod
    def no_visit_method(node: Node, ctx: Context):
        """The method visit_FooNode (with FooNode given in self.visit) does not exist."""
        print(ctx)
        print(f"NOUGARO INTERNAL ERROR: No visit_{type(node).__name__} method defined in {_ORIGIN_FILE}.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with all informations "
              f"above.")
        raise Exception(f'No visit_{type(node).__name__} method defined in {_ORIGIN_FILE}.')

    @staticmethod
    def visit_NumberNode(node: NumberNode, ctx: Context) -> RTResult:
        """Visit NumberNode."""
        assert node.token.value is not None
        assert not isinstance(node.token.value, str)
        return RTResult().success(Number(node.token.value).set_context(ctx).set_pos(node.pos_start, node.pos_end))

    @staticmethod
    def visit_NumberENumberNode(node: NumberENumberNode, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit NumberENumberNode."""
        assert node.exponent_token.value is not None
        assert not isinstance(node.exponent_token.value, str)
        assert node.num_token.value is not None
        assert not isinstance(node.num_token.value, str)
        value = node.num_token.value * (10 ** node.exponent_token.value)
        if isinstance(value, int) or isinstance(value, float):
            return RTResult().success(Number(value).set_context(ctx).set_pos(node.pos_start, node.pos_end))
        else:
            print(ctx)
            print(f"NOUGARO INTERNAL ERROR: in visit_NumberENumberNode method defined in {_ORIGIN_FILE},\n"
                  f"{value=}, {methods_instead_of_funcs=}\n"
                  f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with all "
                  f"informations above.")
            raise Exception(f'{value=} in {_ORIGIN_FILE}.visit_NumberENumberNode.')

    @staticmethod
    def visit_StringNode(node: StringNode, ctx: Context) -> RTResult:
        """Visit StringNode"""
        assert isinstance(node.token.value, str)
        return RTResult().success(
            String(node.token.value).set_context(ctx).set_pos(node.pos_start, node.pos_end)
        )

    def visit_AbsNode(self, node: AbsNode, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit AbsNode"""
        result = RTResult()
        node_to_abs = node.node_to_abs
        value_to_abs = result.register(self.visit(node_to_abs, ctx, methods_instead_of_funcs))
        if result.should_return():
            return result
        if not isinstance(value_to_abs, Number):
            assert value_to_abs is not None
            assert value_to_abs.pos_start is not None
            assert value_to_abs.pos_end is not None
            return result.failure(RTTypeError(
                value_to_abs.pos_start, value_to_abs.pos_end,
                f"expected number, got {value_to_abs.type_}.",
                ctx, origin_file=f"{_ORIGIN_FILE}.visit_AbsNode"
            ))
        new_value = value_to_abs.copy()
        new_value.value = abs(new_value.value)
        return result.success(new_value.set_context(ctx).set_pos(node.pos_start, node.pos_end))

    def visit_ListNode(self, node: ListNode, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit ListNode"""
        result = RTResult()
        elements: list[Value] = []

        for element_node, mul in node.element_nodes:  # we visit every node from the list
            if not mul:
                value = result.register(self.visit(element_node, ctx, methods_instead_of_funcs))
                if result.should_return() or value is None:  # if there is an error
                    return result
                elements.append(value)
            else:
                extend_list_: Value | None = result.register(self.visit(element_node, ctx, methods_instead_of_funcs))
                if result.should_return() or extend_list_ is None:  # if there is an error
                    return result
                if not isinstance(extend_list_, List):
                    assert extend_list_.pos_start is not None
                    assert extend_list_.pos_end is not None
                    return result.failure(RTTypeError(
                        extend_list_.pos_start, extend_list_.pos_end,
                        f"expected a list value after '*', but got {extend_list_.type_}.",
                        ctx,
                        origin_file=f"{_ORIGIN_FILE}.visit_ListNode"
                    ))
                elements.extend(extend_list_.elements)

        return result.success(List(elements).set_context(ctx).set_pos(node.pos_start, node.pos_end))

    def visit_BinOpNode(self, node: BinOpNode, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit BinOpNode"""
        res = RTResult()
        left = self._visit_value_that_can_have_attributes(node.left_node, res, ctx, methods_instead_of_funcs)
        if res.should_return():
            return res
        assert isinstance(left, Value)

        if node.op_token.matches(TT["KEYWORD"], 'and') and left.is_false():
            # operator is "and" and the value is false
            return res.success(FALSE.copy().set_pos(node.pos_start, node.pos_end))

        if node.op_token.matches(TT["KEYWORD"], 'or') and left.is_true():
            # operator is "or" and the value is true
            return res.success(TRUE.copy().set_pos(node.pos_start, node.pos_end))

        right = self._visit_value_that_can_have_attributes(node.right_node, res, ctx, methods_instead_of_funcs)
        if res.should_return():
            return res
        assert isinstance(right, Value)

        # we check for what is the operator token, then we execute the corresponding method
        if node.op_token.type == TT["PLUS"]:
            result, error = left.added_to(right)
        elif node.op_token.type == TT["MINUS"]:
            result, error = left.subbed_by(right)
        elif node.op_token.type == TT["MUL"]:
            result, error = left.multiplied_by(right)
        elif node.op_token.type == TT["DIV"]:
            result, error = left.dived_by(right)
        elif node.op_token.type == TT["PERC"]:
            result, error = left.modded_by(right)
        elif node.op_token.type == TT["FLOORDIV"]:
            result, error = left.floor_dived_by(right)
        elif node.op_token.type == TT["POW"]:
            result, error = left.powered_by(right)
        elif node.op_token.type == TT["EE"]:
            result, error = left.get_comparison_eq(right)
        elif node.op_token.type == TT["NE"]:
            result, error = left.get_comparison_ne(right)
        elif node.op_token.type == TT["LT"]:
            result, error = left.get_comparison_lt(right)
        elif node.op_token.type == TT["GT"]:
            result, error = left.get_comparison_gt(right)
        elif node.op_token.type == TT["LTE"]:
            result, error = left.get_comparison_lte(right)
        elif node.op_token.type == TT["GTE"]:
            result, error = left.get_comparison_gte(right)
        elif node.op_token.matches(TT["KEYWORD"], 'and'):
            result, error = left.and_(right)
        elif node.op_token.matches(TT["KEYWORD"], 'or'):
            result, error = left.or_(right)
        elif node.op_token.matches(TT["KEYWORD"], 'xor'):
            result, error = left.xor_(right)
        elif node.op_token.type == TT["BITWISEAND"]:
            result, error = left.bitwise_and(right)
        elif node.op_token.type == TT["BITWISEOR"]:
            result, error = left.bitwise_or(right)
        elif node.op_token.type == TT["BITWISEXOR"]:
            result, error = left.bitwise_xor(right)
        else:
            print(ctx)
            print("NOUGARO INTERNAL ERROR : Result is not defined after executing "
                  f"{_ORIGIN_FILE}.visit_BinOpNode because of an invalid token.\n"
                  f"{methods_instead_of_funcs=}\n"
                  "Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with the information "
                  "above")
            raise Exception(f"Result is not defined after executing {_ORIGIN_FILE}.visit_BinOpNode")

        if error is not None:  # there is an error
            return res.failure(error)
        
        assert result is not None
        return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_BinOpCompNode(self, node: BinOpCompNode, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit BinOpCompNode"""
        res = RTResult()
        nodes_and_tokens_list = node.nodes_and_tokens_list
        IS_COMPARISON = len(nodes_and_tokens_list) != 1
        if not IS_COMPARISON:
            assert isinstance(nodes_and_tokens_list[0], Node) or isinstance(nodes_and_tokens_list[0], list)
            value = self._visit_value_that_can_have_attributes(
                nodes_and_tokens_list[0], res, ctx, methods_instead_of_funcs
            )
            if res.should_return():
                return res
            assert isinstance(value, Value)
            return res.success(value)

        visited_nodes_and_tokens_list: list[Value | Token] = []

        # just list of visited nodes
        for index, element in enumerate(nodes_and_tokens_list):
            if index % 2 == 0:  # we take only nodes and not ops
                assert isinstance(element, Node) or isinstance(element, list)
                value = self._visit_value_that_can_have_attributes(element, res, ctx, methods_instead_of_funcs)
                if res.should_return():
                    return res
                assert isinstance(value, Value)
                visited_nodes_and_tokens_list.append(value)
            else:
                assert isinstance(element, Token)
                visited_nodes_and_tokens_list.append(element)

        test_result = FALSE.copy()  # FALSE is Nougaro False
        # let's test!
        for index, element in enumerate(visited_nodes_and_tokens_list):
            if index % 2 != 0:  # we take only nodes and not ops
                continue
            assert isinstance(element, Value)

            # test
            try:
                op_token = visited_nodes_and_tokens_list[index + 1]
                right = visited_nodes_and_tokens_list[index + 2]
                assert isinstance(op_token, Token)
                assert isinstance(right, Value)
            except IndexError:
                break

            if op_token.type == TT["EE"]:
                test_result, error = element.get_comparison_eq(right)
            elif op_token.type == TT["NE"]:
                test_result, error = element.get_comparison_ne(right)
            elif op_token.type == TT["LT"]:
                test_result, error = element.get_comparison_lt(right)
            elif op_token.type == TT["GT"]:
                test_result, error = element.get_comparison_gt(right)
            elif op_token.type == TT["LTE"]:
                test_result, error = element.get_comparison_lte(right)
            elif op_token.type == TT["GTE"]:
                test_result, error = element.get_comparison_gte(right)
            elif op_token.matches(TT["KEYWORD"], 'in'):
                test_result, error = element.is_in(right)
            else:
                print(ctx)
                print(
                    f"NOUGARO INTERNAL ERROR: Result is not defined after executing "
                    f"{_ORIGIN_FILE}.visit_BinOpCompNode because of an invalid token.\n"
                    f"{methods_instead_of_funcs}\n"
                    f"Note for devs: the actual invalid token is {op_token.type}:{op_token.value}.\n"
                    f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with the "
                    f"information above")
                raise Exception("Result is not defined after executing "
                                f"{_ORIGIN_FILE}.visit_BinOpCompNode")
            if error is not None:  # there is an error
                return res.failure(error)
            assert test_result is not None
            if test_result.value == FALSE.value:  # the test is false so far: no need to continue
                return res.success(test_result.set_pos(node.pos_start, node.pos_end))
        return res.success(test_result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node: UnaryOpNode, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit UnaryOpNode (-x, not x, ~x)"""
        result = RTResult()
        if isinstance(node.node, list):
            if len(node.node) == 1:
                value = result.register(self.visit(node.node[0], ctx, methods_instead_of_funcs))
            else:
                print(ctx)
                print(
                    f"NOUGARO INTERNAL ERROR: len(node.node) != 1 in {_ORIGIN_FILE}.visit_UnaryOpNode.\n"
                    f"{node.node=}, {methods_instead_of_funcs=}\n"
                    f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with the "
                    f"information above.")
                raise Exception(f"len(node.node) != 1 in {_ORIGIN_FILE}.visit_UnaryOpNode.")
        else:
            value = result.register(self.visit(node.node, ctx, methods_instead_of_funcs))
        if result.should_return():
            return result
        assert value is not None

        error = None

        if node.op_token.type == TT["MINUS"]:
            value, error = value.multiplied_by(
                Number(-1).set_pos(node.op_token.pos_start, node.op_token.pos_end)
            )  # -x is like x*-1
        elif node.op_token.matches(TT["KEYWORD"], 'not'):
            value = FALSE if value.is_true() else TRUE
        elif node.op_token.type == TT["BITWISENOT"]:
            value, error = value.bitwise_not()

        if error is not None:  # there is an error
            return result.failure(error)
        
        assert value is not None
        return result.success(value.set_pos(node.pos_start, node.pos_end))

    def visit_VarAccessNode(self, node: VarAccessNode, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit VarAccessNode"""
        attribute_error = node.attr
        result = RTResult()
        var_names_list: list[Token | Node] = node.var_name_tokens_list  # there is a list because it can be `a ? b ? c`
        value = None
        var_name: Token | Node = var_names_list[0]  # first we take the first identifier
        for var_name in var_names_list:  # we check for all the identifiers
            IS_IDENTIFIER = isinstance(var_name, Token) and var_name.type == TT["IDENTIFIER"]
            if not IS_IDENTIFIER:
                assert isinstance(var_name, Node)
                value = result.register(self.visit(var_name, ctx, methods_instead_of_funcs))  # here var_name is an expr
                if result.should_return():
                    return result
                break
            assert ctx.symbol_table is not None
            assert isinstance(var_name, Token)
            assert isinstance(var_name.value, str)
            value = ctx.symbol_table.get(var_name.value)  # we get the value of the variable
            if value is not None:  # if the variable is defined, we can stop here
                break

        VARIABLE_IS_DEFINED = value is not None
        if not VARIABLE_IS_DEFINED:
            if attribute_error:
                assert node.pos_start is not None
                assert node.pos_end is not None
                assert isinstance(var_name, Token)
                assert isinstance(var_name.value, str)
                return result.failure(RTAttributeError(
                    node.pos_start, node.pos_end, ctx.display_name, var_name.value, ctx,
                    f"{_ORIGIN_FILE}.visit_varAccessNode"
                ))

            SINGLE_IDENTIFIER = len(var_names_list) == 1
            if SINGLE_IDENTIFIER:
                assert node.pos_start is not None
                assert node.pos_end is not None
                assert isinstance(var_name, Token)
                assert isinstance(var_name.value, str)
                return self._undefined(
                    node.pos_start, node.pos_end, var_name.value, ctx, result, f"{_ORIGIN_FILE}.visit_VarAccessNode"
                )
            else:  # none of the identifiers is defined
                assert node.pos_start is not None
                assert node.pos_end is not None
                return result.failure(RTNotDefinedError(
                    node.pos_start, node.pos_end, f"none of the given identifiers is defined.", ctx,
                    f"{_ORIGIN_FILE}.visit_varAccessNode"
                ))

        # we get the value
        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(ctx)
        return result.success(value)

    def visit_VarAssignNode(self, node: VarAssignNode, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit VarAssignNode"""
        result = RTResult()
        var_names: list[list[Token | Node]] = node.var_names

        values: list[Value] = []
        if node.value_nodes is not None:
            for value_node in node.value_nodes:  # we get the values
                value = result.register(self.visit(value_node, ctx, methods_instead_of_funcs))
                if result.should_return() or result.old_should_return or value is None:
                    return result
                assert value is not None
                values.append(value)

        equal = node.equal.type  # we get the equal type

        if equal in [TT["INCREMENT"], TT["DECREMENT"]]:
            values = [Number(1).set_pos(node.equal.pos_start, node.equal.pos_end)] * len(var_names)
            if equal == TT["INCREMENT"]:
                equal = TT["PLUSEQ"]
            else:
                equal = TT["MINUSEQ"]

        if len(var_names) != len(values):
            assert node.pos_start is not None
            assert node.pos_end is not None
            return result.failure(RunTimeError(
                node.pos_start, node.pos_end,
                f"there should be the same amount of identifiers and values. "
                f"There are {len(var_names)} identifiers and {len(values)} values.",
                ctx, origin_file=f"{_ORIGIN_FILE}.visit_VarAssignNode"
            ))

        final_values: list[Value] = []
        assert ctx.symbol_table is not None
        for i, var_name in enumerate(var_names):
            IS_SINGLE_VAR_NAME = len(var_name) == 1
            if IS_SINGLE_VAR_NAME:
                NAME_IS_IDENTIFIER = isinstance(var_name[0], Token) and var_name[0].type == TT["IDENTIFIER"]
                if not NAME_IS_IDENTIFIER:
                    assert var_name[0].pos_start is not None
                    assert var_name[0].pos_end is not None
                    return result.failure(RunTimeError(
                        var_name[0].pos_start, var_name[0].pos_end,
                        "excepted identifier.",
                        ctx, origin_file=f"{_ORIGIN_FILE}.visit_VarAssignNode"
                    ))
                
                assert isinstance(var_name[0], Token)
                assert isinstance(var_name[0].value, str)
                final_var_name: str = var_name[0].value

                variable_exists = final_var_name in ctx.symbol_table.symbols
                if variable_exists:
                    var_actual_value: Value | None = ctx.symbol_table.get(final_var_name)
                else:
                    var_actual_value: Value | None = None
                value: Value | None = None
            else:  # var a.b.(...).z = value
                if isinstance(var_name[0], Token) and var_name[0].type == TT["IDENTIFIER"]:
                    assert isinstance(var_name[0].value, str)
                    value = ctx.symbol_table.get(var_name[0].value)
                    if value is None:
                        assert var_name[0].pos_start is not None
                        assert var_name[0].pos_end is not None
                        return self._undefined(
                            var_name[0].pos_start, var_name[0].pos_end, var_name[0].value, ctx, result,
                            origin_file="src.runtime.interpreter.Interpreter.visit_VarAssignNode"
                        )
                elif isinstance(var_name[0], Token):
                    if var_name[0].type in TOKENS_NOT_TO_QUOTE:
                        err_msg = f"unexpected token: {var_name[0].type}."
                    else:
                        err_msg = f"unexpected token: '{var_name[0].type}'."
                    return result.failure(InvalidSyntaxError(
                        var_name[0].pos_start, var_name[0].pos_end,
                        err_msg, origin_file="src.runtime.interpreter.Interpreter.visit_VarAssignNode"
                    ))
                else:
                    value = result.register(self.visit(var_name[0], ctx, methods_instead_of_funcs))
                    if result.should_return():
                        return result
                
                assert isinstance(value, Value)

                for node_or_tok in var_name[1:-1]:
                    new_ctx = Context(display_name=value.__repr__(), parent=ctx)
                    new_ctx.symbol_table = SymbolTable()
                    new_ctx.symbol_table.set_whole_table(value.attributes)
                    new_ctx.symbol_table.parent = ctx.symbol_table

                    if isinstance(node_or_tok, Token) and node_or_tok.type == TT["IDENTIFIER"]:
                        assert isinstance(node_or_tok.value, str)
                        value = new_ctx.symbol_table.get(node_or_tok.value)
                        if value is None:
                            assert node_or_tok.pos_start is not None
                            assert node_or_tok.pos_end is not None
                            return self._undefined(
                                node_or_tok.pos_start, node_or_tok.pos_end, node_or_tok.value, new_ctx, result,
                                origin_file=f"{_ORIGIN_FILE}.visit_VarAssignNode"
                            )
                    elif isinstance(node_or_tok, Token):
                        if node_or_tok.type in TOKENS_NOT_TO_QUOTE:
                            err_msg = f"unexpected token: {node_or_tok.type}."
                        else:
                            err_msg = f"unexpected token: '{node_or_tok.type}'."
                        return result.failure(InvalidSyntaxError(
                            node_or_tok.pos_start, node_or_tok.pos_end,
                            err_msg, origin_file="src.runtime.interpreter.Interpreter.visit_VarAssignNode"
                        ))
                    else:
                        if not (isinstance(node_or_tok, VarAccessNode) or isinstance(node_or_tok, CallNode)):
                            assert node_or_tok.pos_start is not None
                            assert node_or_tok.pos_end is not None
                            return result.failure(RunTimeError(
                                node_or_tok.pos_start, node_or_tok.pos_end,
                                f"unexpected node: {node_or_tok.__class__.__name__}.",
                                ctx, origin_file="src.runtime.interpreter.Interpreter.visit_VarAssignNode"
                            ))
                        value = result.register(self.visit(node_or_tok, new_ctx, methods_instead_of_funcs,
                                                           other_ctx=ctx))
                        if result.should_return():
                            return result
                        assert value is not None

                assert isinstance(var_name[-1], Token)
                TOKEN_IS_IDENTIFIER = var_name[-1].type == TT["IDENTIFIER"]
                if not TOKEN_IS_IDENTIFIER:
                    assert var_name[-1].pos_start is not None
                    assert var_name[-1].pos_end is not None
                    return result.failure(RunTimeError(
                        var_name[-1].pos_start, var_name[-1].pos_end,
                        "expected valid identifier.",
                        ctx, origin_file="src.runtime.interpreter.Interpreter.visit_VarAssignNode"
                    ))

                assert isinstance(var_name[-1].value, str)
                final_var_name: str = var_name[-1].value
                variable_exists = final_var_name in value.attributes
                if variable_exists:
                    var_actual_value: Value | None = value.attributes[var_name[-1].value]
                else:
                    var_actual_value: Value | None = None

            if equal == TT["EQ"]:  # just a regular equal, we can modify/create the variable in the symbol table
                final_value, error = values[i], None  # we want to return the new value of the variable
            elif variable_exists:  # edit variable
                assert isinstance(var_actual_value, Value)  # a little cheesy
                var_actual_value.set_pos(var_name[0].pos_start, var_name[-1].pos_end)
                if equal == TT["PLUSEQ"]:
                    final_value, error = var_actual_value.added_to(values[i])
                elif equal == TT["MINUSEQ"]:
                    final_value, error = var_actual_value.subbed_by(values[i])
                elif equal == TT["MULTEQ"]:
                    final_value, error = var_actual_value.multiplied_by(values[i])
                elif equal == TT["DIVEQ"]:
                    final_value, error = var_actual_value.dived_by(values[i])
                elif equal == TT["POWEQ"]:
                    final_value, error = var_actual_value.powered_by(values[i])
                elif equal == TT["FLOORDIVEQ"]:
                    final_value, error = var_actual_value.floor_dived_by(values[i])
                elif equal == TT["PERCEQ"]:
                    final_value, error = var_actual_value.modded_by(values[i])
                elif equal == TT["OREQ"]:
                    final_value, error = var_actual_value.or_(values[i])
                elif equal == TT["XOREQ"]:
                    final_value, error = var_actual_value.xor_(values[i])
                elif equal == TT["ANDEQ"]:
                    final_value, error = var_actual_value.and_(values[i])
                elif equal == TT["BITWISEANDEQ"]:
                    final_value, error = var_actual_value.bitwise_and(values[i])
                elif equal == TT["BITWISEOREQ"]:
                    final_value, error = var_actual_value.bitwise_or(values[i])
                elif equal == TT["BITWISEXOREQ"]:
                    final_value, error = var_actual_value.bitwise_xor(values[i])
                elif equal == TT["EEEQ"]:
                    final_value, error = var_actual_value.get_comparison_eq(values[i])
                elif equal == TT["LTEQ"]:
                    final_value, error = var_actual_value.get_comparison_lt(values[i])
                elif equal == TT["GTEQ"]:
                    final_value, error = var_actual_value.get_comparison_gt(values[i])
                elif equal == TT["LTEEQ"]:
                    final_value, error = var_actual_value.get_comparison_lte(values[i])
                elif equal == TT["GTEEQ"]:
                    final_value, error = var_actual_value.get_comparison_gte(values[i])
                else:  # this is not supposed to happen
                    print(
                        f"Note: there was a problem in {_ORIGIN_FILE}.visit_VarAssignNode.\n"
                        "Please report this error at https://jd-develop.github.io/nougaro/bugreport.html "
                        "with all infos.\n"
                        "Note that your variable will be set to the value you given.\n"
                        f"For the dev: equal token '{equal}' is in EQUALS but not planned in "
                        "visit_VarAssignNode"
                    )
                    error = None
                    final_value = values[i]
            else:  # variable does not exist
                assert node.pos_start is not None
                assert node.pos_end is not None
                return self._undefined(node.pos_start, node.pos_end, final_var_name, ctx, result,
                                       f"{_ORIGIN_FILE}.visit_VarAssignNode", edit=True)

            if error is not None:  # there is an error
                assert node.pos_start is not None
                assert node.pos_end is not None
                error.set_pos(node.pos_start, node.pos_end)
                return result.failure(error)

            if not IS_SINGLE_VAR_NAME:
                assert value is not None
                assert isinstance(var_name[-1], Token)
                assert isinstance(var_name[-1].value, str)
                assert final_value is not None
                value.attributes[var_name[-1].value] = final_value
            else:
                assert final_value is not None
                ctx.symbol_table.set(final_var_name, final_value)

            final_values.append(final_value)

        self.update_symbol_table(ctx)
        # we return the (new) value(s) of the variable(s).
        if len(final_values) != 1:
            return result.success(
                List(final_values).set_pos(node.pos_start, node.pos_end)
            )
        else:
            return result.success(
                final_values[0].set_pos(node.pos_start, node.pos_end)
            )

    def visit_VarDeleteNode(self, node: VarDeleteNode, ctx: Context) -> RTResult:
        """Visit VarDeleteNode"""
        result = RTResult()
        var_name = node.var_name_token.value  # we get the var name
        assert isinstance(var_name, str)
        assert ctx.symbol_table is not None

        if var_name not in ctx.symbol_table.symbols:  # the variable is not defined, so we can't delete it
            assert node.pos_start is not None
            assert node.pos_end is not None
            return self._undefined(node.pos_start, node.pos_end, var_name, ctx, result,
                                   f"{_ORIGIN_FILE}.visit_varDeleteNode")

        ctx.symbol_table.remove(var_name)

        self.update_symbol_table(ctx)
        return result.success(NoneValue(False))

    def visit_IfNode(self, node: IfNode, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit IfNode"""
        result = RTResult()
        IF_AND_ELIF_CASES = node.cases
        for condition, body_expr in IF_AND_ELIF_CASES:
            condition_value = result.register(self.visit(condition, ctx, methods_instead_of_funcs))
            if result.should_return():  # check for errors
                return result
            assert condition_value is not None

            if condition_value.is_true():  # if it is true: we execute the body code then we return the value
                expr_value = result.register(self.visit(body_expr, ctx, methods_instead_of_funcs))
                if result.should_return():  # check for errors
                    return result
                assert expr_value is not None
                return result.success(expr_value)

        ELSE_CASE = node.else_case is not None
        if ELSE_CASE:
            assert node.else_case is not None
            else_value = result.register(self.visit(node.else_case, ctx, methods_instead_of_funcs))
            if result.should_return():  # check for errors
                return result
            assert else_value is not None
            return result.success(else_value)

        return result.success(NoneValue(False))

    def visit_AssertNode(self, node: AssertNode, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit AssertNode"""
        result = RTResult()
        assertion = result.register(self.visit(node.assertion, ctx, methods_instead_of_funcs))  # we get the assertion
        if result.should_return():  # check for errors
            return result
        assert assertion is not None
        if node.errmsg is None:
            errmsg = String("").set_pos(node.pos_start, node.pos_end).set_context(ctx)
        else:
            errmsg = result.register(self.visit(node.errmsg, ctx, methods_instead_of_funcs))  # we get the error message
            if result.should_return():  # check for errors
                return result
            assert errmsg is not None

        if not isinstance(errmsg, String):  # we check if the error message is a String
            assert errmsg.pos_start is not None
            assert errmsg.pos_end is not None
            return result.failure(RTTypeError(
                errmsg.pos_start, errmsg.pos_end,
                f"error message should be a str, not {errmsg.type_}.",
                ctx, f"{_ORIGIN_FILE}.visit_Assert_Node"
            ))

        if assertion.is_false():  # the assertion is not true, we return an error
            assert assertion.pos_start is not None
            assert assertion.pos_end is not None
            return result.failure(RTAssertionError(
                assertion.pos_start, assertion.pos_end,
                errmsg.value,
                ctx, f"{_ORIGIN_FILE}.visit_AssertNode"
            ))

        return result.success(NoneValue(False))

    def visit_ForNode(self, node: ForNode, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit ForNode. for i = start to end then"""
        result = RTResult()
        elements: list[Value] = []

        start_value = result.register(self.visit(node.start_value_node, ctx, methods_instead_of_funcs))
        if result.should_return():  # check for errors
            return result
        assert start_value is not None
        if not (isinstance(start_value, Number) and isinstance(start_value.value, int)):
            assert start_value.pos_start is not None
            assert start_value.pos_end is not None
            return result.failure(RTTypeError(
                start_value.pos_start, start_value.pos_end,
                f"start value should be an integer, not {start_value.type_}.",
                ctx, origin_file=f"{_ORIGIN_FILE}.visit_ForNode"
            ))

        end_value = result.register(self.visit(node.end_value_node, ctx, methods_instead_of_funcs))
        if result.should_return():  # check for errors
            return result
        assert end_value is not None
        if not (isinstance(end_value, Number) and isinstance(end_value.value, int)):
            assert end_value.pos_start is not None
            assert end_value.pos_end is not None
            return result.failure(RTTypeError(
                end_value.pos_start, end_value.pos_end,
                f"end value should be an integer, not {end_value.type_}.",
                ctx, origin_file=f"{_ORIGIN_FILE}.visit_ForNode"
            ))

        if node.step_value_node is not None:  # we get the step value, if there is one
            step_value = result.register(self.visit(node.step_value_node, ctx, methods_instead_of_funcs))
            if result.should_return():  # check for errors
                return result
            assert step_value is not None
        else:
            step_value = Number(1)  # no step value: default is 1
        if not (isinstance(step_value, Number) and isinstance(step_value.value, int)):
            assert step_value.pos_start is not None
            assert step_value.pos_end is not None
            return result.failure(RTTypeError(
                step_value.pos_start, step_value.pos_end,
                f"step value should be an integer, not {step_value.type_}.",
                ctx, origin_file=f"{_ORIGIN_FILE}.visit_ForNode"
            ))

        # we make an end condition
        # if step value is *positive*, the end value is *more* than the initial value
        # if step value is *negative*, the end value is *less* than the initial value
        i = start_value.value
        POSITIVE_STEP = step_value.value >= 0
        if POSITIVE_STEP:
            condition = (lambda: i < end_value.value)
        else:
            condition = (lambda: i > end_value.value)

        assert ctx.symbol_table is not None
        assert isinstance(node.var_name_token.value, str)

        while condition():
            ctx.symbol_table.set(node.var_name_token.value, Number(i))  # we set the iterating variable
            self.update_symbol_table(ctx)
            i += step_value.value  # we add up the step value to the iterating variable

            value = result.register(self.visit(node.body_node, ctx, methods_instead_of_funcs))
            if result.loop_should_continue:
                elements.append(NoneValue(False))
                continue  # will continue the 'while condition()' -> the interpreted 'for' loop is continued

            if result.loop_should_break:
                elements.append(NoneValue(False))
                break  # will break the 'while condition()' -> the interpreted 'for' loop is break

            if result.should_return():
                # if there is an error or a 'return' statement
                return result
            assert value is not None

            elements.append(value)

        return result.success(
            List(elements).set_context(ctx).set_pos(node.pos_start, node.pos_end)
        )

    def visit_ForNodeList(self, node: ForNodeList, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit ForNodeList. for i in list then"""
        result = RTResult()
        elements: list[Value] = []

        iterable_ = result.register(self.visit(node.list_node, ctx, methods_instead_of_funcs))  # we get the list
        if result.should_return():  # check for errors
            return result

        if isinstance(iterable_, List):
            python_iterable = iterable_.elements
        elif isinstance(iterable_, String):
            python_iterable = iterable_.to_python_str()
        else:  # this is not a list nor a str
            assert node.list_node.pos_start is not None
            assert node.list_node.pos_end is not None
            assert iterable_ is not None
            return result.failure(RTTypeError(
                node.list_node.pos_start, node.list_node.pos_end,
                f"expected a list or a str after 'in', but found {iterable_.type_}.",
                ctx, f"{_ORIGIN_FILE}.visit_ForNodeList"
            ))

        assert ctx.symbol_table is not None
        assert isinstance(node.var_name_token.value, str)
        for element in python_iterable:
            # we set the variable to the actual list element
            if isinstance(element, str):
                element = String(element)
            ctx.symbol_table.set(node.var_name_token.value, element)
            self.update_symbol_table(ctx)
            value = result.register(self.visit(node.body_node, ctx, methods_instead_of_funcs))

            if result.loop_should_continue:
                elements.append(NoneValue(False))
                continue  # will continue the 'for e in iterable_.elements' -> the interpreted 'for' loop is
                #           continued

            if result.loop_should_break:
                elements.append(NoneValue(False))
                break  # will break the 'for e in iterable_.elements' -> the interpreted 'for' loop is break

            if result.should_return():
                # error or 'return' statement
                return result
            assert value is not None

            elements.append(value)

        return result.success(
            List(elements).set_context(ctx).set_pos(node.pos_start, node.pos_end)
        )

    def visit_WhileNode(self, node: WhileNode, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit WhileNode"""
        result = RTResult()
        elements: list[Value] = []

        condition = result.register(self.visit(node.condition_node, ctx, methods_instead_of_funcs))
        if result.should_return():  # check for errors
            return result
        assert condition is not None

        while condition.is_true():
            value = result.register(self.visit(node.body_node, ctx, methods_instead_of_funcs))
            if result.loop_should_continue:
                elements.append(NoneValue(False))
                continue

            if result.loop_should_break:
                elements.append(NoneValue(False))
                break

            if result.should_return():
                # error or 'return' statement
                return result
            assert value is not None

            elements.append(value)

            condition = result.register(self.visit(node.condition_node, ctx, methods_instead_of_funcs))
            if result.should_return():  # check for errors
                return result
            assert condition is not None

        return result.success(
            List(elements).set_context(ctx).set_pos(node.pos_start, node.pos_end)
        )

    def visit_DoWhileNode(self, node: DoWhileNode, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit DoWhileNode"""
        result = RTResult()
        elements: list[Value] = []

        while True:
            value = result.register(self.visit(node.body_node, ctx, methods_instead_of_funcs))
            if result.loop_should_continue:
                elements.append(NoneValue(False))
                continue

            if result.loop_should_break:
                elements.append(NoneValue(False))
                break

            if result.should_return():
                # error or 'return' statement
                return result
            assert value is not None

            elements.append(value)

            condition = result.register(self.visit(node.condition_node, ctx, methods_instead_of_funcs))
            if result.should_return():  # check for errors
                return result
            assert condition is not None

            if not condition.is_true():  # the condition isn't true: we break the loop
                break

        return result.success(
            List(elements).set_context(ctx).set_pos(node.pos_start, node.pos_end)
        )

    def visit_FuncDefNode(self, node: FuncDefNode, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit FuncDefNode"""
        result = RTResult()

        func_name = None
        if node.var_name_token is not None:
            func_name = node.var_name_token.value
            assert isinstance(func_name, str)

        body_node = node.body_node
        param_names: list[str] = []
        for param_name in node.param_names_tokens:
            assert isinstance(param_name.value, str)
            param_names.append(param_name.value)

        if not methods_instead_of_funcs:
            func_value = Function(func_name, body_node, param_names, node.should_auto_return).set_context(ctx).set_pos(
                node.pos_start, node.pos_end
            )
        else:
            func_value = Method(func_name, body_node, param_names, node.should_auto_return).set_context(ctx).set_pos(
                node.pos_start, node.pos_end
            )

        if func_name is not None:
            assert ctx.symbol_table is not None
            ctx.symbol_table.set(func_name, func_value)
            self.update_symbol_table(ctx)

        return result.success(func_value)

    def visit_ClassNode(self, node: ClassNode, ctx: Context) -> RTResult:
        """Visit ClassNode"""
        result = RTResult()

        class_name = None
        if node.var_name_token is not None:
            class_name = node.var_name_token.value
            assert isinstance(class_name, str)

        body_node = node.body_node
        parent = None
        if node.parent_var_name_token is not None:
            parent_var_name = node.parent_var_name_token.value
            assert ctx.symbol_table is not None
            assert isinstance(parent_var_name, str)
            if not ctx.symbol_table.exists(parent_var_name):
                assert node.parent_var_name_token.pos_start is not None
                assert node.parent_var_name_token.pos_end is not None
                return self._undefined(
                    node.parent_var_name_token.pos_start,
                    node.parent_var_name_token.pos_end,
                    parent_var_name,
                    ctx, result,
                    f"{_ORIGIN_FILE}.visit_ClassNode"
                )

            parent_value = ctx.symbol_table.get(parent_var_name)
            assert parent_value is not None
            if not isinstance(parent_value, Constructor):
                assert node.parent_var_name_token.pos_start is not None
                assert node.parent_var_name_token.pos_end is not None
                return result.failure(RTTypeError(
                    node.parent_var_name_token.pos_start, node.parent_var_name_token.pos_end,
                    f"expected class constructor, got {parent_value.type_} instead.",
                    ctx,
                    origin_file=f"{_ORIGIN_FILE}.visit_ClassNode"
                ))
            parent = parent_value

        class_ctx = Context(class_name, ctx).set_symbol_table(SymbolTable(ctx.symbol_table))
        assert class_ctx.symbol_table is not None
        result.register(self.visit(body_node, class_ctx, methods_instead_of_funcs=True))
        if result.should_return():
            return result

        class_value = Constructor(class_name, class_ctx.symbol_table, {}, parent).set_context(ctx).set_pos(
            node.pos_start, node.pos_end
        )

        if class_name is not None:
            assert ctx.symbol_table is not None
            ctx.symbol_table.set(class_name, class_value)
            self.update_symbol_table(ctx)

        return result.success(class_value)

    def visit_CallNode(self, node: CallNode, node_to_call_context: Context, outer_context: Context,
                       methods_instead_of_funcs: bool) -> RTResult:
        """Visit CallNode"""
        result = RTResult()

        value_to_call = result.register(self.visit(node.node_to_call, node_to_call_context, methods_instead_of_funcs))
        if result.should_return():  # check for errors
            return result
        assert value_to_call is not None
        # we copy it and set a new pos
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        if isinstance(value_to_call, BaseFunction):  # if the value is a function
            args: list[Value] = []
            call_with_module_context: bool = value_to_call.call_with_module_context
            # call the function
            for arg_node, mul in node.arg_nodes:  # we check the arguments
                if not mul:
                    arg = result.register(self.visit(arg_node, outer_context, methods_instead_of_funcs))
                    if result.should_return():
                        return result
                    assert arg is not None
                    args.append(arg)
                    continue

                list_ = result.register(self.visit(arg_node, outer_context, methods_instead_of_funcs))
                if result.should_return():
                    return result
                assert list_ is not None
                if not isinstance(list_, List):
                    assert list_.pos_start is not None
                    assert list_.pos_end is not None
                    return result.failure(RTTypeError(
                        list_.pos_start, list_.pos_end,
                        f"expected a list value after '*', but got {list_.type_}.",
                        outer_context,
                        origin_file=f"{_ORIGIN_FILE}.visit_CallNode"
                    ))
                args.extend(list_.elements)

            if call_with_module_context:
                use_context = value_to_call.module_context
            elif isinstance(value_to_call, Method):
                use_context = outer_context
                assert outer_context.symbol_table is not None
                assert value_to_call.object_ is not None
                outer_context.symbol_table.set("this", value_to_call.object_)
                if outer_context.parent is not None:
                    outer_context.symbol_table.parent = outer_context.parent.symbol_table
                self.update_symbol_table(outer_context)
            else:
                use_context = None

            if outer_context.parent is None:
                exec_from = f"{outer_context.display_name}"
            else:
                exec_from = f"{outer_context.display_name} from {outer_context.parent.display_name}"

            return_value = result.register(value_to_call.execute(
                args, Interpreter, self.run, self.noug_dir,
                exec_from=exec_from,
                use_context=use_context,
                cli_args=self.args,
                work_dir=self.work_dir
            ))

            if result.should_return():  # check for errors
                return result
            assert return_value is not None

            return_value = return_value.set_pos(node.pos_start, node.pos_end).set_context(outer_context)
            return result.success(return_value)

        elif isinstance(value_to_call, Constructor):  # the value is an object constructor
            if len(node.arg_nodes) != 0:
                assert node.arg_nodes[0][0].pos_start is not None
                assert node.arg_nodes[0][0].pos_end is not None
                return result.failure(RTTypeError(
                    node.arg_nodes[0][0].pos_start, node.arg_nodes[0][0].pos_end,
                    f"instanciation takes no arguments.",
                    outer_context,
                    origin_file=f"{_ORIGIN_FILE}.visit_CallNode"
                ))

            return self._init_constructor(value_to_call, outer_context, result, node)

        elif isinstance(value_to_call, List):  # the value is a list
            # get the element at the given index
            if len(node.arg_nodes) == 0:
                assert node.pos_start is not None
                assert node.pos_end is not None
                return result.failure(RunTimeError(
                    node.pos_start, node.pos_end,
                    f"please give at least one index.",
                    outer_context, origin_file=f"{_ORIGIN_FILE}.visit_CallNode"
                ))

            elif len(node.arg_nodes) == 1:  # there is only one index given
                index = result.register(self.visit(node.arg_nodes[0][0], outer_context, methods_instead_of_funcs))
                if result.should_return():
                    return result
                assert index is not None
                if not (isinstance(index, Number) and isinstance(index.value, int)):
                    assert index.pos_start is not None
                    assert index.pos_end is not None
                    return result.failure(RunTimeError(
                        index.pos_start, index.pos_end,
                        f"indexes must be integers, not {index.type_}.",
                        outer_context, origin_file=f"{_ORIGIN_FILE}.visit_CallNode"
                    ))

                index = index.value
                try:
                    return_value = value_to_call[index].copy().set_pos(node.pos_start, node.pos_end)
                    return result.success(return_value)
                except IndexError:
                    assert node.arg_nodes[0][0].pos_start is not None
                    assert node.arg_nodes[0][0].pos_end is not None
                    return result.failure(RTIndexError(
                        node.arg_nodes[0][0].pos_start, node.arg_nodes[0][0].pos_end,
                        f'list index {index} out of range.',
                        outer_context, f"{_ORIGIN_FILE}.visit_CallNode"
                    ))

            else:  # there is more than one index given
                return_value_list: list[Value] = []
                for arg_node in node.arg_nodes:  # for every index
                    index = result.register(self.visit(arg_node[0], outer_context, methods_instead_of_funcs))
                    if result.should_return():
                        return result
                    assert index is not None
                    if not (isinstance(index, Number) and isinstance(index.value, int)):
                        assert arg_node[0].pos_start is not None
                        assert arg_node[0].pos_end is not None
                        return result.failure(RunTimeError(
                            arg_node[0].pos_start, arg_node[0].pos_end,
                            f"indexes must be integers, not {index.type_}.",
                            outer_context, origin_file=f"{_ORIGIN_FILE}.Visit_CallNode"
                        ))

                    index = index.value
                    try:
                        return_value_list.append(value_to_call[index])
                    except IndexError:
                        assert arg_node[0].pos_start is not None
                        assert arg_node[0].pos_end is not None
                        return result.failure(RTIndexError(
                            arg_node[0].pos_start, arg_node[0].pos_end,
                            f'list index {index} out of range.',
                            outer_context, f"{_ORIGIN_FILE}.Visit_CallNode"
                        ))

                return result.success(
                    List(return_value_list).set_context(outer_context).set_pos(node.pos_start, node.pos_end)
                )

        elif isinstance(value_to_call, String):  # the value is a string
            # get the element at the given index
            if len(node.arg_nodes) == 0:
                assert node.pos_start is not None
                assert node.pos_end is not None
                return result.failure(RunTimeError(
                    node.pos_start, node.pos_end,
                    f"please give at least one index.",
                    outer_context, origin_file=f"{_ORIGIN_FILE}.Visit_CallNode"
                ))
            elif len(node.arg_nodes) == 1:  # there is only one index given
                index = result.register(self.visit(node.arg_nodes[0][0], outer_context, methods_instead_of_funcs))
                if result.should_return():
                    return result
                assert index is not None
                if not (isinstance(index, Number) and isinstance(index.value, int)):
                    assert index.pos_start is not None
                    assert index.pos_end is not None
                    return result.failure(RunTimeError(
                        index.pos_start, index.pos_end,
                        f"indexes must be integers, not {index.type_}.",
                        outer_context, origin_file=f"{_ORIGIN_FILE}.visit_CallNode"
                    ))
                index = index.value
                try:  # we try to return the value at the index
                    return_value = String(value_to_call.value[index]).set_context(outer_context).set_pos(
                        node.pos_start, node.pos_end
                    )
                    return result.success(return_value)
                except IndexError:  # index error
                    assert node.arg_nodes[0][0].pos_start is not None
                    assert node.arg_nodes[0][0].pos_end is not None
                    return result.failure(RTIndexError(
                        node.arg_nodes[0][0].pos_start, node.arg_nodes[0][0].pos_end,
                        f'string index {index} out of range.',
                        outer_context, f"{_ORIGIN_FILE}.visit_CallNode"
                    ))

            else:  # there is more than one index given
                return_value = ""
                for arg_node in node.arg_nodes:  # for every index
                    index = result.register(self.visit(arg_node[0], outer_context, methods_instead_of_funcs))
                    if result.should_return():
                        return result
                    assert index is not None
                    if not (isinstance(index, Number) and isinstance(index.value, int)):
                        assert index.pos_start is not None
                        assert index.pos_end is not None
                        return result.failure(RunTimeError(
                            index.pos_start, index.pos_end,
                            f"indexes must be integers, not {index.type_}.",
                            outer_context, origin_file=f"{_ORIGIN_FILE}.Visit_CallNode"
                        ))

                    index = index.value
                    try:
                        return_value += value_to_call.value[index]
                    except IndexError:
                        assert arg_node[0].pos_start is not None
                        assert arg_node[0].pos_end is not None
                        return result.failure(RTIndexError(
                            arg_node[0].pos_start, arg_node[0].pos_end,
                            f'string index {index} out of range.',
                            outer_context, f"{_ORIGIN_FILE}.Visit_CallNode"
                        ))
                return result.success(
                    String(return_value).set_context(outer_context).set_pos(node.pos_start, node.pos_end)
                )

        else:  # the object is not callable
            assert node.pos_start is not None
            assert node.pos_end is not None
            return result.failure(RunTimeError(
                node.pos_start, node.pos_end,
                f"{value_to_call.type_} is not callable.",
                outer_context, origin_file=f"{_ORIGIN_FILE}.Visit_CallNode"
            ))

    # todo: separate call methods

    def _init_constructor(self, constructor: Constructor, outer_context: Context, result: RTResult, node: Node,
                          object_to_set_this: Object | None = None) -> RTResult:
        """Initialize a constructor. Recursive method."""
        call_with_module_context: bool = constructor.call_with_module_context

        obj_attrs: dict[str, Value] = dict()
        for key in constructor.symbol_table.symbols:
            value = constructor.symbol_table.symbols[key]
            if isinstance(value, List):
                obj_attrs[key] = value.true_copy()
            else:
                obj_attrs[key] = value.copy()
        object_ = Object(obj_attrs, constructor).set_pos(constructor.pos_start, constructor.pos_end)
        object_.type_ = constructor.name
        if call_with_module_context:
            assert constructor.module_context is not None
            inner_ctx = Context(constructor.name, constructor.module_context)
            inner_ctx.symbol_table = SymbolTable(constructor.module_context.symbol_table)
        else:
            inner_ctx = Context(constructor.name, outer_context)
            inner_ctx.symbol_table = SymbolTable(constructor.symbol_table)

        if object_to_set_this is None:
            inner_ctx.symbol_table.set("this", object_)
        else:
            inner_ctx.symbol_table.set("this", object_to_set_this)
        self.update_symbol_table(inner_ctx)
        object_.inner_context = inner_ctx
        for attr in obj_attrs.keys():
            value_to_set_object = obj_attrs[attr]
            if isinstance(value_to_set_object, Method):
                if object_to_set_this is None:
                    value_to_set_object.object_ = object_
                else:
                    value_to_set_object.object_ = object_to_set_this

        if result.should_return():  # check for errors
            return result

        if constructor.parent is not None:
            if object_to_set_this is None:
                parent = result.register(
                    self._init_constructor(constructor.parent, outer_context, result, node, object_)
                )
            else:
                parent = result.register(
                    self._init_constructor(constructor.parent, outer_context, result, node, object_to_set_this)
                )
            if result.should_return():
                return result
            assert parent is not None
            assert isinstance(parent, Object)

            constructor_attrs = constructor.symbol_table.symbols.copy()
            for key in parent.attributes.keys():
                if key in constructor_attrs.keys():
                    new_value = constructor_attrs[key]
                    if isinstance(new_value, Method):
                        new_value.object_ = object_
                    object_.attributes[key] = new_value
                else:
                    object_.attributes[key] = parent.attributes[key]

        return_value = object_.set_pos(node.pos_start, node.pos_end).set_context(outer_context)
        return result.success(return_value)

    def visit_ReturnNode(self, node: ReturnNode, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit ReturnNode"""
        result = RTResult()

        if node.node_to_return is not None:  # 'return foo'
            value = result.register(self.visit(node.node_to_return, ctx, methods_instead_of_funcs))
            if result.should_return():  # check for errors
                return result
            assert value is not None
        else:  # only 'return'
            value = NoneValue(False)

        return result.success_return(value, node.pos_start, node.pos_end)

    @staticmethod
    def visit_ContinueNode(node: ContinueNode) -> RTResult:
        """Visit ContinueNode"""
        return RTResult().success_continue(node.pos_start, node.pos_end)  # set RTResult().loop_should_continue to True

    @staticmethod
    def visit_BreakNode(node: BreakNode) -> RTResult:
        """Visit BreakNode"""
        return RTResult().success_break(node.pos_start, node.pos_end)  # set RTResult().loop_should_continue to True

    def visit_ImportNode(self, node: ImportNode, ctx: Context) -> RTResult:
        """Visit ImportNode"""
        result = RTResult()
        identifiers: list[Token] = node.identifiers  # we get the module identifier token
        is_nougaro_lib = is_python_lib = False
        endswith_slash = self.work_dir.endswith("/") or self.work_dir.endswith("\\")
        if not endswith_slash:
            self.work_dir += "/"
        if self.debug:
            print("==========")
            print("Debug info")
            print("==========")
            print(f"workdir is {self.work_dir}")

        if len(identifiers) != 1:
            path = self.work_dir
            last_i = len(identifiers) - 1
            for i, identifier in enumerate(identifiers):
                should_be_dir = i != last_i

                assert isinstance(identifier.value, str)
                if should_be_dir:
                    if not os.path.isdir(path + identifier.value):
                        assert identifier.pos_start is not None
                        assert identifier.pos_end is not None
                        return result.failure(RTFileNotFoundError(
                            identifier.pos_start, identifier.pos_end, identifier.value, ctx,
                            origin_file=f"{_ORIGIN_FILE}.visit_ImportNode",
                            folder=True
                        ))
                    path += identifier.value + "/"
                    continue

                noug_lib_exists = os.path.exists(path + identifier.value + ".noug")
                if noug_lib_exists:
                    path += identifier.value + ".noug"
                    is_nougaro_lib = True
                else:
                    assert identifier.pos_start is not None
                    assert identifier.pos_end is not None
                    return result.failure(RTFileNotFoundError(
                        identifier.pos_start, identifier.pos_end,
                        f"{identifier.value}.noug",
                        ctx,
                        origin_file=f"{_ORIGIN_FILE}.visit_ImportNode"
                    ))
            name_to_import = identifiers[-1].value
            path = os.path.abspath(path)
        else:
            identifier = identifiers[0]
            name_to_import = identifier.value  # we get the module identifier
            IS_LOCAL_LIB = os.path.exists(self.work_dir + f"{name_to_import}.noug")
            is_nougaro_lib = os.path.exists(os.path.abspath(self.noug_dir + f"/lib_/{name_to_import}.noug"))
            is_python_lib = os.path.exists(os.path.abspath(self.noug_dir + f"/lib_/{name_to_import}_.py"))
            if IS_LOCAL_LIB:
                path = os.path.abspath(self.work_dir + f"{name_to_import}.noug")
                is_nougaro_lib = True
            elif is_nougaro_lib:
                path = os.path.abspath(self.noug_dir + f"/lib_/{name_to_import}.noug")
            elif is_python_lib:
                path = os.path.abspath(self.noug_dir + f"/lib_/{name_to_import}_.py")
            else:
                path = ""
        identifier = identifiers[-1]

        if self.debug:
            print(f"path is {path}")
            print(f"name to import is {name_to_import}")
            print(f"{is_nougaro_lib=}, {is_python_lib=}")
            print("==========")

        as_identifier = node.as_identifier
        if as_identifier is None:
            import_as_name = name_to_import
        else:
            import_as_name = as_identifier.value

        if is_nougaro_lib:
            with open(path) as lib_:
                text = lib_.read()

            value, error, _ = self.run(file_name=f"{name_to_import} (lib)", text=text, noug_dir=self.noug_dir,
                                       exec_from=ctx.display_name, use_default_symbol_table=True, work_dir=self.work_dir)
            if error is not None:
                return result.failure(error)
            if result.should_return():
                return result
            assert value is not None

            assert value.context is not None
            what_to_import = value.context.what_to_export.symbols
        elif is_python_lib:
            try:
                module = importlib.import_module(f"lib_.{name_to_import}_")
                what_to_import = module.WHAT_TO_IMPORT
            except ImportError:
                assert identifier.pos_start is not None
                assert identifier.pos_end is not None
                return result.failure(RTNotDefinedError(
                    identifier.pos_start, identifier.pos_end, f"name '{name_to_import}' is not a module.", ctx,
                    origin_file=f"{_ORIGIN_FILE}.visit_ImportNode\n"
                    "(troubleshooting: is python importlib working?)"
                ))
        else:
            assert identifier.pos_start is not None
            assert identifier.pos_end is not None
            return result.failure(RTNotDefinedError(
                identifier.pos_start, identifier.pos_end, f"name '{name_to_import}' is not a module.", ctx,
                origin_file=f"{_ORIGIN_FILE}.visit_ImportNode\n"
                "(troubleshooting: not involving importlib. Is path detection working?)"
            ))

        assert isinstance(name_to_import, str)
        assert isinstance(import_as_name, str)
        assert ctx.symbol_table is not None
        module_value = Module(name_to_import, what_to_import)
        ctx.symbol_table.set(import_as_name, module_value)
        self.update_symbol_table(ctx)

        return result.success(module_value)

    def visit_ExportNode(self, node: ExportNode, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit ExportNode"""
        result = RTResult()
        expr_or_identifier: Node | Token = node.expr_or_identifier
        is_expr = isinstance(expr_or_identifier, Node)

        if is_expr:
            value_to_export = result.register(
                self.visit(expr_or_identifier, ctx, methods_instead_of_funcs=methods_instead_of_funcs)
            )
            if result.should_return():
                return result
            assert value_to_export is not None
        else:
            assert ctx.symbol_table is not None
            assert isinstance(expr_or_identifier.value, str)
            value_to_export = ctx.symbol_table.get(expr_or_identifier.value)
            assert expr_or_identifier.pos_start is not None
            assert expr_or_identifier.pos_end is not None
            if value_to_export is None:
                return self._undefined(
                    expr_or_identifier.pos_start,
                    expr_or_identifier.pos_end,
                    expr_or_identifier.value,
                    ctx,
                    result,
                    origin_file=f"{_ORIGIN_FILE}.visit_ExportNode"
                )
        if node.as_identifier is None:
            if not is_expr:
                export_as_name = expr_or_identifier.value
            else:
                export_as_name = None
        else:
            export_as_name = node.as_identifier.value

        if export_as_name is None:
            return result.failure(RunTimeError(
                node.pos_start, node.pos_end,
                "expected a name to export.",
                ctx, origin_file=f"{_ORIGIN_FILE}.visit_ExportNode"
            ))

        if isinstance(value_to_export, BaseFunction):
            value_to_export.call_with_module_context = True
            value_to_export.module_context = ctx.copy()
        assert isinstance(export_as_name, str)
        ctx.what_to_export.set(export_as_name, value_to_export)

        return result.success(value_to_export)

    def visit_WriteNode(self, node: WriteNode, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit WriteNode"""
        result = RTResult()

        expr_to_write = node.expr_to_write  # we get the expression to write
        file_name_expr = node.file_name_expr  # we get the file name
        to_token = node.to_token  # we get the 'to' token (>> or !>>)
        line_number = node.line_number  # we get the line number (if no line number is given, line number is 'last')
        if to_token.type == TT["TO"]:  # '>>' is python 'a+' mode
            open_mode = 'a+'
        elif to_token.type == TT["TO_AND_OVERWRITE"]:  # '!>>' is python 'w+' mode
            open_mode = 'w+'
        else:
            open_mode = 'a+'

        str_to_write = result.register(self.visit(expr_to_write, ctx, methods_instead_of_funcs))
        if result.should_return():  # check for errors
            return result
        assert str_to_write is not None
        if not isinstance(str_to_write, String):  # if the str is not a String
            assert str_to_write.pos_start is not None
            assert str_to_write.pos_end is not None
            return result.failure(RTTypeError(
                str_to_write.pos_start, str_to_write.pos_end, f"expected str, got {str_to_write.type_}.", ctx,
                f"{_ORIGIN_FILE}.visit_WriteNode"
            ))

        file_name = result.register(self.visit(file_name_expr, ctx, methods_instead_of_funcs))
        if result.should_return():  # check for errors
            return result
        assert file_name is not None
        if not isinstance(file_name, String):  # if the file name is not a String
            assert file_name.pos_start is not None
            assert file_name.pos_end is not None
            return result.failure(RTTypeError(
                file_name.pos_start, file_name.pos_end, f"expected str, got {file_name.type_}.", ctx,
                f"{_ORIGIN_FILE}.visit_WriteNode"
            ))

        str_to_write_value = str_to_write.value
        file_name_value = file_name.value

        if file_name_value == '<stdout>':  # print in console
            if open_mode == 'w+':  # can not overwrite the console
                clear_screen()
            print(str_to_write_value)
            return result.success(str_to_write)

        try:
            if line_number == 'last':  # if no line number was given
                with open(file_name_value, open_mode, encoding='UTF-8') as file:  # we (over)write our text
                    file.write(str_to_write_value)
            else:  # a line number was given
                assert isinstance(line_number, int)
                file_was_created = False
                if not os.path.exists(file_name_value):  # the file does not exist
                    with open(file_name_value, 'w+', encoding='UTF-8'):  # we create our file
                        file_was_created = True
                with open(file_name_value, 'r+', encoding='UTF-8') as file:  # we read our file
                    file_data = file.readlines()
                if line_number > len(file_data):  # if it exceeds, we add some blank lines
                    with open(file_name_value, 'a+', encoding='UTF-8') as file:  # no matter the open mode
                        # here "int(file_was_created)" is 1 if the file is empty or 0 if the file is not empty.
                        file.write('\n' * (line_number - int(file_was_created) - len(file_data)))
                        file.write(str_to_write_value)
                else:  # if it does not exceed the file length
                    if open_mode == 'a+':  # we add our text to the end of the line
                        if line_number == 0:  # we insert at the top of the file
                            file_data.insert(0, str_to_write_value + '\n')
                        elif line_number > 0:
                            file_data[line_number - 1] = file_data[line_number - 1].replace('\n', '')
                            file_data[line_number - 1] += str_to_write_value + '\n'
                        else:  # line number is negative
                            return result.failure(RTIndexError(
                                node.pos_start, node.pos_end, "line number can not be negative.", ctx,
                                f"{_ORIGIN_FILE}.visit_WriteNode"
                            ))
                    else:  # open_mode == 'w+'
                        if line_number == 0:  # we insert at the top of the file
                            file_data.insert(0, str_to_write_value + '\n')
                        elif line_number > 0:  # we replace the line by the new one
                            file_data[line_number - 1] = str_to_write_value + '\n'
                        else:  # line number is negative
                            return result.failure(RTIndexError(
                                node.pos_start, node.pos_end, "line number can not be negative.", ctx,
                                f"{_ORIGIN_FILE}.visit_WriteNode"
                            ))

                    # we replace our old file by the new one
                    with open(file_name_value, 'w+', encoding='UTF-8') as file:
                        file.writelines(file_data)
        except Exception as e:  # python error
            return result.failure(
                RunTimeError(
                    node.pos_start, node.pos_end,
                    f"unable to write in file '{file_name_value}'. "
                    f"More info: Python{e.__class__.__name__}: {e}",
                    ctx,
                    origin_file=f"{_ORIGIN_FILE}.visit_WriteNode"
                )
            )

        return result.success(str_to_write)

    def visit_ReadNode(self, node: ReadNode, ctx: Context, methods_instead_of_funcs: bool) -> RTResult:
        """Visit ReadNode"""
        result = RTResult()
        file_name_expr = node.file_name_expr  # we get the file name
        identifier = node.identifier  # we get the variable to put the file/line
        line_number = node.line_number  # we get the line number (if the line number is not given, equals to 'all')

        file_name = result.register(self.visit(file_name_expr, ctx, methods_instead_of_funcs))
        if result.error is not None:  # check for errors
            return result
        assert file_name is not None
        if not isinstance(file_name, String):  # check if the str is a String
            assert file_name.pos_start is not None
            assert file_name.pos_end is not None
            return result.failure(RTTypeError(
                file_name.pos_start, file_name.pos_end, f"expected str, got {file_name.type_}.", ctx,
                f"{_ORIGIN_FILE}.visit_ReadNode"
            ))
        file_name_value = file_name.value

        if file_name_value != "<stdin>":
            try:
                if line_number == 'all':  # read all the file
                    with open(file_name_value, 'r+', encoding='UTF-8') as file:
                        file_str = file.read()
                else:  # read a single line
                    assert isinstance(line_number, int)
                    with open(file_name_value, 'r+', encoding='UTF-8') as file:
                        file_data = file.readlines()
                        if 0 < line_number <= len(file_data):  # good index
                            file_str = file_data[line_number - 1]
                        else:  # wrong index
                            return result.failure(RTIndexError(
                                node.pos_start, node.pos_end, f"{line_number}.", ctx,
                                f"{_ORIGIN_FILE}.visit_ReadNode"
                            ))
            except FileNotFoundError:  # file not found
                return result.failure(RTFileNotFoundError(
                    node.pos_start, node.pos_end, file_name_value, ctx,
                    f"{_ORIGIN_FILE}.visit_ReadNode"
                ))
            except Exception as e:  # other python error
                return result.failure(RunTimeError(
                    node.pos_start, node.pos_end,
                    f"unable to read file '{file_name_value}'. "
                    f"More info: Python{e.__class__.__name__}: {e}",
                    ctx, origin_file=f"{_ORIGIN_FILE}.visit_ReadNode"
                ))
        else:
            file_str = input()

        if identifier is not None:  # an identifier is given
            assert ctx.symbol_table is not None
            assert isinstance(identifier.value, str)
            ctx.symbol_table.set(identifier.value, String(file_str))
            self.update_symbol_table(ctx)

        return result.success(String(file_str))

    @staticmethod
    def visit_DollarPrintNode(node: DollarPrintNode, ctx: Context) -> RTResult:
        """Visit DollarPrintNode."""
        result = RTResult()
        assert ctx.symbol_table is not None
        assert isinstance(node.identifier.value, str)
        if node.identifier.value == "":
            print("$")
            value_to_return = String("$").set_pos(node.pos_start, node.pos_end)
        elif ctx.symbol_table.exists(node.identifier.value, True):
            value_to_return = ctx.symbol_table.get(node.identifier.value)
            if value_to_return is not None:
                print(value_to_return.to_python_str())
            else:
                value_to_return = String(str(value_to_return))
                print(str(value_to_return))
        else:
            print(f"${node.identifier.value}")
            value_to_return = String(f"${node.identifier.value}").set_pos(node.pos_start, node.pos_end)

        return result.success(value_to_return)

    @staticmethod
    def visit_NoNode() -> RTResult:
        """There is no node"""
        return RTResult().success(List([NoneValue(False)]))
