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

## Enable i2c Features:
If you are unable to access the i2c features on the Raspberry Pi, you may need to modify the config.txt file to enable it.

Unlike the Raspberry Pi OS, which stores its **config.txt** file in the **/boot** directory, Ubuntu uses the **/boot/firmware** directory.[askUbuntu article](https://askubuntu.com/questions/1462320/updating-raspberrypi-4b-from-ubuntu-server-20-04-to-22-04-caused-usercfg-txt-to)

At the top of the config.txt file under the **[all]** section, comment out the existing _dtparam_ and add a custom entry for the fan.
```
[all]
# Enable the audio output…..
# Commented out by me
#dtparam=i2c_arm=on
# Added this dtparam for GeeekPi
dtparam=i2c_arm=on,i2c_arm_baudrate=400000
```

At the bottom of the config.txt file under the **[all]** section, I added the _dtoverlay_ entry.
```
[all]
# Added this overlay for the UCtronics shutdown feature
dtoverlay=gpio-shutdown,gpio_pin=4,active_low=1,gpio_pull=up
```

After a reboot the power button now operated properly within Ubuntu.  Hopefully this will help others experiencing the same issue.



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
