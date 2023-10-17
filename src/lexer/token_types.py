#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# NO IMPORTS

"""File for token types list. For Token class, please refer to ./token.py"""

# dict of all the token types
TT = {
    "NEWLINE": 'new line',       # new line
    
    "INT": 'int',                # integer, corresponds to python int
    "FLOAT": 'float',            # float number, corresponds to python float
    "STRING": 'str',             # string type, corresponds to python str
    "IDENTIFIER": 'identifier',  # Identifier of a var name
    "KEYWORD": 'keyword',        # Keyword, like "var"
    "DOT": ".",                  # .

    "E_INFIX": "e",              # e infix in a number (123e12 is 123*10^12)

    "PLUS": '+',                 # +
    "MINUS": '-',                # -
    "MUL": '*',                  # *
    "DIV": '/',                  # /
    "POW": '^',                  # ^
    "PERC": '%',                 # %
    "FLOORDIV": '//',            # //
    
    "TO": '>>',                  # >>
    "TO_AND_OVERWRITE": '!>>',   # !>>
    
    "EQ": '=',                   # =
    "PLUSEQ": '+=',              # +=
    "MINUSEQ": '-=',             # -=
    "MULTEQ": '*=',              # *=
    "DIVEQ": '/=',               # /=
    "POWEQ": '^=',               # ^=
    "PERCEQ": '%=',              # %=
    "FLOORDIVEQ": '//=',         # //=
    "OREQ": "||=",               # ||=
    "ANDEQ": "&&=",              # &&=
    "XOREQ": "^^^=",             # ^^^=
    "BITWISEOREQ": "|=",         # |=
    "BITWISEANDEQ": "&=",        # &=
    "BITWISEXOREQ": "^^=",       # ^^=
    "EEEQ": "===",               # ===
    "LTEEQ": "<==",              # <==
    "GTEEQ": ">==",              # >==
    "LTEQ": "<<=",               # <<=
    "GTEQ": ">>=",               # >>=
    
    "BITWISEOR": '|',            # |
    "BITWISEAND": '&',           # &
    "BITWISEXOR": '^^',          # ^^
    "BITWISENOT": '~',           # ~
    
    "EE": '==',                  # ==
    "NE": '!=',                  # !=
    "LT": '<',                   # <
    "GT": '>',                   # >
    "LTE": '<=',                 # <=
    "GTE": '>=',                 # >=
    
    "RPAREN": ')',               # )
    "LPAREN": '(',               # (
    "RSQUARE": ']',              # ]
    "LSQUARE": '[',              # [
    
    "COMMA": ',',                # ,
    "ARROW": '->',               # ->
    "INTERROGATIVE_PNT": '?',    # ?

    "DOLLAR": "$",               # $
    
    "EOF": 'end of file',        # end of file
}

KEYWORDS = [                        # List of all the keywords (TT["KEYWORD"])
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
    # classes
    'class',
    # modules
    'import',
    'export',
    'as',
    # files
    'write',
    'read',
    # assertion
    'assert',
]

TOKENS_NOT_TO_QUOTE = [
    TT["NEWLINE"],
    TT["INT"],
    TT["STRING"],
    TT["IDENTIFIER"],
    TT["KEYWORD"],
    TT["EOF"]
]

EQUALS = [  # all the assignment tokens ('=', '+=', ...) but not the equal tokens for tests ('==', '!=', ...)
    TT["EQ"],
    TT["PLUSEQ"],
    TT["MINUSEQ"],
    TT["MULTEQ"],
    TT["DIVEQ"],
    TT["POWEQ"],
    TT["FLOORDIVEQ"],
    TT["PERCEQ"],
    TT["OREQ"],
    TT["ANDEQ"],
    TT["XOREQ"],
    TT["BITWISEANDEQ"],
    TT["BITWISEOREQ"],
    TT["BITWISEXOREQ"],
    TT["EEEQ"],
    TT["LTEEQ"],
    TT["GTEEQ"],
    TT["LTEQ"],
    TT["GTEQ"]
]
