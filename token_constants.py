#!/usr/bin/env python3
# coding:utf-8
# this file is part of NOUGARO language, created by Jean Dubois (github.com/jd-develop)
# Public Domain
# no imports

TT_INT = 'INT'                # integer, correspond to python int
TT_FLOAT = 'FLOAT'            # float number, correspond to python float
TT_IDENTIFIER = 'IDENTIFIER'  # Identifier of a var name
TT_KEYWORD = 'KEYWORD'        # Keyword, like "VAR"
TT_PLUS = 'PLUS'              # +
TT_MINUS = 'MINUS'            # -
TT_MUL = 'MUL'                # *
TT_DIV = 'DIV'                # /
TT_POW = 'POW'                # ^
TT_EQ = 'EQ'                  # =
TT_RPAREN = 'RPAREN'          # )
TT_LPAREN = 'LPAREN'          # (
TT_EOF = 'EOF'                # end of file
KEYWORDS = [
    'VAR'
]
