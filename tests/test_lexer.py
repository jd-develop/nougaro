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
import src.lexer.token
from src.lexer.token_types import TT
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

    def test_identifiers_and_keywords(self):
        lx = src.lexer.lexer.Lexer("", "var identifier assert True")
        tokens, error = lx.make_tokens()
        self.assertIsNone(error)

        self.assertEqual(len(tokens), 5)
        for i in range(4):
            self.assertIsInstance(tokens[i], src.lexer.token.Token)
        self.assert_(tokens[0].matches(TT["KEYWORD"], "var"))
        self.assert_(tokens[1].matches(TT["IDENTIFIER"], "identifier"))
        self.assert_(tokens[2].matches(TT["KEYWORD"], "assert"))
        self.assert_(tokens[3].matches(TT["IDENTIFIER"], "True"))
        self.assert_(tokens[4].type == TT["EOF"])
