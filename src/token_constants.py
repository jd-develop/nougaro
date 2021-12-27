#!/usr/bin/env python3
# coding:utf-8
# this file is part of NOUGARO language, created by Jean Dubois (github.com/jd-develop)
# Public Domain
# Token definitions
# no imports

TT_INT = 'INT'                # integer, corresponds to python int
TT_FLOAT = 'FLOAT'            # float number, corresponds to python float
TT_STRING = 'STRING'          # string type, corresponds to python str
TT_IDENTIFIER = 'IDENTIFIER'  # Identifier of a var name
TT_KEYWORD = 'KEYWORD'        # Keyword, like "var"
TT_PLUS = 'PLUS'              # +
TT_MINUS = 'MINUS'            # -
TT_MUL = 'MUL'                # *
TT_DIV = 'DIV'                # /
TT_POW = 'POW'                # ^
TT_EQ = 'EQ'                  # =
TT_RPAREN = 'RPAREN'          # )
TT_LPAREN = 'LPAREN'          # (
TT_RSQUARE = 'RSQUARE'        # ]
TT_LSQUARE = 'LSQUARE'        # [
TT_ABS = 'ABS'                # |
TT_EE = 'EE'                  # ==
TT_NE = 'NE'                  # !=
TT_LT = 'LT'                  # <
TT_GT = 'GT'                  # >
TT_LTE = 'LTE'                # <=
TT_GTE = 'GTE'                # >=
TT_COMMA = 'COMMA'            # ,
TT_ARROW = 'ARROW'            # ->
TT_EOF = 'EOF'                # end of file
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
