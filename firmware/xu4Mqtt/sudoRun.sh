#!/bin/bash
sleep 30
hwclock --systohc
chmod -R 777 /dev/ttyACM*
chmod -R 777 /dev/gpiomem*
chmod -R 777 /dev/ttyUSB*
chmod -R 777 /dev/i2c*

