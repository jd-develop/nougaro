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
the aforementionned directories, they are copied and eventually updated.
"""

# IMPORTS
# nougaro modules imports
import src.noug_version
# built-in python imports
import os
import platform
import pathlib
import json

DATA_VERSION = src.noug_version.DATA_VERSION

README_TEXT = [
    "# Config files\n",
    "This directory stores the Nougaro config files.\n",
    "The config files of the version `version_id` are stored under `./version_id/data_version`.\n",
    "Please refer to `./version_guide.txt` to know what is the `version_id` of your nougaro version.\n"
]


def _write_readme(readme_file: str, version_guide_file: str, version: str, version_id: str):
    """Writes the README and the version guide"""
    if not os.path.isfile(readme_file):
        with open(readme_file, "w+", encoding="UTF-8") as readme:
            readme.writelines(README_TEXT)

    with open(readme_file, "w+", encoding="UTF-8") as readme:
        if readme.readlines() != README_TEXT:
            readme.writelines(README_TEXT)
    
    
    if os.path.isfile(version_guide_file):
        with open(version_guide_file, "r+", encoding="UTF-8") as versions_f:
            versions = versions_f.readlines()
    else:
        versions = []
    
    if f"Version {version} has an id of {version_id}.\n" not in versions:
        with open(version_guide_file, "a+", encoding="UTF-8") as versions_f_ap:
            versions_f_ap.write(f"Version {version} has an id of {version_id}.\n")


def _determine_config_directory():
    """And create it if it doesn’t exists"""
    system = platform.system()
    if system == "Darwin":  # macOS
        root_config_directory = os.path.abspath(os.path.expanduser("~/Library/Preferences/org.jd-develop.nougaro/"))
        if not os.path.isdir(root_config_directory):
            os.mkdir(root_config_directory)
    elif system == "Windows":  # Windows
        jd_develop_directory = os.path.expandvars('%APPDATA%\\jd-develop\\')
        root_config_directory = os.path.abspath(os.path.expandvars('%APPDATA%\\jd-develop\\nougaro\\'))
        if not os.path.isdir(jd_develop_directory):
            os.mkdir(jd_develop_directory)
        if not os.path.isdir(root_config_directory):
            os.mkdir(root_config_directory)
    else:  # Unix and GNU/Linux
        jd_develop_directory = os.path.expanduser("~/.config/jd-develop/")
        root_config_directory = os.path.abspath(os.path.expanduser("~/.config/jd-develop/nougaro/"))
        if not os.path.isdir(jd_develop_directory):
            os.mkdir(jd_develop_directory)
        if not os.path.isdir(root_config_directory):
            os.mkdir(root_config_directory)

    version, version_id = src.noug_version.VERSION, src.noug_version.VERSION_ID

    _write_readme(root_config_directory + "/" + "README.md", root_config_directory + "/" + "version_guide.txt", version, str(version_id))
    
    version_directory = os.path.abspath(root_config_directory + "/" + str(version_id) + "/")
    if not os.path.isdir(version_directory):
        os.mkdir(version_directory)
    config_directory = os.path.abspath(version_directory + "/" + str(DATA_VERSION) + "/")
    if not os.path.isdir(config_directory):
        os.mkdir(config_directory)

    return config_directory + "/", root_config_directory + "/"


try:
    CONFIG_DIRECTORY, _LEGACY_CONFIG_DIRECTORY = _determine_config_directory()
    ROOT_CONFIG_DIRECTORY = _LEGACY_CONFIG_DIRECTORY
except FileExistsError as e:
    print("FATAL ERROR IN conffile MODULE. One of the directories already exist as a file.")
    print("Please report this bug at https://github.com/jd-develop/nougaro/issues/new/choose.")
    print("Please copy this error message in the bug report")
    raise e


def _find_files_in_legacy_directories():
    """Returns debug, print_context"""
    noug_dir = os.path.abspath(pathlib.Path(__file__).parent.parent.absolute())

    abspaths = {
        "debug": os.path.abspath(noug_dir + "/config/debug.nconf"),
        "debug_old": os.path.abspath(noug_dir + "/config/debug.conf"),
        "print_context": os.path.abspath(noug_dir + "/config/print_context.nconf"),
        "print_context_old": os.path.abspath(noug_dir + "/config/print_context.conf"),
        "debug_root_dir": os.path.abspath(_LEGACY_CONFIG_DIRECTORY + "debug.nconf"),
        "print_context_root_dir": os.path.abspath(_LEGACY_CONFIG_DIRECTORY + "print_context.nconf"),
        "were_copied": os.path.abspath(_LEGACY_CONFIG_DIRECTORY + "were_copied.nconf")
    }

    if os.path.exists(abspaths["were_copied"]):
        return "0", "0"

    if os.path.exists(abspaths["debug_root_dir"]):
        with open(abspaths["debug_root_dir"], "r", encoding="UTF-8") as debug_f:
            debug = debug_f.read()
    elif os.path.exists(abspaths["debug"]):
        with open(abspaths["debug"], "r", encoding="UTF-8") as debug_f:
            debug = debug_f.read()
    elif os.path.exists(abspaths["debug_old"]):
        with open(abspaths["debug_old"], "r", encoding="UTF-8") as debug_f:
            debug = debug_f.read()
    else:
        debug = "0"

    if os.path.exists(abspaths["print_context_root_dir"]):
        with open(abspaths["print_context_root_dir"], "r", encoding="UTF-8") as print_context_f:
            print_context = print_context_f.read()
    elif os.path.exists(abspaths["print_context"]):
        with open(abspaths["print_context"], "r", encoding="UTF-8") as print_context_f:
            print_context = print_context_f.read()
    elif os.path.exists(abspaths["print_context_old"]):
        with open(abspaths["print_context_old"], "r", encoding="UTF-8") as print_context_f:
            print_context = print_context_f.read()
    else:
        print_context = "0"
    
    if debug.endswith("\n"):
        debug = debug[:-1]
    if print_context.endswith("\n"):
        print_context = print_context[:-1]

    if debug not in ["0", "1"]:
        print(f"[CONFFILES] Warning: 'debug' was not set to 0 or 1, resetting to 0.")
        debug = "0"
    if print_context not in ["0", "1"]:
        print("[CONFFILES] Warning: 'print_context' was not set to 0 or 1, resetting to 0.")
        print_context = "0"

    with open(abspaths["were_copied"], "w+", encoding="UTF-8") as wcf:
        wcf.write("Legacy files no longer need to be copied.")

    return debug, print_context


def _create_or_copy_files():
    """Returns data version as an integer"""
    debug, print_context = _find_files_in_legacy_directories()

    with open(CONFIG_DIRECTORY + "debug.nconf", "w+", encoding="UTF-8") as debug_nnf:
        debug_nnf.write(debug)
    with open(CONFIG_DIRECTORY + "print_context.nconf", "w+", encoding="UTF-8") as print_context_nnf:
        print_context_nnf.write(print_context)
    with open(CONFIG_DIRECTORY + "print_time.nconf", "w+", encoding="UTF-8") as print_context_nnf:
        print_context_nnf.write("0")


def create_config_files():
    # checks if the config path is empty (create or copy config files)
    if len(os.listdir(CONFIG_DIRECTORY)) == 0:
        _create_or_copy_files()
    
    define_expected_type("debug", "int")
    define_expected_type("print_context", "int")
    define_expected_type("print_time", "int")


def access_data(config_file: str):
    """Return None if the file does not exist."""
    if config_file == "DATA_VERSION":
        return str(DATA_VERSION)
    if not os.path.exists(CONFIG_DIRECTORY + config_file + ".nconf"):
        return None
    with open(CONFIG_DIRECTORY + config_file + ".nconf", "r", encoding="UTF-8") as file:
        return file.read()


def write_data(config_file: str, data: str, silent: bool = False, return_error_messages: bool = False):
    if config_file == "DATA_VERSION":
        errmsg = "[CONFFILES] Can not write in DATA_VERSION: name is reserved."
        if not silent:
            print(errmsg)
        if return_error_messages:
            return errmsg
        return
    if get_expected_type(config_file) == "int":
        if not data.isnumeric():
            errmsg = f"[CONFFILES] Can not write this data in {config_file}: incorrect data type: " \
                     f"expected data type is int, not str."
            if not silent:
                print(errmsg)
            if return_error_messages:
                return errmsg
            return
    with open(CONFIG_DIRECTORY + config_file + ".nconf", "w+", encoding="UTF-8") as file:
        file.write(data)


def define_expected_type(config_file: str, data_type: str):
    if not os.path.exists(CONFIG_DIRECTORY + "expected_types.nconf.json"):
        with open(CONFIG_DIRECTORY + "expected_types.nconf.json", "w+", encoding="UTF-8") as file:
            file.write("{}\n")
    with open(CONFIG_DIRECTORY + "expected_types.nconf.json", "r+", encoding="UTF-8") as file:
        json_loaded = json.load(file)
    json_loaded[config_file] = data_type
    with open(CONFIG_DIRECTORY + "expected_types.nconf.json", "w+", encoding="UTF-8") as file:
        json.dump(json_loaded, file)


def get_expected_type(config_file: str):
    with open(CONFIG_DIRECTORY + "expected_types.nconf.json", "r+", encoding="UTF-8") as file:
        json_loaded = json.load(file)
    return json_loaded.get(config_file)
