#!/bin/bash
#
sleep 60
kill $(pgrep -f 'grafanaUpdate.py')
sleep 5
python3 grafanaUpdate.py &
sleep 5
python3 ipReader.py
