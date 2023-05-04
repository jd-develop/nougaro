#!/usr/bin/bash

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) jd-dev@laposte.net
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see https://www.gnu.org/licenses/.

# This file is used to build Nougaro for Linux using Nuitka (requires python3)

echo "WARNING: please execute this script ONLY in a safe environnement, like in a sandbox directory."
echo "WARNING: this script may use Internet connection, and having an Internet connection is recommended. However, you can execute the script without any Internet connection."
read -p "Continue? [y/N] " -r c

echo "WARNING: a pip command will be executed (see below) and may (in edge cases) break your python installation or your OS (it won't)"
echo "WARNING: this is the command : 'python3 -m pip install --upgrade pip wheel colorama nuitka --break-system-packages'"
read -p "Continue? [y/N] " -r d

echo "WARNING: please make sure patchelf is installed on your system."
echo "WARNING: to install it, execute 'apt/dnf/yum install patchelf'"
read -p "Continue? [y/N] " -r d

if [[ $c == [Yy] && $d == [Yy] ]]; then
    python3 -m pip install --upgrade pip wheel colorama nuitka --break-system-packages

    read -p "Nougaro version: " -r nougversion
    read -p "Phase (beta for example): " -r nougphase

    python3 -m nuitka --standalone --include-package=lib_ shell.py

    cp -r example.noug highlight\ theme\ for\ NPP.xml LICENSE README.md shell.py CODE_OF_CONDUCT.md how_it_works.md test_file.noug examples lib_ src config shell.dist/

    echo "Renaming and compressing…"
    mv shell.dist nougaro-"$nougversion"-"$nougphase"-linux-bin
    tar -czf nougaro-"$nougversion"-"$nougphase"-linux-bin.tar.gz nougaro-"$nougversion"-"$nougphase"-linux-bin/
fi
