#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports: NO IMPORTS
# built-in python imports
import pprint


# ##########
# RUNTIME RESULT
# ##########
class RTResult:
    """Result of a node interpretation"""
    def __init__(self):
        self.value = None  # result value
        self.function_return_value = None  # for FunctionNode : the value that the function returns
        self.error = None  # any error that can have been encountered while interpreting

        self.loop_should_continue = False  # there is a 'continue' statement
        self.loop_should_break = False  # there is a 'break' statement
        self.old_should_return = False  # The old value of self.should_return()

        self.reset()

    def reset(self):
        """Reset attrs to their default value"""
        self.value = None
        self.function_return_value = None
        self.error = None

        self.loop_should_continue = False
        self.loop_should_break = False
        self.old_should_return = False

    def register(self, result):
        """Register another result in this result"""
        if not self.old_should_return:  # True -> DON'T TOUCH IT, False -> change to the new
            self.old_should_return = self.should_return()

        # we copy the attrs of other result into the self attrs
        if result.error is not None:
            self.error = result.error
        else:
            self.error = None
        self.function_return_value = result.function_return_value
        self.loop_should_continue = result.loop_should_continue
        self.loop_should_break = result.loop_should_break

        return result.value  # we return the other result value

    def success(self, value):  # success, we clean up our attrs, we write the new value, and we return self
        self.reset()
        self.value = value
        return self

    def success_return(self, value):  # same as self.success for self.function_return_value
        self.reset()
        self.function_return_value = value
        return self

    def success_continue(self):  # same as self.success for self.loop_should_continue
        self.reset()
        self.loop_should_continue = True
        return self

    def success_break(self):  # same as self.success for self.loop_should_break
        self.reset()
        self.loop_should_break = True
        return self

    def failure(self, error):  # same as self.success for self.error
        self.reset()
        self.error = error
        return self

    def should_return(self) -> bool:  # if we should stop the interpretation because of an error, or a statement
        #                               (return, break, continue)
        return (
            self.error or
            self.function_return_value or
            self.loop_should_continue or
            self.loop_should_break
        )

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "RTResult: " + pprint.pformat(
            {"value": self.value,
             "function_return_value": self.function_return_value,
             "error": self.error,
             "loop_should_continue": self.loop_should_continue,
             "loop_should_break": self.loop_should_break,
             "old_should_return": self.old_should_return}
        )
