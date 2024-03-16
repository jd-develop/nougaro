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
        major = ver_json_loaded.get("major")
        minor = ver_json_loaded.get("minor")
        patch = ver_json_loaded.get("patch")
        phase = ver_json_loaded.get("phase")
        phase_minor = ver_json_loaded.get("phase-minor")
        version = f"{major}.{minor}.{patch}-{phase}"
        if phase_minor != 0:
            version += f".{phase_minor}"
        version_id = ver_json_loaded.get("version-id")
    return major, minor, patch, phase, phase_minor, version, version_id


MAJOR, MINOR, PATCH, PHASE, PHASE_MINOR, VERSION, VERSION_ID = _read_noug_version_json()
