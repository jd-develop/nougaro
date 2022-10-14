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
# we create a symbol table, then we define base things a symbol table needs
global_symbol_table = SymbolTable()
set_symbol_table(global_symbol_table)  # This function is in src.set_symbol_table


with open("config/noug_version.json") as ver_json:  # we get the nougaro version from noug_version.json
    ver_json_loaded = json.load(ver_json)
    version_ = ver_json_loaded.get("phase") + " " + ver_json_loaded.get("noug_version")


# ##########
# RUN
# ##########
def run(file_name: str, text: str, version: str = version_, exec_from: str = "(shell)",
        actual_context: str = "<program>"):
    """Run the given code.
    The code is given through the `text` argument."""
    # we set version and context in the symbol table
    global_symbol_table.set("__noug_version__", String(version))
    global_symbol_table.set("__exec_from__", String(exec_from))
    global_symbol_table.set("__actual_context__", String(actual_context))

    # we make tokens with the Lexer
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()
    if error is not None:  # if there is any error, we just stop
        return None, error
    # print(tokens)  # uncomment this line to print the tokens

    # make the abstract syntax tree (AST) with the parser
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error is not None:  # if there is any error, we just stop
        return None, ast.error
    # print(ast)  # uncomment this line to print the AST

    # run the code (interpreter)
    interpreter = src.interpreter.Interpreter(run)
    context = Context('<program>')  # create the context of the interpreter
    # don't forget to change the context symbol table to the global symbol table
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)  # visit the main node of the AST with the created context
    # print(context)  # uncomment this line to print the context of the interpreter

    # finally, return the value and the error given by the interpreter
    # errors are managed by the shell.py file that calls this `run` function
    return result.value, result.error
