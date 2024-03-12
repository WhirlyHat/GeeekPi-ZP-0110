#!/usr/bin/python3

import RPi.GPIO as GPIO
import subprocess
import logging
import sys

from time     import sleep;
from datetime import datetime;
from zoneinfo import ZoneInfo;

class FanControlService:
    ## Private Constants - DO NOT MODIFY THESE VALUES ##
    _GPIO_PIN       = 14   # GPIO pin used to control the fan
    _PWM_FREQ       = 100  # PWM frequency in Hertz
    _PWM_MAX        = 100  # PWM duty cycle MAXIMUM
    _PWM_MIN        = 0    # PWM duty cycle MINIMUM
    _PWM_OFF        = 0    # PWM duty cycle OFF

    ## Public Attributes ##
    on_threshold   = int() # Celsius degrees when fan turns ON
    off_threshold  = int() # Celsius degrees when fan turns OFF
    sleep_interval = int() # Seconds between core temperature polling
    
    ## Built-in & Private Methods ##
    def __init__(self,on_threshold=60,off_threshold=40,sleep_interval=60):
        # Set initial values for private attributes
        self.on_threshold   = on_threshold
        self.off_threshold  = off_threshold
        self.sleep_interval = sleep_interval

        # Instantiate loggers
        self.logger = self._init_logger()
        self.logger.info('%s: instance created', type(self).__name__)

        # Instantiate GPIO.PWM
        self.pwm = self._init_gpio()

        # Set initial states
        self.logger.info('%s: setting initial fan state to \'OFF\'', type(self).__name__)
        self.pwm.start(self._PWM_OFF)
        self.fan_state = 'OFF'
        self.logger.info('%s', self.__str__())

    def __str__(self):
        return type(self).__name__ + f": polls every {self.sleep_interval} secs; " + \
            f"turns ON at {self.on_threshold}\N{DEGREE SIGN}C ({self.Fahrenheit(self.on_threshold)}\N{DEGREE SIGN}F) " + \
            f"and OFF at {self.off_threshold}\N{DEGREE SIGN}C ({self.Fahrenheit(self.off_threshold)}\N{DEGREE SIGN}F)."

    def _init_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(logging.DEBUG) # Available levels: critical, error, debug, info, warning
        stdout_handler.setFormatter(logging.Formatter(self.logTimestamp()+' | %(levelname)8s | %(message)s'))
        logger.addHandler(stdout_handler)
        return logger
    
    def _init_gpio(self):
        GPIO.setmode(GPIO.BCM) # Broadcom SOC channel names
        GPIO.setwarnings(False) # Suppress "RuntimeWarning: This channel is already in use"
        GPIO.setup(self._GPIO_PIN, GPIO.OUT) # Configure as an output channel
        return GPIO.PWM(self._GPIO_PIN, self._PWM_FREQ) # Create PWM instance
    
    ## Public Methods ##
    def logTimestamp(self):
        current_dt = datetime.now()
        current_dt = current_dt.replace(tzinfo=ZoneInfo('localtime'))

        if current_dt.tzinfo == None or current_dt.tzinfo.utcoffset(current_dt) == None:
            # Timezone Naive - Failed to set zone information
            return current_dt.strftime("%Y-%m-%d %A %H:%M:%S")
        else:
            # Timezone Aware - Zone information configured
            return current_dt.strftime("%Y-%m-%d %A %H:%M:%S %Z %z")

    def core_temp(self):
        try:
            degrees = subprocess.getoutput("vcgencmd measure_temp | sed 's/[^0-9.]//g'")
            degrees = round(float(degrees))
            return degrees
        except (IndexError, ValueError,) as e:
            # Exception types may need to be modified
            raise RuntimeError('Could not obtain core temperature output.') from e

    def Fahrenheit(self,degrees):
        return round(float(((degrees * 1.8)+32)))

    def start(self):
        # Validate the on_threshold and off_threshold values
        if self.off_threshold >= self.on_threshold:
            raise RuntimeError('off_threshold must be less than the on_threshold value.')
        
        try:
            while True:
                current_temp = self.core_temp()
                current_status = ""

                if self.fan_state == 'ON':
                    current_status = 'Cooling'
                else:
                    current_status = 'Normal'
                
                log_message = 'Core Temp:{0:3}\N{DEGREE SIGN}C ({1:3}\N{DEGREE SIGN}F) <> Fan:{2:>4} <> Status: {3}'.format(
                    current_temp, self.Fahrenheit(current_temp), self.fan_state, current_status)
                
                self.logger.info(log_message)

                # Start fan if upper threshold reached AND fan is NOT already running
                if current_temp > self.on_threshold and self.fan_state == "OFF":                    
                    log_message = 'Core Temp:{0:3}\N{DEGREE SIGN}C ({1:3}\N{DEGREE SIGN}F) <> Fan:{2:>4} <> '.format(
                        current_temp, self.Fahrenheit(current_temp), self.fan_state)
                    log_message += 'Status: HEAT over{0:3}\N{DEGREE SIGN}C ({1:3}\N{DEGREE SIGN}F) limit'.format( 
                        self.on_threshold, self.Fahrenheit(self.on_threshold))
                    self.logger.warning(log_message)

                    self.fan_state = "ON"
                    self.pwm.ChangeDutyCycle(self._PWM_MAX)

                # Stop fan if lower threshold reached AND fan is running
                if current_temp < self.off_threshold and self.fan_state == "ON":
                    log_message = 'Core Temp:{0:3}\N{DEGREE SIGN}C ({1:3}\N{DEGREE SIGN}F) <> Fan:{2:>4} <> '.format(
                        current_temp, self.Fahrenheit(current_temp), self.fan_state)
                    log_message += 'Status: COOLED device under{0:3}\N{DEGREE SIGN}C ({1:3}\N{DEGREE SIGN}F) limit'.format(
                        self.off_threshold, self.Fahrenheit(self.off_threshold))
                    self.logger.warning(log_message)

                    self.fan_state = "OFF"
                    self.pwm.ChangeDutyCycle(self._PWM_OFF)

                previous_temp = current_temp
                sleep(self.sleep_interval)

        except KeyboardInterrupt:
            # Remove ^C text displayed on screen
            sys.stderr.write("\b\b\r")

            self.logger.warning('Keyboard interrupt signal (SIGINT) received...')
            self.stop()
    
    def stop(self):
        self.logger.info('Stopping the PWM service...')
        self.pwm.stop()

        self.logger.info('Cleaning up objects and environment...')
        del self.on_threshold
        del self.off_threshold    
        del self.sleep_interval
        del self.fan_state
        del self.pwm
        del self.logger

        sys.exit(0)

## Main section ##
if __name__ == '__main__':
    GeeekPi = FanControlService(on_threshold=41,off_threshold=32,sleep_interval=60)
    GeeekPi.start()
