#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
from src.lexer.position import DEFAULT_POSITION
from src.runtime.symbol_table import SymbolTable
from src.runtime.values.basevalues.basevalues import String, Value, NoneValue, Number
from src.runtime.values.functions.builtin_function import BuiltInFunction
import src.noug_version
# built-in python imports
import platform
import sys
import pprint


def set_symbol_table(symbol_table: SymbolTable):
    """Configures the global symbol table
    :param symbol_table: src.symbol_table.SymbolTable
    """
    # Constants
    symbol_table.set("null", Number(0, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()))
    symbol_table.set("True", Number(1, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()))
    symbol_table.set("False", Number(0, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()))
    symbol_table.set("None", NoneValue(DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy(), True))

    # Built-in functions
    for function in BuiltInFunction.builtin_functions:
        symbol_table.set(function, BuiltInFunction(function))

    symbol_table.set("esrever", BuiltInFunction('reverse'))

    # Hum...
    symbol_table.set("answerToTheLifeTheUniverseAndEverything", Number(42, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()))
    symbol_table.set("numberOfHornsOnAnUnicorn", Number(1, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()))
    symbol_table.set("theLoneliestNumber", Number(1, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()))

    # Technical
    symbol_table.set('__os_name__', String(platform.system(), DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()))
    symbol_table.set('__os_release__', String(platform.uname().release, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()))
    symbol_table.set('__os_version__', String(platform.uname().version, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()))
    symbol_table.set(
        '__python_version__',
        String(
            str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "." + str(sys.version_info[2]),
            DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()
        )
    )
    # platform.system() may be 'Linux', 'Windows', 'Darwin', 'Java', etc. according to Python doc
    # it can also be 'FreeBSD', 'OpenBSD', [add here other OSes where you tested platform.system()]
    symbol_table.set('__base_value__', Value(DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()))

    # GPL
    symbol_table.set(
        '__disclaimer_of_warranty__',
        String(
            "GNU GPL 3.0, 15, Disclaimer of Warranty:\n\n"
            "  THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY\n"
            "APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT\n"
            "HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM \"AS IS\" WITHOUT WARRANTY\n"
            "OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,\n"
            "THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR\n"
            "PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM\n"
            "IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF\n"
            "ALL NECESSARY SERVICING, REPAIR OR CORRECTION.",
            DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy()
        )
    )

    symbol_table.set(
        "__noug_version__", String(src.noug_version.VERSION, DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy())
    )
    symbol_table.set(
        "__data_version__",
        String(str(src.noug_version.DATA_VERSION), DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy())
    )
    symbol_table.set(
        "__version_id__",
        String(str(src.noug_version.VERSION_ID), DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy())
    )

    symbols_copy: dict[str, Value] = symbol_table.symbols.copy()
    if '__symbol_table__' in symbols_copy.keys():
        del symbols_copy['__symbol_table__']
    symbol_table.set(
        '__symbol_table__',
        String(pprint.pformat(symbols_copy), DEFAULT_POSITION.copy(), DEFAULT_POSITION.copy())
    )
