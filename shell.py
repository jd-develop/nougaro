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

# Works with python 3.11 and 3.12

# IMPORTS
# nougaro modules imports
import src.nougaro as nougaro
from src.misc import print_in_red
from src.runtime.values.basevalues.value import Value
from src.runtime.values.basevalues.basevalues import List
from src.errors.errors import Error
# built in python imports
import json
import sys
import os
import platform
import pathlib
if platform.system() in ["Linux", "Darwin"] or "BSD" in platform.system():
    try:
        import readline  # browse command history # type: ignore
    except ImportError:
        pass

def check_arguments(args: list[str], noug_dir: str, version: str):
    line_to_exec = None
    if len(args) == 0:  # there is a file to exec
        return "<stdin>", None

    if args[0] == "-c" or args[0] == "-cd":
        path = "<commandline>"
        try:
            line_to_exec = args[1]
            del args[1]
        except IndexError:
            print_in_red("Expected argument with '-c' and '-cd'.")
            sys.exit(1)
        # note that bash, zsh and fiSH automatically delete quotes.
        # TODO: test in windows cmd and powershell
        assert isinstance(line_to_exec, str), "please report this bug on GitHub: https://github.com/" \
                                              "jd-develop/nougaro"
    elif args[0] == "--help" or args[0] == "-h":
        with open(os.path.abspath(noug_dir + "/config/help"), "r+", encoding="UTF-8") as help_file:
            what_to_print = help_file.readlines()[1:]
        for line in what_to_print:
            print(line, end="")
        sys.exit()
    elif args[0] == "--version" or args[0] == "-V":
        print(version)
        sys.exit()
    else:
        if not os.path.exists(args[0]):  # we check if the file exist, if not we quit with an error message
            print_in_red(f"[nougaro] file '{args[0]}' does not exist.")
            sys.exit(-1)  # DO NOT USE exit() OR quit() PYTHON BUILTINS !!!
        elif args[0] in ["<stdin>", "<stdout>", "<commandline>"]:
            # these names can not be files : <stdin> is the shell input and <stdout> is his output
            print_in_red(f"[nougaro] file '{args[0]}' can not be used by Nougaro because this name is used "
                         f"internally.\n"
                         f"[nougaro] This is not an unexpected error, you do not need to open an issue on "
                         f"GitHub.\n"
                         f"[nougaro] Note that the Nougaro shell will open.")
            path = "<stdin>"  # this opens the shell
        else:  # valid file :)
            path = args[0]

    return path, line_to_exec


def execute_file(path: str, debug_on: bool, noug_dir: str, version: str, args: list[str]):
    work_dir = os.path.dirname(os.path.realpath(path))
    endswith_slash = work_dir.endswith("/") or work_dir.endswith("\\")
    if endswith_slash:
        work_dir += "/"
    if debug_on:
        print(f"Nougaro working directory is {work_dir} ({type(work_dir)})")

    with open(path, encoding="UTF-8") as file:
        file_content = str(file.read())

    if file_content == "":  # no need to run this empty file
        error = None
    else:  # the file isn't empty, let's run it !
        try:
            error = nougaro.run('<stdin>', file_content, noug_dir, version, args=args, work_dir=work_dir)[1]
        except KeyboardInterrupt:  # if CTRL+C, just exit the Nougaro shell
            print_in_red("\nKeyboardInterrupt")
            sys.exit()
        except EOFError:
            print_in_red("\nEOF")
            sys.exit()

    if error is not None:  # there is an error, so before exiting we have to say "OH NO IT'S BROKEN"
        print_in_red(error.as_string())
        sys.exit(1)


def print_result_and_error(result: Value | None, error: Error | None, args: list[str], exit_on_cd: bool = False):
    if error is not None:  # there is an error, we print it in RED because OMG AN ERROR
        print_in_red(error.as_string())
        return
    if result is None:
        return
    if exit_on_cd and args[0] == "-cd":
        return
    if not isinstance(result, List):
        print("WARNING: Looks like something went wrong. Don't panic, and just report this bug at:\n"
              "https://jd-develop.github.io/nougaro/bugreport.html.\n"
              "Error details: result from src.nougaro.run in shell is not a List.")
        print(f"The actual result is {result}, of type {type(result)}, error is {error}.")
        return

    if len(result.elements) == 1:  # there is one single result, let's print it without the "[]".
        if result.elements[0].should_print:  # if the value should be printed, let's print it!
            print(result.elements[0])
    else:  # there is multiple results, when there is multi-line statements (like `print(a);var a+=1`)
        # this code is to know what the list contains
        # if the list contains only NoneValues that shouldn't be printed, we don't print it
        # in any other case, we do.
        should_print = False
        for e in result.elements:
            if e.should_print:
                should_print = True
                break  # same here
        if should_print:  # if we should print, we print
            print(result)


