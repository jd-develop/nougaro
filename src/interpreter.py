#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# IMPORTS
# nougaro modules imports
from src.values.basevalues import Number, String, List, NoneValue, Value
from src.values.specific_values.number import FALSE
from src.values.functions.function import Function
from src.values.functions.base_function import BaseFunction
from src.constants import VARS_CANNOT_MODIFY, MODULES
from src.nodes import *
from src.errors import NotDefinedError, RunTimeError, RTIndexError
from src.token_constants import *
from src.runtime_result import RTResult
from src.context import Context
# built-in python imports
# no imports


# ##########
# INTERPRETER
# ##########
class Interpreter:
    def __init__(self, run):
        self.run = run

    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)

        return method(node, context)

    @staticmethod
    def no_visit_method(node, context: Context):
        print(context)
        print(f"NOUGARO INTERNAL ERROR : No visit_{type(node).__name__} method defined in nougaro.Interpreter.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/redirect1.html with all informations "
              f"above.")
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
            if result.should_return():
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
        elif node.op_token.type == TT_PERC:
            result, error = left.modded_by(right)
        elif node.op_token.type == TT_FLOORDIV:
            result, error = left.floor_dived_by(right)
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
        elif node.op_token.type == TT_BITWISEAND:
            result, error = left.bitwise_and(right)
        elif node.op_token.type == TT_BITWISEOR:
            result, error = left.bitwise_or(right)
        elif node.op_token.type == TT_BITWISEXOR:
            result, error = left.bitwise_xor(right)
        else:
            print(context)
            print("NOUGARO INTERNAL ERROR : Result is not defined after executing "
                  "src.interpreter.Interpreter.visit_BinOpNode because of an invalid token.\n"
                  "Please report this bug at https://jd-develop.github.io/nougaro/redirect1.html with the information "
                  "below")
            raise Exception("Result is not defined after executing src.interpreter.Interpreter.visit_BinOpNode")

        if error is not None:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_BinOpCompNode(self, node: BinOpCompNode, context: Context):
        res = RTResult()
        nodes_and_tokens_list = node.nodes_and_tokens_list
        if len(nodes_and_tokens_list) == 1:
            return self.visit(nodes_and_tokens_list[0], context)
        visited_nodes_and_tokens_list = []

        # just list of visited nodes
        for index, element in enumerate(nodes_and_tokens_list):
            if index % 2 == 0:  # we take only nodes and not ops
                visited_nodes_and_tokens_list.append(res.register(self.visit(element, context)))
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
                if op_token.type == TT_EE:
                    test_result, error = element.get_comparison_eq(right)
                elif op_token.type == TT_NE:
                    test_result, error = element.get_comparison_ne(right)
                elif op_token.type == TT_LT:
                    test_result, error = element.get_comparison_lt(right)
                elif op_token.type == TT_GT:
                    test_result, error = element.get_comparison_gt(right)
                elif op_token.type == TT_LTE:
                    test_result, error = element.get_comparison_lte(right)
                elif op_token.type == TT_GTE:
                    test_result, error = element.get_comparison_gte(right)
                elif op_token.matches(TT_KEYWORD, 'in'):
                    test_result, error = element.is_in(right)
                else:
                    print(context)
                    print(
                        f"NOUGARO INTERNAL ERROR : Result is not defined after executing "
                        f"src.interpreter.Interpreter.visit_BinOpCompNode because of an invalid token.\n"
                        f"Note for devs : the actual invalid token is {op_token.type}.\n"
                        f"Please report this bug at https://jd-develop.github.io/nougaro/redirect1.html with the "
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

    def visit_UnaryOpNode(self, node: UnaryOpNode, context: Context):
        result = RTResult()
        number = result.register(self.visit(node.node, context))
        if result.should_return():
            return result

        error = None

        if node.op_token.type == TT_MINUS:
            number, error = number.multiplied_by(Number(-1))
        elif node.op_token.matches(TT_KEYWORD, 'not'):
            number, error = number.not_()
        elif node.op_token.type == TT_BITWISENOT:
            number, error = number.bitwise_not()

        if error is not None:
            return result.failure(error)
        else:
            return result.success(number.set_pos(node.pos_start, node.pos_end))

    @staticmethod
    def visit_VarAccessNode(node: VarAccessNode, context: Context):
        result = RTResult()
        var_names_list = node.var_name_tokens_list
        value = None
        var_name = var_names_list[0]
        for var_name in var_names_list:
            value = context.symbol_table.get(var_name.value)
            if value is not None:
                break

        if value is None:
            if len(var_names_list) == 1:
                if var_name.value == "eexit" or var_name.value == "exxit" or var_name.value == "exiit" or \
                        var_name.value == "exitt":
                    return result.failure(
                        NotDefinedError(
                            node.pos_start, node.pos_end, f"name '{var_name.value}' is not defined. Did you mean 'exit'"
                                                          f"?", context
                        )
                    )
                else:
                    return result.failure(
                        NotDefinedError(
                            node.pos_start, node.pos_end, f"name '{var_name.value}' is not defined.", context
                        )
                    )
            else:
                return result.failure(
                    NotDefinedError(
                        node.pos_start, node.pos_end, f"none of the given identifiers is defined.", context
                    )
                )

        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return result.success(value)

    def visit_VarAssignNode(self, node: VarAssignNode, context: Context):
        result = RTResult()
        var_name = node.var_name_token.value
        value = result.register(self.visit(node.value_node, context))
        equal = node.equal.type
        if result.should_return():
            return result

        if var_name not in VARS_CANNOT_MODIFY:
            if equal == TT_EQ:
                context.symbol_table.set(var_name, value)
                final_value = value
            else:
                if var_name in context.symbol_table.symbols:
                    var_actual_value: Value = context.symbol_table.get(var_name)
                    if equal == TT_PLUSEQ:
                        final_value, error = var_actual_value.added_to(value)
                    elif equal == TT_MINUSEQ:
                        final_value, error = var_actual_value.subbed_by(value)
                    elif equal == TT_MULTEQ:
                        final_value, error = var_actual_value.multiplied_by(value)
                    elif equal == TT_DIVEQ:
                        final_value, error = var_actual_value.dived_by(value)
                    elif equal == TT_POWEQ:
                        final_value, error = var_actual_value.powered_by(value)
                    elif equal == TT_FLOORDIVEQ:
                        final_value, error = var_actual_value.floor_dived_by(value)
                    elif equal == TT_PERCEQ:
                        final_value, error = var_actual_value.modded_by(value)
                    elif equal == TT_OREQ:
                        final_value, error = var_actual_value.or_(value)
                    elif equal == TT_XOREQ:
                        final_value, error = var_actual_value.excl_or(value)
                    elif equal == TT_ANDEQ:
                        final_value, error = var_actual_value.and_(value)
                    elif equal == TT_BITWISEANDEQ:
                        final_value, error = var_actual_value.bitwise_and(value)
                    elif equal == TT_BITWISEOREQ:
                        final_value, error = var_actual_value.bitwise_or(value)
                    elif equal == TT_BITWISEXOREQ:
                        final_value, error = var_actual_value.bitwise_xor(value)
                    else:  # this is not supposed to happen
                        print("Note: it was a problem in src.interpreter.Interpreter.visit_VarAssignNode. Please report"
                              " this error at https://jd-develop.github.io/nougaro/bugreport.html with all infos.")
                        error = None
                        final_value = value

                    if error is not None:
                        error.set_pos(node.pos_start, node.pos_end)
                        return result.failure(error)
                    context.symbol_table.set(var_name, final_value)
                else:
                    return result.failure(NotDefinedError(node.pos_start, node.pos_end,
                                                          f"name '{var_name}' is not defined yet.",
                                                          value.context))
        else:
            return result.failure(RunTimeError(node.pos_start, node.pos_end,
                                               f"can not create a variable with builtin name '{var_name}'.",
                                               value.context))
        return result.success(final_value)

    @staticmethod
    def visit_VarDeleteNode(node: VarDeleteNode, context: Context):
        result = RTResult()
        var_name = node.var_name_token.value

        if var_name not in context.symbol_table.symbols:
            return result.failure(NotDefinedError(node.pos_start, node.pos_end, f"name '{var_name}' is not defined.",
                                                  context))

        if var_name not in VARS_CANNOT_MODIFY:
            context.symbol_table.remove(var_name)
        else:
            return result.failure(RunTimeError(node.pos_start, node.pos_end,
                                               f"can not delete value assigned to builtin name '{var_name}'.",
                                               context))
        return result.success(NoneValue(False))

    def visit_IfNode(self, node: IfNode, context: Context):
        result = RTResult()
        for condition, expr, should_return_none in node.cases:
            condition_value = result.register(self.visit(condition, context))
            if result.should_return():
                return result

            if condition_value.is_true():
                expr_value = result.register(self.visit(expr, context))
                if result.should_return():
                    return result
                return result.success(NoneValue(False) if should_return_none else expr_value)

        if node.else_case is not None:
            expr, should_return_none = node.else_case
            else_value = result.register(self.visit(expr, context))
            if result.should_return():
                return result
            return result.success(NoneValue(False) if should_return_none else else_value)

        return result.success(NoneValue(False))

    def visit_ForNode(self, node: ForNode, context: Context):
        result = RTResult()
        elements = []

        start_value = result.register(self.visit(node.start_value_node, context))
        if result.should_return():
            return result

        end_value = result.register(self.visit(node.end_value_node, context))
        if result.should_return():
            return result

        if node.step_value_node is not None:
            step_value = result.register(self.visit(node.step_value_node, context))
            if result.should_return():
                return result
        else:
            step_value = Number(1)

        i = start_value.value
        condition = (lambda: i < end_value.value) if step_value.value >= 0 else (lambda: i > end_value.value)

        while condition():
            context.symbol_table.set(node.var_name_token.value, Number(i))
            i += step_value.value

            value = result.register(self.visit(node.body_node, context))
            if result.should_return() and not result.loop_should_break and not result.loop_should_continue:
                return result

            if result.loop_should_continue:
                continue  # will continue the 'while condition()' -> the interpreted 'for' loop is continued ^^

            if result.loop_should_break:
                break  # will break the 'while condition()' -> the interpreted 'for' loop is break

            elements.append(value)

        return result.success(
            NoneValue(False) if node.should_return_none else
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_ForNodeList(self, node: ForNodeList, context: Context):
        result = RTResult()
        elements = []

        list_ = result.register(self.visit(node.list_node, context))
        if result.should_return():
            return result

        if isinstance(list_, List):
            for i in list_.elements:
                context.symbol_table.set(node.var_name_token.value, i)
                value = result.register(self.visit(node.body_node, context))
                if result.should_return() and not result.loop_should_break and not result.loop_should_continue:
                    return result

                if result.loop_should_continue:
                    continue  # will continue the 'for i in list_.elements' -> the interpreted 'for' loop is continued

                if result.loop_should_break:
                    break  # will break the 'for i in list_.elements' -> the interpreted 'for' loop is break

                elements.append(value)

            return result.success(
                NoneValue(False) if node.should_return_none else
                List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
            )
        else:
            return result.failure(
                RunTimeError(node.list_node.pos_start, node.list_node.pos_end,
                             f"expected a list after 'in', but found {list_.type_}.",
                             context)
            )

    def visit_WhileNode(self, node: WhileNode, context: Context):
        result = RTResult()
        elements = []

        while True:
            condition = result.register(self.visit(node.condition_node, context))
            if result.should_return():
                return result

            if not condition.is_true():
                break

            value = result.register(self.visit(node.body_node, context))
            if result.should_return() and not result.loop_should_break and not result.loop_should_continue:
                return result

            if result.loop_should_continue:
                continue  # will continue the 'while True' -> the interpreted 'while' loop is continued

            if result.loop_should_break:
                break  # will break the 'while True' -> the interpreted 'while' loop is break

            elements.append(value)

        return result.success(
            NoneValue(False) if node.should_return_none else
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    @staticmethod
    def visit_FuncDefNode(node: FuncDefNode, context: Context):
        result = RTResult()
        func_name = node.var_name_token.value if node.var_name_token is not None else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_tokens]
        func_value = Function(func_name, body_node, arg_names, node.should_auto_return).set_context(context).set_pos(
            node.pos_start, node.pos_end
        )

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
        if result.should_return():
            return result
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        if isinstance(value_to_call, BaseFunction):
            # call the function
            for arg_node in node.arg_nodes:
                args.append(result.register(self.visit(arg_node, context)))
                if result.should_return():
                    return result

            return_value = result.register(value_to_call.execute(args, Interpreter, self.run))
            if result.should_return():
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

    def visit_ReturnNode(self, node: ReturnNode, context: Context):
        result = RTResult()

        if node.node_to_return is not None:
            value = result.register(self.visit(node.node_to_return, context))
            if result.should_return():
                return result
        else:
            value = NoneValue(False)

        return result.success_return(value)

    @staticmethod
    def visit_ContinueNode(node: ContinueNode, context: Context):
        return RTResult().success_continue()

    @staticmethod
    def visit_BreakNode(node: BreakNode, context: Context):
        return RTResult().success_break()

    @staticmethod
    def visit_ImportNode(node: ImportNode, context: Context):
        result = RTResult()
        identifier: Token = node.identifier
        name_to_import = identifier.value
        is_module = False

        if name_to_import in MODULES:
            is_module = True

        if not is_module:
            return result.failure(
                NotDefinedError(
                    node.pos_start, node.pos_end, f"name '{name_to_import}' is not a module.", context
                )
            )

        if name_to_import == 'random':
            from lib_.random_ import Random
            context.symbol_table.set('random_randint', Random('randint'))

        return result.success(NoneValue(False))

    @staticmethod
    def visit_NoNode(node: NoNode, context: Context):
        return RTResult().success(NoneValue(False))
