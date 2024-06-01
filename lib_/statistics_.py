#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
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

__LIB_VERSION__ = 2


class RTStatisticsError(RunTimeError):
    """StatisticsError is an error that can be triggered ONLY via functions in this module."""
    def __init__(self, pos_start: Position, pos_end: Position, details: str, context: Context,
                 origin_file: str = "lib_.statistics_"):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="StatisticsError",
                         origin_file=origin_file)


class Statistics(ModuleFunction):
    """ Statistics module """
    functions: dict[str, BuiltinFunctionDict] = {}

    def __init__(self, name: str):
        super().__init__("statistics", name, functions=self.functions)

    def copy(self):
        """Return a copy of self"""
        copy = Statistics(self.name)
        return self.set_context_and_pos_to_a_copy(copy)
    
    def is_eq(self, other: Value):
        return isinstance(other, Statistics) and self.name == other.name

    # =========
    # FUNCTIONS
    # =========
    def execute_statistics_mean(self, exec_ctx: Context):
        """Returns the mean of a statistical series"""
        # Params:
        # * data
        assert exec_ctx.symbol_table is not None
        data = exec_ctx.symbol_table.getf('data')  # we get the data
        if not isinstance(data, List):  # we check if the data is under the form of a list
            assert data is not None
            return RTResult().failure(RTTypeErrorF(
                data.pos_start, data.pos_end, "first", "statistics.mean", "list", data,
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_mean"
            ))

        data_: list[int | float] = []
        for e in data.elements:
            if not isinstance(e, Number):  # the data must contain only numbers
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in function 'statistics.mean' must be a list of numbers, but found an"
                    f" element of type '{e.type_}'.",
                    exec_ctx, "lib_.statistics_.Statistics.execute_statistics_mean"
                ))
            data_.append(e.value)

        if len(data_) == 0:  # data must not be empty
            return RTResult().failure(RTStatisticsError(
                data.pos_start, data.pos_end,
                "first argument of built-in function 'statistics.mean' must not be empty.",
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_mean"
            ))

        try:
            mean_ = statistics.mean(data_)  # we try to calculate the mean of our list
        except statistics.StatisticsError as exception:
            return RTResult().failure(RTStatisticsError(
                self.pos_start, self.pos_end, str(exception) + '.', exec_ctx
            ))

        return RTResult().success(Number(mean_, self.pos_start, self.pos_end))

    functions["mean"] = {
        "function": execute_statistics_mean,
        "param_names": ["data"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_statistics_geometric_mean(self, exec_ctx: Context):
        """Returns the geometric mean of a statistical series"""
        # Params:
        # * data
        assert exec_ctx.symbol_table is not None
        data = exec_ctx.symbol_table.getf('data')  # we get the data
        if not isinstance(data, List):  # the data must be a list
            assert data is not None
            return RTResult().failure(RTTypeErrorF(
                data.pos_start, data.pos_end, "first", "statistics.geometric_mean", "list", data,
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_geometric_mean"
            ))

        data_: list[int | float] = []
        for e in data.elements:
            if not isinstance(e, Number):
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in function 'statistics.geometric_mean' must be a list of "
                    f"positive numbers, but found an element of type '{e.type_}'.",
                    exec_ctx, "lib_.statistics_.Statistics.execute_statistics_geometric_mean"
                ))
            if e.value < 0:
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in function 'statistics.geometric_mean' must be a list of "
                    f"positive numbers, but found a negative number of value {e.value}.",
                    exec_ctx, "lib_.statistics_.Statistics.execute_statistics_geometric_mean"
                ))
            data_.append(e.value)

        if len(data_) == 0:  # data must not be empty
            return RTResult().failure(RTStatisticsError(
                data.pos_start, data.pos_end,
                "first argument of built-in function 'statistics.geometric_mean' must not be empty.",
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_geometric_mean"
            ))

        try:
            geometric_mean_ = statistics.geometric_mean(data_)  # we try to calculate the geometric mean
        except Exception as exception:
            return RTResult().failure(RunTimeError(
                self.pos_start, self.pos_end,
                f"python statistics.geometric_mean() crashed with this error: "
                f"{exception.__class__.__name__}: {exception}.\n"
                f"PLEASE REPORT THIS BUG BY FOLLOWING THIS LINK: https://jd-develop.github.io/nougaro/bugreport.html!",
                exec_ctx, origin_file="lib_.statistics_.Statistics.execute_statistics_geometric_mean"
            ))

        return RTResult().success(Number(geometric_mean_, self.pos_start, self.pos_end))

    functions["geometric_mean"] = {
        "function": execute_statistics_geometric_mean,
        "param_names": ["data"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_statistics_harmonic_mean(self, exec_ctx: Context):
        """Returns the harmonic mean of a statistical series"""
        # Params:
        # * data
        # Optional params:
        # * weights
        assert exec_ctx.symbol_table is not None
        data = exec_ctx.symbol_table.getf('data')  # we get the data
        if not isinstance(data, List):  # the data must be a list
            assert data is not None
            return RTResult().failure(RTTypeErrorF(
                data.pos_start, data.pos_end, "first", "statistics.harmonic_mean", "list", data,
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_harmonic_mean"
            ))

        weights = exec_ctx.symbol_table.getf('weights')  # we get the list of weights
        if weights is not None and not isinstance(weights, List):  # if the weights list is defined but not a list
            return RTResult().failure(RTTypeErrorF(
                weights.pos_start, weights.pos_end, "second", "statistics.harmonic_mean", "list", weights,
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_harmonic_mean"
            ))

        if weights is not None and len(weights.elements) != len(data.elements):
            # if the weights list is defined but doesn't match with the data
            return RTResult().failure(RTIndexError(
                data.pos_start, weights.pos_end,
                "the two arguments of built-in function 'statistics_harmonic_mean' must have the same length.",
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_harmonic_mean"
            ))

        data_: list[int | float] = []
        for e in data.elements:
            if not isinstance(e, Number):  # the data must contain only numbers
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in function 'statistics.harmonic_mean' must be a list of positive"
                    f" numbers, but found an element of type '{e.type_}'.",
                    exec_ctx, "lib_.statistics_.Statistics.execute_statistics_harmonic_mean"
                ))
            if e.value < 0:  # the data must contain only positive numbers
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    "first argument of built-in function 'statistics.harmonic_mean' must be a list of "
                    f"positives numbers, but found a negative element of value '{e.value}'.",
                    exec_ctx, "lib_.statistics_.Statistics.execute_statistics_harmonic_mean"
                ))
            data_.append(e.value)

        if len(data_) == 0:  # data must not be empty
            return RTResult().failure(RTStatisticsError(
                data.pos_start, data.pos_end,
                "first argument of built-in function 'statistics.harmonic_mean' must not be empty.",
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_harmonic_mean"
            ))

        if weights is not None:  # if there is weights
            weights_: list[int | float] | None = []
            for e in weights.elements:
                if not isinstance(e, Number):  # a weight must be a positive number
                    return RTResult().failure(RTTypeError(
                        e.pos_start, e.pos_end,
                        f"first argument of built-in function 'statistics.harmonic_mean' must be a list of "
                        f"positive numbers, but found an element of type '{e.type_}'.",
                        exec_ctx, "lib_.statistics_.Statistics.execute_statistics_harmonic_mean"
                    ))
                if e.value < 0:  # a weight must be a positive number
                    return RTResult().failure(RTTypeError(
                        e.pos_start, e.pos_end,
                        "first argument of built-in function 'statistics.harmonic_mean' must be a list of "
                        f"positives numbers, but found a negative element of value '{e.value}'.",
                        exec_ctx, "lib_.statistics_.Statistics.execute_statistics_harmonic_mean"
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
                exec_ctx, origin_file="lib_.statistics_.Statistics.execute_statistics_harmonic_mean"
            ))

        return RTResult().success(Number(harmonic_mean_, self.pos_start, self.pos_end))

    functions["harmonic_mean"] = {
        "function": execute_statistics_harmonic_mean,
        "param_names": ["data"],
        "optional_params": ["weights"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_statistics_median(self, exec_ctx: Context):
        """Calculates the median of a statistical series"""
        # Params:
        # * data
        assert exec_ctx.symbol_table is not None
        data = exec_ctx.symbol_table.getf('data')  # we get the data
        if not isinstance(data, List):  # data must be a list
            assert data is not None
            return RTResult().failure(RTTypeErrorF(
                data.pos_start, data.pos_end, "first", "statistics.median", "list", data,
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_median"
            ))

        data_: list[int | float] = []
        for e in data.elements:
            if not isinstance(e, Number):  # data must contain only numbers
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in function 'statistics.median' must be a list of numbers, not "
                    f"{e.type_}.", exec_ctx, "lib_.statistics_.Statistics.execute_statistics_median"
                ))
            data_.append(e.value)

        if len(data_) == 0:  # data must not be empty
            return RTResult().failure(RTStatisticsError(
                data.pos_start, data.pos_end,
                "first argument of built-in function 'statistics.median' must not be empty.",
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_median"
            ))

        try:  # we try to calculate the median
            median_ = statistics.median(data_)
        except statistics.StatisticsError as exception:
            return RTResult().failure(RTStatisticsError(
                self.pos_start, self.pos_end, str(exception) + '.', exec_ctx,
                "lib_.statistics_.Statistics.execute_statistics_median"
            ))

        return RTResult().success(Number(median_, self.pos_start, self.pos_end))

    functions["median"] = {
        "function": execute_statistics_median,
        "param_names": ["data"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

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
        # By default, n=4 and method='exclusive'

        assert exec_ctx.symbol_table is not None
        data = exec_ctx.symbol_table.getf('data')  # we get the data
        if not isinstance(data, List):  # the data must be a list
            assert data is not None
            return RTResult().failure(RTTypeErrorF(
                data.pos_start, data.pos_end, "first", "statistics.quantiles", "list", data,
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_quantiles"
            ))

        n = exec_ctx.symbol_table.getf('n')  # we get 'n' (the number of quantiles we want)
        if n is None:  # if it's not defined, we want quartiles by default
            n = Number(4, self.pos_start, self.pos_end)

        if not (isinstance(n, Number) and isinstance(n.value, int)):  # 'n' must be a number
            return RTResult().failure(RTTypeErrorF(
                n.pos_start, n.pos_end, "second", "statistics.quantiles", "int", n,
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_quantiles"
            ))

        if n.value < 1:  # 'n' must be at least 1
            return RTResult().failure(RTStatisticsError(
                n.pos_start, n.pos_end,
                "second argument of built-in function 'statistics.quantiles' must be greater than or equal to 1.",
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_quantiles"
            ))

        method = exec_ctx.symbol_table.getf('method')  # we get the method we use
        if method is None:
            method = String('exclusive', self.pos_start, self.pos_end)  # if the method is not defined we use the exclusive method

        if not isinstance(method, String):  # the method must be a string
            return RTResult().failure(RTTypeErrorF(
                method.pos_start, method.pos_end, "third", "statistics.quantiles", "str", method,
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_quantiles"
            ))

        method_name = method.value
        # the following is dumb but not as much as VScode type checking extension
        if method_name == "inclusive":
            method_name_correct = "inclusive"
        elif method_name == "exclusive":
            method_name_correct = "exclusive"
        else:
            return RTResult().failure(RTStatisticsError(
                method.pos_start, method.pos_end,
                f"unknown method: {method.value}.",
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_quantiles"
            ))

        data_: list[int | float] = []
        for e in data.elements:
            if not isinstance(e, Number):  # the data must contain only numbers
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in function 'statistics.quantiles' must be a list of numbers, but "
                    f"found an element of type '{e.type_}'.",
                    exec_ctx, "lib_.statistics_.Statistics.execute_statistics_quantiles"
                ))
            data_.append(e.value)

        if len(data_) in [0, 1]:
            return RTResult().failure(RTStatisticsError(
                data.pos_start, data.pos_end,
                "first argument of built-in function 'statistics.quantiles' must have at least two elements.",
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_quantiles"
            ))

        try:  # we try to calculate quantiles
            quantiles_ = statistics.quantiles(data_, n=n.value, method=method_name_correct)
        except statistics.StatisticsError as exception:
            return RTResult().failure(RTStatisticsError(
                self.pos_start, self.pos_end, str(exception) + '.', exec_ctx,
                "lib_.statistics_.Statistics.execute_statistics_quantiles"
            ))

        new_quantiles = [py2noug(q, self.pos_start, self.pos_end) for q in quantiles_]
        return RTResult().success(List(new_quantiles, self.pos_start, self.pos_end))

    functions["quantiles"] = {
        "function": execute_statistics_quantiles,
        "param_names": ["data"],
        "optional_params": ["n", "method"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }
    
    def execute_statistics_scope(self, exec_ctx: Context):
        """Returns the scope of a list, i.e. the difference between the max and the min value."""
        # Params:
        # * data
        assert exec_ctx.symbol_table is not None
        data = exec_ctx.symbol_table.getf('data')  # we get the data
        if not isinstance(data, List):  # data must be a list
            assert data is not None
            return RTResult().failure(RTTypeErrorF(
                data.pos_start, data.pos_end, "first", "statistics.scope", "list", data,
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_scope"
            ))

        data_: list[int | float] = []
        for e in data.elements:
            if not isinstance(e, Number):  # data must contain only numbers
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in function 'statistics.scope' must be a list of numbers, but found an "
                    f"element of type '{e.type_}'.", exec_ctx, "lib_.statistics_.Statistics.execute_statistics_scope"
                ))
            data_.append(e.value)

        if len(data_) < 1:  # data must not be empty
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in function 'statistics.scope' must not be empty.", exec_ctx,
                "lib_.statistics_.Statistics.execute_statistics_scope"
            ))

        scope = max(data_) - min(data_)  # we calculate the scope
        return RTResult().success(Number(scope, self.pos_start, self.pos_end))

    functions["scope"] = {
        "function": execute_statistics_scope,
        "param_names": ["data"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_statistics_mode(self, exec_ctx: Context):
        """The mode of a list, i.e. the most common value."""
        # Params:
        # * data
        assert exec_ctx.symbol_table is not None
        data = exec_ctx.symbol_table.getf('data')  # we get the data
        if not isinstance(data, List):  # the data must be a list
            assert data is not None
            return RTResult().failure(RTTypeErrorF(
                data.pos_start, data.pos_end, "first", "statistics.mode", "list", data,
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_mode"
            ))

        data_: list[int | float] = []
        for e in data.elements:
            if not isinstance(e, Number):  # the data must contain only numbers
                return RTResult().failure(RTTypeError(
                    e.pos_start, e.pos_end,
                    f"first argument of built-in function 'statistics.mode' must be a list of numbers, but found an "
                    f"element of type '{e.type_}'.", exec_ctx, "lib_.statistics_.Statistics.execute_statistics_mode"
                ))
            data_.append(e.value)

        if len(data_) < 1:  # the data must not be empty
            return RTResult().failure(RTTypeError(
                data.pos_start, data.pos_end,
                "first argument of built-in function 'statistics.mode' must not be empty.", exec_ctx,
                "lib_.statistics_.Statistics.execute_statistics_mode"
            ))

        mode = statistics.mode(data_)  # we calculate the mode
        return RTResult().success(Number(mode, self.pos_start, self.pos_end))

    functions["mode"] = {
        "function": execute_statistics_mode,
        "param_names": ["data"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }

    def execute_statistics_multimode(self, exec_ctx: Context):
        """The list of the modes of a list/str, i.e. the most common values."""
        # Params:
        # * data
        assert exec_ctx.symbol_table is not None
        data = exec_ctx.symbol_table.getf('data')  # we get the data
        if not (isinstance(data, List) or isinstance(data, String)):  # we check if the data is a list or a str
            assert data is not None
            return RTResult().failure(RTTypeErrorF(
                data.pos_start, data.pos_end, "first", "statistics.multimode", "list", data,
                exec_ctx, "lib_.statistics_.Statistics.execute_statistics_multimode", or_="str"
            ))

        if isinstance(data, List):
            data_: list[int | float | str] | str = []
            for e in data.elements:
                if not (isinstance(e, Number) or isinstance(e, String)):  # data must contain only str and nums
                    return RTResult().failure(RTTypeError(
                        e.pos_start, e.pos_end,
                        f"first argument of built-in function 'statistics.multimode' must be a str, or a list that does"
                        f" not contains elements of type '{e.type_}'.",
                        exec_ctx, "lib_.statistics_.Statistics.execute_statistics_multimode"
                    ))
                data_.append(e.value)
        else:
            data_ = data.value

        multimode = statistics.multimode(data_)  # we calculate the multimode
        new_multimode = [py2noug(e, self.pos_start, self.pos_end) for e in multimode]
        return RTResult().success(List(new_multimode, self.pos_start, self.pos_end))

    functions["multimode"] = {
        "function": execute_statistics_multimode,
        "param_names": ["data"],
        "optional_params": [],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }


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
