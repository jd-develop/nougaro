#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.runtime.symbol_table import SymbolTable
from src.runtime.values.number_constants import *
from src.runtime.values.basevalues.basevalues import String, Value, NoneValue
from src.runtime.values.functions.builtin_function import BuiltInFunction
from src.constants import PROTECTED_VARS
# built-in python imports
import platform
import sys
import pprint


def set_symbol_table(symbol_table: SymbolTable):
    """Configures the global symbol table
    :param symbol_table: src.symbol_table.SymbolTable
    """
    # Constants
    symbol_table.set("null", NULL)
    symbol_table.set("True", TRUE)
    symbol_table.set("False", FALSE)
    symbol_table.set("None", NoneValue(True))

    # Built-in functions
    symbol_table.set("void", BuiltInFunction('void'))

    symbol_table.set("run", BuiltInFunction('run'))
    symbol_table.set("example", BuiltInFunction('example'))

    symbol_table.set("print", BuiltInFunction('print'))
    symbol_table.set("print_in_red", BuiltInFunction('print_in_red'))
    symbol_table.set("print_ret", BuiltInFunction('print_ret'))
    symbol_table.set("print_in_red_ret", BuiltInFunction('print_in_red_ret'))
    symbol_table.set("input", BuiltInFunction('input'))
    symbol_table.set("input_int", BuiltInFunction('input_int'))
    symbol_table.set("input_num", BuiltInFunction('input_num'))
    symbol_table.set("clear", BuiltInFunction('clear'))

    symbol_table.set("is_int", BuiltInFunction('is_int'))
    symbol_table.set("is_float", BuiltInFunction('is_float'))
    symbol_table.set("is_num", BuiltInFunction('is_num'))
    symbol_table.set("is_str", BuiltInFunction('is_str'))
    symbol_table.set("is_list", BuiltInFunction('is_list'))
    symbol_table.set("is_func", BuiltInFunction('is_func'))
    symbol_table.set("is_module", BuiltInFunction('is_module'))
    symbol_table.set("is_none", BuiltInFunction('is_none'))
    symbol_table.set("type", BuiltInFunction('type'))
    symbol_table.set("__py_type__", BuiltInFunction('py_type'))
    symbol_table.set("str", BuiltInFunction('str'))
    symbol_table.set("list", BuiltInFunction('list'))
    symbol_table.set("int", BuiltInFunction('int'))
    symbol_table.set("float", BuiltInFunction('float'))
    symbol_table.set("round", BuiltInFunction('round'))

    symbol_table.set("append", BuiltInFunction('append'))
    symbol_table.set("pop", BuiltInFunction('pop'))
    symbol_table.set("insert", BuiltInFunction('insert'))
    symbol_table.set("extend", BuiltInFunction('extend'))
    symbol_table.set("get", BuiltInFunction('get'))
    symbol_table.set("replace", BuiltInFunction('replace'))
    symbol_table.set("max", BuiltInFunction('max'))
    symbol_table.set("min", BuiltInFunction('min'))
    symbol_table.set("len", BuiltInFunction('len'))
    symbol_table.set("sort", BuiltInFunction('sort'))
    symbol_table.set("reverse", BuiltInFunction('reverse'))

    symbol_table.set("split", BuiltInFunction('split'))
    symbol_table.set("upper", BuiltInFunction('upper'))
    symbol_table.set("lower", BuiltInFunction('lower'))
    symbol_table.set("ord", BuiltInFunction('ord'))
    symbol_table.set("chr", BuiltInFunction('chr'))
    symbol_table.set("startswith", BuiltInFunction('startswith'))
    symbol_table.set("endswith", BuiltInFunction('endswith'))

    # Hum...
    symbol_table.set("answerToTheLifeTheUniverseAndEverything", Number(42))
    symbol_table.set("numberOfHornsOnAnUnicorn", Number(1))
    symbol_table.set("theLoneliestNumber", Number(1))
    symbol_table.set("rickroll", BuiltInFunction('rickroll'))
    symbol_table.set("nougaro", BuiltInFunction('nougaro'))

    # Technical
    symbol_table.set("exit", BuiltInFunction('exit'))
    symbol_table.set("system_call", BuiltInFunction('system_call'))
    symbol_table.set("__python__", BuiltInFunction('__python__'))
    symbol_table.set('__os_name__', String(platform.system()))
    symbol_table.set('__os_release__', String(platform.uname().release))
    symbol_table.set('__os_version__', String(platform.uname().version))
    symbol_table.set('__python_version__',
                     String(
                         str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "." + str(sys.version_info[2])
                     ))
    # platform.system() may be 'Linux', 'Windows', 'Darwin', 'Java', etc. according to Python doc
    # it can also be 'FreeBSD', 'OpenBSD', [add here other OSes where you tested platform.system()]
    symbol_table.set('__base_value__', Value())

    # GPL
    symbol_table.set('__disclaimer_of_warranty__',
                     String(
                         "GNU GPL 3.0, 15, Disclaimer of Warranty :\n\n"
                         "  THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY\n"
                         "APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT\n"
                         "HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM \"AS IS\" WITHOUT WARRANTY\n"
                         "OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,\n"
                         "THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR\n"
                         "PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM\n"
                         "IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF\n"
                         "ALL NECESSARY SERVICING, REPAIR OR CORRECTION."
                     ))
    symbol_table.set("__gpl__", BuiltInFunction('__gpl__'))

    symbol_table.set("__is_keyword__", BuiltInFunction('__is_keyword__'))
    symbol_table.set("__is_valid_token_type__", BuiltInFunction('__is_valid_token_type__'))
    symbol_table.set("__test__", BuiltInFunction("__test__"))
    symbol_table.set("__how_many_lines_of_code__", BuiltInFunction("__how_many_lines_of_code__"))

    symbols_copy: dict[str, Value] = symbol_table.symbols.copy()
    if '__symbol_table__' in symbols_copy.keys():
        del symbols_copy['__symbol_table__']
    symbol_table.set('__symbol_table__', String(pprint.pformat(symbols_copy)))

    # test_protected_vars(symbol_table)


def test_protected_vars(symbol_table: SymbolTable):
    """Test if all the variables in the symbol table are protected in writing or not. Used while coding."""
    error_count = 0
    for symbol in symbol_table.symbols:
        if symbol not in PROTECTED_VARS:
            if symbol not in [
                "numberOfHornsOnAnUnicorn",
                "theLoneliestNumber",
                "rickroll",
                "__how_many_lines_of_code__"
            ]:
                print(f"missing {symbol} in PROTECTED_VARS")
                error_count += 1
    if error_count == 0:
        print("Good job! Basic SymbolTable does not contain unprotected vars! :)")
