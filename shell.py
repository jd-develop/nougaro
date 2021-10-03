#!/usr/bin/env python3
# coding:utf-8
# this file is part of NOUGARO language, created by Jean Dubois (github.com/jd-develop)
# Public Domain
# Actually running with Python 3.9.7

# IMPORTS
# nougaro modules imports
import nougaro
# build in python imports
import json

with open("version.json") as ver_json:
    ver_json_loaded = json.load(ver_json)
    version = ver_json_loaded.get("version")

print(f"Welcome to Nougaro Shell ! You are actually using the version {version}.")

while True:
    text = input("nougaro> ")
    result, error = nougaro.run('<stdin>', text)

    if text == "exit":
        break
    elif text == "ver":
        print(version)
    elif error is not None:
        nougaro.print_in_red(error.as_string())
    else:
        print(result)
