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
        lx = src.lexer.lexer.Lexer("", "ç")
        tokens, error = lx.make_tokens()
        pos = src.lexer.position.Position(0, 0, 0, "", "ç")
        expected_error = src.errors.errors.IllegalCharError(
            pos, pos.copy().advance(),
            "'ç' is an illegal character (U+E7, LATIN SMALL LETTER C WITH CEDILLA)"
        )

        self.assertEqual(tokens, [])
        assert error is not None
        self.assertEqual(error.as_string(), expected_error.as_string())

    def test_identifiers_and_keywords(self):
        lx = src.lexer.lexer.Lexer("", "var identifier assert True")
        tokens, error = lx.make_tokens()
        self.assertIsNone(error)

        self.assertEqual(len(tokens), 5)
        for i in range(4):
            self.assertIsInstance(tokens[i], src.lexer.token.Token)
        self.assertTrue(tokens[0].matches(TT["KEYWORD"], "var"))
        self.assertTrue(tokens[1].matches(TT["IDENTIFIER"], "identifier"))
        self.assertTrue(tokens[2].matches(TT["KEYWORD"], "assert"))
        self.assertTrue(tokens[3].matches(TT["IDENTIFIER"], "True"))
        self.assertEqual(tokens[4].type, TT["EOF"])
