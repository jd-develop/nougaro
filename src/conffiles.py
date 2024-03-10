#!/usr/bin/env python3
# -*- coding=utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""conffiles
This file contains the create_or_update_config_files function, which creates and updates the format of config files
depending on if files exists and what is their format (data-version).

The configuration files are stored in the following places:
* Under Unix (except macOS) or GNU/Linux
$HOME/.config/jd-develop/nougaro/
* Under macOS
$HOME/Library/Preferences/org.jd-develop.nougaro/
* Under Windows
%APPDATA%\\jd-develop\\nougaro\\

If config files in ./config/ (where . is the nougaro repository root directory) are found and if no files exist in
the aforementionned directories, they are copied (with data-version=1) and eventually updated.
"""

# IMPORTS
# nougaro modules imports
# no imports
# built-in python imports
import os
import platform
import pathlib
import shutil


def _determine_config_directory():
    """And create it if it doesn’t exists"""
    system = platform.system()
    if system == "Darwin":  # macOS
        config_directory = os.path.expanduser("~/Library/Preferences/org.jd-develop.nougaro/")
        if not os.path.isdir(config_directory):
            os.mkdir(config_directory)
    elif system == "Windows":  # Windows
        config_directory = os.path.expandvars('%APPDATA%\\jd-develop\\nougaro\\')
        if not os.path.isdir(os.path.expandvars('%APPDATA%\\jd-develop\\')):
            os.mkdir(os.path.expandvars('%APPDATA%\\jd-develop\\'))
        if not os.path.isdir(config_directory):
            os.mkdir(config_directory)
    else:  # Unix and GNU/Linux
        config_directory = os.path.expanduser("~/.config/jd-develop/nougaro/")
        if not os.path.isdir(os.path.expanduser("~/.config/jd-develop/")):
            os.mkdir(os.path.expanduser("~/.config/jd-develop/"))
        if not os.path.isdir(config_directory):
            os.mkdir(config_directory)
    return config_directory


try:
    CONFIG_DIRECTORY = _determine_config_directory()
except FileExistsError as e:
    print("FATAL ERROR IN conffile MODULE. One of the directories already exist as a file.")
    print("Please report this bug at https://github.com/jd-develop/nougaro/issues/new/choose.")
    print("Please copy this error message in the bug report")
    raise e


def _create_or_copy_files():
    """Returns data version as an integer"""
    noug_dir = os.path.abspath(pathlib.Path(__file__).parent.parent.absolute())

    abspaths = {
        "debug": os.path.abspath(noug_dir + "/config/debug.nconf"),
        "debug_old": os.path.abspath(noug_dir + "/config/debug.conf"),
        "print_context": os.path.abspath(noug_dir + "/config/print_context.nconf"),
        "print_context_old": os.path.abspath(noug_dir + "/config/print_context.conf")
    }

    if os.path.exists(abspaths["debug"]):
        with open(abspaths["debug"], "r+") as debug_f:
            debug = debug_f.read()
    elif os.path.exists(abspaths["debug_old"]):
        with open(abspaths["debug_old"], "r+") as debug_f:
            debug = debug_f.read()
    else:
        debug = "0"

    if os.path.exists(abspaths["print_context"]):
        with open(abspaths["print_context"], "r+") as print_context_f:
            print_context = print_context_f.read()
    elif os.path.exists(abspaths["print_context_old"]):
        with open(abspaths["print_context_old"], "r+") as print_context_f:
            print_context = print_context_f.read()
    else:
        print_context = "0"
    
    if debug not in ["0", "1"]:
        print("[CONFFILES] Warning: 'debug' was not set to 0 or 1, resetting to 0.")
        debug = "0"
    if print_context not in ["0", "1"]:
        print("[CONFFILES] Warning: 'print_context' was not set to 0 or 1, resetting to 0.")
        print_context = "0"

    data_ver = 1
    with open(CONFIG_DIRECTORY + "DATA_VERSION.nconf", "w+") as data_ver_f:
        data_ver_f.write(str(data_ver))
    with open(CONFIG_DIRECTORY + "debug.nconf", "w+") as debug_nnf:
        debug_nnf.write(debug)
    with open(CONFIG_DIRECTORY + "print_context.nconf", "w+") as print_context_nnf:
        print_context_nnf.write(print_context)
    return data_ver


def _unknown_data_version():
    print("[CONFFILES] Warning: unknown data version. Resetting everything. A backup will be created (but it may fail).")
    shutil.copytree(CONFIG_DIRECTORY, CONFIG_DIRECTORY[:-1]+"_BACKUP/", dirs_exist_ok=True)
    shutil.rmtree(CONFIG_DIRECTORY)
    _determine_config_directory()
    _create_or_copy_files()


def create_or_update_config_files():
    # checks if the config path is empty (create or copy config files)
    if len(os.listdir(CONFIG_DIRECTORY)) == 0:
        _create_or_copy_files()

    # update
    if not os.path.exists(CONFIG_DIRECTORY + "DATA_VERSION.nconf"):
        _unknown_data_version()
        
    with open(CONFIG_DIRECTORY + "DATA_VERSION.nconf", "r+") as data_version_f:
        data_version = data_version_f.read()

    try:
        data_version = int(data_version)
    except ValueError:
        data_version = _unknown_data_version()

    if data_version == 0:
        _create_or_copy_files()
    elif data_version == 1:
        pass  # up to date
    

def access_data(config_file: str):
    """Return None if the file does not exist."""
    if not os.path.exists(CONFIG_DIRECTORY + config_file + ".nconf"):
        return None
    with open(CONFIG_DIRECTORY + config_file + ".nconf", "r+") as file:
        return file.read()
    

def write_data(config_file: str, data: str, silent: bool = False, return_error_messages: bool = False):
    if config_file == "DATA_VERSION":
        errmsg = "[CONFFILES] Can not write in DATA_VERSION, too risky…"
        if not silent:
            print(errmsg)
        if return_error_messages:
            return errmsg
        return
    with open(CONFIG_DIRECTORY + config_file + ".nconf", "w+") as file:
        file.write(data)
