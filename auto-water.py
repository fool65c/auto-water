import sys
import yaml
import time 
import smbus
import RPi.GPIO as GPIO
from prometheus_client import start_http_server, Gauge


class WaterValve():
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT)

    def off(self):
        GPIO.output(self.pin, GPIO.LOW)

    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)

    @property
    def status(self):
        if GPIO.input(self.pin) == GPIO.LOW:
            return 0
        elif GPIO.input(self.pin) == GPIO.HIGH:
            return 1

        return 'UNKNOWN'

class Sensor():
    def __init__(self, bus, address):
        self.bus = smbus.SMBus(bus)
        self.address = address

    def get_sensor_data(self):
        # SHT31 address, 0x44(68)
        self.bus.write_i2c_block_data(self.address, 0x2C, [0x06])

        data = self.bus.read_i2c_block_data(self.address, 0x00, 6)

        # Convert the data
        temp = data[0] * 256 + data[1]
        fTemp = -49 + (315 * temp / 65535.0)
        humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

        return fTemp, humidity

    @property
    def temp(self):
        temp, _ = self.get_sensor_data()
        return temp

    @property
    def humidity(self):
        _, humidity = self.get_sensor_data()
        return humidity

class ConfigException(Exception):
    pass

class SensorConfig():
    def __init__(self, config):
        self.i2c_bus = config['i2c_bus']
        self.address = config['address']

class WaterValveConfig():
    def __init__(self, config):
        self.pin = config['pin']

class WaterThresholdConfig():
    def __init__(self, config):
        self.start = config['start']
        self.stop = config['stop']

class PrometheusConfig():
    def __init__(self, config):
        self.port = config['port']


class Config():
    def __init__(self, file):
        config = self.__read_config(file)
        self.name = config['Name']
        self.sensor = SensorConfig(config['Sensor'])
        self.water_valve = WaterValveConfig(config['WaterValve'])
        self.water_thresholds = WaterThresholdConfig(config['WaterThresholds'])
        self.prometheus = PrometheusConfig(config['Prometheus'])

    def __read_config(self, file_path):
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
            self.__validate_config(config)
            return config

    def __validate_config(self, config):
        if 'Name' not in config:
            raise ConfigException('Name key required')

        if 'Sensor' not in config:
            raise ConfigException('Sensor dictionary required in config')

        if 'i2c_bus' not in config['Sensor']:
            raise ConfigException('i2c_bus key required in Sensor dictionary')

        if 'address' not in config['Sensor']:
            raise ConfigException('address key required in Sensor dictionary')

        if 'WaterValve' not in config:
            raise ConfigException('WaterValve dictionary required in config')

        if 'pin' not in config['WaterValve']:
            raise ConfigException('pin key required in WaterValve dictionary')

        if 'WaterThresholds' not in config:
            raise ConfigException('WaterThresholds dictionary required in config')

        if 'start' not in config['WaterThresholds']:
            raise ConfigException('start key required in WaterThresholds dictionary')

        if 'stop' not in config['WaterThresholds']:
            raise ConfigException('stop key required in WaterThresholds dictionary')

        if'Prometheus' not in config:
            raise ConfigException('Prometheus dictionary required in config')

        if 'port' not in config['Prometheus']:
            raise ConfigException('port key required in Prometheus dictionary')

        return True

def main():
    # Setup GPIO in board mode
    GPIO.setmode(GPIO.BCM)

    # read the config
    config = Config(sys.argv[1])

    # Start up the server to expose the metrics.
    start_http_server(config.prometheus.port)

    # Define the prometheus gauges
    temp_gauge = Gauge(f'auto_water_temperature_F', 'The temperature in F of the plant bed')
    humidity_gauge = Gauge(f'auto_water_humidity', 'The humidity in the plant bed')
    water_valve_gauge = Gauge(f'auto_water_valve_status', 'Status of the water valve, 1 on, 0 off')

    # Define the sensor and water valve
    sensor = Sensor(config.sensor.i2c_bus, config.sensor.address)
    water_valve = WaterValve(config.water_valve.pin)

    # loop until killed
    while True:
        print(f'starting water check: water on {config.water_thresholds.start} water off {config.water_thresholds.stop}')
        humidity = sensor.humidity
        if humidity <= config.water_thresholds.start:
            print('turning water on')
        if humidity >= config.water_thresholds.stop:
            print('turning water off')
            water_valve.off()
        print(f'Status - Temp: {sensor.temp} Humidity: {sensor.humidity} Water Valve: {water_valve.status}')
        temp_gauge.set(sensor.temp)
        humidity_gauge.set(sensor.humidity)
        water_valve_gauge.set(water_valve.status)
        print('-'*30)
        time.sleep(600)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python auto_water.py <config_file>')
        sys.exit(1)

    try:
        main()
    finally:
        GPIO.cleanup()

