# GeeekPi-ZP-0110
The project contains scripts to configure and control the GeeekPi ZP-0110 heatsink with fan
for use with Raspberry Pi 4B single board computers (SBC).

Automatic fan control is enabled with the ```raspi-config``` utility however it ONLY supports the
Raspberry Pi OS.  For other OS (e.g., Ubuntu) a python script will need to be used to automatically control the fan when the temperature threshold is reached.

Follow the instructions provided by GeeekPi to enable fan control on Raspberry Pi OS. For product details or a sample Python script you can refer to the 52pi.com wiki page at: https://wiki.52pi.com/index.php/ZP-0110

## Prerequisites:
**Install the Python and i2c packages using the command below:**
```
sudo apt install -y python3-pip python3-dev python3-pil python3-setuptools python3-rpi.gpio i2c-tools
```
**Add the user account to the i2c group.**
```
sudo usermod -aG i2c someacct
```

## Add the Automated Script:
**Change to the **/opt** directory that is used for installing third-party (non-standard) software.**
```
cd /opt
```

**Clone the GeeekPi-ZP-0110 Github repository.**
```
git clone https://www.github.com/WhirlyHat/GeeekPi-ZP-0110.git
```

**Run the deployment script using ```sudo```.**
```
sudo bash ./GeeekPi-ZP-0110/deploy-service.sh
```

**Answer the questions when prompted to continue the installation.**
```
Existing service installation found.
Do you want to overwrite? (Y/n)
y
Creating a new service unit: /etc/systemd/system/pwm-fan-control.service
Successfully created service unit file.
Reloading systemd daemon...
Enabling the service: pwm-fan-control.service
Starting the service: pwm-fan-control.service
Service pwm-fan-control.service successfully enabled and started!
```

**Use systemctl to view the service status.**
```
systemctl status pwm-fan-control
```

**Reboot the system.**
```
sudo reboot now
```

## Customize the Triggers and Polling Interval:
Modify the following three variables in the ```/service/pwm-fan-control.py``` python file to specify when the fan turns on/off and how frequently the script checks the temperature.  _Note: Temperatures are measured in Celsius by default._

>Celsius degrees when the fan turns ON:
```
ON_THRESHOLD  = <integer>
```

>
>Celsius degrees when the fan turns OFF:
```
OFF_THRESHOLD = <integer>
```

>
>Seconds to wait until the next core temperature polling:
```
SLEEP_INTERVAL = <integer>
```

