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

# NO IMPORTS

# ##########
# RUNTIME RESULT
# ##########
class RTResult:
    def __init__(self):
        self.value = None
        self.function_return_value = None
        self.error = None

        self.loop_should_continue = False
        self.loop_should_break = False

        self.reset()

    def reset(self):
        """Reset attrs to their default value"""
        self.value = None
        self.function_return_value = None
        self.error = None

        self.loop_should_continue = False
        self.loop_should_break = False

    def register(self, result):
        if result.error is not None:
            self.error = result.error
        else:
            self.error = None
        self.function_return_value = result.function_return_value
        self.loop_should_continue = result.loop_should_continue
        self.loop_should_break = result.loop_should_break
        return result.value

    def success(self, value):
        self.reset()
        self.value = value
        return self

    def success_return(self, value):
        self.reset()
        self.function_return_value = value
        return self

    def success_continue(self):
        self.reset()
        self.loop_should_continue = True
        return self

    def success_break(self):
        self.reset()
        self.loop_should_break = True
        return self

    def failure(self, error):
        self.reset()
        self.error = error
        return self

    def should_return(self):
        return (
            self.error or
            self.function_return_value or
            self.loop_should_continue or
            self.loop_should_break
        )
