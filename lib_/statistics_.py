#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# IMPORTS
# nougaro modules imports
from src.values.py2noug import py2noug
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
              f"Please report this bug at https://jd-develop.github.io/nougaro/bugreport.html with all informations "
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
        except statistics.StatisticsError as exception:
            if str(exception) == "mean requires at least one data point":
                return RTResult().failure(RTStatisticsError(
                    data.pos_start, data.pos_end,
                    "first argument of built-in module function 'statistics_mean' must not be empty.",
                    exec_ctx
                ))
            else:
                return RTResult().failure(RTStatisticsError(
                    self.pos_start, self.pos_end, str(exception) + '.', exec_ctx
                ))

        return RTResult().success(Number(mean_))

    execute_statistics_mean.arg_names = ['data']
    execute_statistics_mean.optional_args = []
    execute_statistics_mean.should_respect_args_number = True

    def execute_statistics_geometric_mean(self, exec_ctx: Context):
        """Like python statistics.geometric_mean()"""
        # Params:
        # * data
        data = exec_ctx.symbol_table.get('data')
        if not isinstance(data, List):
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_geometric_mean' must be a list of positive "
                "numbers.",
                exec_ctx
            ))

        data_ = []
        for e in data.elements:
            if not isinstance(e, Number):
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in module function 'statistics_geometric_mean' must be a list of "
                    f"positive numbers, not {e.type_}.",
                    exec_ctx
                ))
            data_.append(e.value)

        try:
            geometric_mean_ = statistics.geometric_mean(data_)
        except statistics.StatisticsError as exception:
            is_empty_python_exceptions = [
                "mean requires at least one data point",
                "fmean requires at least one data point",
                "geometric mean requires a non-empty dataset containing positive numbers"
            ]
            if str(exception) in is_empty_python_exceptions:
                return RTResult().failure(RTStatisticsError(
                    data.pos_start, data.pos_end,
                    "first argument of built-in module function 'statistics_geometric_mean' must be a non-empty list "
                    "that only contains positive numbers.",
                    exec_ctx
                ))
            else:
                return RTResult().failure(RunTimeError(
                    self.pos_start, self.pos_end,
                    f"python statistics.geometric_mean() crashed with this error: "
                    f"{exception.__class__.__name__}: {exception}. PLEASE REPORT THIS BUG BY FOLLOWING THIS LINK: "
                    f"https://jd-develop.github.io/nougaro/bugreport.html !",
                    exec_ctx
                ))
        except Exception as exception:
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"python statistics.geometric_mean() crashed with this error: "
                f"{exception.__class__.__name__}: {exception}. PLEASE REPORT THIS BUG BY FOLLOWING THIS LINK: "
                f"https://jd-develop.github.io/nougaro/bugreport.html !",
                exec_ctx
            ))

        return RTResult().success(Number(geometric_mean_))

    execute_statistics_geometric_mean.arg_names = ['data']
    execute_statistics_geometric_mean.optional_args = []
    execute_statistics_geometric_mean.should_respect_args_number = True

    def execute_statistics_harmonic_mean(self, exec_ctx: Context):
        """Like python statistics.harmonic_mean()"""
        # Params:
        # * data
        # Optional params:
        # * weights
        data = exec_ctx.symbol_table.get('data')
        if not isinstance(data, List):
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_harmonic_mean' must be a list of numbers.",
                exec_ctx
            ))

        weights = exec_ctx.symbol_table.get('weights')
        if weights is not None and not isinstance(weights, List):
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "second argument of built-in module function 'statistics_harmonic_mean' must be a list of numbers.",
                exec_ctx
            ))

        if weights is not None and len(weights.elements) != len(data.elements):
            return RTResult().failure(RTIndexError(
                data.pos_start, weights.pos_end,
                "the two arguments of built-in module function 'statistics_harmonic_mean' must have the same length.",
                exec_ctx
            ))

        data_ = []
        for e in data.elements:
            if not isinstance(e, Number):
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in module function 'statistics_harmonic_mean' must be a list of positive"
                    f" numbers, not {e.type_}.",
                    exec_ctx
                ))
            if e.value < 0:
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    "first argument of built-in module function 'statistics_harmonic_mean' must be a list of "
                    "positives numbers.",
                    exec_ctx
                ))
            data_.append(e.value)

        if weights is not None:
            weights_ = []
            for e in weights.elements:
                if not isinstance(e, Number):
                    return RTResult().failure(RTTypeError(
                        e.pos_start, e.pos_end,
                        f"first argument of built-in module function 'statistics_harmonic_mean' must be a list of "
                        f"positive numbers, not {e.type_}.",
                        exec_ctx
                    ))
                if e.value < 0:
                    return RTResult().failure(RTTypeError(
                        e.pos_start, e.pos_end,
                        "first argument of built-in module function 'statistics_harmonic_mean' must be a list of "
                        "positives numbers.",
                        exec_ctx
                    ))
                weights_.append(e.value)
        else:
            weights_ = None

        try:
            if weights_ is None:
                harmonic_mean_ = statistics.harmonic_mean(data_)
            else:
                harmonic_mean_ = statistics.harmonic_mean(data_, weights=weights_)
        except statistics.StatisticsError as exception:
            is_empty_python_exceptions = [
                "harmonic_mean requires at least one data point",
            ]
            if str(exception) in is_empty_python_exceptions:
                return RTResult().failure(RTStatisticsError(
                    data.pos_start, data.pos_end,
                    "first argument of built-in module function 'statistics_harmonic_mean' must not be empty.",
                    exec_ctx
                ))
            else:
                return RTResult().failure(RunTimeError(
                    self.pos_start, self.pos_end,
                    f"python statistics.harmonic_mean() crashed with this error: "
                    f"{exception.__class__.__name__}: {exception}. PLEASE REPORT THIS BUG BY FOLLOWING THIS LINK: "
                    f"https://jd-develop.github.io/nougaro/bugreport.html !",
                    exec_ctx
                ))
        except Exception as exception:
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"python statistics.harmonic_mean() crashed with this error: "
                f"{exception.__class__.__name__}: {exception}. PLEASE REPORT THIS BUG BY FOLLOWING THIS LINK: "
                f"https://jd-develop.github.io/nougaro/bugreport.html !",
                exec_ctx
            ))

        return RTResult().success(Number(harmonic_mean_))

    execute_statistics_harmonic_mean.arg_names = ['data']
    execute_statistics_harmonic_mean.optional_args = ['weights']
    execute_statistics_harmonic_mean.should_respect_args_number = True

    def execute_statistics_median(self, exec_ctx: Context):
        """Like python statistics.median()"""
        # Params:
        # * data
        data = exec_ctx.symbol_table.get('data')
        if not isinstance(data, List):
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_median' must be a list of numbers.",
                exec_ctx
            ))

        data_ = []
        for e in data.elements:
            if not isinstance(e, Number):
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in module function 'statistics_median' must be a list of numbers, not "
                    f"{e.type_}.", exec_ctx
                ))
            data_.append(e.value)

        try:
            median_ = statistics.median(data_)
        except statistics.StatisticsError as exception:
            if str(exception) == "no median for empty data":
                return RTResult().failure(RTStatisticsError(
                    data.pos_start, data.pos_end,
                    "first argument of built-in module function 'statistics_median' must not be empty.",
                    exec_ctx
                ))
            else:
                return RTResult().failure(RTStatisticsError(
                    self.pos_start, self.pos_end, str(exception) + '.', exec_ctx
                ))

        return RTResult().success(Number(median_))

    execute_statistics_median.arg_names = ['data']
    execute_statistics_median.optional_args = []
    execute_statistics_median.should_respect_args_number = True

    # HERE THE DISCLAIMER BEFORE THE DECLARATION OF PYTHON statistics.quantiles FUNCTION:

    # Notes on methods for computing quantiles
    # ----------------------------------------
    #
    # There is no one perfect way to compute quantiles.  Here we offer
    # two methods that serve common needs.  Most other packages
    # surveyed offered at least one or both of these two, making them
    # "standard" in the sense of "widely-adopted and reproducible".
    # They are also easy to explain, easy to compute manually, and have
    # straight-forward interpretations that aren't surprising.

    # The default method is known as "R6", "PERCENTILE.EXC", or "expected
    # value of rank order statistics". The alternative method is known as
    # "R7", "PERCENTILE.INC", or "mode of rank order statistics".

    # For sample data where there is a positive probability for values
    # beyond the range of the data, the R6 exclusive method is a
    # reasonable choice.  Consider a random sample of nine values from a
    # population with a uniform distribution from 0.0 to 1.0.  The
    # distribution of the third ranked sample point is described by
    # betavariate(alpha=3, beta=7) which has mode=0.250, median=0.286, and
    # mean=0.300.  Only the latter (which corresponds with R6) gives the
    # desired cut point with 30% of the population falling below that
    # value, making it comparable to a result from an inv_cdf() function.
    # The R6 exclusive method is also idempotent.

    # For describing population data where the end points are known to
    # be included in the data, the R7 inclusive method is a reasonable
    # choice.  Instead of the mean, it uses the mode of the beta
    # distribution for the interior points.  Per Hyndman & Fan, "One nice
    # property is that the vertices of Q7(p) divide the range into n - 1
    # intervals, and exactly 100p% of the intervals lie to the left of
    # Q7(p) and 100(1 - p)% of the intervals lie to the right of Q7(p)."

    # If needed, other methods could be added.  However, for now, the
    # position is that fewer options make for easier choices and that
    # external packages can be used for anything more advanced.

    # REMEMBER THAT THIS IS THE DISCLAIMER BEFORE THE DECLARATION OF PYTHON statistics.quantiles FUNCTION :)

    def execute_statistics_quantiles(self, exec_ctx: Context):
        """Like python statistics.quantiles()
        Here the doc of statistics.quantiles() python function:

        Divide *data* into *n* continuous intervals with equal probability.

        Returns a list of (n - 1) cut points separating the intervals.

        Set *n* to 4 for quartiles (the default).  Set *n* to 10 for deciles.
        Set *n* to 100 for percentiles which gives the 99 cuts points that
        separate *data* in to 100 equal sized groups.

        The *data* can be any iterable containing sample.
        The cut points are linearly interpolated between data points.

        If *method* is set to *inclusive*, *data* is treated as population
        data.  The minimum value is treated as the 0th percentile and the
        maximum value is treated as the 100th percentile.
        """
        # Params:
        # * data
        # Optional params:
        # * n
        # * method

        # By default n=4 and method='exclusive'

        data = exec_ctx.symbol_table.get('data')
        if not isinstance(data, List):
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_quantiles' must be a list of numbers.",
                exec_ctx
            ))

        n = exec_ctx.symbol_table.get('n')
        if n is None:
            n = Number(4)

        if not isinstance(n, Number):
            return RTResult().failure(RTTypeError(
                n.pos_start, n.pos_end,
                "second argument of built-in module function 'statistics_quantiles' must be a number.",
                exec_ctx
            ))

        if n.value < 1:
            return RTResult().failure(RTStatisticsError(
                n.pos_start, n.pos_end,
                "second argument of built-in module function 'statistics_quantiles' must be at least 1.",
                exec_ctx
            ))

        method = exec_ctx.symbol_table.get('method')
        if method is None:
            method = String('exclusive')

        if not isinstance(method, String):
            return RTResult().failure(RTTypeError(
                method.pos_start, method.pos_end,
                "third argument of built-in module function 'statistics_quantiles' must be a str.",
                exec_ctx
            ))

        if method.value not in ['exclusive', 'inclusive']:
            return RTResult().failure(RTStatisticsError(
                method.pos_start, method.pos_end,
                f"unknown method: {method.value}.",
                exec_ctx
            ))

        data_ = []
        for e in data.elements:
            if not isinstance(e, Number):
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in module function 'statistics_quantiles' must be a list of numbers, not "
                    f"{e.type_}.", exec_ctx
                ))
            data_.append(e.value)

        try:
            quantiles_ = statistics.quantiles(data_, n=n.value, method=method.value)
        except statistics.StatisticsError as exception:
            if str(exception) == "must have at least two data points":
                return RTResult().failure(RTStatisticsError(
                    data.pos_start, data.pos_end,
                    "first argument of built-in module function 'statistics_median' must have at least two elements.",
                    exec_ctx
                ))
            else:
                return RTResult().failure(RTStatisticsError(
                    self.pos_start, self.pos_end, str(exception) + '.', exec_ctx
                ))

        return RTResult().success(List(quantiles_))

    execute_statistics_quantiles.arg_names = ['data']
    execute_statistics_quantiles.optional_args = []
    execute_statistics_quantiles.should_respect_args_number = True
    
    def execute_statistics_scope(self, exec_ctx: Context):
        """The scope of a list, i.e. the difference between the max and the min value."""
        # Params:
        # * data
        data = exec_ctx.symbol_table.get('data')
        if not isinstance(data, List):
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_scope' must be a list of numbers.",
                exec_ctx
            ))

        data_ = []
        for e in data.elements:
            if not isinstance(e, Number):
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in module function 'statistics_scope' must be a list of numbers, not "
                    f"{e.type_}.", exec_ctx
                ))
            data_.append(e.value)

        if len(data_) < 1:
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_scope' must not be empty.", exec_ctx
            ))

        scope = max(data_) - min(data_)
        return RTResult().success(Number(scope))

    execute_statistics_scope.arg_names = ['data']
    execute_statistics_scope.optional_args = []
    execute_statistics_scope.should_respect_args_number = True

    def execute_statistics_mode(self, exec_ctx: Context):
        """The mode of a list, i.e. the most common value."""
        # Params:
        # * data
        data = exec_ctx.symbol_table.get('data')
        if not isinstance(data, List):
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_mode' must be a list of numbers.",
                exec_ctx
            ))

        data_ = []
        for e in data.elements:
            if not isinstance(e, Number):
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in module function 'statistics_mode' must be a list of numbers, not "
                    f"{e.type_}.", exec_ctx
                ))
            data_.append(e.value)

        if len(data_) < 1:
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_mode' must not be empty.", exec_ctx
            ))

        mode = statistics.mode(data_)
        return RTResult().success(Number(mode))

    execute_statistics_mode.arg_names = ['data']
    execute_statistics_mode.optional_args = []
    execute_statistics_mode.should_respect_args_number = True

    def execute_statistics_multimode(self, exec_ctx: Context):
        """The list of the modes of a list/str, i.e. the most common values."""
        # Params:
        # * data
        data = exec_ctx.symbol_table.get('data')
        if not (isinstance(data, List) or isinstance(data, String)):
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_multimode' must be a list or a str.",
                exec_ctx
            ))

        if isinstance(data, List):
            data_ = []
            for e in data.elements:
                if not (isinstance(e, Number) or isinstance(e, String)):
                    return RTResult().failure(RTTypeError(
                        e.pos_start, e.pos_end,
                        f"first argument of built-in module function 'statistics_multimode' must be a list that does"
                        f" not contains {e.type_}or a str.",
                        exec_ctx
                    ))
                data_.append(e.value)
        elif isinstance(data, String):
            data_ = data.value
        else:
            # i.d.k. why I put a 'else', but it's funny to put an Easter Egg to people that read the code :)
            # -Jean Dubois
            raise NotImplementedError("How the f*** did this error happened? This is not possible!")

        multimode = statistics.multimode(data_)
        multimode_ = []
        for e in multimode:
            multimode_.append(py2noug(e))
        return RTResult().success(List(multimode_))

    execute_statistics_multimode.arg_names = ['data']
    execute_statistics_multimode.optional_args = []
    execute_statistics_multimode.should_respect_args_number = True


WHAT_TO_IMPORT = {
    "mean": Statistics("mean"),
    "geometric_mean": Statistics("geometric_mean"),
    "harmonic_mean": Statistics("harmonic_mean"),
    "median": Statistics("median"),
    "quantiles": Statistics("quantiles"),
    "scope": Statistics("scope"),
    "mode": Statistics("mode"),
    "multimode": Statistics("multimode"),
}
