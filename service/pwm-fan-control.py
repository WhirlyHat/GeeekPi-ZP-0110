#!/usr/bin/python3

import RPi.GPIO as GPIO
import time
import subprocess

################################################################
ON_THRESHOLD = 40 # Celsius degrees when fan turns ON
OFF_THRESHOLD = 36 # Celsius degrees when fan turns OFF
SLEEP_INTERVAL = 10 # Seconds between core temperature polling
GPIO_PIN = 14 # GPIO pin used to control the fan
PWM_FREQ = 100 # PWM frequency in Hertz
PWM_MAX = 100 # PWM duty cycle MAXIMUM
PWM_MIN = 0 # PWM duty cycle MINIMUM
################################################################
fanState = "OFF" # String value to track the fan's state (on/off)
################################################################
GPIO.setmode(GPIO.BCM) # Broadcom SOC channel names
GPIO.setwarnings(False) # Suppress "RuntimeWarning: This channel is already in use"
GPIO.setup(GPIO_PIN,GPIO.OUT) # Configure output channel
pwm = GPIO.PWM(GPIO_PIN,PWM_FREQ) # Create PWM instance
pwm.start(PWM_MIN) # Set initial PWM state

def get_celsius():
    celsius = subprocess.getoutput("vcgencmd measure_temp | sed 's/[^0-9.]//g'")
    celsius = round(float(celsius))
    try:
        return celsius
    except (IndexError, ValueError,) as e:
        # exception types may be incorrect
        raise RuntimeError('Could not obtain core temperature output.') from e

if __name__ == '__main__':
    # Validate the ON and OFF thresholds
    if OFF_THRESHOLD >= ON_THRESHOLD:
        raise RuntimeError('OFF_THRESHOLD must be less than ON_THRESHOLD')
    else:
        print("\nPress CTRL + C to quit \n")
    
    try:
        while True:
            celsius = get_celsius()
            # Display temperature and fan state message
            print(\
                "Current Temp: " + str(celsius) + "C"\
                " -- "\
                "Upper: " + str(ON_THRESHOLD) + "C"\
                " / "\
                "Lower: " + str(OFF_THRESHOLD) + "C"\
                " -- "\
                "Fan: " + fanState \
            )

            # Start fan if upper threshold reached AND fan is NOT already running.
            if celsius > ON_THRESHOLD and fanState == "OFF":
                pwm.ChangeDutyCycle(PWM_MAX)
                fanState = "ON"
                print(\
                    "Temp " + str(celsius) + "C "\
                    "exceeded " + str(ON_THRESHOLD) + "C upper threshold"\
                    " -- "\
                    "Switching to Active Cooling"\
                )
                
            # Stop fan if lower threshold reached AND fan is running.
            elif celsius < OFF_THRESHOLD and fanState == "ON":
                pwm.ChangeDutyCycle(PWM_MIN)
                fanState = "OFF"
                print(\
                    "Temp " + str(celsius) + "C "\
                    "reached " + str(OFF_THRESHOLD) + "C lower threshold"\
                    " -- "\
                    "Switching to Passive Cooling"\
                )

            time.sleep(SLEEP_INTERVAL)
    except KeyboardInterrupt:
        print("\nStopping service...")
        pwm.stop()
        print("Performing resource cleanup...")
        GPIO.cleanup() # Free up any resources used and return all channels back to safe defaults
        print("Done")