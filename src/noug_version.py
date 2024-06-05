#!/usr/bin/env python3
# -*- coding=utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""noug_version

This files reads the noug_version.json once, then returns it.
"""
import os
import json
import pathlib


def _read_noug_version_json():
    noug_dir = os.path.abspath(pathlib.Path(__file__).parent.parent.absolute())

    with open(os.path.abspath(noug_dir + "/noug_version.json")) as ver_json:
        # we load the nougaro version stored in noug_version.json
        ver_json_loaded = json.load(ver_json)
        major: int = ver_json_loaded.get("major")
        minor: int = ver_json_loaded.get("minor")
        patch: int = ver_json_loaded.get("patch")
        phase: str = ver_json_loaded.get("phase")
        release_serial: int = ver_json_loaded.get("release-serial")

        version_id: int = ver_json_loaded.get("version-id")
        data_version: int = ver_json_loaded.get("data-version")
        lib_version: int = ver_json_loaded.get("lib-version")

        version: str = f"{major}.{minor}.{patch}-{phase}"
        if release_serial != 0:
            version += f".{release_serial}"
    return major, minor, patch, phase, release_serial, version, version_id, data_version, lib_version


MAJOR, MINOR, PATCH, PHASE, RELEASE_SERIAL, VERSION, VERSION_ID, DATA_VERSION, LIB_VERSION = _read_noug_version_json()
