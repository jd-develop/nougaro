#!/usr/bin/env python3
# -*- coding:utf-8 -*-

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

# Works with Python 3.10 and 3.11

# IMPORTS
# nougaro modules imports
import src.nougaro as nougaro
from src.misc import print_in_red
from src.values.basevalues import List, NoneValue
# built in python imports
import json
import sys
import os
import platform
import pathlib
if platform.system() in ["Linux", "Darwin"] or "BSD" in platform.system():
    try:
        import readline  # browse command history
    except ImportError:
        pass


def main():
    noug_dir = os.path.abspath(pathlib.Path(__file__).parent.absolute())

    with open(os.path.abspath(noug_dir + "/config/debug.conf")) as debug_f:
        debug_on = bool(int(debug_f.read()))

    with open(os.path.abspath(noug_dir + "/config/print_context.conf")) as print_context_f:
        print_context = bool(int(print_context_f.read()))

    # message for PR-makers: if you have a better idea to how to do these things with CLI arguments, make a PR :)
    args = sys.argv
    # print(args)

    # print(f"Arguments count: {len(sys.argv)}")
    # for i, arg in enumerate(sys.argv):
    #     print(f"Argument {i:>6}: {arg}")

    # Uncomment 3 last lines to understand the following code.
    # Tested on Windows and in WSL. Tested after compiling with Nuitka on Windows.
    # if 'shell' in args[0] or 'nougaro' in args[0]:  # shell.py, shell.exe, nougaro.exe, etc.
    #     del args[0]
    del args[0]

    # print(args)

    if len(args) != 0:  # there is a file to exec
        if not os.path.exists(args[0]):  # we check if the file exist, if not we quit with an error message
            print_in_red(f"[nougaro] file '{args[0]}' does not exist.")
            sys.exit(-1)  # DO NOT USE exit() OR quit() PYTHON BUILTINS !!!
        elif args[0] in ["<stdin>", "<stdout>"]:
            # these names can not be files : <stdin> is the shell input and <stdout> is his output
            print_in_red(f"[nougaro] file '{args[0]}' can not be used by Nougaro because this name is used internally."
                         f"\n"
                         f"[nougaro] This is not an unexpected error, you do not need to open an issue on the GitHub.\n"
                         f"[nougaro] Note that the Nougaro shell will open.")
            path = "<stdin>"  # this opens the shell
        else:  # valid file :)
            path = args[0]
    else:  # there is no file given, so we have to open the shell
        path = "<stdin>"

    with open(os.path.abspath(noug_dir + "/config/noug_version.json")) as ver_json:
        # we load the nougaro version stored in noug_version.json
        ver_json_loaded = json.load(ver_json)
        version = ver_json_loaded.get("phase") + " " + ver_json_loaded.get("noug_version")

    if path == "<stdin>":  # we open the shell
        # this text is always printed when we start the shell
        print(f"Welcome to Nougaro {version} on {platform.system()}! "
              f"Contribute : https://github.com/jd-develop/nougaro/")
        print("This program is under GPL license. For details, type __gpl__() or __gpl__(1) to stay in terminal.\n"
              "This program comes with ABSOLUTELY NO WARRANTY; for details type `__disclaimer_of_warranty__'.")
        print("Did you find a bug? Consider reporting it at https://jd-develop.github.io/nougaro/bugreport.html")
        if debug_on:
            print("DEBUG mode is ENABLED")
        if print_context:
            print("PRINT CONTEXT debug option is ENABLED")
        print()  # blank line

        while True:  # the shell loop (like game loop in a video game but, obviously, Nougaro isn't a video game)
            try:  # we ask for an input to be interpreted
                text = input("nougaro> ")
            except KeyboardInterrupt:  # if CTRL+C, exit the shell
                print_in_red("\nKeyboardInterrupt")
                break  # breaks the `while True` loop to the end of the file
            except EOFError:
                print_in_red("\nEOF")
                break  # breaks the `while True` loop to the end of the file
                
            if str(text) == "" or text is None:  # nothing was entered: we don't do anything
                result, error = None, None
            else:  # there's an input
                try:  # we try to run it
                    result, error = nougaro.run('<stdin>', text, noug_dir, version)
                except KeyboardInterrupt:  # if CTRL+C, just stop to run the line and ask for another input
                    print_in_red("\nKeyboardInterrupt")
                    continue  # continue the `while True` loop
                except EOFError:
                    print_in_red("\nEOF")
                    break  # breaks the `while True` loop to the end of the file

            if error is not None:  # there is an error, we print it in RED because OMG AN ERROR
                print_in_red(error.as_string())
            elif result is not None:  # there is no error, but there is a result
                if isinstance(result, List):  # the result is always a nougaro List value
                    if len(result.elements) == 1:  # there is one single result, let's print it without the "[]".
                        if not isinstance(result.elements[0], NoneValue):  # result is not a Nougaro NoneValue
                            print(result.elements[0])
                        else:  # result is a Nougaro NoneValue
                            if result.elements[0].should_print:  # if the NoneValue should be printed, let's print it!
                                print(result.elements[0])
                    else:  # there is multiple results, when there is multi-line statements (like `print(a);var a+=1`)
                        # this code is to know what the list contains
                        # if the list contains only NoneValues that shouldn't be printed, we don't print it
                        # in any other case, we do.
                        should_print = False
                        for e in result.elements:
                            if not isinstance(e, NoneValue):
                                should_print = True
                                # no need to continue looping : it takes a long time, and it's useless because we have
                                # to print anything, so we break this
                                break
                            else:
                                if e.should_print:
                                    should_print = True
                                    break  # same here
                        if should_print:  # if we should print, we print
                            print(result)
                else:  # the result is not a Nougaro List. If you know when that happens, tell me, please.
                    print("WARNING: Looks like something went wrong. Don't panic, and just report this bug at:\n"
                          "https://jd-develop.github.io/nougaro/bugreport.html."
                          "Error details: result from src.nougaro.run in shell is not a List.")
                    continue
            else:  # there is no error nor result. If you know when that happens, tell me, please.
                continue
    else:  # we don't open the shell because we have to run a file.
        with open(path, encoding="UTF-8") as file:
            file_content = str(file.read())
        if file_content == "" or file_content is None:  # no need to run this empty file
            result, error = None, None
        else:  # the file isn't empty, let's run it !
            try:
                result, error = nougaro.run('<stdin>', file_content, noug_dir, version)
            except KeyboardInterrupt:  # if CTRL+C, just exit the Nougaro shell
                print_in_red("\nKeyboardInterrupt")
                sys.exit()
            except EOFError:
                print_in_red("\nEOF")
                sys.exit()
        if error is not None:  # there is an error, so before exiting we have to say "OH NO IT'S BROKEN"
            print_in_red(error.as_string())


if __name__ == '__main__':  # ond day, someone told me that it was good to do that
    main()
