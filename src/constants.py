#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# IMPORTS
# nougaro modules imports
# no imports
# built-in python imports
import string

# ##########
# CONSTANTS
# ##########
DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

# ***** INDEV *****
FRENCH_MODE_LOWERCASE = "àäæçéèêëîïôöœùüÿ"
FRENCH_MODE_UPPERCASE = FRENCH_MODE_LOWERCASE.upper()
FRENCH_MODE = FRENCH_MODE_LOWERCASE + FRENCH_MODE_UPPERCASE
# *****************

IDENTIFIERS_LEGAL_CHARS = LETTERS + '_'  # + FRENCH_MODE  # needs more testing

# Special NOUGAROIGNORE comment delimiters

NOUGARO_IGNORE = [prefix1 + prefix2 + prefix3 + "NOUGAROIGNORE" for prefix1 in "#@/%!$;" for prefix2 in "#@/%!$;" for prefix3 in ["", " "]]
