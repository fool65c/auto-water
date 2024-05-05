# 17/11 27/13
import smbus
import time

import RPi.GPIO as GPIO


class WaterValve():
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT)

    def off(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def on(self):
        GPIO.output(self.pin, GPIO.LOW)


def main():
    # Setup GPIO in board mode
    GPIO.setmode(GPIO.BCM)


    WaterValve(22).off()
    WaterValve(23).off()


if __name__ == "__main__":
    try:
        main()
    finally:
        GPIO.cleanup()

