#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
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
from src.lexer.lexer import Lexer
from src.parser.parser import Parser
import src.runtime.interpreter
from src.runtime.symbol_table import SymbolTable
from src.runtime.set_symbol_table import set_symbol_table
from src.errors.errors import *
from src.runtime.values.basevalues.value import Value
from src.runtime.values.basevalues.basevalues import String, List, NoneValue
from src.misc import nice_str_from_idk
# built-in python imports
import json
import os.path
from typing import Sequence

# ##########
# SYMBOL TABLE
# ##########
# we create a symbol table, then we define base things a symbol table needs
global_symbol_table = SymbolTable()
set_symbol_table(global_symbol_table)  # This function is in src.set_symbol_table
default_symbol_table = global_symbol_table.copy()


# ##########
# RUN
# ##########
def run(
        file_name: str,
        text: str | None,
        noug_dir: str,
        version: str | None = None,
        exec_from: str | None = "(shell)",
        actual_context: str = "<program>",
        use_default_symbol_table: bool = False,
        use_context: Context | None = None,
        args: Sequence[str | String] | None = None,
        work_dir: str | None = None
) -> tuple[Value, None] | tuple[None, Error]:
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
            major = ver_json_loaded.get("major")
            minor = ver_json_loaded.get("minor")
            patch = ver_json_loaded.get("patch")
            phase = ver_json_loaded.get("phase")
            phase_minor = ver_json_loaded.get("phase-minor")
            version = f"{major}.{minor}.{patch}-{phase}"
            if phase_minor != 0:
                version += f".{phase_minor}"

    # we set version and context in the symbol table
    if args is None:
        new_args_values: list[Value] = []
        new_args_strings: list[String] = []
        global_symbol_table.set("__args__", List([]))
    else:
        new_args_values: list[Value] = list(map(nice_str_from_idk, args))
        new_args_strings: list[String] = list(map(nice_str_from_idk, args))
        global_symbol_table.set("__args__", List(new_args_values))
    global_symbol_table.set("__noug_version__", String(version))
    global_symbol_table.set("__exec_from__", String(str(exec_from)))
    global_symbol_table.set("__actual_context__", String(actual_context))
    global_symbol_table.set("__noug_dir__", String(noug_dir))

    # we make tokens with the Lexer
    if text is None:
        return NoneValue(False), None
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()
    if error is not None:  # if there is any error, we just stop
        return None, error
    assert tokens is not None
    if debug_on:
        print(tokens)

    # make the abstract syntax tree (AST) with the parser
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error is not None:  # if there is any error, we just stop
        return None, ast.error
    assert ast.node is not None
    if debug_on:
        print(ast)

    # run the code (interpreter)
    if work_dir is None:
        work_dir = noug_dir
    interpreter = src.runtime.interpreter.Interpreter(run, noug_dir, new_args_strings, work_dir)
    if use_context is None:
        context = Context('<program>')  # create the context of the interpreter
        # don't forget to change the context symbol table to the global symbol table
        if use_default_symbol_table:
            context.symbol_table = default_symbol_table.copy()
            context.symbol_table.set("__noug_version__", String(version))
            context.symbol_table.set("__exec_from__", String(str(exec_from)))
            context.symbol_table.set("__actual_context__", String(actual_context))
            context.symbol_table.set("__noug_dir__", String(noug_dir))
        else:  # this is how the shell “remember” the values
            context.symbol_table = global_symbol_table
    else:
        context = use_context  # do not .copy() here
    interpreter.update_symbol_table(context)

    # visit the main node of the AST with the created context
    assert not isinstance(ast.node, list)
    result = interpreter.visit(ast.node, context, False, main_visit=True)
    if print_context:
        print(context.__str__())
    if result.error is not None:
        return None, result.error
    assert result.value is not None

    # finally, return the value and the error given by the interpreter
    # errors are managed by the shell.py file that calls this `run` function
    return result.value, None


if __name__ == "__main__":
    print("Please use shell.py in the nougaro root directory in order to execute the Nougaro Python Interpreter")
