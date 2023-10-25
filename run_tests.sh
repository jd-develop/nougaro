#!/usr/bin/env sh
python3 shell.py -c "__test__()"
# python3 shell.py -c "__test__(1)"  # use this to print "OK (thing)" when (thing) is tested, useful for debugging
return_code=$?
if [ $return_code != 0 ]; then exit $return_code; fi

python3 -m tests.tests
return_code=$?
if [ $return_code != 0 ]; then exit $return_code; fi
