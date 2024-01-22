#!/usr/bin/env sh
# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

echo 0 > config/SHOULD_TEST_PRINT_OK

python3 shell.py tests/test_file.noug
# python3 shell.py -c "__test__(1)"  # use this to print "OK (thing)" when (thing) is tested, useful for debugging
return_code=$?
if [ $return_code != 0 ]; then exit $return_code; fi

python3 shell.py tests/test_import_in_current_dir.noug
return_code=$?
if [ $return_code != 0 ]; then exit $return_code; fi

python3 shell.py -v
return_code=$?
if [ $return_code != 0 ]; then exit $return_code; fi

python3 -m tests.tests
return_code=$?
if [ $return_code != 0 ]; then exit $return_code; fi
