#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.lexer.position import Position, DEFAULT_POSITION
from src.runtime.context import Context
from src.runtime.values.basevalues.value import Value
from src.runtime.runtime_result import RTResult
from src.runtime.values.basevalues.basevalues import List, Number, String
from src.errors.errors import RTTypeError, RunTimeError
from src.runtime.values.tools.py2noug import noug2py
# built-in python imports
from typing import Coroutine, Any
import sys


def _get_comparison_gt(list_to_sort_: list[Value], index_: int) -> tuple[Number, None] | tuple[None, RunTimeError]:
    if index_ + 1 < len(list_to_sort_):
        comp, error_ = list_to_sort_[index_].get_comparison_gt(list_to_sort_[index_ + 1])
        if error_ is not None:
            return None, error_
        else:
            assert isinstance(comp, Number)
    else:
        comp = Number(False, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy())
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


def _true_list_copy(list_to_copy: list[Value]) -> list[Value]:
    """Return a copy of the original list, where each elementn is a copy"""
    new_list: list[Value] = []
    for value in list_to_copy:
        new_list.append(value.copy())
    return new_list


def _slow_sort(list_to_sort: list[Value], start_idx: int, end_idx: int,
               n_th_element: int) -> None | RunTimeError:
    """Sorts list_to_sort in place, from start_idx to end_idx. If n_th_element
    is >0, prints “n elements sorted” when the n-th element is sorted, then
    calls the recursive sort with n_th_element+1"""
    if start_idx >= end_idx:
        return

    middle_idx = (start_idx+end_idx) // 2
    _slow_sort(list_to_sort, start_idx, middle_idx, 0)
    _slow_sort(list_to_sort, middle_idx+1, end_idx, 0)
    comp, error_ = list_to_sort[middle_idx].get_comparison_gt(list_to_sort[end_idx])
    if error_ is not None:
        return error_
    assert comp is not None
    if comp.is_true():
        list_to_sort[end_idx], list_to_sort[middle_idx] = list_to_sort[middle_idx], list_to_sort[end_idx]

    n_th_element_plus_1 = 0
    if n_th_element > 0:
        print(f"(slow sort) {n_th_element} elements sorted.")
        n_th_element_plus_1 = n_th_element + 1
    _slow_sort(list_to_sort, start_idx, end_idx-1, n_th_element_plus_1)


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
        sorted_ = _true_list_copy(list_to_sort)
        for i in range(len(sorted_)):
            if i == len(sorted_):
                break

            comparison, error = _get_comparison_gt(sorted_, i)
            if error is not None:
                return result.failure(error)

            assert comparison is not None

            while i + 1 < len(sorted_) and comparison.is_true():
                sorted_.pop(i + 1)
                comparison, error = _get_comparison_gt(sorted_, i)
                if error is not None:
                    return result.failure(error)
                assert comparison is not None

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
        sorted_ = _true_list_copy(list_to_sort)
        is_sorted_, error = _is_sorted(sorted_)
        if error is not None:
            return result.failure(error)
        while not is_sorted_:
            is_sorted_, error = _is_sorted(sorted_)
            if error is not None:
                return result.failure(error)
    elif mode == "panic":
        sorted_ = _true_list_copy(list_to_sort)
        is_sorted_, error = _is_sorted(sorted_)
        if error is not None:
            return result.failure(error)
        if not is_sorted_:
            if sys.platform == "win32":  # Windows does not support illegal hardware instructions
                # this causes a segfault
                a = map(str, sorted_)
                for i in range(1000000):
                    a = map(str, a)
                a = list(a)
            else:
                # this causes an illegal hardware instruction
                from ctypes import CFUNCTYPE, addressof, c_void_p
                from mmap import mmap, PAGESIZE, PROT_READ, PROT_WRITE, PROT_EXEC
                buf = mmap(-1, PAGESIZE, prot=PROT_READ | PROT_WRITE | PROT_EXEC)
                buf.write(b'\x0f\x04')
                CFUNCTYPE(c_void_p)(addressof(c_void_p.from_buffer(buf)))()
    elif mode == "slow" or mode == "slow-verbose":  # slowsort
        sorted_ = _true_list_copy(list_to_sort)
        _slow_sort(sorted_, 0, len(sorted_)-1, int(mode == "slow-verbose"))
    else:  # mode is none of the above
        return result.failure(RunTimeError(
            mode_noug.pos_start, mode_noug.pos_end,
            "this mode does not exist. Available modes:\n"
            "    * 'timsort' (default),\n"
            "    * 'miracle',\n"
            "    * 'panic',\n"
            "    * 'sleep',\n"
            "    * 'slow',\n"
            "    * 'stalin'.",
            exec_ctx, origin_file="src.runtime.values.functions.builtin_function.BuiltInFunction.execute_sort"
        ))

    return result.success(List(sorted_, pos_start, pos_end))
