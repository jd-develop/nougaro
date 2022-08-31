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
from src.values.basevalues import Number, String, List, NoneValue, Value
from src.values.specific_values.number import FALSE
from src.values.functions.function import Function
from src.values.functions.base_function import BaseFunction
from src.constants import PROTECTED_VARS, MODULES
from src.nodes import *
from src.errors import NotDefinedError, RunTimeError, RTIndexError, RTTypeError, RTFileNotFoundError, RTAssertionError
from src.token_types import TT
from src.runtime_result import RTResult
from src.context import Context
from src.misc import CustomInterpreterVisitMethod
# built-in python imports
from inspect import signature


# ##########
# INTERPRETER
# ##########
# noinspection PyPep8Naming
class Interpreter:
    def __init__(self, run):
        self.run = run

    def visit(self, node, ctx):
        method_name = f'visit_{type(node).__name__}'
        method: CustomInterpreterVisitMethod = getattr(self, method_name, self.no_visit_method)

        signature_ = signature(method)
        if len(signature_.parameters) <= 1:  # def method(self) is 1 param, def staticmethod() is 0 param
            return method()

        return method(node, ctx)

    @staticmethod
    def no_visit_method(node, ctx: Context):
        print(ctx)
        print(f"NOUGARO INTERNAL ERROR : No visit_{type(node).__name__} method defined in nougaro.Interpreter.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with all informations "
              f"above.")
        raise Exception(f'No visit_{type(node).__name__} method defined in nougaro.Interpreter.')

    @staticmethod
    def visit_NumberNode(node: NumberNode, ctx: Context):
        return RTResult().success(Number(node.token.value).set_context(ctx).set_pos(node.pos_start, node.pos_end))

    @staticmethod
    def visit_StringNode(node: StringNode, ctx: Context):
        return RTResult().success(
            String(node.token.value).set_context(ctx).set_pos(node.pos_start, node.pos_end)
        )

    def visit_ListNode(self, node: ListNode, ctx: Context):
        result = RTResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(result.register(self.visit(element_node, ctx)))
            if result.should_return():
                return result

        return result.success(List(elements).set_context(ctx).set_pos(node.pos_start, node.pos_end))

    def visit_BinOpNode(self, node: BinOpNode, ctx: Context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, ctx))
        if res.error is not None:
            return res
        right = res.register(self.visit(node.right_node, ctx))
        if res.error is not None:
            return res

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

        if error is not None:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_BinOpCompNode(self, node: BinOpCompNode, ctx: Context):
        res = RTResult()
        nodes_and_tokens_list = node.nodes_and_tokens_list
        if len(nodes_and_tokens_list) == 1:
            return self.visit(nodes_and_tokens_list[0], ctx)
        visited_nodes_and_tokens_list = []

        # just list of visited nodes
        for index, element in enumerate(nodes_and_tokens_list):
            if index % 2 == 0:  # we take only nodes and not ops
                visited_nodes_and_tokens_list.append(res.register(self.visit(element, ctx)))
                if res.error is not None:
                    return res
            else:
                visited_nodes_and_tokens_list.append(element)

        test_result = FALSE
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
                        f"Note for devs : the actual invalid token is {op_token.type}.\n"
                        f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with the "
                        f"information below")
                    raise Exception("Result is not defined after executing "
                                    "src.interpreter.Interpreter.visit_BinOpCompNode")
                if error is not None:
                    return res.failure(error)
                if test_result.value == 0:
                    return res.success(test_result.set_pos(node.pos_start, node.pos_end))
            else:
                pass
        return res.success(test_result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node: UnaryOpNode, ctx: Context):
        result = RTResult()
        number = result.register(self.visit(node.node, ctx))
        if result.should_return():
            return result

        error = None

        if node.op_token.type == TT["MINUS"]:
            number, error = number.multiplied_by(Number(-1))
        elif node.op_token.matches(TT["KEYWORD"], 'not'):
            number, error = number.not_()
        elif node.op_token.type == TT["BITWISENOT"]:
            number, error = number.bitwise_not()

        if error is not None:
            return result.failure(error)
        else:
            return result.success(number.set_pos(node.pos_start, node.pos_end))

    @staticmethod
    def visit_VarAccessNode(node: VarAccessNode, ctx: Context):
        result = RTResult()
        var_names_list = node.var_name_tokens_list
        value = None
        var_name = var_names_list[0]
        for var_name in var_names_list:
            value = ctx.symbol_table.get(var_name.value)
            if value is not None:
                break

        if value is None:
            if len(var_names_list) == 1:
                if var_name.value == "eexit" or var_name.value == "exxit" or var_name.value == "exiit" or \
                        var_name.value == "exitt":
                    return result.failure(
                        NotDefinedError(
                            node.pos_start, node.pos_end,
                            f"name '{var_name.value}' is not defined. Did you mean 'exit'?",
                            ctx
                        )
                    )
                else:
                    if ctx.symbol_table.exists(f'__{var_name.value}__'):
                        return result.failure(
                            NotDefinedError(
                                node.pos_start, node.pos_end,
                                f"name '{var_name.value}' is not defined, but '__{var_name.value}__' is.",
                                ctx
                            )
                        )
                    else:
                        return result.failure(
                            NotDefinedError(
                                node.pos_start, node.pos_end, f"name '{var_name.value}' is not defined.", ctx
                            )
                        )
            else:
                return result.failure(
                    NotDefinedError(
                        node.pos_start, node.pos_end, f"none of the given identifiers is defined.", ctx
                    )
                )

        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(ctx)
        return result.success(value)

    def visit_VarAssignNode(self, node: VarAssignNode, ctx: Context):
        result = RTResult()
        var_name = node.var_name_token.value
        value = result.register(self.visit(node.value_node, ctx))
        equal = node.equal.type
        if result.should_return():
            return result

        if var_name not in PROTECTED_VARS:
            if equal == TT["EQ"]:
                ctx.symbol_table.set(var_name, value)
                final_value = value
            else:
                if var_name in ctx.symbol_table.symbols:
                    var_actual_value: Value = ctx.symbol_table.get(var_name)
                    if equal == TT["PLUSEQ"]:
                        final_value, error = var_actual_value.added_to(value)
                    elif equal == TT["MINUSEQ"]:
                        final_value, error = var_actual_value.subbed_by(value)
                    elif equal == TT["MULTEQ"]:
                        final_value, error = var_actual_value.multiplied_by(value)
                    elif equal == TT["DIVEQ"]:
                        final_value, error = var_actual_value.dived_by(value)
                    elif equal == TT["POWEQ"]:
                        final_value, error = var_actual_value.powered_by(value)
                    elif equal == TT["FLOORDIVEQ"]:
                        final_value, error = var_actual_value.floor_dived_by(value)
                    elif equal == TT["PERCEQ"]:
                        final_value, error = var_actual_value.modded_by(value)
                    elif equal == TT["OREQ"]:
                        final_value, error = var_actual_value.or_(value)
                    elif equal == TT["XOREQ"]:
                        final_value, error = var_actual_value.xor_(value)
                    elif equal == TT["ANDEQ"]:
                        final_value, error = var_actual_value.and_(value)
                    elif equal == TT["BITWISEANDEQ"]:
                        final_value, error = var_actual_value.bitwise_and(value)
                    elif equal == TT["BITWISEOREQ"]:
                        final_value, error = var_actual_value.bitwise_or(value)
                    elif equal == TT["BITWISEXOREQ"]:
                        final_value, error = var_actual_value.bitwise_xor(value)
                    elif equal == TT["EEEQ"]:
                        final_value, error = var_actual_value.get_comparison_eq(value)
                    elif equal == TT["LTEQ"]:
                        final_value, error = var_actual_value.get_comparison_lt(value)
                    elif equal == TT["GTEQ"]:
                        final_value, error = var_actual_value.get_comparison_gt(value)
                    elif equal == TT["LTEEQ"]:
                        final_value, error = var_actual_value.get_comparison_lte(value)
                    elif equal == TT["GTEEQ"]:
                        final_value, error = var_actual_value.get_comparison_gte(value)
                    else:  # this is not supposed to happen
                        print(f"Note: it was a problem in src.interpreter.Interpreter.visit_VarAssignNode. Please"
                              f" report this error at https://jd-develop.github.io/nougaro/bugreport.html with all"
                              f" infos.\n"
                              f"For the dev: equal token '{equal}' is in EQUALS but not planned in visit_VarAssignNode")
                        error = None
                        final_value = value

                    if error is not None:
                        error.set_pos(node.pos_start, node.pos_end)
                        return result.failure(error)
                    ctx.symbol_table.set(var_name, final_value)
                else:
                    if ctx.symbol_table.exists(f'__{var_name.value}__'):
                        return result.failure(
                            NotDefinedError(
                                node.pos_start, node.pos_end, f"name '{var_name.value}' is not defined yet, "
                                                              f"but '__{var_name.value}__' is.", ctx
                            )
                        )
                    else:
                        return result.failure(
                            NotDefinedError(
                                node.pos_start, node.pos_end, f"name '{var_name.value}' is not defined yet.", ctx
                            )
                        )
        else:
            return result.failure(RunTimeError(node.pos_start, node.pos_end,
                                               f"can not create or edit a variable with builtin name '{var_name}'.",
                                               ctx))
        return result.success(final_value)

    @staticmethod
    def visit_VarDeleteNode(node: VarDeleteNode, ctx: Context):
        result = RTResult()
        var_name = node.var_name_token.value

        if var_name not in ctx.symbol_table.symbols:
            return result.failure(NotDefinedError(node.pos_start, node.pos_end, f"name '{var_name}' is not defined.",
                                                  ctx))

        if var_name not in PROTECTED_VARS:
            ctx.symbol_table.remove(var_name)
        else:
            return result.failure(RunTimeError(node.pos_start, node.pos_end,
                                               f"can not delete value assigned to builtin name '{var_name}'.",
                                               ctx))
        return result.success(NoneValue(False))

    def visit_IfNode(self, node: IfNode, ctx: Context):
        result = RTResult()
        for condition, expr, should_return_none in node.cases:
            condition_value = result.register(self.visit(condition, ctx))
            if result.should_return():
                return result

            if condition_value.is_true():
                expr_value = result.register(self.visit(expr, ctx))
                if result.should_return():
                    return result
                return result.success(NoneValue(False) if should_return_none else expr_value)

        if node.else_case is not None:
            expr, should_return_none = node.else_case
            else_value = result.register(self.visit(expr, ctx))
            if result.should_return():
                return result
            return result.success(NoneValue(False) if should_return_none else else_value)

        return result.success(NoneValue(False))

    def visit_AssertNode(self, node: AssertNode, ctx: Context):
        result = RTResult()
        assertion = result.register(self.visit(node.assertion, ctx))
        errmsg = result.register(self.visit(node.errmsg, ctx))
        if result.should_return():
            return result

        assert True  # Yup, you've just found an Easter Egg ;)

        if not isinstance(errmsg, String):
            return result.failure(RTTypeError(
                errmsg.pos_start, errmsg.pos_end,
                f"error message should be a str, not {errmsg.type_}.",
                ctx
            ))

        if not assertion.is_true():
            return result.failure(RTAssertionError(
                assertion.pos_start, assertion.pos_end,
                errmsg.value,
                ctx
            ))

        return result.success(NoneValue(False))

    def visit_ForNode(self, node: ForNode, ctx: Context):
        result = RTResult()
        elements = []

        start_value = result.register(self.visit(node.start_value_node, ctx))
        if result.should_return():
            return result

        end_value = result.register(self.visit(node.end_value_node, ctx))
        if result.should_return():
            return result

        if node.step_value_node is not None:
            step_value = result.register(self.visit(node.step_value_node, ctx))
            if result.should_return():
                return result
        else:
            step_value = Number(1)

        i = start_value.value
        condition = (lambda: i < end_value.value) if step_value.value >= 0 else (lambda: i > end_value.value)

        while condition():
            ctx.symbol_table.set(node.var_name_token.value, Number(i))
            i += step_value.value

            value = result.register(self.visit(node.body_node, ctx))
            if result.should_return() and not result.loop_should_break and not result.loop_should_continue:
                return result

            if result.loop_should_continue:
                continue  # will continue the 'while condition()' -> the interpreted 'for' loop is continued ^^

            if result.loop_should_break:
                break  # will break the 'while condition()' -> the interpreted 'for' loop is break

            elements.append(value)

        return result.success(
            NoneValue(False) if node.should_return_none else
            List(elements).set_context(ctx).set_pos(node.pos_start, node.pos_end)
        )

    def visit_ForNodeList(self, node: ForNodeList, ctx: Context):
        result = RTResult()
        elements = []

        list_ = result.register(self.visit(node.list_node, ctx))
        if result.should_return():
            return result

        if isinstance(list_, List):
            for i in list_.elements:
                ctx.symbol_table.set(node.var_name_token.value, i)
                value = result.register(self.visit(node.body_node, ctx))
                if result.should_return() and not result.loop_should_break and not result.loop_should_continue:
                    return result

                if result.loop_should_continue:
                    continue  # will continue the 'for i in list_.elements' -> the interpreted 'for' loop is continued

                if result.loop_should_break:
                    break  # will break the 'for i in list_.elements' -> the interpreted 'for' loop is break

                elements.append(value)

            return result.success(
                NoneValue(False) if node.should_return_none else
                List(elements).set_context(ctx).set_pos(node.pos_start, node.pos_end)
            )
        else:
            return result.failure(
                RTTypeError(node.list_node.pos_start, node.list_node.pos_end,
                            f"expected a list after 'in', but found {list_.type_}.",
                            ctx)
            )

    def visit_WhileNode(self, node: WhileNode, ctx: Context):
        result = RTResult()
        elements = []

        while True:
            condition = result.register(self.visit(node.condition_node, ctx))
            if result.should_return():
                return result

            if not condition.is_true():
                break

            value = result.register(self.visit(node.body_node, ctx))
            if result.should_return() and not result.loop_should_break and not result.loop_should_continue:
                return result

            if result.loop_should_continue:
                continue  # will continue the 'while True' -> the interpreted 'while' loop is continued

            if result.loop_should_break:
                break  # will break the 'while True' -> the interpreted 'while' loop is break

            elements.append(value)

        return result.success(
            NoneValue(False) if node.should_return_none else
            List(elements).set_context(ctx).set_pos(node.pos_start, node.pos_end)
        )

    def visit_DoWhileNode(self, node: DoWhileNode, ctx: Context):
        result = RTResult()
        elements = []

        value = result.register(self.visit(node.body_node, ctx))
        if result.should_return():
            return result

        elements.append(value)

        while True:
            condition = result.register(self.visit(node.condition_node, ctx))
            if result.should_return():
                return result

            if not condition.is_true():
                break

            value = result.register(self.visit(node.body_node, ctx))
            if result.should_return() and not result.loop_should_break and not result.loop_should_continue:
                return result

            if result.loop_should_continue:
                continue  # will continue the 'while True' -> the interpreted 'while' loop is continued

            if result.loop_should_break:
                break  # will break the 'while True' -> the interpreted 'while' loop is break

            elements.append(value)

        return result.success(
            NoneValue(False) if node.should_return_none else
            List(elements).set_context(ctx).set_pos(node.pos_start, node.pos_end)
        )

    @staticmethod
    def visit_FuncDefNode(node: FuncDefNode, ctx: Context):
        result = RTResult()
        func_name = node.var_name_token.value if node.var_name_token is not None else None
        body_node = node.body_node
        param_names = [param_name.value for param_name in node.param_names_tokens]
        func_value = Function(func_name, body_node, param_names, node.should_auto_return).set_context(ctx).set_pos(
            node.pos_start, node.pos_end
        )

        if node.var_name_token is not None:
            if func_name not in PROTECTED_VARS:
                ctx.symbol_table.set(func_name, func_value)
            else:
                return result.failure(RunTimeError(node.pos_start, node.pos_end,
                                                   f"can not create a function with builtin name '{func_name}'.",
                                                   ctx))

        return result.success(func_value)

    def visit_CallNode(self, node: CallNode, ctx: Context):
        result = RTResult()
        args = []

        value_to_call = result.register(self.visit(node.node_to_call, ctx))
        if result.should_return():
            return result
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        if isinstance(value_to_call, BaseFunction):
            # call the function
            for arg_node in node.arg_nodes:
                args.append(result.register(self.visit(arg_node, ctx)))
                if result.should_return():
                    return result

            try:
                return_value = result.register(value_to_call.execute(args, Interpreter, self.run,
                                                                     exec_from=f"{ctx.display_name} from"
                                                                               f" {ctx.parent.display_name}"))
            except Exception:
                return_value = result.register(value_to_call.execute(args, Interpreter, self.run,
                                                                     exec_from=f"{ctx.display_name}"))
            if result.should_return():
                return result
            return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(ctx)
            return result.success(return_value)

        elif isinstance(value_to_call, List):
            # get the element at the index given
            if len(node.arg_nodes) == 1:
                index = result.register(self.visit(node.arg_nodes[0], ctx))
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
                                ctx
                            )
                        )
                else:
                    return result.failure(RunTimeError(
                        node.pos_start, node.pos_end,
                        f"indexes must be integers, not {index.type_}.",
                        ctx
                    ))
            elif len(node.arg_nodes) > 1:
                return_value = []
                for arg_node in node.arg_nodes:
                    index = result.register(self.visit(arg_node, ctx))
                    if isinstance(index, Number):
                        index = index.value
                        try:
                            return_value.append(value_to_call[index])
                        except Exception:
                            return result.failure(
                                RTIndexError(
                                    arg_node.pos_start, arg_node.pos_end,
                                    f'list index {index} out of range.',
                                    ctx
                                )
                            )
                    else:
                        return result.failure(RunTimeError(
                            arg_node.pos_start, arg_node.pos_end,
                            f"indexes must be integers, not {index.type_}.",
                            ctx
                        ))
                return result.success(List(return_value).set_context(ctx).set_pos(node.pos_start, node.pos_end))
            else:
                return result.failure(RunTimeError(
                    node.pos_start, node.pos_end,
                    f"please give at least one index.",
                    ctx
                ))
        else:
            return result.failure(RunTimeError(
                node.pos_start, node.pos_end,
                f"{value_to_call.type_} is not callable.",
                ctx
            ))

    def visit_ReturnNode(self, node: ReturnNode, ctx: Context):
        result = RTResult()

        if node.node_to_return is not None:
            value = result.register(self.visit(node.node_to_return, ctx))
            if result.should_return():
                return result
        else:
            value = NoneValue(False)

        return result.success_return(value)

    @staticmethod
    def visit_ContinueNode():
        return RTResult().success_continue()

    @staticmethod
    def visit_BreakNode():
        return RTResult().success_break()

    @staticmethod
    def visit_ImportNode(node: ImportNode, ctx: Context):
        result = RTResult()
        identifier: Token = node.identifier
        name_to_import = identifier.value
        is_module = False

        if name_to_import in MODULES:
            is_module = True

        if not is_module:
            if f'__{name_to_import}__' in MODULES:
                return result.failure(
                    NotDefinedError(
                        node.pos_start, node.pos_end, f"name '{name_to_import}' is not a module, "
                                                      f"but '__{name_to_import}__' is.", ctx
                    )
                )
            else:
                return result.failure(
                    NotDefinedError(
                        node.pos_start, node.pos_end, f"name '{name_to_import}' is not a module.", ctx
                    )
                )

        from lib_.__TABLE_OF_MODULES__ import TABLE_OF_MODULES
        what_to_import = TABLE_OF_MODULES[name_to_import]
        for key in what_to_import.keys():
            ctx.symbol_table.set(f"{name_to_import}_{key}", what_to_import[key])

        return result.success(NoneValue(False))

    def visit_WriteNode(self, node: WriteNode, ctx: Context):
        result = RTResult()
        expr_to_write = node.expr_to_write
        file_name_expr = node.file_name_expr
        to_token = node.to_token
        line_number = node.line_number
        if to_token.type == TT["TO"]:
            open_mode = 'a+'
        elif to_token.type == TT["TO_AND_OVERWRITE"]:
            open_mode = 'w+'
        else:
            open_mode = 'a+'

        str_to_write = result.register(self.visit(expr_to_write, ctx))
        if result.error is not None:
            return result
        if not isinstance(str_to_write, String):
            return result.failure(
                RTTypeError(
                    str_to_write.pos_start, str_to_write.pos_end, f"expected str, got {str_to_write.type_}.", ctx
                )
            )

        file_name = result.register(self.visit(file_name_expr, ctx))
        if result.error is not None:
            return result
        if not isinstance(file_name, String):
            return result.failure(
                RTTypeError(
                    file_name.pos_start, file_name.pos_end, f"expected str, got {file_name.type_}.", ctx
                )
            )

        str_to_write_value = str_to_write.value
        file_name_value = file_name.value

        if file_name_value == '<stdout>':
            if open_mode == 'w':
                return result.failure(
                    RunTimeError(
                        node.pos_start, node.pos_end, f"can not overwrite <stdout>.", ctx
                    )
                )
            print(str_to_write_value)
            return result.success(str_to_write)

        try:
            if line_number == 'last':
                with open(file_name_value, open_mode, encoding='UTF-8') as file:
                    file.write(str_to_write_value)
                    file.close()
            else:
                with open(file_name_value, 'r+', encoding='UTF-8') as file:
                    file_data = file.readlines()
                    file.close()
                if line_number > len(file_data):
                    with open(file_name_value, 'a+', encoding='UTF-8') as file:
                        file.write('\n' * (line_number - len(file_data)))
                        file.write(str_to_write_value)
                        file.close()
                else:
                    if open_mode == 'a+':
                        if line_number == 0:
                            file_data.insert(0, str_to_write_value + '\n')
                        elif line_number > 0:
                            file_data[line_number - 1] = file_data[line_number - 1].replace('\n', '')
                            file_data[line_number - 1] += str_to_write_value + '\n'
                        else:
                            return result.failure(
                                RTIndexError(
                                    node.pos_start, node.pos_end, "line number can not be negative.", ctx
                                )
                            )
                    else:  # open_mode == 'w+'
                        if line_number == 0:
                            file_data.insert(0, str_to_write_value + '\n')
                        elif line_number > 0:
                            file_data[line_number - 1] = str_to_write_value + '\n'
                        else:
                            return result.failure(
                                RTIndexError(
                                    node.pos_start, node.pos_end, "line number can not be negative.", ctx
                                )
                            )

                    with open(file_name_value, 'w+', encoding='UTF-8') as file:
                        file.writelines(file_data)
                        file.close()
        except Exception as e:
            return result.failure(
                RunTimeError(
                    node.pos_start, node.pos_end, f"unable to write in file '{file_name_value}'. "
                                                  f"More info : Python{e.__class__.__name__}: {e}", ctx
                )
            )

        return result.success(str_to_write)

    def visit_ReadNode(self, node: ReadNode, ctx: Context):
        result = RTResult()
        file_name_expr = node.file_name_expr
        identifier = node.identifier
        line_number = node.line_number

        file_name = result.register(self.visit(file_name_expr, ctx))
        if result.error is not None:
            return result
        if not isinstance(file_name, String):
            return result.failure(
                RTTypeError(
                    file_name.pos_start, file_name.pos_end, f"expected str, got {file_name.type_}.", ctx
                )
            )
        file_name_value = file_name.value

        try:
            if line_number == 'all':
                with open(file_name_value, 'r+', encoding='UTF-8') as file:
                    file_str = file.read()
                    file.close()
            else:
                with open(file_name_value, 'r+', encoding='UTF-8') as file:
                    file_data = file.readlines()
                    file.close()
                    if 0 < line_number <= len(file_data):
                        file_str = file_data[line_number - 1]
                    else:
                        return result.failure(
                            RTIndexError(
                                node.pos_start, node.pos_end, f"{line_number}.", ctx
                            )
                        )
        except FileNotFoundError:
            return result.failure(
                RTFileNotFoundError(
                    node.pos_start, node.pos_end, f"file '{file_name_value}' does not exist.", ctx
                )
            )
        except Exception as e:
            return result.failure(
                RunTimeError(
                    node.pos_start, node.pos_end, f"unable to write in file '{file_name_value}'. "
                                                  f"More info : Python{e.__class__.__name__}: {e}", ctx
                )
            )

        if identifier is not None:
            if identifier.value not in PROTECTED_VARS:
                ctx.symbol_table.set(identifier.value, String(file_str))
            else:
                return result.failure(
                    RunTimeError(
                        node.pos_start, node.pos_end,
                        f"unable to create a variable with builtin name '{identifier.value}'.",
                        ctx
                    )
                )

        return result.success(String(file_str))

    @staticmethod
    def visit_NoNode():
        return RTResult().success(NoneValue(False))
