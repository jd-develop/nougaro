#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.misc import is_num
from src.runtime.values.basevalues.basevalues import String, Number, List, Value, NoneValue
# built-in python imports
from typing import Any


# This next line should be uncommented when the project (fully) switches to python 3.12, and the type of the "value"
# argument in the "py2noug" function should be defined as "val"
# (todo)
# type val = Value | str | int | float | bool | list[val] | dict[val, val] | None
def py2noug(value: Value | str | int | float | bool | list[Any] | dict[Any, Any] | None) -> Value:
    """Converts python values to nougaro ones"""
    if isinstance(value, Value):
        return value
    elif isinstance(value, str):
        return String(value)
    elif is_num(value):
        # sometimes, type checking strict is very dumb
        assert isinstance(value, int) or isinstance(value, float)
        return Number(value)
    elif isinstance(value, bool):
        return Number(int(value))
    elif isinstance(value, list) or isinstance(value, tuple):
        list_ = list(value)  # we want a list instead of a tuple
        list_ = list(map(py2noug, list_))  # todo: when project fully switches to 3.12 remove this: # type: ignore
        return List(list_)
    elif isinstance(value, dict):
        list_ = list(value.items())
        list_ = list(map(py2noug, list_))  # todo: when project fully switches to 3.12 remove this: # type: ignore
        return List(list_)
    elif value is None:
        return NoneValue()
    else:
        return Value()  # we just return a base value if there is no equivalent...


# todo: move this to unittests
test_, err = py2noug(
    {"a": ["b", 12], 13: "c"}
).get_comparison_eq(
    List([
        List([String("a"), List([String("b"), Number(12)])]),
        List([Number(13), String("c")])
    ]))
assert test_ is not None
assert test_.is_true()


def noug2py(value: Value, none_instead_of_raw_value: bool = True) -> Any:
    """Converts nougaro values to python ones."""
    if isinstance(value, String) or isinstance(value, Number):
        return value.value
    elif isinstance(value, List):
        return [noug2py(e) for e in value.elements]
    elif isinstance(value, NoneValue):
        return None
    else:
        if none_instead_of_raw_value:
            return None
        else:
            return value
