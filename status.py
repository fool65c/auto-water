# 17/11 27/13
import smbus

import RPi.GPIO as GPIO


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

class Sensor():
    def __init__(self, bus):
        self.bus = smbus.SMBus(bus)

    def get_sensor_data(self):
        # SHT31 address, 0x44(68)
        self.bus.write_i2c_block_data(0x44, 0x2C, [0x06])

        data = self.bus.read_i2c_block_data(0x44, 0x00, 6)

        # Convert the data
        temp = data[0] * 256 + data[1]
        fTemp = -49 + (315 * temp / 65535.0)
        humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

        return fTemp, humidity

def main():
    # Setup GPIO in board mode
    GPIO.setmode(GPIO.BOARD)

    sensors = [Sensor(1), Sensor(3)]
    valves = [WaterValve(11), WaterValve(13)]

    for sensor in sensors:
        print(f'sensor {sensor.bus}: {sensor.get_sensor_data}')

    for valve in valves:
        print(f'valve {valve.pin}: {valve.status}')

if __name__ == "__main__":
    try:
        main()
    finally:
        GPIO.cleanup()

