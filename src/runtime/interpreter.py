#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.runtime.values.basevalues.basevalues import Number, String, List, NoneValue, Value, Module, Constructor, Object
from src.runtime.values.defined_values.number import FALSE
from src.runtime.values.functions.function import Function
from src.runtime.values.functions.base_function import BaseFunction
from src.constants import PROTECTED_VARS
from src.parser.nodes import *
from src.errors.errors import *
from src.lexer.token_types import TT
from src.runtime.runtime_result import RTResult
from src.runtime.context import Context
from src.misc import CustomInterpreterVisitMethod
from src.runtime.symbol_table import SymbolTable
# built-in python imports
from inspect import signature
import os.path
import importlib
import pprint


# ##########
# INTERPRETER
# ##########
# noinspection PyPep8Naming
class Interpreter:
    def __init__(self, run, noug_dir_):
        self.run = run
        self.noug_dir = noug_dir_

    @staticmethod
    def update_symbol_table(ctx: Context):
        symbols_copy: dict = ctx.symbol_table.symbols.copy()
        if '__symbol_table__' in symbols_copy.keys():
            del symbols_copy['__symbol_table__']
        # print(type(symbols_copy))
        # print(str(symbols_copy))
        ctx.symbol_table.set('__symbol_table__', String(pprint.pformat(symbols_copy)))

    def visit(self, node: Node, ctx: Context, other_ctx: Context = None):
        """Visit a node."""
        method_name = f'visit_{type(node).__name__}'
        method: CustomInterpreterVisitMethod = getattr(self, method_name, self.no_visit_method)
        if other_ctx is None:
            other_ctx = ctx.copy()

        signature_ = signature(method)
        if len(signature_.parameters) <= 1:  # def method(self) is 1 param, def staticmethod() is 0 param
            return method()
        elif len(signature_.parameters) == 3:
            return method(node, ctx, other_ctx)

        return method(node, ctx)

    @staticmethod
    def no_visit_method(node, ctx: Context):
        """The method visit_FooNode (with FooNode given in self.visit) does not exist."""
        print(ctx)
        print(f"NOUGARO INTERNAL ERROR : No visit_{type(node).__name__} method defined in nougaro.Interpreter.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with all informations "
              f"above.")
        raise Exception(f'No visit_{type(node).__name__} method defined in nougaro.Interpreter.')

    @staticmethod
    def visit_NumberNode(node: NumberNode, ctx: Context) -> RTResult:
        """Visit NumberNode."""
        return RTResult().success(Number(node.token.value).set_context(ctx).set_pos(node.pos_start, node.pos_end))

    @staticmethod
    def visit_NumberENumberNode(node: NumberENumberNode, ctx: Context) -> RTResult:
        """Visit NumberENumberNode."""
        value = node.num_token.value * (10 ** node.exponent_token.value)
        if isinstance(value, int) or isinstance(value, float):
            return RTResult().success(Number(value).set_context(ctx).set_pos(node.pos_start, node.pos_end))
        else:
            print(ctx)
            print(f"NOUGARO INTERNAL ERROR : in visit_NumberENumberNode method defined in nougaro.Interpreter,\n"
                  f"{value=}\n"
                  f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with all "
                  f"informations above.")
            raise Exception(f'{value=} in interpreter.Interpreter.visit_NumberENumberNode.')

    @staticmethod
    def visit_StringNode(node: StringNode, ctx: Context) -> RTResult:
        """Visit StringNode"""
        return RTResult().success(
            String(node.token.value).set_context(ctx).set_pos(node.pos_start, node.pos_end)
        )

    def visit_ListNode(self, node: ListNode, ctx: Context) -> RTResult:
        """Visit ListNode"""
        result = RTResult()
        elements = []

        for element_node, mul in node.element_nodes:  # we visit every node from the list
            if mul:
                list_: Value = result.register(self.visit(element_node, ctx))
                if not isinstance(list_, List):
                    return result.failure(
                        RTTypeError(
                            list_.pos_start, list_.pos_end,
                            f"expected a list value after '*', but got '{list_.type_}.",
                            ctx,
                            origin_file="src.interpreter.Interpreter.visit_ListNode"
                        )
                    )
                elements.extend(list_.elements)
            else:
                elements.append(result.register(self.visit(element_node, ctx)))
                if result.should_return():  # if there is an error
                    return result

        return result.success(List(elements).set_context(ctx).set_pos(node.pos_start, node.pos_end))

    def visit_BinOpNode(self, node: BinOpNode, ctx: Context) -> RTResult:
        """Visit BinOpNode"""
        res = RTResult()
        if not isinstance(node.left_node, list):
            left = res.register(self.visit(node.left_node, ctx))  # left term/factor/etc.
            if res.should_return():  # check for errors
                return res
        else:
            value: Value = res.register(self.visit(node.left_node[0], ctx))
            if res.should_return():
                return res
            if len(node.left_node) != 1:
                for node_ in node.left_node[1:]:
                    new_ctx = Context(display_name=value.__repr__())
                    new_ctx.symbol_table = SymbolTable()
                    new_ctx.symbol_table.set_whole_table(value.attributes)
                    if isinstance(node_, VarAccessNode):
                        node_.attr = True
                    attr_ = res.register(self.visit(node_, new_ctx, ctx))
                    if res.should_return():
                        return res
                    value = attr_
            left = value

        if node.op_token.matches(TT["KEYWORD"], 'and') and not left.is_true():
            # operator is "and" and the value is false
            return res.success(FALSE.copy().set_pos(node.pos_start, node.pos_end))

        if not isinstance(node.right_node, list):
            right = res.register(self.visit(node.right_node, ctx))  # right term/factor/etc.
            if res.should_return():  # check for errors
                return res
        else:
            value: Value = res.register(self.visit(node.right_node[0], ctx))
            if res.should_return():
                return res
            if len(node.right_node) != 1:
                for node_ in node.right_node[1:]:
                    new_ctx = Context(display_name=value.__repr__())
                    new_ctx.symbol_table = SymbolTable()
                    new_ctx.symbol_table.set_whole_table(value.attributes)
                    if isinstance(node_, VarAccessNode):
                        node_.attr = True
                    attr_ = res.register(self.visit(node_, new_ctx, ctx))
                    if res.should_return():
                        return res
                    value = attr_
            right = value

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
                  "src.interpreter.Interpreter.visit_BinOpNode because of an invalid token.\n"
                  "Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with the information "
                  "below")
            raise Exception("Result is not defined after executing src.interpreter.Interpreter.visit_BinOpNode")

        if error is not None:  # there is an error
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_BinOpCompNode(self, node: BinOpCompNode, ctx: Context) -> RTResult:
        """Visit BinOpCompNode"""
        res = RTResult()
        nodes_and_tokens_list = node.nodes_and_tokens_list
        if len(nodes_and_tokens_list) == 1:  # there is no comparison
            if not isinstance(nodes_and_tokens_list[0], list):
                return self.visit(nodes_and_tokens_list[0], ctx)
            else:
                value: Value = res.register(self.visit(node.nodes_and_tokens_list[0][0], ctx))
                if res.should_return():
                    return res
                if len(node.nodes_and_tokens_list[0]) != 1:
                    for node_ in node.nodes_and_tokens_list[0][1:]:
                        new_ctx = Context(display_name=value.__repr__())
                        new_ctx.symbol_table = SymbolTable()
                        new_ctx.symbol_table.set_whole_table(value.attributes)
                        if isinstance(node_, VarAccessNode):
                            node_.attr = True
                        attr_ = res.register(self.visit(node_, new_ctx, ctx))
                        if res.should_return():
                            return res
                        value = attr_
                return res.success(value)

        visited_nodes_and_tokens_list = []

        # just list of visited nodes
        for index, element in enumerate(nodes_and_tokens_list):
            if index % 2 == 0:  # we take only nodes and not ops
                if not isinstance(element, list):
                    visited_nodes_and_tokens_list.append(res.register(self.visit(element, ctx)))
                    if res.should_return():
                        return res
                else:
                    value: Value = res.register(self.visit(element[0], ctx))
                    if res.should_return():
                        return res
                    if len(element) != 1:
                        for node_ in element[1:]:
                            new_ctx = Context(display_name=value.__repr__())
                            new_ctx.symbol_table = SymbolTable()
                            new_ctx.symbol_table.set_whole_table(value.attributes)
                            if isinstance(node_, VarAccessNode):
                                node_.attr = True
                            attr_ = res.register(self.visit(node_, new_ctx, ctx))
                            if res.should_return():
                                return res
                            value = attr_
                    visited_nodes_and_tokens_list.append(value)
            else:
                visited_nodes_and_tokens_list.append(element)

        test_result = FALSE.copy()  # FALSE is Nougaro False
        # let's test!
        for index, element in enumerate(visited_nodes_and_tokens_list):
            if index % 2 == 0:  # we take only visited nodes and not ops
                # test
                try:
                    op_token = visited_nodes_and_tokens_list[index + 1]
                    right = visited_nodes_and_tokens_list[index + 2]
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
                        f"NOUGARO INTERNAL ERROR : Result is not defined after executing "
                        f"src.interpreter.Interpreter.visit_BinOpCompNode because of an invalid token.\n"
                        f"Note for devs : the actual invalid token is {op_token.type}:{op_token.value}.\n"
                        f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with the "
                        f"information below")
                    raise Exception("Result is not defined after executing "
                                    "src.interpreter.Interpreter.visit_BinOpCompNode")
                if error is not None:  # there is an error
                    return res.failure(error)
                if test_result.value == FALSE.value:  # the test is false so far: no need to continue
                    return res.success(test_result.set_pos(node.pos_start, node.pos_end))
            else:
                pass
        return res.success(test_result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node: UnaryOpNode, ctx: Context) -> RTResult:
        """Visit UnaryOpNode (-x, not x, ~x)"""
        result = RTResult()
        if isinstance(node.node, list):
            if len(node.node) == 1:
                number = result.register(self.visit(node.node[0], ctx))
            else:
                print(ctx)
                print(
                    f"NOUGARO INTERNAL ERROR : len(node.node) != 1 in src.interpreter.Interpreter.visit_UnaryOpNode.\n"
                    f"{node.node=}\n"
                    f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with the "
                    f"information below.")
                raise Exception("len(node.node) != 1 in src.interpreter.Interpreter.visit_UnaryOpNode.")
        else:
            number = result.register(self.visit(node.node, ctx))
        if result.should_return():
            return result

        error = None

        if node.op_token.type == TT["MINUS"]:
            number, error = number.multiplied_by(Number(-1))  # -x is like x*-1
        elif node.op_token.matches(TT["KEYWORD"], 'not'):
            number, error = number.not_()
        elif node.op_token.type == TT["BITWISENOT"]:
            number, error = number.bitwise_not()

        if error is not None:  # there is an error
            return result.failure(error)
        else:
            return result.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_VarAccessNode(self, node: VarAccessNode, ctx: Context) -> RTResult:
        """Visit VarAccessNode"""
        attribute_error = node.attr
        result = RTResult()
        var_names_list: list[Token | Node] = node.var_name_tokens_list  # there is a list because it can be `a ? b ? c`
        value = None
        var_name = var_names_list[0]  # first we take the first identifier
        for i, var_name in enumerate(var_names_list):  # we check for all the identifiers
            if isinstance(var_name, Token) and var_name.type == TT["IDENTIFIER"]:
                value = ctx.symbol_table.get(var_name.value)  # we get the value of the variable
                if value is not None:  # if the variable is defined, we can stop here
                    break
            else:
                var_name: Node
                value = result.register(self.visit(var_name, ctx))  # here var_name is an expr
                if not result.should_return():
                    break

        if value is None:  # the variable is not defined
            if len(var_names_list) == 1:
                if (var_name.value == "eexit" or var_name.value == "exxit" or var_name.value == "exiit" or
                        var_name.value == "exitt") and 'exit' in ctx.symbol_table.symbols.keys():
                    # my keyboard is sh*tty, so sometimes it types a letter twice...
                    if not attribute_error:
                        return result.failure(
                            RTNotDefinedError(
                                node.pos_start, node.pos_end,
                                f"name '{var_name.value}' is not defined. Did you mean 'exit'?",
                                ctx, "src.interpreter.Interpreter.visit_varAccessNode"
                            )
                        )
                    else:
                        return result.failure(
                            RTAttributeError(
                                node.pos_start, node.pos_end, ctx.display_name, var_name.value, ctx,
                                "src.interpreter.Interpreter.visit_varAccessNode"
                            )
                        )
                else:
                    if ctx.symbol_table.exists(f'__{var_name.value}__'):
                        # e.g. the user typed symbol_table instead of __symbol_table__
                        if not attribute_error:
                            return result.failure(
                                RTNotDefinedError(
                                    node.pos_start, node.pos_end,
                                    f"name '{var_name.value}' is not defined. Did you mean '__{var_name.value}__'?",
                                    ctx, "src.interpreter.Interpreter.visit_varAccessNode"
                                )
                            )
                        else:
                            return result.failure(
                                RTAttributeError(
                                    node.pos_start, node.pos_end, ctx.display_name, var_name.value, ctx,
                                    "src.interpreter.Interpreter.visit_varAccessNode"
                                )
                            )
                    else:  # not defined at all
                        if not attribute_error:
                            return result.failure(
                                RTNotDefinedError(
                                    node.pos_start, node.pos_end, f"name '{var_name.value}' is not defined.", ctx,
                                    "src.interpreter.Interpreter.visit_varAccessNode"
                                )
                            )
                        else:
                            return result.failure(
                                RTAttributeError(
                                    node.pos_start, node.pos_end, ctx.display_name, var_name.value, ctx,
                                    "src.interpreter.Interpreter.visit_varAccessNode"
                                )
                            )
            else:  # none of the identifiers is defined
                if not attribute_error:
                    return result.failure(
                        RTNotDefinedError(
                            node.pos_start, node.pos_end, f"none of the given identifiers is defined.", ctx,
                            "src.interpreter.Interpreter.visit_varAccessNode"
                        )
                    )
                else:
                    return result.failure(
                        RTAttributeError(
                            node.pos_start, node.pos_end, ctx.display_name, var_name.value, ctx,
                            "src.interpreter.Interpreter.visit_varAccessNode"
                        )
                    )

        # we get the value
        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(ctx)
        return result.success(value)

    def visit_VarAssignNode(self, node: VarAssignNode, ctx: Context) -> RTResult:
        """Visit VarAssignNode"""
        result = RTResult()
        var_names = [tok.value for tok in node.var_name_tokens]  # we get the names of the vars to modify / create
        values = [result.register(self.visit(node, ctx)) for node in node.value_nodes]  # we get the values
        equal = node.equal.type  # we get the equal type
        if result.should_return() or result.old_should_return:  # check for errors
            return result

        if len(var_names) != len(values):
            return result.failure(
                RunTimeError(
                    node.pos_start, node.pos_end, f"there should be the same amount of identifiers and values. "
                                                  f"There is {len(var_names)} identifiers and {len(values)} values.",
                    ctx, origin_file="src.interpreter.Interpreter.visit_VarAssignNode"
                )
            )

        final_values = []
        # print(len(final_values))
        # print(final_values)
        for i, var_name in enumerate(var_names):
            if var_name not in PROTECTED_VARS:  # this constant is the list of all var names you can't modify
                #                                 (unless you want to break nougaro)
                if equal == TT["EQ"]:  # just a regular equal, we can modify/create the variable in the symbol table
                    ctx.symbol_table.set(var_name, values[i])
                    final_value = values[i]  # we want to return the new value of the variable
                else:
                    if var_name in ctx.symbol_table.symbols:  # edit a variable
                        var_actual_value: Value = ctx.symbol_table.get(var_name)  # actual value of the variable
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
                            print(f"Note: it was a problem in src.interpreter.Interpreter.visit_VarAssignNode. Please"
                                  f" report this error at https://jd-develop.github.io/nougaro/bugreport.html with all"
                                  f" infos.\n"
                                  f"For the dev: equal token '{equal}' is in EQUALS but not planned in "
                                  f"visit_VarAssignNode")
                            error = None
                            final_value = values[i]

                        if error is not None:  # there is an error
                            error.set_pos(node.pos_start, node.pos_end)
                            return result.failure(error)
                        ctx.symbol_table.set(var_name, final_value)  # we can edit the variable. We will return
                        #                                              final_value
                    else:
                        if ctx.symbol_table.exists(f'__{var_name}__'):
                            # e.g. user entered `var foo += 1` instead of `var __foo__ += 1`
                            return result.failure(
                                RTNotDefinedError(
                                    node.pos_start, node.pos_end, f"name '{var_name}' is not defined yet. "
                                                                  f"Did you mean '__{var_name}__'?", ctx,
                                    "src.interpreter.Interpreter.visit_VarAssignNode"
                                )
                            )
                        else:
                            return result.failure(
                                RTNotDefinedError(
                                    node.pos_start, node.pos_end, f"name '{var_name}' is not defined yet.", ctx,
                                    "src.interpreter.Interpreter.visit_VarAssignNode"
                                )
                            )
            else:  # protected variable name
                return result.failure(RunTimeError(node.pos_start, node.pos_end,
                                                   f"can not create or edit a variable with builtin name '{var_name}'.",
                                                   ctx, origin_file="src.interpreter.Interpreter.visit_VarAssignNode"))
            final_values.append(final_value)

        self.update_symbol_table(ctx)
        return result.success(
            List(final_values).set_pos(node.pos_start, node.pos_end) if len(final_values) != 1 else final_values[0]
        )  # we return the (new) value(s) of the variable(s).

    def visit_VarDeleteNode(self, node: VarDeleteNode, ctx: Context) -> RTResult:
        """Visit VarDeleteNode"""
        result = RTResult()
        var_name = node.var_name_token.value  # we get the var name

        if var_name not in ctx.symbol_table.symbols:  # the variable is not defined thus we can't delete it
            return result.failure(RTNotDefinedError(node.pos_start, node.pos_end, f"name '{var_name}' is not defined.",
                                                    ctx, "src.interpreter.Interpreter.visit_VarDeleteNode"))

        if var_name not in PROTECTED_VARS:  # the variable isn't protected, we can safely delete it
            ctx.symbol_table.remove(var_name)
        else:  # the variable is protected
            return result.failure(RunTimeError(node.pos_start, node.pos_end,
                                               f"can not delete value assigned to builtin name '{var_name}'.",
                                               ctx, origin_file="src.interpreter.Interpreter.visit_VarDeleteNode"))

        self.update_symbol_table(ctx)
        return result.success(NoneValue(False))

    def visit_IfNode(self, node: IfNode, ctx: Context) -> RTResult:
        """Visit IfNode"""
        result = RTResult()
        for condition, expr in node.cases:  # all the possible cases
            condition_value = result.register(self.visit(condition, ctx))  # we register the condition
            if result.should_return():  # check for errors
                return result

            if condition_value.is_true():  # if it is true: we execute the body code then we return the value
                expr_value = result.register(self.visit(expr, ctx))
                if result.should_return():  # check for errors
                    return result
                return result.success(expr_value)

        if node.else_case is not None:  # if none of the if elif cases are true, we check for an else case
            expr = node.else_case
            else_value = result.register(self.visit(expr, ctx))
            if result.should_return():  # check for errors
                return result
            return result.success(else_value)

        return result.success(NoneValue(False))

    def visit_AssertNode(self, node: AssertNode, ctx: Context) -> RTResult:
        """Visit AssertNode"""
        result = RTResult()
        assertion = result.register(self.visit(node.assertion, ctx))  # we get the assertion
        if result.should_return():  # check for errors
            return result
        errmsg = result.register(self.visit(node.errmsg, ctx))  # we get the error message
        if result.should_return():  # check for errors
            return result

        assert True  # Yup, you've just found an Easter Egg ;)

        if not isinstance(errmsg, String):  # we check if the error message is a String
            return result.failure(RTTypeError(
                errmsg.pos_start, errmsg.pos_end,
                f"error message should be a str, not {errmsg.type_}.",
                ctx, "src.interpreter.Interpreter.visit_Assert_Node"
            ))

        if not assertion.is_true():  # the assertion is not true, we return an error
            return result.failure(RTAssertionError(
                assertion.pos_start, assertion.pos_end,
                errmsg.value,
                ctx, "src.interpreter.Interpreter.visit_AssertNode"
            ))

        return result.success(NoneValue(False))

    def visit_ForNode(self, node: ForNode, ctx: Context) -> RTResult:
        """Visit ForNode"""
        result = RTResult()
        elements = []

        start_value = result.register(self.visit(node.start_value_node, ctx))  # we get the start value
        if result.should_return():  # check for errors
            return result

        end_value = result.register(self.visit(node.end_value_node, ctx))  # we get the end value
        if result.should_return():  # check for errors
            return result

        if node.step_value_node is not None:  # we get the step value, if there is one
            step_value = result.register(self.visit(node.step_value_node, ctx))
            if result.should_return():  # check for errors
                return result
        else:
            step_value = Number(1)  # no step value: default is 1

        # we make an end condition
        # if step value >= 0, the end value is more than the initial value
        # if step value < 0, the end value is less than the initial value
        i = start_value.value
        condition = (lambda: i < end_value.value) if step_value.value >= 0 else (lambda: i > end_value.value)

        while condition():
            ctx.symbol_table.set(node.var_name_token.value, Number(i))  # we set the iterating variable
            self.update_symbol_table(ctx)
            i += step_value.value  # we add up the step value to the iterating variable

            value = result.register(self.visit(node.body_node, ctx))  # we execute code in the body node
            if result.should_return() and not result.loop_should_break and not result.loop_should_continue:
                # if there is an error or a 'return' statement
                return result

            if result.loop_should_continue:
                continue  # will continue the 'while condition()' -> the interpreted 'for' loop is continued ^^

            if result.loop_should_break:
                break  # will break the 'while condition()' -> the interpreted 'for' loop is break

            elements.append(value)

        return result.success(
            List(elements).set_context(ctx).set_pos(node.pos_start, node.pos_end)
        )

    def visit_ForNodeList(self, node: ForNodeList, ctx: Context) -> RTResult:
        """Visit ForNodeList"""
        result = RTResult()
        elements = []

        iterable_ = result.register(self.visit(node.list_node, ctx))  # we get the list
        if result.should_return():  # check for errors
            return result

        if isinstance(iterable_, List):  # if the list is really a list
            for e in iterable_.elements:
                # we set the in-game... wait, the in-code 'e' variable to the actual list element
                ctx.symbol_table.set(node.var_name_token.value, e)
                self.update_symbol_table(ctx)
                value = result.register(self.visit(node.body_node, ctx))  # we execute the body node
                if result.should_return() and not result.loop_should_break and not result.loop_should_continue:
                    # error or 'return' statement
                    return result

                if result.loop_should_continue:
                    continue  # will continue the 'for e in iterable_.elements' -> the interpreted 'for' loop is
                    #           continued

                if result.loop_should_break:
                    break  # will break the 'for e in iterable_.elements' -> the interpreted 'for' loop is break

                elements.append(value)

            return result.success(
                List(elements).set_context(ctx).set_pos(node.pos_start, node.pos_end)
            )
        elif isinstance(iterable_, String):
            for e in iterable_.to_str():
                # we set the in-game... wait, the in-code 'e' variable to the actual str char
                ctx.symbol_table.set(node.var_name_token.value, String(e))
                self.update_symbol_table(ctx)
                value = result.register(self.visit(node.body_node, ctx))  # we execute the body node
                if result.should_return() and not result.loop_should_break and not result.loop_should_continue:
                    # error or 'return' statement
                    return result

                if result.loop_should_continue:
                    continue  # will continue the 'for e in iterable_.to_str()' -> the interpreted 'for' loop is
                    #           continued

                if result.loop_should_break:
                    break  # will break the 'for e in iterable_.to_str()' -> the interpreted 'for' loop is break

                elements.append(value)

            return result.success(
                List(elements).set_context(ctx).set_pos(node.pos_start, node.pos_end)
            )
        else:  # this is not a list nor a str
            return result.failure(
                RTTypeError(node.list_node.pos_start, node.list_node.pos_end,
                            f"expected a list or a str after 'in', but found {iterable_.type_}.",
                            ctx, "src.interpreter.Interpreter.visit_ForNodeList")
            )

    def visit_WhileNode(self, node: WhileNode, ctx: Context) -> RTResult:
        """Visit WhileNode"""
        result = RTResult()
        elements = []

        while True:  # we will break when it's finished ;)
            condition = result.register(self.visit(node.condition_node, ctx))  # we get the condition
            if result.should_return():  # check for errors
                return result

            if not condition.is_true():  # the condition isn't true : we break our 'while True'
                break

            value = result.register(self.visit(node.body_node, ctx))  # we execute the body node
            if result.should_return() and not result.loop_should_break and not result.loop_should_continue:
                # error or 'return' statement
                return result

            if result.loop_should_continue:
                continue  # will continue the 'while True' -> the interpreted 'while' loop is continued

            if result.loop_should_break:
                break  # will break the 'while True' -> the interpreted 'while' loop is break

            elements.append(value)

        return result.success(
            List(elements).set_context(ctx).set_pos(node.pos_start, node.pos_end)
        )

    def visit_DoWhileNode(self, node: DoWhileNode, ctx: Context) -> RTResult:
        """Visit DoWhileNode"""
        result = RTResult()
        elements = []

        value = result.register(self.visit(node.body_node, ctx))  # we execute the body node for a first time
        if result.should_return() and not result.loop_should_break and not result.loop_should_continue:
            # error or 'return' statement
            return result

        if not result.loop_should_continue:
            # if there is a 'continue', we don't want the value to be returned
            elements.append(value)

        if not result.loop_should_break:  # if the loop has break, we no longer want to execute that
            while True:
                condition = result.register(self.visit(node.condition_node, ctx))  # we get the condition
                if result.should_return():  # check for errors
                    return result

                if not condition.is_true():  # the condition isn't true: we break the loop
                    break

                value = result.register(self.visit(node.body_node, ctx))  # we execute the body node
                if result.should_return() and not result.loop_should_break and not result.loop_should_continue:
                    # error or 'return' statement
                    return result

                if result.loop_should_continue:
                    continue  # will continue the 'while True' -> the interpreted 'while' loop is continued

                if result.loop_should_break:
                    break  # will break the 'while True' -> the interpreted 'while' loop is break

                elements.append(value)

        return result.success(
            List(elements).set_context(ctx).set_pos(node.pos_start, node.pos_end)
        )

    def visit_FuncDefNode(self, node: FuncDefNode, ctx: Context) -> RTResult:
        """Visit FuncDefNode"""
        result = RTResult()
        # if there is no name given -> None
        func_name = node.var_name_token.value if node.var_name_token is not None else None
        body_node = node.body_node
        param_names = [param_name.value for param_name in node.param_names_tokens]
        func_value = Function(func_name, body_node, param_names, node.should_auto_return).set_context(ctx).set_pos(
            node.pos_start, node.pos_end
        )  # we already create the Function value, but we'll maybe not return it

        if node.var_name_token is not None:  # the function have a name
            if func_name not in PROTECTED_VARS:  # if the name isn't protected, we can set it in the symbol table
                ctx.symbol_table.set(func_name, func_value)
                self.update_symbol_table(ctx)
            else:  # the name is protected
                return result.failure(RunTimeError(node.pos_start, node.pos_end,
                                                   f"can not create a function with builtin name '{func_name}'.",
                                                   ctx, origin_file="src.interpreter.Interpreter.visit_FuncDefNode"))

        return result.success(func_value)  # we return our Function value

    def visit_ClassNode(self, node: ClassNode, ctx: Context) -> RTResult:
        """Visit ClassNode"""
        result = RTResult()
        # if there is no name given -> None
        class_name = node.var_name_token.value if node.var_name_token is not None else None
        body_node = node.body_node
        parent_var_name = node.parent_var_name_token.value if node.parent_var_name_token is not None else None
        if parent_var_name is not None:
            if not ctx.symbol_table.exists(parent_var_name):
                return result.failure(
                    RTNotDefinedError(
                        node.parent_var_name_token.pos_start, node.parent_var_name_token.pos_end,
                        f"name {parent_var_name} is not defined.",
                        ctx,
                        origin_file="src.runtime.interpreter.visit_ClassNode"
                    )
                )
            else:
                parent_value: Value = ctx.symbol_table.get(parent_var_name)
                if isinstance(parent_value, Constructor):
                    parent = parent_value
                else:
                    return result.failure(
                        RTTypeError(
                            node.parent_var_name_token.pos_start, node.parent_var_name_token.pos_end,
                            f"expected class, got {parent_value.type_} instead.",
                            ctx,
                            origin_file="src.runtime.interpreter.visit_ClassNode"
                        )
                    )
        else:
            parent = None
        class_value = Constructor(class_name, body_node, {}, parent).set_context(ctx).set_pos(
            node.pos_start, node.pos_end
        )  # we already create the Class value, but we'll maybe not return it

        if node.var_name_token is not None:  # the function have a name
            if class_name not in PROTECTED_VARS:  # if the name isn't protected, we can set it in the symbol table
                ctx.symbol_table.set(class_name, class_value)
                self.update_symbol_table(ctx)
            else:  # the name is protected
                return result.failure(RunTimeError(node.pos_start, node.pos_end,
                                                   f"can not create a function with builtin name '{class_name}'.",
                                                   ctx, origin_file="src.interpreter.Interpreter.visit_ClassNode"))

        return result.success(class_value)  # we return our Function value

    def visit_CallNode(self, node: CallNode, node_to_call_context: Context, outer_context: Context) -> RTResult:
        """Visit CallNode"""
        result = RTResult()

        value_to_call = result.register(self.visit(node.node_to_call, node_to_call_context))  # we get the value to call
        if result.should_return():  # check for errors
            return result
        # we copy it and set a new pos
        value_to_call: Value = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        if isinstance(value_to_call, BaseFunction):  # if the value is a function
            args = []
            call_with_module_context: bool = value_to_call.call_with_module_context
            # call the function
            for arg_node, mul in node.arg_nodes:  # we check the arguments
                if not mul:
                    args.append(result.register(self.visit(arg_node, outer_context)))
                    if result.should_return():  # check for errors
                        return result
                else:
                    list_: Value = result.register(self.visit(arg_node, outer_context))
                    if not isinstance(list_, List):
                        return result.failure(
                            RTTypeError(
                                list_.pos_start, list_.pos_end,
                                f"expected a list value after '*', but got '{list_.type_}.",
                                outer_context,
                                origin_file="src.interpreter.Interpreter.visit_CallNode"
                            )
                        )
                    args.extend(list_.elements)

            if call_with_module_context:
                if outer_context.parent is None:
                    return_value = result.register(value_to_call.execute(
                        args, Interpreter, self.run, self.noug_dir, exec_from=f"{outer_context.display_name}",
                        use_context=value_to_call.module_context))
                else:
                    return_value = result.register(value_to_call.execute(
                        args, Interpreter, self.run, self.noug_dir, exec_from=f"{outer_context.display_name} from "
                                                                              f"{outer_context.parent.display_name}",
                        use_context=value_to_call.module_context))
            else:
                if outer_context.parent is None:
                    return_value = result.register(value_to_call.execute(
                        args, Interpreter, self.run, self.noug_dir, exec_from=f"{outer_context.display_name}"))
                else:
                    return_value = result.register(value_to_call.execute(
                        args, Interpreter, self.run, self.noug_dir, exec_from=f"{outer_context.display_name} from "
                                                                              f"{outer_context.parent.display_name}"))

            if result.should_return():  # check for errors
                return result

            return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(outer_context)
            return result.success(return_value)

        elif isinstance(value_to_call, Constructor):  # the value is an object constructor
            args = []
            call_with_module_context: bool = value_to_call.call_with_module_context
            # call the function
            for arg_node, mul in node.arg_nodes:  # we check the arguments
                if not mul:
                    args.append(result.register(self.visit(arg_node, outer_context)))
                    if result.should_return():  # check for errors
                        return result
                else:
                    list_: Value = result.register(self.visit(arg_node, outer_context))
                    if not isinstance(list_, List):
                        return result.failure(
                            RTTypeError(
                                list_.pos_start, list_.pos_end,
                                f"expected a list value after '*', but got '{list_.type_}.",
                                outer_context,
                                origin_file="src.interpreter.Interpreter.visit_CallNode"
                            )
                        )
                    args.extend(list_.elements)

            object_ = Object({"__constructor__": value_to_call})
            if call_with_module_context:
                inner_ctx = Context(value_to_call.name, value_to_call.module_context)
                inner_ctx.symbol_table = SymbolTable(value_to_call.module_context.symbol_table)
            else:
                inner_ctx = Context(value_to_call.name, outer_context)
                inner_ctx.symbol_table = SymbolTable(outer_context.symbol_table)

            inner_ctx.symbol_table.set("this", object_)
            self.update_symbol_table(inner_ctx)
            body = result.register(self.visit(value_to_call.body_node, inner_ctx))
            # todo: faire en sorte que les différentes valeurs définies dans la classe soient attributs de l'objet

            if result.should_return():  # check for errors
                return result

            return_value = object_.set_pos(node.pos_start, node.pos_end).set_context(outer_context)
            return result.success(return_value)

        elif isinstance(value_to_call, List):  # the value is a list
            # get the element at the given index
            if len(node.arg_nodes) == 1:  # there is only one index given
                index = result.register(self.visit(node.arg_nodes[0][0], outer_context))
                if isinstance(index, Number):  # the index should be a number
                    index = index.value
                    try:  # we try to return the value at the index
                        return_value = value_to_call[index]
                        return result.success(return_value)
                    except Exception:  # index error
                        return result.failure(
                            RTIndexError(
                                node.arg_nodes[0][0].pos_start, node.arg_nodes[0][0].pos_end,
                                f'list index {index} out of range.',
                                outer_context, "src.interpreter.Interpreter.visit_CallNode"
                            )
                        )
                else:  # the index is not a number
                    return result.failure(RunTimeError(
                        node.pos_start, node.pos_end,
                        f"indexes must be integers, not {index.type_}.",
                        outer_context, origin_file="src.interpreter.Interpreter.visit_CallNode"
                    ))
            elif len(node.arg_nodes) > 1:  # there is more than one index given
                return_value = []
                for arg_node in node.arg_nodes:  # for every index
                    index = result.register(self.visit(arg_node[0], outer_context))
                    if isinstance(index, Number):  # the index should be a number
                        index = index.value
                        try:  # we try to return the value at the given index
                            return_value.append(value_to_call[index])
                        except Exception:  # index error
                            return result.failure(
                                RTIndexError(
                                    arg_node[0].pos_start, arg_node[0].pos_end,
                                    f'list index {index} out of range.',
                                    outer_context, "src.interpreter.Interpreter.Visit_CallNode"
                                )
                            )
                    else:  # the index is not a number
                        return result.failure(RunTimeError(
                            arg_node[0].pos_start, arg_node[0].pos_end,
                            f"indexes must be integers, not {index.type_}.",
                            outer_context, origin_file="src.interpreter.Interpreter.Visit_CallNode"
                        ))
                return result.success(
                    List(return_value).set_context(outer_context).set_pos(node.pos_start, node.pos_end)
                )
            else:  # there is no index given
                return result.failure(RunTimeError(
                    node.pos_start, node.pos_end,
                    f"please give at least one index.",
                    outer_context, origin_file="src.interpreter.Interpreter.Visit_CallNode"
                ))

        elif isinstance(value_to_call, String):  # the value is a string
            # get the element at the given index
            if len(node.arg_nodes) == 1:  # there is only one index given
                index = result.register(self.visit(node.arg_nodes[0][0], outer_context))
                if isinstance(index, Number):  # the index should be a number
                    index = index.value
                    try:  # we try to return the value at the index
                        return_value = String(value_to_call.value[index]).set_context(outer_context).set_pos(
                            node.pos_start, node.pos_end
                        )
                        return result.success(return_value)
                    except Exception:  # index error
                        return result.failure(
                            RTIndexError(
                                node.arg_nodes[0][0].pos_start, node.arg_nodes[0][0].pos_end,
                                f'string index {index} out of range.',
                                outer_context, "src.interpreter.Interpreter.visit_CallNode"
                            )
                        )
                else:  # the index is not a number
                    return result.failure(RunTimeError(
                        node.pos_start, node.pos_end,
                        f"indexes must be integers, not {index.type_}.",
                        outer_context, origin_file="src.interpreter.Interpreter.visit_CallNode"
                    ))
            elif len(node.arg_nodes) > 1:  # there is more than one index given
                return_value = ""
                for arg_node in node.arg_nodes:  # for every index
                    index = result.register(self.visit(arg_node[0], outer_context))
                    if isinstance(index, Number):  # the index should be a number
                        index = index.value
                        try:  # we try to return the value at the given index
                            return_value += value_to_call.value[index]
                        except Exception:  # index error
                            return result.failure(
                                RTIndexError(
                                    arg_node[0].pos_start, arg_node[0].pos_end,
                                    f'string index {index} out of range.',
                                    outer_context, "src.interpreter.Interpreter.Visit_CallNode"
                                )
                            )
                    else:  # the index is not a number
                        return result.failure(RunTimeError(
                            arg_node[0].pos_start, arg_node[0].pos_end,
                            f"indexes must be integers, not {index.type_}.",
                            outer_context, origin_file="src.interpreter.Interpreter.Visit_CallNode"
                        ))
                return result.success(
                    String(return_value).set_context(outer_context).set_pos(node.pos_start, node.pos_end)
                )
            else:  # there is no index given
                return result.failure(RunTimeError(
                    node.pos_start, node.pos_end,
                    f"please give at least one index.",
                    outer_context, origin_file="src.interpreter.Interpreter.Visit_CallNode"
                ))
        else:  # the object is not callable
            return result.failure(RunTimeError(
                node.pos_start, node.pos_end,
                f"{value_to_call.type_} is not callable.",
                outer_context, origin_file="src.interpreter.Interpreter.Visit_CallNode"
            ))

    def visit_ReturnNode(self, node: ReturnNode, ctx: Context) -> RTResult:
        """Visit ReturnNode"""
        result = RTResult()

        if node.node_to_return is not None:  # 'return foo'
            value = result.register(self.visit(node.node_to_return, ctx))  # we get the value (foo)
            if result.should_return():  # check for errors
                return result
        else:  # only 'return'
            value = NoneValue(False)

        return result.success_return(value)

    @staticmethod
    def visit_ContinueNode() -> RTResult:
        """Visit ContinueNode"""
        return RTResult().success_continue()  # set RTResult().loop_should_continue to True

    @staticmethod
    def visit_BreakNode() -> RTResult:
        """Visit BreakNode"""
        return RTResult().success_break()  # set RTResult().loop_should_continue to True

    def visit_ImportNode(self, node: ImportNode, ctx: Context) -> RTResult:
        """Visit ImportNode"""
        result = RTResult()
        identifier: Token = node.identifier  # we get the module identifier token
        name_to_import = identifier.value  # we get the module identifier

        if os.path.exists(os.path.abspath(self.noug_dir + f"/lib_/{name_to_import}.noug")):
            with open(os.path.abspath(self.noug_dir + f"/lib_/{name_to_import}.noug")) as lib_:
                text = lib_.read()

            value, error = self.run(file_name=f"{name_to_import} (lib)", text=text, noug_dir=self.noug_dir,
                                    exec_from=ctx.display_name, use_default_symbol_table=True)
            value: Value
            if error is not None:
                return result.failure(error)
            if result.should_return():
                return result

            what_to_import = value.context.what_to_export.symbols
        else:
            try:
                module = importlib.import_module(f"lib_.{name_to_import}_")
                what_to_import = module.WHAT_TO_IMPORT
            except ImportError:
                return result.failure(
                    RTNotDefinedError(
                        identifier.pos_start, identifier.pos_end, f"name '{name_to_import}' is not a module.", ctx,
                        "src.interpreter.Interpreter.visit_ImportNode\n"
                        "(troubleshooting: do python importlib is working?)"
                    )
                )

        module_value = Module(name_to_import, what_to_import)
        ctx.symbol_table.set(name_to_import, module_value)
        self.update_symbol_table(ctx)

        return result.success(module_value)

    @staticmethod
    def visit_ExportNode(node: ExportNode, ctx: Context) -> RTResult:
        """Visit ExportNode"""
        identifier: Token = node.identifier
        name_to_export = identifier.value
        value_to_export = ctx.symbol_table.get(name_to_export)
        if value_to_export is None:
            return RTResult().failure(
                RTNotDefinedError(
                    identifier.pos_start, identifier.pos_end, f"name '{name_to_export}' is not defined.", ctx,
                    "src.interpreter.Interpreter.visit_ExportNode"
                )
            )
        if isinstance(value_to_export, BaseFunction):
            value_to_export.call_with_module_context = True
            value_to_export.module_context = ctx.copy()
            ctx.what_to_export.set(name_to_export, value_to_export)
        else:
            ctx.what_to_export.set(name_to_export, value_to_export)

        return RTResult().success(NoneValue(False))

    def visit_WriteNode(self, node: WriteNode, ctx: Context) -> RTResult:
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

        str_to_write = result.register(self.visit(expr_to_write, ctx))  # we get the str to write
        if result.should_return():  # check for errors
            return result
        if not isinstance(str_to_write, String):  # if the str is not a String
            return result.failure(
                RTTypeError(
                    str_to_write.pos_start, str_to_write.pos_end, f"expected str, got {str_to_write.type_}.", ctx,
                    "src.interpreter.Interpreter.visit_WriteNode"
                )
            )

        file_name = result.register(self.visit(file_name_expr, ctx))  # we get the str of the file name
        if result.should_return():  # check for errors
            return result
        if not isinstance(file_name, String):  # if the file name is not a String
            return result.failure(
                RTTypeError(
                    file_name.pos_start, file_name.pos_end, f"expected str, got {file_name.type_}.", ctx,
                    "src.interpreter.Interpreter.visit_WriteNode"
                )
            )

        str_to_write_value = str_to_write.value
        file_name_value = file_name.value

        if file_name_value == '<stdout>':  # print in console
            if open_mode == 'w+':  # can not overwrite the console
                return result.failure(
                    RunTimeError(
                        node.pos_start, node.pos_end, f"can not overwrite <stdout>.", ctx,
                        origin_file="src.interpreter.Interpreter.visit_WriteNode"
                    )
                )
            print(str_to_write_value)
            return result.success(str_to_write)

        try:
            if line_number == 'last':  # if no line number was given
                with open(file_name_value, open_mode, encoding='UTF-8') as file:  # we (over)write our text
                    file.write(str_to_write_value)
            else:  # a line number was given
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
                            return result.failure(
                                RTIndexError(
                                    node.pos_start, node.pos_end, "line number can not be negative.", ctx,
                                    "src.interpreter.Interpreter.visit_WriteNode"
                                )
                            )
                    else:  # open_mode == 'w+'
                        if line_number == 0:  # we insert at the top of the file
                            file_data.insert(0, str_to_write_value + '\n')
                        elif line_number > 0:  # we replace the line by the new one
                            file_data[line_number - 1] = str_to_write_value + '\n'
                        else:  # line number is negative
                            return result.failure(
                                RTIndexError(
                                    node.pos_start, node.pos_end, "line number can not be negative.", ctx,
                                    "src.interpreter.Interpreter.visit_WriteNode"
                                )
                            )

                    # we replace our old file by the new one
                    with open(file_name_value, 'w+', encoding='UTF-8') as file:
                        file.writelines(file_data)
        except Exception as e:  # python error
            return result.failure(
                RunTimeError(
                    node.pos_start, node.pos_end, f"unable to write in file '{file_name_value}'. "
                                                  f"More info : Python{e.__class__.__name__}: {e}", ctx,
                    origin_file="src.interpreter.Interpreter.visit_WriteNode"
                )
            )

        return result.success(str_to_write)

    def visit_ReadNode(self, node: ReadNode, ctx: Context) -> RTResult:
        """Visit ReadNode"""
        result = RTResult()
        file_name_expr = node.file_name_expr  # we get the file name
        identifier = node.identifier  # we get the variable to put the file/line
        line_number = node.line_number  # we get the line number (if the line number is not given, equals to 'all')

        file_name = result.register(self.visit(file_name_expr, ctx))  # we get the str of the file name
        if result.error is not None:  # check for errors
            return result
        if not isinstance(file_name, String):  # check if the str is a String
            return result.failure(
                RTTypeError(
                    file_name.pos_start, file_name.pos_end, f"expected str, got {file_name.type_}.", ctx,
                    "src.interpreter.Interpreter.visit_ReadNode"
                )
            )
        file_name_value = file_name.value

        if file_name_value != "<stdin>":
            try:
                if line_number == 'all':  # read all the file
                    with open(file_name_value, 'r+', encoding='UTF-8') as file:
                        file_str = file.read()
                else:  # read a single line
                    with open(file_name_value, 'r+', encoding='UTF-8') as file:
                        file_data = file.readlines()
                        if 0 < line_number <= len(file_data):  # good index
                            file_str = file_data[line_number - 1]
                        else:  # wrong index
                            return result.failure(
                                RTIndexError(
                                    node.pos_start, node.pos_end, f"{line_number}.", ctx,
                                    "src.interpreter.Interpreter.visit_ReadNode"
                                )
                            )
            except FileNotFoundError:  # file not found
                return result.failure(
                    RTFileNotFoundError(
                        node.pos_start, node.pos_end, file_name_value, ctx,
                        "src.interpreter.Interpreter.visit_ReadNode"
                    )
                )
            except Exception as e:  # other python error
                return result.failure(
                    RunTimeError(
                        node.pos_start, node.pos_end, f"unable to write in file '{file_name_value}'. "
                                                      f"More info : Python{e.__class__.__name__}: {e}", ctx,
                        origin_file="src.interpreter.Interpreter.visit_ReadNode"
                    )
                )
        else:
            file_str = input()

        if identifier is not None:  # an identifier is given
            if identifier.value not in PROTECTED_VARS:  # the identifier is not protected
                ctx.symbol_table.set(identifier.value, String(file_str))
                self.update_symbol_table(ctx)
            else:
                return result.failure(
                    RunTimeError(
                        node.pos_start, node.pos_end,
                        f"unable to create a variable with builtin name '{identifier.value}'.",
                        ctx, origin_file="src.interpreter.Interpreter.visit_ReadNode"
                    )
                )

        return result.success(String(file_str))

    @staticmethod
    def visit_NoNode() -> RTResult:
        """There is no node"""
        return RTResult().success(NoneValue(False))
