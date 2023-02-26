#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.misc import is_num
from src.runtime.values.basevalues.basevalues import *
# built-in python imports
from typing import Any


def py2noug(value: Any):
    """Converts python values to nougaro ones"""
    if isinstance(value, str):
        return String(value)
    elif is_num(value):
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


def noug2py(value: Any):
    """Converts nougaro values to python ones."""
    if isinstance(value, String) or isinstance(value, Number):
        return value.value
    elif isinstance(value, List):
        return value.elements
    elif isinstance(value, NoneValue):
        return None
    else:
        return None
