# GeeekPi-ZP-0110
# Repository contains scripts to configure and control the GeeekPi ZP-0110 heatsink with fan
# for Raspberry Pi 4B single board computers (SBC).
#
# Automatic fan control is enabled with the raspi-config utility however it only supports the
# Raspberry Pi OS.  For other OS (e.g., Ubuntu) a python script may be used to enable the fan
# when the temperature threshold is reached.
#
# Prerequisites:
# Python and i2c packages may be installed using the command below:
# sudo apt install -y python3-pip python3-dev python3-pil python3-setuptools python3-rpi.gpio i2c-tools
# sudo usermod -aG i2c someacct
#
# 
