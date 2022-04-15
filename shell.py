#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# this file is part of the NOUGARO language, created by Jean Dubois (https://github.com/jd-develop)
# Public Domain
# Actually running with Python 3.9, works with Python 3.10

# IMPORTS
# nougaro modules imports
import src.nougaro as nougaro
from src.misc import print_in_red
from src.values.basevalues import List, NoneValue
# built in python imports
import json
import sys
import os.path


def main():
    # message for PR-makers: if you have a better idea to how to do these things with CLI arguments, make a PR :)
    args = sys.argv
    # print(args)

    # print(f"Arguments count: {len(sys.argv)}")
    # for i, arg in enumerate(sys.argv):
    #     print(f"Argument {i:>6}: {arg}")

    # Uncomment 3 last lines to understand the following code.
    # Tested on Windows and in WSL. Tested after compiling with Nuitka on Windows.
    if 'shell' in args[0] or 'nougaro' in args[0]:  # shell.py, shell.exe, nougaro.exe, etc.
        del args[0]

    # print(args)

    if len(args) != 0:  # there is a file to exec
        if not os.path.exists(args[0]):
            print_in_red(f"[nougaro] file '{args[0]}' does not exist.")
            path = None
            exit(-1)
        elif args[0].startswith("<"):
            print_in_red(f"[nougaro] file '{args[0]}' can not be used by Nougaro because this name is used internally."
                         f"\n"
                         f"[nougaro] This is not an unexpected error, you do not need to open an issue on the GitHub.\n"
                         f"[nougaro] Note that the Nougaro shell will open.")
            path = "<stdin>"
        else:
            path = args[0]
    else:  # there is no file
        path = "<stdin>"

    with open("noug_version.json") as ver_json:
        ver_json_loaded = json.load(ver_json)
        version = ver_json_loaded.get("phase") + " " + ver_json_loaded.get("noug_version")

    if path == "<stdin>":
        print(f"Welcome to Nougaro {version}! Contribute : https://github.com/jd-develop/nougaro/")

        while True:
            text = input("nougaro> ")
            if str(text) == "" or text is None:
                result, error = None, None
            else:
                result, error = nougaro.run('<stdin>', text, version)

            if error is not None:
                print_in_red(error.as_string())
            elif result is not None:
                if isinstance(result, List):
                    if len(result.elements) == 1:
                        if not isinstance(result.elements[0], NoneValue):
                            print(result.elements[0])
                        else:
                            if result.elements[0].should_print:
                                print(result.elements[0])
                    else:
                        print(result)
                else:
                    continue
            else:
                continue
    else:
        file = open(path, encoding="UTF-8")
        file_content = str(file.read())
        file.close()
        if file_content == "" or file_content is None:
            result, error = None, None
        else:
            result, error = nougaro.run('<stdin>', file_content, version)
        if error is not None:
            print_in_red(error.as_string())


if __name__ == '__main__':
    main()
