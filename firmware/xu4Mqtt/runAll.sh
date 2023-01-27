#!/bin/bash
#
sleep 60
kill $(pgrep -f 'ips7100ReaderV1.py')
sleep 5
python3 ips7100ReaderV1.py &
sleep 5

kill $(pgrep -f 'readI2c.py')
sleep 5
python3 readI2c.py &
sleep 5

kill $(pgrep -f 'GPSReader.py')
sleep 5
python3 GPSReader.py &
sleep 5

kill $(pgrep -f 'batteryReader.py')
sleep 5
python3 batteryReader.py &
sleep 5


python3 ipReader.py
sleep 5