#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
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
# PARSE RESULT
# ##########
class ParseResult:
    """Result of parsed tokens, with a parent node."""
    def __init__(self):
        self.error = None  # any error that may have been encountered
        self.node = None  # parent node of the code (the parent node is a ListNode)
        self.advance_count = 0
        self.to_reverse_count = 0

    def __repr__(self):
        return str(self.node)

    def register_advancement(self):
        """Register an advancement of 1 token"""
        self.advance_count += 1

    def register(self, result):
        """Register a node"""
        self.advance_count += result.advance_count
        if result.error is not None:
            self.error = result.error
        return result.node

    def try_register(self, result):
        """Try register a node"""
        if result.error is not None:
            self.to_reverse_count = result.advance_count
            return None
        return self.register(result)

    def success(self, node):
        """Set self.node"""
        self.node = node
        return self

    def failure(self, error):
        """Set self.error"""
        if self.error is None or self.advance_count == 0:
            self.error = error
        return self
