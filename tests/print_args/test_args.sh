#!/usr/bin/env sh
# Nougaro : a python-interpreted high-level programming language
# Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) <jd-dev@laposte.net>

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

if [ ! "$1" ]; then python=python3; else python=$1; fi

$python shell.py tests/print_args/print_args1.noug
return_code=$?
if [ $return_code != 0 ]; then exit $return_code; fi

$python shell.py tests/print_args/print_args2.noug foo bar
return_code=$?
if [ $return_code != 0 ]; then exit $return_code; fi

$python shell.py tests/print_args/print_args_different1.noug
return_code=$?
if [ $return_code != 0 ]; then exit $return_code; fi

$python shell.py tests/print_args/print_args_different2.noug foo bar
return_code=$?
if [ $return_code != 0 ]; then exit $return_code; fi

$python shell.py -c "assert __args__ == ['-c', 'salut']" salut
return_code=$?
if [ $return_code != 0 ]; then exit $return_code; fi
