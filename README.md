# GeeekPi-ZP-0110
The project contains scripts to configure and control the GeeekPi ZP-0110 heatsink with fan
for use with Raspberry Pi 4B single board computers (SBC).

Automatic fan control is enabled with the raspi-config utility however it ONLY supports the
Raspberry Pi OS.  For other OS (e.g., Ubuntu) a python script will need to be used to automatically control the fan when the temperature threshold is reached.

Follow the instructions provided by GeeekPi to enable fan control on Raspberry Pi OS. For product details or a sample Python script you can refer to the 52pi.com wiki page at: https://wiki.52pi.com/index.php/ZP-0110

## Prerequisites:
>Install the Python and i2c packages using the command below:
```bash
sudo apt install -y python3-pip python3-dev python3-pil python3-setuptools python3-rpi.gpio i2c-tools
```
>Add the user account to the i2c group.
```bash
sudo usermod -aG i2c someacct
```

## Add the Automated Script:
** Change to the /opt directory that is used for installing third-party (non-standard) software.



### Enable fan control and temperature threshold
**Add the following to the /boot/config.txt file**
```bash
dtoverlay=gpio-fan,gpiopin=14,temp=60000
```
**_Note: Temperature is measured in millicelsius. The fan turns off when the temperature falls by 10℃._**

**Reboot the system.**
```bash
sudo reboot now
```
