# minWeZeroNodes
Contains firmware for Mints Wearable Nodes built with Raspberry Pi zero 2W

## Enabling I2C
To enable I2C you need to do three things.

add the line dtparam=i2c_arm=on to /boot/config.txt
add the line i2c-dev to /etc/modules
reboot

## Install Wiring Pi 
```
sudo apt-get purge wiringpi
hash -r
git clone --branch final_official_2.50 https://github.com/WiringPi/WiringPi.git ~/wiringpi
cd ~/wiringPi
./build
```

## Setting up the RTC
https://learn.adafruit.com/adding-a-real-time-clock-to-raspberry-pi/set-rtc-time

## Setting Time 
https://github.com/mi3nts/instructables/blob/master/linux/timeZoneSet.md
