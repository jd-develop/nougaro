#!/usr/bin/env sh
python3 shell.py -c "__test__()"
return_code=$?
if [ $return_code != 0 ]; then exit $return_code; fi

python3 -m tests.tests
return_code=$?
if [ $return_code != 0 ]; then exit $return_code; fi
