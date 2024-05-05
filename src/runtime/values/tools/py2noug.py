#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.lexer.position import Position as _Position, DEFAULT_POSITION
from src.misc import is_num
from src.runtime.values.basevalues.basevalues import String, Number, List, Value, NoneValue
# built-in python imports
from typing import Any


# This next line should be uncommented when the project (fully) switches to python 3.12, and the type of the "value"
# argument in the "py2noug" function should be defined as "val"
# (todo)
# type val = Value | str | int | float | bool | list[val] | dict[val, val] | None
def py2noug(
        value: Value | str | int | float | bool | list[Any] | dict[Any, Any] | tuple[Any, ...] | None,
        pos_start: _Position, pos_end: _Position
) -> Value:
    """Converts python values to nougaro ones"""
    if isinstance(value, Value):
        return value
    elif isinstance(value, str):
        return String(value, pos_start, pos_end)
    elif is_num(value):
        # sometimes, type checking strict is very dumb
        assert isinstance(value, int) or isinstance(value, float)
        return Number(value, pos_start, pos_end)
    elif isinstance(value, bool):
        return Number(value, pos_start, pos_end)
    elif isinstance(value, list) or isinstance(value, tuple):
        list_ = list(value)  # we want a list instead of a tuple
        new_list: list[Value] = []
        for elt in list_:
            new_list.append(py2noug(elt, pos_start, pos_end))
        return List(new_list, pos_start, pos_end)
    elif isinstance(value, dict):
        list_ = list(value.items())
        new_list: list[Value] = []
        for elt in list_:
            new_list.append(py2noug(elt, pos_start, pos_end))
        return List(new_list, pos_start, pos_end)
    elif value is None:
        return NoneValue(pos_start, pos_end)
    else:
        return Value(pos_start, pos_end)  # we just return a base value if there is no equivalent...


# todo: move this to unittests
_list1: Value = List(
    [
        String("a", DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()),
        List([
            String("b", DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()),
            Number(12, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy())
            ], DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy())
    ], DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()
)
_list2: Value = List(
    [Number(13, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()),
     String("c", DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy())
    ], DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()
)
_list_to_comp_with: list[Value] = [
    _list1,
    _list2
]

_test_, _err = py2noug(
    {"a": ["b", 12], 13: "c"}, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()
).get_comparison_eq(
    List(_list_to_comp_with, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy())
)
assert _test_ is not None
assert _test_.is_true()
assert _err is None


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
