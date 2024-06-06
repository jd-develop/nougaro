#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.lexer.position import Position
from src.runtime.context import Context
from src.runtime.values.basevalues.value import Value
from src.runtime.runtime_result import RTResult
from src.runtime.values.basevalues.basevalues import List, Number, String
from src.runtime.values.number_constants import FALSE
from src.errors.errors import RTTypeError, RunTimeError
from src.runtime.values.tools.py2noug import noug2py
# built-in python imports
from typing import Coroutine, Any


def _get_comparison_gt(list_to_sort_: list[Value], index_: int) -> tuple[Number, None] | tuple[None, RunTimeError]:
    if index_ + 1 < len(list_to_sort_):
        comp, error_ = list_to_sort_[index_].get_comparison_gt(list_to_sort_[index_ + 1])
        if error_ is not None:
            return None, error_
        else:
            assert isinstance(comp, Number)
    else:
        comp = FALSE.copy()
    return comp, None


def _is_sorted(list_to_sort: list[Value]) -> tuple[bool, None] | tuple[None, RunTimeError]:
    for i in range(len(list_to_sort)):
        if i+1 == len(list_to_sort):
            continue
        comp, error = _get_comparison_gt(list_to_sort, i)
        if error is not None:
            return None, error
        assert comp is not None
        if comp.is_true():
            return False, None
    return True, None


def sort(
        list_: List, mode_noug: String, result: RTResult, exec_ctx: Context,
        pos_start: Position, pos_end: Position
) -> RTResult:
    mode = mode_noug.value
    list_to_sort: list[Value] = list_.elements
    if mode == "timsort":  # default python sort algorithm
        try:
            sorted_ = sorted(list_to_sort, key=lambda val: noug2py(val, False))
        except TypeError as e:
            return result.failure(RTTypeError(
                list_.pos_start, list_.pos_end,
                str(e), exec_ctx,
                origin_file="src.runtime.values.functions.builtin_function.BuiltInFunction.execute_sort"
            ))
    elif mode == "stalin":  # stalin sort
        for i in range(len(list_to_sort)):
            if i == len(list_to_sort):
                break

            comparison, error = _get_comparison_gt(list_to_sort, i)
            if error is not None:
                return result.failure(error)
            
            assert comparison is not None

            while i + 1 < len(list_to_sort) and comparison.is_true():
                list_to_sort.pop(i + 1)
                comparison, error = _get_comparison_gt(list_to_sort, i)
                if error is not None:
                    return result.failure(error)
                assert comparison is not None

        sorted_ = list_to_sort  
    elif mode == "sleep" or mode == "sleep-verbose":  # sleep sort
        # sleep sort was implemented by Mistera. Please refer to him if you have any questions about it, as I
        # completely don’t have any ideas on how tf asyncio works
        import asyncio

        sorted_: list[Value] = []
        list_to_sort_only_nums: list[int] = []
        for i in list_to_sort:
            if not isinstance(i, Number) or not isinstance(i.value, int):
                return result.failure(RTTypeError(
                    i.pos_start, i.pos_end, 
                    f"sleep mode: expected list of int, but found {i.type_} inside the list.",
                    exec_ctx,
                    origin_file="src.runtime.values.functions.builtin_function.BuiltInFunction.execute_sort"
                ))
            if i.value < 0:
                return result.failure(RTTypeError(
                    i.pos_start, i.pos_end,
                    f"sleep mode: expected list of positive integers, but found negative integer {i.value} inside "
                    f"the list.",
                    exec_ctx,
                    origin_file="src.runtime.values.functions.builtin_function.BuiltInFunction.execute_sort"

                ))
            list_to_sort_only_nums.append(i.value)

        async def execute_coroutine_list(_list: list[Coroutine[Any, Any, None]]):
            await asyncio.gather(*_list)

        async def wait_and_append(i_: int):
            nonlocal sorted_
            await asyncio.sleep(i_)
            if mode == "sleep-verbose":
                print(f"(sleep sort) Currently appending {i_} to the final list.")
            sorted_.append(Number(i_, pos_start, pos_end))

        list_of_coroutines = [wait_and_append(i) for i in list_to_sort_only_nums]
        asyncio.run(execute_coroutine_list(list_of_coroutines))
    elif mode == "miracle":
        sorted_ = list_to_sort
        is_sorted_, error = _is_sorted(sorted_)
        if error is not None:
            return result.failure(error)
        while not is_sorted_:
            is_sorted_, error = _is_sorted(sorted_)
            if error is not None:
                return result.failure(error)
    elif mode == "panic":
        sorted_ = list_to_sort
        is_sorted_, error = _is_sorted(sorted_)
        if error is not None:
            return result.failure(error)
        if not is_sorted_:
            # this causes a segfault
            a = map(str, sorted_)
            for i in range(1000000):
                a = map(str, a)
            a = list(a)
    else:  # mode is none of the above
        return result.failure(RunTimeError(
            mode_noug.pos_start, mode_noug.pos_end,
            "this mode does not exist. Available modes:\n"
            "\t* 'timsort' (default),\n"
            "\t* 'stalin',\n"
            "\t* 'sleep',\n"
            "\t* 'miracle',\n"
            "\t* 'panic'.",
            exec_ctx, origin_file="src.runtime.values.functions.builtin_function.BuiltInFunction.execute_sort"
        ))

    return result.success(List(sorted_, pos_start, pos_end))
