#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain
# Actually running with Python 3.9, works with Python 3.10

# IMPORTS
# nougaro modules imports
from src.lexer import Lexer
from src.parser import Parser
import src.interpreter

from src.symbol_table import SymbolTable
from src.set_symbol_table import set_symbol_table
from src.errors import *
from src.values.basevalues import String
# built-in python imports
import json


# ##########
# SYMBOL TABLE
# ##########
global_symbol_table = SymbolTable()
set_symbol_table(global_symbol_table)  # This function is in src.set_symbol_table


with open("noug_version.json") as ver_json:
    ver_json_loaded = json.load(ver_json)
    version_ = ver_json_loaded.get("phase") + " " + ver_json_loaded.get("noug_version")


# ##########
# RUN
# ##########
def run(file_name, text, version: str = version_, exec_from: str = "(shell)"):
    """Run the given code"""
    # set version in symbol table
    global_symbol_table.set("noug_version", String(version))
    global_symbol_table.set("__exec_from__", String(exec_from))

    # make tokens
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()
    if error is not None:
        return None, error
    # print(tokens)

    # make the abstract syntax tree (parser)
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error is not None:
        return None, ast.error
    # print(ast)

    # run the code (interpreter)
    interpreter = src.interpreter.Interpreter(run)
    interpreter.__init__(run)
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)
    # print(context)
    # pprint.pprint(global_symbol_table)

    return result.value, result.error
