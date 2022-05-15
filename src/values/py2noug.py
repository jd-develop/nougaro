#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# IMPORTS
# nougaro modules imports
from src.misc import is_num
from src.values.basevalues import *
# built-in python imports
from typing import Any


def py2noug(value: Any):
    if isinstance(value, str):
        return String(value)
    elif is_num(value):
        return Number(value)
    elif isinstance(value, list) or isinstance(value, tuple):
        list_ = list(value)
        return List(list_)
    else:
        return Value()
