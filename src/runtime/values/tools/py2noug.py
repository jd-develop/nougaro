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
from src.runtime.values.basevalues.basevalues import *
# built-in python imports
from typing import Any


# This next line should be uncommented when the project (fully) switches to python 3.12, and the type of the "value"
# argument in the "py2noug" function should be defined as "val"
# (todo)
# type val = str | int | float | bool | list[val] | None
def py2noug(value: str | int | float | bool | list[Any] | None):
    """Converts python values to nougaro ones"""
    if isinstance(value, str):
        return String(value)
    elif is_num(value):
        # sometimes, type checking strict is very dumb
        assert isinstance(value, int) or isinstance(value, float)
        return Number(value)
    elif isinstance(value, bool):
        return Number(int(value))
    elif isinstance(value, list) or isinstance(value, tuple):
        list_ = list(value)  # we want a list instead of a tuple
        return List(list_)
    elif value is None:
        return NoneValue()
    else:
        return Value()  # we just return a base value if there is no equivalent...


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
