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

# IMPORTS
# nougaro modules imports
from src.misc import is_num
from src.values.basevalues import *
# built-in python imports
from typing import Any


def py2noug(value: Any):
    """Converts python values to nougaro ones"""
    if isinstance(value, str):
        return String(value)
    elif is_num(value):
        return Number(value)
    elif isinstance(value, list) or isinstance(value, tuple):
        list_ = list(value)  # we want a list instead of a tuple
        return List(list_)
    elif value is None:
        return NoneValue()
    else:
        return Value()  # we just return a base value if there is no equivalent...
