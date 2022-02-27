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
