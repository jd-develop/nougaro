#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# IMPORTS
# nougaro modules imports
from src.values.functions.builtin_function import *
# Comment about the above line : Context, RTResult and values are imported in builtin_function.py
import src.errors
# built-in python imports
import statistics


class RTStatisticsError(src.errors.RunTimeError):
    def __init__(self, pos_start, pos_end, details, context: Context):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="StatisticsError")
        self.context = context


class Statistics(BaseBuiltInFunction):
    """ Module Statistics """
    def __init__(self, name):
        super().__init__(name)

    def __repr__(self):
        return f'<built-in function statistics_{self.name}>'

    def execute(self, args, interpreter_, run, exec_from: str = "<invalid>"):
        result = RTResult()
        exec_context = self.generate_new_context()
        exec_context.symbol_table.set("__exec_from__", String(exec_from))
        exec_context.symbol_table.set("__actual_context__", String(self.name))

        method_name = f'execute_statistics_{self.name}'
        method: CustomBuiltInFuncMethod = getattr(self, method_name, self.no_visit_method)

        result.register(self.check_and_populate_args(method.arg_names, args, exec_context,
                                                     optional_args=method.optional_args,
                                                     should_respect_args_number=method.should_respect_args_number))
        if result.should_return():
            return result

        try:
            return_value = result.register(method(exec_context))
        except TypeError:
            try:
                return_value = result.register(method())
            except TypeError:  # it only executes when coding
                return_value = result.register(method(exec_context))
        if result.should_return():
            return result
        return result.success(return_value)

    def no_visit_method(self, exec_context: Context):
        print(exec_context)
        print(f"NOUGARO INTERNAL ERROR : No execute_statistics_{self.name} method defined in lib_.statistics_.\n"
              f"Please report this bug at https://jd-develop.github.io/nougaro/redirect1.html with all informations "
              f"above.")
        raise Exception(f'No execute_statistics_{self.name} method defined in lib_.statistics_.')

    def copy(self):
        copy = Statistics(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    # =========
    # FUNCTIONS
    # =========
    def execute_statistics_mean(self, exec_ctx: Context):
        """Like python statistics.mean()"""
        # Params:
        # * data
        data = exec_ctx.symbol_table.get('data')
        if not isinstance(data, List):
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_mean' must be a list of numbers.",
                exec_ctx
            ))

        data_ = []
        for e in data.elements:
            if not isinstance(e, Number):
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in module function 'statistics_mean' must be a list of numbers, not "
                    f"{e.type_}.",
                    exec_ctx
                ))
            data_.append(e.value)

        try:
            mean_ = statistics.mean(data_)
        except statistics.StatisticsError as e:
            if str(e) == "mean requires at least one data point":
                return RTResult().failure(RTStatisticsError(
                    data.pos_start, data.pos_end,
                    "first argument of built-in module function 'statistics_mean' must not be empty.",
                    exec_ctx
                ))
            else:
                return RTResult().failure(RTStatisticsError(
                    self.pos_start, self.pos_end, str(e) + '.', exec_ctx
                ))

        return RTResult().success(Number(mean_))

    execute_statistics_mean.arg_names = ['data']
    execute_statistics_mean.optional_args = []
    execute_statistics_mean.should_respect_args_number = True


WHAT_TO_IMPORT = {
    "mean": Statistics("mean"),
}
