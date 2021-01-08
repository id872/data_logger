# -*- coding: utf-8 -*-
""" This module supports DS18B20 temperature sensors
"""
from collections import Counter, OrderedDict
from time import sleep

from w1thermsensor import W1ThermSensor

from app_logger import app_logging
from devices.device import BaseDevice, dev_read_time_decorator


class W1Ds18b20(BaseDevice):
    MAX_INIT_ATTEMPTS = 10
    RE_INIT_WAIT_TIME_SEC = 2
    MAX_COUNT_MEASURES = 45
    MAX_OBSOLETE_DATA_THRESH = 10

    def __init__(self, sensor_id, sensor_name):
        super().__init__(dev_name=sensor_name, dev_id=sensor_id)
        self.w1_sensor = None
        self.temperatures = []
        self.obsolete_data_count = 0

    def try_initialize(self):
        if self.w1_sensor:
            return True

        for _ in range(self.MAX_INIT_ATTEMPTS):
            try:
                self.w1_sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, self.dev_id)
                app_logging.debug("Sensor '%s' ('%s') initialized", self.dev_id, self.dev_name)
                return True
            # catching expected & unexpected exceptions from third-party library
            # pylint: disable=W0703
            except Exception as ex:
                sleep(self.RE_INIT_WAIT_TIME_SEC)
                app_logging.error('Sensor id=[%s] could not be initialized. Next attempt...',
                                  self.dev_id)
                app_logging.debug(str(ex))
                continue

        app_logging.error("Sensor '%s' ('%s') could not be initialized", self.dev_id, self.dev_name)
        return False

    @dev_read_time_decorator
    def read_temperature(self):
        """ Reads temperature from kernel DS18B20 slave file"""

        def w1_sensor_read_valid_temperature():
            """ Mechanism for getting valid temperature value
            (in case when W1 connection is not stable) """
            values = [self.w1_sensor.get_temperature() for _ in range(6)]
            return Counter(values).most_common(1)[0][0]

        if len(self.temperatures) > self.MAX_COUNT_MEASURES:
            self.temperatures.pop(0)
        if not self.try_initialize():
            app_logging.debug('Sensor [%s] is not initialized', self.dev_name)
            return
        try:
            self.temperatures.append(w1_sensor_read_valid_temperature())
            self.obsolete_data_count = 0
        # catching expected & unexpected exceptions from third-party library
        # pylint: disable=W0703
        except Exception as ex:
            self.read_error_count += 1
            app_logging.debug("Read temperature from sensor '%s' ('%s') failed.\n%s",
                              self.dev_id, self.dev_name,
                              ex)

    def __count_avg_temperature(self):
        """ Counts average temperature from temperature buffer """
        if self.temperatures:
            self.obsolete_data_count += 1
            return sum(self.temperatures) / len(self.temperatures)
        return None

    def read_data_json(self) -> dict or None:
        avg_temp = self.__count_avg_temperature()

        if self.obsolete_data_count >= self.MAX_OBSOLETE_DATA_THRESH:
            app_logging.debug('Obsolete data. Obsolete data counter: %d',
                              self.obsolete_data_count)
            avg_temp = None

        return OrderedDict({
            'temperature': str(round(avg_temp, 2)) if avg_temp else avg_temp
        })
