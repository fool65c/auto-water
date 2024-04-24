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

class PlantBed():
    def __init__(self, water_level, water_valve, sensor):
        self.water_level = water_level
        self.valve = water_valve
        self.sensor = sensor

    def water(self):
        try:
            temp, humidity = self.sensor.get_sensor_data()
        except Exception as e:
            temp = 0
            humidity = 10000000000000
            print(f'failed to get sensor data {e}')
        print ("Temperature in Fahrenheit is : %.2f F" %temp)
        print ("Relative Humidity is : %.2f %%RH" %humidity)
        
        if humidity < self.water_level:
            print('Turning Water on')
            self.valve.on()
        else:
            print('Turning Water off')
            self.valve.off()

def main():
    # Setup GPIO in board mode
    GPIO.setmode(GPIO.BOARD)


    plant_bed_one = PlantBed(
            75,
            WaterValve(13),
            Sensor(3)
        )

    while True:
        print('plant_bed_1')
        plant_bed_one.water()
        print('-'*30)
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    finally:
        GPIO.cleanup()

