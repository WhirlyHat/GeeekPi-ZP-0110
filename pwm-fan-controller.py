#!/usr/bin/python3

import RPi.GPIO as GPIO
import time
import subprocess

################################################################
ON_THRESHOLD = 36 # Celsius degrees when fan turns ON
OFF_THRESHOLD = 34 # Celsius degrees when fan turns OFF
SLEEP_INTERVAL = 10 # Seconds between core temperature polling
GPIO_PIN = 14 # GPIO pin used to control the fan
PWM_FREQ = 100 # PWM frequency in Hertz
PWM_MAX = 100 # PWM duty cycle MAXIMUM
PWM_MIN = 0 # PWM duty cycle MINIMUM
################################################################
GPIO.setmode(GPIO.BCM) # Broadcom SOC channel names
GPIO.setup(GPIO_PIN,GPIO.OUT) # Configure output channel
pwm = GPIO.PWM(GPIO_PIN,PWM_FREQ) # Create PWM instance
pwm.start(PWM_MIN) # Set initial PWM state

def get_celsius():
    celsius = subprocess.getoutput("vcgencmd measure_temp | sed 's/[^0-9.]//g'")
    try:
        return celsius
    except (IndexError, ValueError,) as e:
        # exception types may be incorrect
        raise RuntimeError('Could not obtain core temperature output.') from e

if __name__ == '__main__':
    # Validate the ON and OFF thresholds
    if OFF_THRESHOLD >= ON_THRESHOLD:
        raise RuntimeError('OFF_THRESHOLD must be less than ON_THRESHOLD')
    
    try:
        while True:
            celsius = round(float(get_celsius()))
            print("Temperature is " + str(celsius) + "C")
            # Turn output ON
            if celsius > ON_THRESHOLD:
                pwm.ChangeDutyCycle(PWM_MAX)
                print("Fan is on")
            # Turn output OFF
            elif celsius < OFF_THRESHOLD:
                pwm.ChangeDutyCycle(PWM_MIN)
                print("Fan is off")
            time.sleep(SLEEP_INTERVAL)
    except KeyboardInterrupt:
        pwm.stop()
        GPIO.cleanup() # Free up any resources used and return all channels back to safe defaults
        print("Ctrl + C pressed -- Terminating program")