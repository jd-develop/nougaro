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

""" Statistics module

    Statistics is a module that provides tools to make statistics.
"""

# IMPORTS
# nougaro modules imports
from lib_.lib_to_make_libs import *
# Comment about the above line : Context, RTResult and values are imported in lib_to_make_libs.py
# built-in python imports
import statistics


class RTStatisticsError(RunTimeError):
    """StatisticsError is an error that can be triggered ONLY via functions in this module."""
    def __init__(self, pos_start, pos_end, details, context: Context):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="StatisticsError")
        self.context = context


class Statistics(Module):
    """ Module Statistics """
    def __init__(self, name):
        super().__init__("statistics", name)

    def copy(self):
        """Return a copy of self"""
        copy = Statistics(self.name)
        return self.set_context_and_pos_to_a_copy(copy)

    # =========
    # FUNCTIONS
    # =========
    def execute_statistics_mean(self, exec_ctx: Context):
        """Returns the mean of a statistical series"""
        # Params:
        # * data
        data = exec_ctx.symbol_table.get('data')  # we get the data
        if not isinstance(data, List):  # we check if the data is under the form of a list
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_mean' must be a list of numbers.",
                exec_ctx
            ))

        data_ = []
        for e in data.elements:
            if not isinstance(e, Number):  # the data must contain only numbers
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in module function 'statistics_mean' must be a list of numbers, not "
                    f"{e.type_}.",
                    exec_ctx
                ))
            data_.append(e.value)

        if len(data_) == 0:  # data must not be empty
            return RTResult().failure(RTStatisticsError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_mean' must not be empty.",
                exec_ctx
            ))

        try:
            mean_ = statistics.mean(data_)  # we try to calculate the mean of our list
        except statistics.StatisticsError as exception:
            return RTResult().failure(RTStatisticsError(
                self.pos_start, self.pos_end, str(exception) + '.', exec_ctx
            ))

        return RTResult().success(Number(mean_))

    execute_statistics_mean.param_names = ['data']
    execute_statistics_mean.optional_params = []
    execute_statistics_mean.should_respect_args_number = True

    def execute_statistics_geometric_mean(self, exec_ctx: Context):
        """Returns the geometric mean of a statistical series"""
        # Params:
        # * data
        data = exec_ctx.symbol_table.get('data')  # we get the data
        if not isinstance(data, List):  # the data must be a list
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
            if e.value < 0:
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in module function 'statistics_geometric_mean' must be a list of "
                    f"positive numbers.",
                    exec_ctx
                ))
            data_.append(e.value)

        if len(data_) == 0:  # data must not be empty
            return RTResult().failure(RTStatisticsError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_geometric_mean' must not be empty.",
                exec_ctx
            ))

        try:
            geometric_mean_ = statistics.geometric_mean(data_)  # we try to calculate the geometric mean
        except Exception as exception:
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"python statistics.geometric_mean() crashed with this error: "
                f"{exception.__class__.__name__}: {exception}.\n"
                f"PLEASE REPORT THIS BUG BY FOLLOWING THIS LINK: https://jd-develop.github.io/nougaro/bugreport.html !",
                exec_ctx
            ))

        return RTResult().success(Number(geometric_mean_))

    execute_statistics_geometric_mean.param_names = ['data']
    execute_statistics_geometric_mean.optional_params = []
    execute_statistics_geometric_mean.should_respect_args_number = True

    def execute_statistics_harmonic_mean(self, exec_ctx: Context):
        """Returns the harmonic mean of a statistical series"""
        # Params:
        # * data
        # Optional params:
        # * weights
        data = exec_ctx.symbol_table.get('data')  # we get the data
        if not isinstance(data, List):  # the data must be a list
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_harmonic_mean' must be a list of numbers.",
                exec_ctx
            ))

        weights = exec_ctx.symbol_table.get('weights')  # we get the list of weights
        if weights is not None and not isinstance(weights, List):  # if the weights list is defined but not a list
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "second argument of built-in module function 'statistics_harmonic_mean' must be a list of numbers.",
                exec_ctx
            ))

        if weights is not None and len(weights.elements) != len(data.elements):
            # if the weights list is defined but doesn't match with the data
            return RTResult().failure(RTIndexError(
                data.pos_start, weights.pos_end,
                "the two arguments of built-in module function 'statistics_harmonic_mean' must have the same length.",
                exec_ctx
            ))

        data_ = []
        for e in data.elements:
            if not isinstance(e, Number):  # the data must contain only numbers
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in module function 'statistics_harmonic_mean' must be a list of positive"
                    f" numbers, not {e.type_}.",
                    exec_ctx
                ))
            if e.value < 0:  # the data must contain only positive numbers
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    "first argument of built-in module function 'statistics_harmonic_mean' must be a list of "
                    "positives numbers.",
                    exec_ctx
                ))
            data_.append(e.value)

        if len(data_) == 0:  # data must not be empty
            return RTResult().failure(RTStatisticsError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_harmonic_mean' must not be empty.",
                exec_ctx
            ))

        if weights is not None:  # if there is weights
            weights_ = []
            for e in weights.elements:
                if not isinstance(e, Number):  # a weight must be a positive number
                    return RTResult().failure(RTTypeError(
                        e.pos_start, e.pos_end,
                        f"first argument of built-in module function 'statistics_harmonic_mean' must be a list of "
                        f"positive numbers, not {e.type_}.",
                        exec_ctx
                    ))
                if e.value < 0:  # a weight must be a positive number
                    return RTResult().failure(RTTypeError(
                        e.pos_start, e.pos_end,
                        "first argument of built-in module function 'statistics_harmonic_mean' must be a list of "
                        "positives numbers.",
                        exec_ctx
                    ))
                weights_.append(e.value)
        else:  # weights list is not defined, so all the weights are 1
            weights_ = None

        try:  # we try to calculate the harmonic mean
            if weights_ is None:  # weights aren't defined
                harmonic_mean_ = statistics.harmonic_mean(data_)
            else:  # they are
                harmonic_mean_ = statistics.harmonic_mean(data_, weights=weights_)
        except Exception as exception:
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"python statistics.harmonic_mean() crashed with this error: "
                f"{exception.__class__.__name__}: {exception}.\n"
                f"PLEASE REPORT THIS BUG BY FOLLOWING THIS LINK: https://jd-develop.github.io/nougaro/bugreport.html !",
                exec_ctx
            ))

        return RTResult().success(Number(harmonic_mean_))

    execute_statistics_harmonic_mean.param_names = ['data']
    execute_statistics_harmonic_mean.optional_params = ['weights']
    execute_statistics_harmonic_mean.should_respect_args_number = True

    def execute_statistics_median(self, exec_ctx: Context):
        """Calculates the median of a statistical series"""
        # Params:
        # * data
        data = exec_ctx.symbol_table.get('data')  # we get the data
        if not isinstance(data, List):  # data must be a list
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_median' must be a list of numbers.",
                exec_ctx
            ))

        data_ = []
        for e in data.elements:
            if not isinstance(e, Number):  # data must contain only numbers
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in module function 'statistics_median' must be a list of numbers, not "
                    f"{e.type_}.", exec_ctx
                ))
            data_.append(e.value)

        if len(data_) == 0:  # data must not be empty
            return RTResult().failure(RTStatisticsError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_median' must not be empty.",
                exec_ctx
            ))

        try:  # we try to calculate the median
            median_ = statistics.median(data_)
        except statistics.StatisticsError as exception:
            return RTResult().failure(RTStatisticsError(
                self.pos_start, self.pos_end, str(exception) + '.', exec_ctx
            ))

        return RTResult().success(Number(median_))

    execute_statistics_median.param_names = ['data']
    execute_statistics_median.optional_params = []
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

    # THAT WAS THE DISCLAIMER BEFORE THE DECLARATION OF PYTHON statistics.quantiles FUNCTION :)

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

        data = exec_ctx.symbol_table.get('data')  # we get the data
        if not isinstance(data, List):  # the data must be a list
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_quantiles' must be a list of numbers.",
                exec_ctx
            ))

        n = exec_ctx.symbol_table.get('n')  # we get 'n' (the number of quantiles we want)
        if n is None:  # if it's not defined, we want quartiles by default
            n = Number(4)

        if not isinstance(n, Number):  # 'n' must be a number
            return RTResult().failure(RTTypeError(
                n.pos_start, n.pos_end,
                "second argument of built-in module function 'statistics_quantiles' must be a number.",
                exec_ctx
            ))

        if n.value < 1:  # 'n' must be at least 1
            return RTResult().failure(RTStatisticsError(
                n.pos_start, n.pos_end,
                "second argument of built-in module function 'statistics_quantiles' must be at least 1.",
                exec_ctx
            ))

        method = exec_ctx.symbol_table.get('method')  # we get the method we use
        if method is None:
            method = String('exclusive')  # if the method is not defined we use the exclusive method

        if not isinstance(method, String):  # the method must be a string
            return RTResult().failure(RTTypeError(
                method.pos_start, method.pos_end,
                "third argument of built-in module function 'statistics_quantiles' must be a str.",
                exec_ctx
            ))

        if method.value not in ['exclusive', 'inclusive']:  # the method should be "inclusive" or "exclusive"
            return RTResult().failure(RTStatisticsError(
                method.pos_start, method.pos_end,
                f"unknown method: {method.value}.",
                exec_ctx
            ))

        data_ = []
        for e in data.elements:
            if not isinstance(e, Number):  # the data must contain only numbers
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in module function 'statistics_quantiles' must be a list of numbers, not "
                    f"{e.type_}.", exec_ctx
                ))
            data_.append(e.value)

        if len(data_) in [0, 1]:
            return RTResult().failure(RTStatisticsError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_median' must have at least two elements.",
                exec_ctx
            ))

        try:  # we try to calculate quantiles
            quantiles_ = statistics.quantiles(data_, n=n.value, method=method.value)
        except statistics.StatisticsError as exception:
            return RTResult().failure(RTStatisticsError(
                self.pos_start, self.pos_end, str(exception) + '.', exec_ctx
            ))

        return RTResult().success(List(quantiles_))

    execute_statistics_quantiles.param_names = ['data']
    execute_statistics_quantiles.optional_params = []
    execute_statistics_quantiles.should_respect_args_number = True
    
    def execute_statistics_scope(self, exec_ctx: Context):
        """Returns the scope of a list, i.e. the difference between the max and the min value."""
        # Params:
        # * data
        data = exec_ctx.symbol_table.get('data')  # we get the data
        if not isinstance(data, List):  # data must be a list
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_scope' must be a list of numbers.",
                exec_ctx
            ))

        data_ = []
        for e in data.elements:
            if not isinstance(e, Number):  # data must contain only numbers
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in module function 'statistics_scope' must be a list of numbers, not "
                    f"{e.type_}.", exec_ctx
                ))
            data_.append(e.value)

        if len(data_) < 1:  # data must not be empty
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_scope' must not be empty.", exec_ctx
            ))

        scope = max(data_) - min(data_)  # we calculate the scope
        return RTResult().success(Number(scope))

    execute_statistics_scope.param_names = ['data']
    execute_statistics_scope.optional_params = []
    execute_statistics_scope.should_respect_args_number = True

    def execute_statistics_mode(self, exec_ctx: Context):
        """The mode of a list, i.e. the most common value."""
        # Params:
        # * data
        data = exec_ctx.symbol_table.get('data')  # we get the data
        if not isinstance(data, List):  # the data must be a list
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_mode' must be a list of numbers.",
                exec_ctx
            ))

        data_ = []
        for e in data.elements:
            if not isinstance(e, Number):  # the data must contain only numbers
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in module function 'statistics_mode' must be a list of numbers, not "
                    f"{e.type_}.", exec_ctx
                ))
            data_.append(e.value)

        if len(data_) < 1:  # the data must not be empty
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_mode' must not be empty.", exec_ctx
            ))

        mode = statistics.mode(data_)  # we calculate the mode
        return RTResult().success(Number(mode))

    execute_statistics_mode.param_names = ['data']
    execute_statistics_mode.optional_params = []
    execute_statistics_mode.should_respect_args_number = True

    def execute_statistics_multimode(self, exec_ctx: Context):
        """The list of the modes of a list/str, i.e. the most common values."""
        # Params:
        # * data
        data = exec_ctx.symbol_table.get('data')  # we get the data
        if not (isinstance(data, List) or isinstance(data, String)):  # we check if the data is a list or a str
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in module function 'statistics_multimode' must be a list or a str.",
                exec_ctx
            ))

        if isinstance(data, List):
            data_ = []
            for e in data.elements:
                if not (isinstance(e, Number) or isinstance(e, String)):  # data must contain only str and nums
                    return RTResult().failure(RTTypeError(
                        e.pos_start, e.pos_end,
                        f"first argument of built-in module function 'statistics_multimode' must be a list that does"
                        f" not contains {e.type_}, or a str.",
                        exec_ctx
                    ))
                data_.append(e.value)
        elif isinstance(data, String):
            data_ = data.value
        else:
            # i.d.k. why I put an 'else', but it's funny to put an Easter Egg to people that read the code :)
            # -Jean Dubois
            raise NotImplementedError("How the f*** did this error happened? This is not possible!")

        multimode = statistics.multimode(data_)  # we calculate the multimode
        multimode_ = []
        for e in multimode:
            multimode_.append(py2noug(e))  # it converts python types to nougaro values
        return RTResult().success(List(multimode_))

    execute_statistics_multimode.param_names = ['data']
    execute_statistics_multimode.optional_params = []
    execute_statistics_multimode.should_respect_args_number = True


WHAT_TO_IMPORT = {  # what are the new entries in the symbol table when the module is imported
    # functions
    "mean": Statistics("mean"),
    "geometric_mean": Statistics("geometric_mean"),
    "harmonic_mean": Statistics("harmonic_mean"),
    "median": Statistics("median"),
    "quantiles": Statistics("quantiles"),
    "scope": Statistics("scope"),
    "mode": Statistics("mode"),
    "multimode": Statistics("multimode"),
}
