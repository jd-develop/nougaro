#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.lexer.position import DEFAULT_POSITION
from src.runtime.values.basevalues.basevalues import Number
# built-in python imports
# no imports

# this is the list of all pre-defined numbers
# some of them are in lib_.math_ (like PI, E, TAU or SQRT_PI)
NULL = Number(0, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy())
FALSE = Number(0, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy())
TRUE = Number(1, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy())
