#!/usr/bin/bash

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) jd-dev@laposte.net
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
# along with this program.  If not, see https://www.gnu.org/licenses/.

# This file is used to build Nougaro for Linux using Nuitka (requires python3)

echo "WARNING: please execute this script ONLY in a safe environnement, like in a sandbox directory."
echo "WARNING: this script may use Internet connection, and having an Internet connection is recommended. However, you can execute the script without any Internet connection."
read -p "Continue? [y/n] " -r c

if [[ $c == [Yy] ]]; then
    python3 -m pip install --upgrade pip wheel colorama nuitka

    read -p "Nougaro version: " -r nougversion
    read -p "Phase (beta for example): " -r nougphase

    python3 -m nuitka --standalone --include-package=lib_ shell.py

    cp -r example.noug highlight\ theme\ for\ NPP.xml LICENSE README.md shell.py CODE_OF_CONDUCT.md how_it_works.md test_file.noug examples lib_ src config shell.dist/

    echo "Renaming and compressing…"
    mv shell.dist nougaro-"$nougversion"-"$nougphase"-linux-bin
    tar -czf nougaro-"$nougversion"-"$nougphase"-linux-bin.tar.gz nougaro-"$nougversion"-"$nougphase"-linux-bin/
fi
