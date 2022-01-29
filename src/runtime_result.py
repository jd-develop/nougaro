#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# NO IMPORTS

# ##########
# RUNTIME RESULT
# ##########
class RTResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, result):
        if result.error is not None:
            self.error = result.error
        return result.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self
