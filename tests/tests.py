#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
# other tests files imports
from tests.test_lexer import TestLexer
# python imports
import sys
import unittest


def suite():
    s = unittest.TestSuite()
    s.addTest(TestLexer('test_invalid_char'))
    s.addTest(TestLexer('test_identifiers_and_keywords'))
    return s


def run_tests():
    runner = unittest.TextTestRunner()
    return runner.run(suite())


if __name__ == "__main__":
    result = run_tests()
    if len(result.failures) != 0:
        sys.exit(1)
