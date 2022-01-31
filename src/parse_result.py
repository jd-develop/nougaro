#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# NO IMPORTS

# ##########
# PARSE RESULT
# ##########
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0
        self.to_reverse_count = 0

    def __repr__(self):
        return str(self.node)

    def register_advancement(self):
        self.advance_count += 1

    def register(self, result):
        self.advance_count += result.advance_count
        if result.error is not None:
            self.error = result.error
        return result.node

    def try_register(self, result):
        if result.error is not None:
            self.to_reverse_count = result.advance_count
            return None
        return self.register(result)

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if self.error is None or self.advance_count == 0:
            self.error = error
        return self
