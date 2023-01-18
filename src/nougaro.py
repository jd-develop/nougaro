#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os.path

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
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
import os.path

# ##########
# SYMBOL TABLE
# ##########
# we create a symbol table, then we define base things a symbol table needs
global_symbol_table = SymbolTable()
set_symbol_table(global_symbol_table)  # This function is in src.set_symbol_table


# ##########
# RUN
# ##########
def run(file_name: str, text: str, noug_dir: str, version: str = None, exec_from: str = "(shell)",
        actual_context: str = "<program>"):
    """Run the given code.
    The code is given through the `text` argument."""
    with open(os.path.abspath(noug_dir + "/config/debug.conf")) as debug_f:
        debug_on = bool(int(debug_f.read()))

    with open(os.path.abspath(noug_dir + "/config/print_context.conf")) as print_context:
        print_context = bool(int(print_context.read()))

    if version is None:
        with open(os.path.abspath(noug_dir + "/config/noug_version.json")) as ver_json:
            # we get the nougaro version from noug_version.json
            ver_json_loaded = json.load(ver_json)
            version = ver_json_loaded.get("phase") + " " + ver_json_loaded.get("noug_version")

    # we set version and context in the symbol table
    global_symbol_table.set("__noug_version__", String(version))
    global_symbol_table.set("__exec_from__", String(exec_from))
    global_symbol_table.set("__actual_context__", String(actual_context))
    global_symbol_table.set("__noug_dir__", String(noug_dir))

    # we make tokens with the Lexer
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()
    if error is not None:  # if there is any error, we just stop
        return None, error
    if debug_on:
        print(tokens)

    # make the abstract syntax tree (AST) with the parser
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error is not None:  # if there is any error, we just stop
        return None, ast.error
    if debug_on:
        print(ast)

    # run the code (interpreter)
    interpreter = src.interpreter.Interpreter(run, noug_dir)
    context = Context('<program>')  # create the context of the interpreter
    # don't forget to change the context symbol table to the global symbol table
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)  # visit the main node of the AST with the created context
    if print_context:
        print(context.__str__())

    # finally, return the value and the error given by the interpreter
    # errors are managed by the shell.py file that calls this `run` function
    return result.value, result.error
