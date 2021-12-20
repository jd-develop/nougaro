#!/usr/bin/env python3
# coding:utf-8
# this file is part of NOUGARO language, created by Jean Dubois (github.com/jd-develop)
# Public Domain
# Actually running with Python 3.9.8, works with Python 3.10

# IMPORTS
# nougaro modules imports
import nougaro
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
        nougaro.print_in_red(error.as_string())
    elif result is not None:
        print(result)
    else:
        pass
