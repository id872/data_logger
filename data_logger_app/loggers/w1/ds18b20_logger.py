# -*- coding: utf-8 -*-
"""Module for logging temperature from DS18B20 sensors
"""
from time import sleep

from app_logger import app_logging
from configs.data_config import CsvConfig, JsonRequestType
from configs.w1_config import DS18B20Config
from devices.w1_ds18b20 import W1Ds18b20
from logdata.data_manager import DataManager
from logdata.json.dev_data import DevData
from loggers.utils.thread_maker import make_thread


class Ds18b20Logger:
    """ Logging DS18B20 sensor temperatures """
    WRITE_TEMPS_EVERY_SEC = 60 * 5
    READ_TEMPS_EVERY_SEC = 15

    def __init__(self):
        self.sensors = []
        self.__initialize_sensors()
        make_thread(self.__measure_temperatures)
        make_thread(self.__write_temperatures)

        app_logging.info('Temperature data logging...')

    def __initialize_sensors(self):
        self.sensors = []

        for s_id, s_name in DS18B20Config.DEV_ID_NAME.items():
            app_logging.debug('Initializing [%s] sensor', s_name)
            self.sensors.append(W1Ds18b20(sensor_name=s_name,
                                          sensor_id=s_id))

    def __measure_temperatures(self):
        while True:
            for sensor in self.sensors:
                sensor.read_temperature()

            sleep(self.READ_TEMPS_EVERY_SEC)

    def __write_temperatures(self):
        sleep(self.READ_TEMPS_EVERY_SEC * 5)
        while True:
            w1_data = DevData(CsvConfig.DS18B20_LOG_DIR_AND_FILE_PREFIX,
                              JsonRequestType.DS18B20)

            for sensor in self.sensors:
                data = sensor.read_data_json()
                if data is None:
                    app_logging.debug('Data is probably obsolete or incomplete. Obsolete counter: %d',
                                      sensor.obsolete_data_count)
                    continue

                w1_data.dev_names.append(sensor.dev_name)
                w1_data.dev_data_readouts.append(data)
                app_logging.debug(sensor)

            if len(w1_data.dev_data_readouts) > 0:
                DataManager.save_data(w1_data)

            sleep(self.WRITE_TEMPS_EVERY_SEC)
