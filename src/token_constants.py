#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain
# Token definitions
# no imports

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
TT_EQ = '='                   # =
TT_RPAREN = ')'               # )
TT_LPAREN = '('               # (
TT_RSQUARE = ']'              # ]
TT_LSQUARE = '['              # [
TT_ABS = '|'                  # |
TT_EE = '=='                  # ==
TT_NE = '!='                  # !=
TT_LT = '<'                   # <
TT_GT = '<'                   # >
TT_LTE = '<='                 # <=
TT_GTE = '>='                 # >=
TT_COMMA = ','                # ,
TT_ARROW = '->'               # ->
TT_EOF = 'end of file'        # end of file
KEYWORDS = [                  # List of all keyword (TT_KEYWORD)
    'var',
    'and',
    'or',
    'not',
    'exclor',
    'if',
    'then',
    'elif',
    'else',
    'for',
    'to',
    'step',
    'while',
    'def'
]

TOKENS_TO_QUOTE = [
    TT_PLUS,
    TT_MINUS,
    TT_MUL,
    TT_DIV,
    TT_POW,
    TT_EQ,
    TT_RPAREN,
    TT_LPAREN,
    TT_RSQUARE,
    TT_LSQUARE,
    TT_ABS,
    TT_EE,
    TT_NE,
    TT_LT,
    TT_GT,
    TT_LTE,
    TT_GTE,
    TT_COMMA,
    TT_ARROW
]
