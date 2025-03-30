from collections import OrderedDict

from devices.device import BaseDevice, dev_read_time_decorator
from devices.i2c.aht21 import AHT21
from devices.i2c.ens160 import ENS160


class Aht21Ens160(BaseDevice):
    def __init__(self, sensor_name, sensor_id):
        super().__init__(dev_name=sensor_name, dev_id=sensor_id)
        self.aht = AHT21()
        self.ens = ENS160()
        self.calibrate_ens_device()

    def calibrate_ens_device(self):
        current_temperature = self.aht.get_temperature()
        current_humidity = self.aht.get_humidity()

        if abs(current_temperature - self.ens.temperature) > 1:
            self.ens.calibrate_temp(current_temperature)

        if abs(current_humidity - self.ens.humidity) > 1:
            self.ens.calibrate_humidity(current_humidity)

    @dev_read_time_decorator
    def read_data_json(self) -> dict or None:
        return OrderedDict(
            {
                "temperature": self.aht.get_temperature(),
                "humidity": self.aht.get_humidity(),
                "aqi": self.ens.get_aqi(),
                "eco2": self.ens.get_eco2(),
                "tvoc": self.ens.get_voc(),
            }
        )
