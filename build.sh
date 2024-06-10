#!/usr/bin/bash

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) jd-dev@laposte.net
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see https://www.gnu.org/licenses/.

# This file is used to build Nougaro for GNU/Linux using Nuitka (requires python, by default python3)
# You can pass your python command in this script as argument (example: ./build.sh python3.11)

if [ ! "$1" ]; then python=python3; else python=$1; fi

echo "WARNING: please execute this script ONLY in a safe environnement, like in a sandbox directory."
echo "WARNING: this script may use Internet connection, and having an Internet connection is recommended. However, you can execute the script without any Internet connection."
echo "INFO: it is recommended to test nougaro before building it. Run 'sh run_tests.sh' to test it."
read -p "Continue? [y/N] " -r c

if [[ $c == [Yy] ]]; then
    echo "WARNING: a pip command will be executed (see below) and may (in edge cases) break your python installation or your OS (it won't)"
    echo "WARNING: this is the command : '$python -m pip install --upgrade pip wheel colorama nuitka --break-system-packages'"
    echo "WARNING: For information, the python version that will be used is $($python --version). Please check if your python version is supported by Nougaro and by Nuitka!"
    echo "INFO: For information, you can pass the command to the Python binary you want as an argument of this script. The default command is python3."
    read -p "Continue? [y/N] " -r d
fi

if [[ $c == [Yy] && $d == [Yy] ]]; then
    echo "WARNING: please make sure patchelf is installed on your system."
    echo "WARNING: to install it, execute 'apt/dnf/yum install patchelf'"
    echo "Moreover, ccache is recommended. Install it with 'apt/dnf/yum install ccache'"
    read -p "Continue? [y/N] " -r e
fi

if [[ $c == [Yy] && $d == [Yy] && $e == [Yy] ]]; then
    $python -m pip install --upgrade pip wheel colorama nuitka --break-system-packages

    return_code=$?
    if [ $return_code != 0 ]; then
        echo "pip returned with error (exit code $return_code)"
        exit $return_code
    fi

    nougversion=$($python shell.py -v)
    echo "Nougaro version: $nougversion"

    $python -m nuitka --standalone --include-package=lib_ --no-deployment-flag=self-execution shell.py

    return_code=$?
    if [ $return_code != 0 ]; then
        echo "Nuitka returned with error (exit code $return_code)"
        exit $return_code
    fi

    echo "Removing bloat… This may cause error messages, don’t worry."
    find . -type d -execdir rm -rf __pycache__/ \;

    echo "Copying…"
    cp -r example.noug LICENSE README.md README.fr.md shell.py CODE_OF_CONDUCT.md CONTRIBUTING.md how_it_works.md tests/ examples/ lib_/ src/ noug_version.json repo-image/ shell.dist/

    echo "Renaming and compressing…"
    mv shell.dist nougaro-"$nougversion"-linux-bin
    tar -czf nougaro-"$nougversion"-linux-bin.tar.gz nougaro-"$nougversion"-linux-bin/

    return_code=$?
    if [ $return_code != 0 ]; then
        echo "tar returned with error (you can compress the folder nougaro-$nougversion-linux-bin yourself if you want)"
        echo "Return code: $return_code"
        exit $return_code
    fi
fi
