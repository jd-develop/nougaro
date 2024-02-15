#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# __future__ import (must be first)
from __future__ import annotations
# nougaro modules imports
from src.parser.nodes import Node
from src.errors.errors import Error


# ##########
# PARSE RESULT
# ##########
class ParseResult:
    """Result of parsed tokens, with a parent node."""
    def __init__(self):
        self.error: Error | None = None  # any error that may have been encountered
        self.node: Node | list[Node] | None = None  # parent node of the code (the parent node is a ListNode)
        self.advance_count = 0
        self.to_reverse_count = 0

    def __repr__(self):
        return str(self.node)

    def register_advancement(self):
        """Register an advancement of 1 token"""
        self.advance_count += 1

    def register(self, result: ParseResult):
        """Register a node"""
        self.advance_count += result.advance_count
        if result.error is not None:
            self.error = result.error
        return result.node

    def try_register(self, result: ParseResult):
        """Try register a node"""
        if result.error is not None:
            self.to_reverse_count = result.advance_count
            return None
        return self.register(result)

    def success(self, node: Node | list[Node]):
        """Set self.node"""
        self.node = node
        return self

    def failure(self, error: Error | None):
        """Set self.error"""
        if self.error is None or self.advance_count == 0:
            self.error = error
        return self
