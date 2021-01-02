# -*- coding: utf-8 -*-
"""Main module for logging sensor/device data
"""

import logging
from datetime import datetime
from os import path, makedirs
from sys import stdout

from logdata.data_manager import get_json_post_payload_data, reload_json_config
from loggers.modbus.santerno_logger import SanternoLogger
from loggers.w1.ds18b20_logger import Ds18b20Logger
from loggers.wifi.airpurifier_logger import AirPurifierLogger
from loggers.wifi.tasmota_plug_logger import TasmotaPlugLogger


class DataMonitor:
    """ Application for monitoring temperature, Air Purity and PV data"""
    THIS_DIR = path.dirname(path.abspath(__file__))
    APP_LOGS_DIR = path.join(THIS_DIR, '.logs')

    def __init__(self):
        self.__log_init()
        self.pv_logger = SanternoLogger()
        self.therm_logger = Ds18b20Logger()
        self.air_purifier_logger = AirPurifierLogger()
        self.tasmota_plug_logger = TasmotaPlugLogger()

    def __log_init(self):
        if not path.isdir(self.APP_LOGS_DIR):
            makedirs(self.APP_LOGS_DIR)

        log_file_path = path.join(self.APP_LOGS_DIR,
                                  datetime.now().strftime("app_script__%d_%m_%Y__%H:%M:%S.log"))
        logging.basicConfig(level=logging.DEBUG,
                            filename=log_file_path,
                            filemode='a',
                            format='%(asctime)s.%(msecs)03d, [%(filename)s/%(funcName)s] -- '
                                   '%(levelname)s --> %(message)s',
                            datefmt='%d-%m-%y_%H:%M:%S')

        std_log_handler = logging.StreamHandler(stdout)
        std_log_handler.setLevel(logging.INFO)
        std_log_handler.setFormatter(
            logging.Formatter('%(asctime)s -- %(filename)s/%(funcName)s -- '
                              '%(levelname)s --> %(message)s'))
        logging.getLogger('DevDataLogger').addHandler(std_log_handler)


def get_option():
    try:
        return int(input('{}\n'.format(get_option.MSG)))
    except (ValueError, SyntaxError):
        print("Not a number. Try again.")
        return None


get_option.MSG = ' '.join(['1 -> Print this message.',
                           '2 -> Set INFO level logging to file.',
                           '3 -> Set DEBUG level logging to file.',
                           '4 -> PV_Active?',
                           '5 -> W1 sensor temperatures.',
                           '6 -> Show JSON post payload.',
                           '7 -> Reload JSON config'])


def main():
    data_monitor = DataMonitor()
    root_logger = logging.getLogger()
    dm_logger = logging.getLogger('DevDataLogger')

    # Getting commands
    while True:
        option = get_option()

        if option is None or option == 1:
            continue
        if option == 2:
            root_logger.handlers[0].setLevel(logging.INFO)
            dm_logger.info('File logger was set to INFO')
        elif option == 3:
            root_logger.handlers[0].setLevel(logging.DEBUG)
            dm_logger.info('File logger was set to DEBUG')
        elif option == 4:
            if not hasattr(data_monitor, 'pv_logger'):
                continue
            dm_logger.info(data_monitor.pv_logger.measure_active)
        elif option == 5:
            if not hasattr(data_monitor, 'therm_logger'):
                continue
            for sensor in data_monitor.therm_logger.sensors:
                dm_logger.info('%s -> %s', sensor.dev_name, sensor.temperatures)
        elif option == 6:
            dm_logger.info(get_json_post_payload_data())
        elif option == 7:
            reload_json_config()


if __name__ == "__main__":
    main()
