#!/usr/bin/env python3
# -*- coding=utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

""" WebBrowser module

    Convenient web-browser controller.

    The webbrowser module allows you to open pages in the browser.
"""
# IMPORTS
# nougaro modules imports
from lib_.lib_to_make_libs import *  # useful stuff to make libs.
# built-in python imports
import webbrowser

__LIB_VERSION__ = 2


class WebBrowserError(RunTimeError):
    """WebBrowserError is an error that can be triggered ONLY via functions in this module."""
    def __init__(self, pos_start: Position, pos_end: Position, details: str, context: Context, origin_file: str = "lib_.webbrowser_"):
        super().__init__(pos_start, pos_end, details, context, rt_error=False, error_name="WebBrowserError", origin_file=origin_file)
        self.context = context


class WebBrowser(ModuleFunction):
    """ WebBrowser Module """
    functions: dict[str, builtin_function_dict] = {}

    def __init__(self, function_name: str):
        super().__init__("webbrowser", function_name, functions=self.functions)

    def copy(self):
        """Return a copy of self"""
        copy = WebBrowser(self.name)
        return self.set_context_and_pos_to_a_copy(copy)
    
    def is_eq(self, other: Value):
        return isinstance(other, WebBrowser) and self.name == other.name
    
    # functions
    def open(self, context: Context):
        """
        Display url using the default browser.
        If new is 0, the url is opened in the same browser window if possible.
        If new is 1, a new browser window is opened if possible.
        If new is 2, a new tab is opened if possible.
        If autoraise is True, the window is raised if possible (note that under many window managers this will occur
        regardless of the setting of this variable).
        """
        assert context.symbol_table is not None
        url = context.symbol_table.getf("url")
        new = context.symbol_table.getf("new")
        autoraise = context.symbol_table.getf("autoraise")

        if not isinstance(url, String):
            assert url is not None
            return RTResult().failure(RTTypeErrorF(
                url.pos_start, url.pos_end, "first", "webbrowser.open", "str", url,
                context, "lib_.webbrowser_.WebBrowser.open"
            ))
        
        if new is None:
            new = Number(0, url.pos_end, self.pos_end).set_context(context)
        if not (isinstance(new, Number) and isinstance(new.value, int)):
            return RTResult().failure(RTTypeErrorF(
                new.pos_start, new.pos_end, "second", "webbrowser.open", "int", new,
                context, "lib_.webbrowser_.WebBrowser.open"
            ))
        if not 0 <= new.value <= 2:
            return RTResult().failure(RunTimeError(
                new.pos_start, new.pos_end, "the 'new' argument should either be 0 (same window), 1 (new window), or 2 (new tab)",
                context, origin_file="lib_.webbrowser_.WebBrowser.open"
            ))
        
        if autoraise is None:
            autoraise = TRUE.copy().set_context(context)
        
        try:
            webbrowser.open(url.value, new.value, autoraise.is_true())
        except webbrowser.Error as e:
            return RTResult().failure(WebBrowserError(
                self.pos_start, self.pos_end, f"{e}",
                context, origin_file="lib_.webbrowser.WebBrowser.open"
            ))

        return RTResult().success(NoneValue(self.pos_start, self.pos_end, False).set_context(context))

    functions["open"] = {
        "function": open,
        "param_names": ["url"],
        "optional_params": ["new", "autoraise"],
        "should_respect_args_number": True,
        "run_noug_dir_work_dir": False,
        "noug_dir": False
    }


WHAT_TO_IMPORT = {
    "open": WebBrowser("open")
}
