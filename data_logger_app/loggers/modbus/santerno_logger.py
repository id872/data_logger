# -*- coding: utf-8 -*-
"""Module for logging Inverters data (power, voltage, current, etc.)
"""
from os import path
from time import sleep

from app_logger import app_logging
from configs.data_config import CsvConfig, JsonRequestType
from configs.modbus_config import SanternoConfig
from devices.modbus_santerno import ModbusSanterno
from logdata.data_manager import DataManager
from logdata.json.dev_data import DevData
from loggers.utils.thread_maker import make_thread


class SanternoLogger:
    """ Logging data from Santerno PV inverters. """
    INVERTER_ACTIVITY_CHECK_TIME_SEC = 60 * 2  # 2 minutes
    MEASURE_EVERY_SEC = 30  # seconds

    def __init__(self):
        if not path.exists(SanternoConfig.PORT_DEV):
            app_logging.error('Device port %s does not exist',
                              SanternoConfig.PORT_DEV)
            return

        self.inverters = []
        self.measure_active = False
        self.__inverters_re_init()
        make_thread(self.__dev_port_and_inverter_monitoring)
        make_thread(self.__measure)

        app_logging.info('Measuring power...')

    def __inverters_re_init(self):
        self.inverters = []

        for inv_adr, inv_name in SanternoConfig.DEV_ID_NAME.items():
            app_logging.debug('%s device initialization', inv_name)
            self.inverters.append(ModbusSanterno(inverter_name=inv_name,
                                                 slave_address=inv_adr,
                                                 tty_port=SanternoConfig.PORT_DEV))

    def __dev_port_and_inverter_monitoring(self):
        def is_dev_port_reattached():
            if path.exists(SanternoConfig.PORT_DEV):
                return False

            app_logging.debug('Device (FTDI or UART) is detached or reattached (by system or user)')

            for port_num in range(0, 20):
                dev_to_check = '{}{}'.format(SanternoConfig.PORT_DEV_NAME, port_num)
                if path.exists(dev_to_check):
                    SanternoConfig.PORT_DEV = dev_to_check
                    self.__inverters_re_init()
                    app_logging.info('New device was initialized: %s', dev_to_check)
                    return True
            app_logging.error('No FTDI/UART device found')
            return False

        while True:
            if is_dev_port_reattached():
                continue

            app_logging.debug('Checking inverter activity function')

            self.measure_active = any([inv.is_up() for inv in self.inverters])
            sleep(self.INVERTER_ACTIVITY_CHECK_TIME_SEC)

    def __measure(self):
        sleep(self.MEASURE_EVERY_SEC)
        while True:
            if not self.measure_active:
                app_logging.debug("Measure is not active.")
                ModbusSanterno.reload_minimalmodbus()
                self.__inverters_re_init()
                sleep(self.INVERTER_ACTIVITY_CHECK_TIME_SEC)
                continue

            modbus_data = DevData(CsvConfig.SANTERNO_LOG_DIR_AND_FILE_PREFIX,
                                  JsonRequestType.SANTERNO)

            for inverter in self.inverters:
                dev_data_read = inverter.read_data_json()
                if dev_data_read is None:
                    app_logging.debug('Data [%s] could not be read.',
                                      inverter.dev_name)
                    continue

                modbus_data.dev_names.append(inverter.dev_name)
                modbus_data.dev_data_readouts.append(inverter.read_data_json())
                app_logging.debug(inverter)

            if len(modbus_data.dev_data_readouts) > 0:
                DataManager.save_data(modbus_data)

            sleep(self.MEASURE_EVERY_SEC)
