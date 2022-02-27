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

with open("version.json") as ver_json:
    ver_json_loaded = json.load(ver_json)
    version = ver_json_loaded.get("version")

print(f"Welcome to Nougaro Shell ! You are actually using the version {version}.")

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
