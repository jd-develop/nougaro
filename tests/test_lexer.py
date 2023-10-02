#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
import src.lexer.lexer
import src.errors.errors
import src.lexer.position
# other tests files imports
# python imports
import unittest


class TestLexer(unittest.TestCase):
    def test_invalid_char(self):
        lx = src.lexer.lexer.Lexer("", "«")
        tokens, error = lx.make_tokens()
        pos = src.lexer.position.Position(0, 0, 0, "", "«")
        expected_error = src.errors.errors.IllegalCharError(
            pos, pos.copy().advance(),
            "'«' is an illegal character (U+AB, LEFT-POINTING DOUBLE ANGLE QUOTATION MARK)"
        )

        self.assertEqual(tokens, [])
        self.assertEqual(error.as_string(), expected_error.as_string())
