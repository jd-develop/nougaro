#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2022  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# NO IMPORTS

"""File for token types list. For Token class, please refer to ./tokens.py"""

# list of all the tokens
TT_NEWLINE = 'new line'       # new line

TT_INT = 'int'                # integer, corresponds to python int
TT_FLOAT = 'float'            # float number, corresponds to python float
TT_STRING = 'str'             # string type, corresponds to python str
TT_IDENTIFIER = 'identifier'  # Identifier of a var name
TT_KEYWORD = 'keyword'        # Keyword, like "var"

TT_PLUS = '+'                 # +
TT_MINUS = '-'                # -
TT_MUL = '*'                  # *
TT_DIV = '/'                  # /
TT_POW = '^'                  # ^
TT_PERC = '%'                 # %
TT_FLOORDIV = '//'            # //

TT_TO = '>>'                  # >>
TT_TO_AND_OVERWRITE = '!>>'   # !>>

TT_EQ = '='                   # =
TT_PLUSEQ = '+='              # +=
TT_MINUSEQ = '-='             # -=
TT_MULTEQ = '*='              # *=
TT_DIVEQ = '/='               # /=
TT_POWEQ = '^='               # ^=
TT_PERCEQ = '%='              # %=
TT_FLOORDIVEQ = '//='         # //=
TT_OREQ = "||="               # ||=
TT_ANDEQ = "&&="              # &&=
TT_XOREQ = "^^^="             # ^^^=
TT_BITWISEOREQ = "|="         # |=
TT_BITWISEANDEQ = "&="        # &=
TT_BITWISEXOREQ = "^^="       # ^^=
TT_EEEQ = "==="               # ===
TT_LTEEQ = "<=="              # <==
TT_GTEEQ = ">=="              # >==
TT_LTEQ = "<<="               # <<=
TT_GTEQ = ">>="               # >>=

TT_BITWISEOR = '|'            # |
TT_BITWISEAND = '&'           # &
TT_BITWISEXOR = '^^'          # ^^
TT_BITWISENOT = '~'           # ~

TT_EE = '=='                  # ==
TT_NE = '!='                  # !=
TT_LT = '<'                   # <
TT_GT = '>'                   # >
TT_LTE = '<='                 # <=
TT_GTE = '>='                 # >=

TT_RPAREN = ')'               # )
TT_LPAREN = '('               # (
TT_RSQUARE = ']'              # ]
TT_LSQUARE = '['              # [

TT_COMMA = ','                # ,
TT_ARROW = '->'               # ->
TT_INTERROGATIVE_PNT = '?'    # ?

TT_EOF = 'end of file'        # end of file

KEYWORDS = [                  # List of all the keywords (TT_KEYWORD)
    # basic keywords
    'var',
    'del',
    'end',
    # boolean
    'and',
    'or',
    'not',
    'xor',
    # tests
    'if',
    'then',
    'elif',
    'else',
    'in',
    # loops
    'for',
    'to',
    'step',
    'while',
    'do',
    'loop',
    'break',
    'continue',
    # functions
    'def',
    'return',
    # modules
    'import',
    # files
    'write',
    'read',
    # assertion
    'assert',
]

TOKENS_TO_QUOTE = [  # list of all the tokens that needs "'" when there are printed (e.g. in an error)
    TT_PLUS,
    TT_MINUS,
    TT_MUL,
    TT_DIV,
    TT_POW,
    TT_PERC,
    TT_FLOORDIV,
    TT_EQ,
    TT_PLUSEQ,
    TT_MINUSEQ,
    TT_MULTEQ,
    TT_DIVEQ,
    TT_POWEQ,
    TT_PERCEQ,
    TT_FLOORDIVEQ,
    TT_ANDEQ,
    TT_OREQ,
    TT_XOREQ,
    TT_BITWISEOREQ,
    TT_BITWISEANDEQ,
    TT_BITWISEXOREQ,
    TT_BITWISEAND,
    TT_BITWISEOR,
    TT_BITWISEXOR,
    TT_RPAREN,
    TT_LPAREN,
    TT_RSQUARE,
    TT_LSQUARE,
    TT_EE,
    TT_NE,
    TT_LT,
    TT_GT,
    TT_LTE,
    TT_GTE,
    TT_COMMA,
    TT_ARROW,
    TT_EEEQ,
    TT_LTEEQ,
    TT_GTEEQ,
    TT_LTEQ,
    TT_GTEQ,
    TT_TO,
    TT_TO_AND_OVERWRITE
]

EQUALS = [  # all the equal tokens ('=', '+=', ...) but not the equal tokens for tests ('==', '!=', ...)
    TT_EQ,
    TT_PLUSEQ,
    TT_MINUSEQ,
    TT_MULTEQ,
    TT_DIVEQ,
    TT_POWEQ,
    TT_FLOORDIVEQ,
    TT_PERCEQ,
    TT_OREQ,
    TT_ANDEQ,
    TT_XOREQ,
    TT_BITWISEANDEQ,
    TT_BITWISEOREQ,
    TT_BITWISEXOREQ,
    TT_EEEQ,
    TT_LTEEQ,
    TT_GTEEQ,
    TT_LTEQ,
    TT_GTEQ
]
