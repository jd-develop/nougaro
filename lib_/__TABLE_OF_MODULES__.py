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
import lib_.math_
import lib_.random_
import lib_.statistics_
import lib_.time_
# built-in python imports
# no imports

TABLE_OF_MODULES = {  # all the modules with all their public functions and constants
    "math": lib_.math_.WHAT_TO_IMPORT,
    "random": lib_.random_.WHAT_TO_IMPORT,
    "statistics": lib_.statistics_.WHAT_TO_IMPORT,
    "time": lib_.time_.WHAT_TO_IMPORT
}
