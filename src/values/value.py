#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain

# IMPORTS
# nougaro modules imports
from src.context import Context
from src.runtime_result import RTResult
from src.errors import RunTimeError
# built-in python imports
# no imports


class Value:
    def __init__(self):
        self.pos_start = self.pos_end = self.context = None
        self.set_pos()
        self.set_context()
        self.type_ = "BaseValue"

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context: Context = None):
        self.context = context
        return self

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multiplied_by(self, other):
        return None, self.illegal_operation(other)

    def modded_by(self, other):
        """ Modulo """
        return None, self.illegal_operation(other)

    def floor_dived_by(self, other):
        """ Floor division """
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        return None, self.illegal_operation(other)

    def powered_by(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        return None, self.can_not_compare(other)

    def get_comparison_ne(self, other):
        return None, self.can_not_compare(other)

    def get_comparison_lt(self, other):
        return None, self.can_not_compare(other)

    def get_comparison_gt(self, other):
        return None, self.can_not_compare(other)

    def get_comparison_lte(self, other):
        return None, self.can_not_compare(other)

    def get_comparison_gte(self, other):
        return None, self.can_not_compare(other)

    def is_in(self, other):
        return None, self.can_not_be_in(other)

    def and_(self, other):
        return None, self.illegal_operation(other)

    def or_(self, other):
        return None, self.illegal_operation(other)

    def not_(self):
        return None, self.illegal_operation()

    def excl_or(self, other):
        """ Exclusive or """
        return None, self.illegal_operation(other)

    def execute(self, args, interpreter_, run):
        return RTResult().failure(self.illegal_operation())

    def abs_(self):
        return RTResult().failure(self.illegal_operation())

    def to_str_(self):
        return None, RTResult().failure(self.illegal_operation())

    def to_int_(self):
        return None, RTResult().failure(self.illegal_operation())

    def to_float_(self):
        return None, RTResult().failure(self.illegal_operation())

    def to_list_(self):
        return None, RTResult().failure(self.illegal_operation())

    def copy(self):
        print(self.context)
        print('NOUGARO INTERNAL ERROR : No copy method defined in Value.copy().\n'
              'Please report this bug at https://jd-develop.github.io/nougaro/redirect1.html with the information below'
              )
        raise Exception('No copy method defined in Value.copy().')

    @staticmethod
    def is_true():
        return False

    def illegal_operation(self, other=None):
        if other is None:
            return RunTimeError(
                self.pos_start, self.pos_end, f'illegal operation with {self.type_}.', self.context
            )
        return RunTimeError(
            self.pos_start, other.pos_end, f'illegal operation between {self.type_} and {other.type_}.', self.context
        )

    def can_not_compare(self, other):
        return RunTimeError(
            self.pos_start, other.pos_end, f'can not compare {self.type_} and {other.type_}.', self.context
        )

    def can_not_be_in(self, other):
        return RunTimeError(
            self.pos_start, other.pos_end, f'{other.type_} is not iterable or can not contain {self.type_}.',
            self.context
        )
