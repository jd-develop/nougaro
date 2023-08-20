#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# no imports


def is_type(value, type_):
    """Types are 'BaseValue', 'str', 'int', 'float', 'list', 'module', 'constructor', 'object', 'NoneValue',
       'BaseFunction', 'func', 'built-in func'"""
    return value.type_ == type_


def is_n_num(value):
    return is_type(value, "int") or is_type(value, "float")