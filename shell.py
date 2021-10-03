#!/usr/bin/env python3
# coding:utf-8
# this file is part of NOUGARO language, created by Jean Dubois (github.com/jd-develop)
# Public Domain
# Actually running with Python 3.9.7
import nougaro

version = "prototype-v1"

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
