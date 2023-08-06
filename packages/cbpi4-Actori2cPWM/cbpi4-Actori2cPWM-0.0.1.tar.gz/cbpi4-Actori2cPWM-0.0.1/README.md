# CraftBeerPi4 Actor i2cPWM Plugin

## Actor i2cPWM ##
Plugin will provide the ability to run actors using Adafruit's DC & Stepper Motor HAT for Raspberry Pi. Reason for using this HAT is to take advantage of a the fully-dedicated PWM driver chip. The PWM control is amazing!

## Installation: ##
First two steps can be combined.
* install i2c support:
    * sudo raspi-config
    * Interface Options
    * I2C
    * Enable by selecting <Yes>
    * sudo reboot
    * After reboot, make sure it's working:
        * sudo i2cdetect -y 1
* configure SPI:
    * sudo raspi-config
    * SPI
    * Enable by selecting <Yes>
    * sudo reboot
    * After reboot, make sure it's working:
        * "ls -l /dev/spidev*"
* sudo pip3 install cbpi4-Actori2cPWM
* or install from repo: sudo pip3 install https://github.com/sjhoglund/cbpi4-Actori2cPWM/archive/main.zip
* cbpi add cbpi4-Actori2cPWM

## Usage: ##
More to come

## Hardware: ##
* Adafruit DC & Stepper Motor HAT
    * https://www.adafruit.com/product/2348

## Changelog: ##
* 01-29-22: (0.0.1) Updated README