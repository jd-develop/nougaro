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

# Works with python 3.11 and 3.12

# IMPORTS
# nougaro modules imports
import src.nougaro as nougaro
from src.misc import print_in_red
from src.runtime.values.basevalues.value import Value
from src.runtime.values.basevalues.basevalues import List
from src.errors.errors import Error
import src.conffiles
# built in python imports
import json
import sys
import os
import platform
import pathlib
import argparse
from datetime import datetime
if platform.system().lower() in ["linux", "darwin"] or "bsd" in platform.system().lower():
    try:
        import readline  # browse command history # type: ignore
    except ImportError:
        readline = None
else:
    readline = None


def check_arguments(args: argparse.Namespace, noug_dir: str, version: str):
    line_to_exec = None

    if args.command is not None or args.command_ is not None:
        if args.command is not None and args.command_ is not None:
            print_in_red("You can only provide one command argument, either '-c' or '-cd', but not both.")
            sys.exit(1)
        if args.file not in ["<stdin>", "<commandline>"]:
            print_in_red("You can not provide a file in addition to a command.")
            sys.exit(1)
        path = "<commandline>"
        if args.command is not None:
            line_to_exec = args.command
        else:
            line_to_exec = args.command_
        # note that bash, zsh and fiSH automatically delete quotes.
        # TODO: test in windows cmd and powershell
        assert isinstance(line_to_exec, str), "please report this bug on GitHub: https://github.com/" \
                                              "jd-develop/nougaro/issues"
    elif args.version:
        print(version)
        sys.exit()
    else:
        if args.file == "<stdin>":
            path = "<stdin>"
        elif args.file == "<stdout>":
            print_in_red("[nougaro] fatal error: can not read <stdout>.")
            sys.exit(1)
        elif args.file == "<commandline>":
            print_in_red("[nougaro] fatal error: no command given")
            sys.exit(1)
        elif not os.path.exists(args.file):  # we check if the file exist, if not we quit with an error message
            print_in_red(f"[nougaro] file '{args.file}' does not exist.")
            sys.exit(-1)  # DO NOT USE exit() OR quit() PYTHON BUILTINS !!!
        else:  # valid file :)
            path = args.file

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
            _, error = nougaro.run('<stdin>', file_content, noug_dir, version, args=args, work_dir=work_dir)
        except KeyboardInterrupt:  # if CTRL+C, just exit the Nougaro shell
            print_in_red("\nKeyboardInterrupt")
            sys.exit()
        except EOFError:
            print_in_red("\nEOF")
            sys.exit()

    if error is not None:  # there is an error, so before exiting we have to say "OH NO IT'S BROKEN"
        print_in_red(error.as_string())
        sys.exit(1)


