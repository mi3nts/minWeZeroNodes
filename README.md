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

## Getting the Serial Port to work 
To manually change the settings, edit the kernel command line with `sudo nano /boot/cmdline.txt`. Find the console entry that refers to the serial0 device, and remove it, including the baud rate setting. It will look something like `console=serial0,115200`. Make sure the rest of the line remains the same, as errors in this configuration can stop the Raspberry Pi from booting.

## Setting up multiple I2C devices 
On the to /boot/config.txt add the following lines
`dtoverlay=i2c-gpio,bus=4,i2c_gpio_delay_us=1,i2c_gpio_sda=23,i2c_gpio_scl=24`
And connect the secondary I2C devices to gpio pins 23(16) and 24(18). 

Inspired by this [link](https://www.instructables.com/Raspberry-PI-Multiple-I2c-Devices/) 

**Note:GPIO pins are not header numbers**

The pin diagrams for the rasbery pi zero are given below:
<img src="https://raw.githubusercontent.com/mi3nts/minWeZeroNodes/main/res/Raspberry-PI-Zero-Pinout-schema.jpg.webp"
     alt="Rasberry Pi Zero Pin Outs"
     style="float: left; margin-right: 10px;" />


## Installing BME280 Library for Rasbery pi 
```pip3 install RPi.bme280``` (Not pip3 install bme280)


## Data Sheet links 
* [SCD30](https://sensirion.com/media/documents/4EAF6AF8/61652C3C/Sensirion_CO2_Sensors_SCD30_Datasheet.pdf)
* [BME280: 1](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf)
* [BME280: 2](https://learn.adafruit.com/adafruit-bme280-humidity-barometric-pressure-temperature-sensor-breakout/downloads)