def main():
    noug_dir = os.path.abspath(pathlib.Path(__file__).parent.absolute())

    with open(os.path.abspath(noug_dir + "/config/debug.conf")) as debug_f:
        debug_on = bool(int(debug_f.read()))

    with open(os.path.abspath(noug_dir + "/config/print_context.conf")) as print_context_f:
        print_context = bool(int(print_context_f.read()))

    # message for PR-makers: if you have a better idea to how to do these things with CLI arguments, make a PR :)
    args = sys.argv.copy()
    # print(args)

    # print(f"Arguments count: {len(sys.argv)}")
    # for i, arg in enumerate(sys.argv):
    #     print(f"Argument {i:>6}: {arg}")

    # Uncomment 3 last lines to understand the following code.
    # Tested on Windows and Linux. Tested after compiling with Nuitka on Windows and Linux.
    del args[0]

    with open(os.path.abspath(noug_dir + "/config/noug_version.json")) as ver_json:
        # we load the nougaro version stored in noug_version.json
        ver_json_loaded = json.load(ver_json)
        major = ver_json_loaded.get("major")
        minor = ver_json_loaded.get("minor")
        patch = ver_json_loaded.get("patch")
        phase = ver_json_loaded.get("phase")
        phase_minor = ver_json_loaded.get("phase-minor")
        version = f"{major}.{minor}.{patch}-{phase}"
        if phase_minor != 0:
            version += f".{phase_minor}"

    path, line_to_exec = check_arguments(args, noug_dir, version)

    has_to_run_a_file = path not in ["<stdin>", "<commandline>"]
    if has_to_run_a_file:
        execute_file(path, debug_on, noug_dir, version, args)
        return

    work_dir = os.getcwd()
    endswith_slash = work_dir.endswith("/") or work_dir.endswith("\\")
    if not endswith_slash:
        work_dir += "/"

    if path == "<stdin>":  # we open the shell
        # this text is always printed when we start the shell
        print(f"Welcome to Nougaro {version} on {platform.system()}! "
              f"Contribute: https://github.com/jd-develop/nougaro/")
        print(f"Changelog: see {noug_dir}/changelog.md")
        print()
        print("This program is under GPL license. For more details, type __gpl__() or __gpl__(1) to stay in terminal."
              "\nThis program comes with ABSOLUTELY NO WARRANTY; for details type `__disclaimer_of_warranty__'.")
        print()
        print("Found a bug? Feel free to report it at https://jd-develop.github.io/nougaro/bugreport.html")
        if debug_on:
            print()
            print(f"Current working directory is {work_dir} ({type(work_dir)})")
            print(f"Python version is {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]} "
                  f"({list(sys.version_info)})")
            print("DEBUG mode is ENABLED")
        if print_context:
            if not debug_on:
                print()
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

            if str(text) == "":  # nothing was entered: we don't do anything
                result, error = None, None
                continue
            try:  # we try to run it
                result, error = nougaro.run('<stdin>', text, noug_dir, version, args=args, work_dir=work_dir)
            except KeyboardInterrupt:  # if CTRL+C, just stop to run the line and ask for another input
                print_in_red("\nKeyboardInterrupt")
                continue  # continue the `while True` loop
            except EOFError:
                print_in_red("\nEOF")
                break  # breaks the `while True` loop to the end of the file

            print_result_and_error(result, error, args)
    elif path == "<commandline>":
        if line_to_exec == "":
            sys.exit()

        try:  # we try to run it
            result, error = nougaro.run('<commandline>', line_to_exec, noug_dir, version, args=args, work_dir=work_dir)
        except KeyboardInterrupt:  # if CTRL+C, just stop to run the line and ask for another input
            print_in_red("\nKeyboardInterrupt")
            sys.exit()
        except EOFError:
            print_in_red("\nEOF")
            sys.exit()

        print_result_and_error(result, error, args, True)


if __name__ == '__main__':  # SOMEBODY ONCE TOLD ME it was good to do that
    main()