def print_result_and_error(result: Value | None, error: Error | None, args: argparse.Namespace,
                           exit_on_cd: bool = False, should_print_stuff: bool = True):
    if error is not None:  # there is an error, we print it in RED because OMG AN ERROR
        print_in_red(error.as_string())
        return
    if result is None:
        return
    if exit_on_cd and args.command_ is not None:
        return
    if not isinstance(result, List):
        print("WARNING: Looks like something went wrong. Don't panic, and just report this bug at:\n"
              "https://jd-develop.github.io/nougaro/bugreport.html.\n"
              "Error details: result from src.nougaro.run in shell is not a List.")
        print(f"The actual result is {result}, of type {type(result)}, error is {error}.")
        return

    if not should_print_stuff:
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

    src.conffiles.create_config_files()

    HISTORY_FILE = src.conffiles.ROOT_CONFIG_DIRECTORY + ".noughistory"
    if readline is not None:
        import atexit
        if not os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "w+") as histf:
                histf.write("")
        readline.read_history_file(HISTORY_FILE)
        atexit.register(readline.write_history_file, HISTORY_FILE)

    debug = src.conffiles.access_data("debug")
    if debug is None:
        debug = 0
    debug_on = bool(int(debug))

    print_context = src.conffiles.access_data("print_context")
    if print_context is None:
        print_context = 0
    print_context = bool(int(print_context))

    argument_parser = argparse.ArgumentParser(
        prog="nougaro",
        description="Nougaro: a programming language.",
        epilog="Any other argument is passed in Nougaro. Arguments can be retrieved using the built-in __args__"
               "variable. For any other information, the documentation is available at "
               "https://github.com/jd-develop/nougaro/wiki"
    )
    
    argument_parser.add_argument("-c", "--command", help="run a command with shell output.")
    argument_parser.add_argument("-d", "--cd", "--command_dont_verbose", help="run a command without shell output.", dest="command_")
    argument_parser.add_argument("-v", "--version", help="print the version and exit.", action="store_true")
    argument_parser.add_argument("file", nargs="?", help="name of the file to run.", default="<stdin>")
    args, nougaro_args = argument_parser.parse_known_args()

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
        version_id = ver_json_loaded.get("version-id")

    path, line_to_exec = check_arguments(args, noug_dir, version)

    has_to_run_a_file = path not in ["<stdin>", "<commandline>"]
    if has_to_run_a_file:
        execute_file(path, debug_on, noug_dir, version, nougaro_args)
        return

    work_dir = os.getcwd()
    endswith_slash = work_dir.endswith("/") or work_dir.endswith("\\")
    if not endswith_slash:
        work_dir += "/"

    # We print stuff if this is an interactive shell.
    # HOWEVER, if we are in a pipe, like `echo "$" | nougaro`, we don’t want our prompt to be printed
    should_print_stuff = sys.stdin.isatty()

    if path == "<stdin>":  # we open the shell
        if should_print_stuff:
            # this text is always printed when we start the shell
            if debug_on:
                print(f"Welcome to Nougaro {version} (id {version_id}) on {platform.system()}!")
            else:
                print(f"Welcome to Nougaro {version} on {platform.system()}!")
            print(f"Contribute: https://github.com/jd-develop/nougaro/")
            print(f"Changelog: see {noug_dir}/changelog.md")
            print()
            print("This program is under GPL license. For more details, type __gpl__()")
            print("or __gpl__(1) to stay in terminal.")
            print("This program comes with ABSOLUTELY NO WARRANTY; for details type")
            print("`__disclaimer_of_warranty__'.")
            print()
            print("Found a bug? Feel free to report it at")
            print("https://jd-develop.github.io/nougaro/bugreport.html")
            # idea: cowsay?
            now = datetime.now()
            if now.month == 12 and 24 <= now.day <= 26:
                print("\nMerry Christmas!")
            elif now.month == now.day == 1:
                print(f"\nHappy new year {now.year}!")
            if debug_on:
                print()
                print(f"Current working directory is {work_dir} ({type(work_dir)})")
                print(f"Current config files directory is {src.conffiles.CONFIG_DIRECTORY} ({type(src.conffiles.CONFIG_DIRECTORY)})")
                data_version = src.conffiles.access_data("DATA_VERSION")
                print(f"Current data version is {data_version} ({type(data_version)})")
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
                if should_print_stuff:
                    text = input("nougaro> ")
                else:
                    text = input()
            except KeyboardInterrupt:  # if CTRL+C, exit the shell
                print_in_red("\nKeyboardInterrupt")
                break  # breaks the `while True` loop to the end of the file
            except EOFError:
                if should_print_stuff:
                    print_in_red("\nEOF")
                break  # breaks the `while True` loop to the end of the file

            if str(text) == "":  # nothing was entered: we don't do anything
                result, error = None, None
                continue
            try:  # we try to run it
                result, error = nougaro.run('<stdin>', text, noug_dir, version, args=nougaro_args, work_dir=work_dir)
            except KeyboardInterrupt:  # if CTRL+C, just stop to run the line and ask for another input
                print_in_red("\nKeyboardInterrupt")
                continue  # continue the `while True` loop
            except EOFError:
                print_in_red("\nEOF")
                break  # breaks the `while True` loop to the end of the file

            print_result_and_error(result, error, args, should_print_stuff=should_print_stuff)
    elif path == "<commandline>":
        if line_to_exec == "":
            sys.exit()

        try:  # we try to run it
            result, error = nougaro.run('<commandline>', line_to_exec, noug_dir, version, args=nougaro_args, work_dir=work_dir)
        except KeyboardInterrupt:  # if CTRL+C, just stop to run the line and ask for another input
            print_in_red("\nKeyboardInterrupt")
            sys.exit()
        except EOFError:
            print_in_red("\nEOF")
            sys.exit()

        print_result_and_error(result, error, args, True)


if __name__ == '__main__':  # SOMEBODY ONCE TOLD ME it was good to do that
    main()
