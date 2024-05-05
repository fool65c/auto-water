# 17/11 27/13
import smbus

import RPi.GPIO as GPIO

from time import sleep

class WaterValve():
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT)

    def off(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def on(self):
        GPIO.output(self.pin, GPIO.LOW)

    @property
    def status(self):
        if GPIO.input(self.pin) == GPIO.LOW:
            return 'ON'
        elif GPIO.input(self.pin) == GPIO.HIGH:
            return 'OFF'

        return 'UNKNOWN'

def main():
    GPIO.setmode(GPIO.BCM)
    wv = WaterValve(22)
    wv.on()
    sleep(60)

if __name__ == "__main__":
    try:
        main()
    finally:
        GPIO.cleanup()

