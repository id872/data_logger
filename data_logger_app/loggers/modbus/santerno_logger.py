# -*- coding: utf-8 -*-
"""Module for logging Inverters data (power, voltage, current, etc.)
"""

import logging
from os import path
from time import sleep

from configs.data_config import CsvConfig, JsonRequestType
from configs.modbus_config import ModbusConfig
from devices.modbus_santerno import ModbusSanterno
from logdata.data_manager import DataManager
from logdata.json.dev_data import DevData
from loggers.utils.thread_maker import make_thread

_LOGGER = logging.getLogger('DevDataLogger')


class SanternoLogger:
    """ Logging data from Santerno PV inverters. """
    INVERTER_ACTIVITY_CHECK_TIME_SEC = 60 * 2  # 2 minutes
    MEASURE_EVERY_SEC = 30  # seconds

    def __init__(self):
        if not path.exists(ModbusConfig.PORT_DEV):
            logging.error('Device port %s does not exist',
                          ModbusConfig.PORT_DEV)
            return

        self.inverters = []
        self.measure_active = False
        self.__inverters_re_init()
        make_thread(self.__dev_port_and_inverter_monitoring)
        make_thread(self.__measure)

        _LOGGER.info('Measuring power...')

    def __inverters_re_init(self):
        self.inverters = []

        for inv_adr, inv_name in ModbusConfig.DEV_ID_NAME.items():
            _LOGGER.debug('%s device initialization', inv_name)
            self.inverters.append(ModbusSanterno(inverter_name=inv_name,
                                                 slave_address=inv_adr,
                                                 tty_port=ModbusConfig.PORT_DEV))

    def __dev_port_and_inverter_monitoring(self):
        def is_dev_port_reattached():
            if path.exists(ModbusConfig.PORT_DEV):
                return False

            _LOGGER.debug('Device (FTDI or UART) is detached or reattached (by system or user)')

            for port_num in range(0, 20):
                dev_to_check = '{}{}'.format(ModbusConfig.PORT_DEV_NAME, port_num)
                if path.exists(dev_to_check):
                    ModbusConfig.PORT_DEV = dev_to_check
                    self.__inverters_re_init()
                    _LOGGER.info('New device was initialized: %s', dev_to_check)
                    return True
            logging.error('No FTDI/UART device found')
            return False

        while True:
            if is_dev_port_reattached():
                continue

            _LOGGER.debug('Checking inverter activity function')

            self.measure_active = any([inv.is_up() for inv in self.inverters])
            sleep(self.INVERTER_ACTIVITY_CHECK_TIME_SEC)

    def __measure(self):
        sleep(self.MEASURE_EVERY_SEC)
        while True:
            if not self.measure_active:
                _LOGGER.debug("Measure is not active.")
                ModbusSanterno.reload_minimalmodbus()
                self.__inverters_re_init()
                sleep(self.INVERTER_ACTIVITY_CHECK_TIME_SEC)
                continue

            modbus_data = DevData(CsvConfig.MODBUS_LOG_DIR_AND_FILE_PREFIX,
                                  JsonRequestType.MODBUS)

            for inverter in self.inverters:
                dev_data_read = inverter.read_data_json()
                if dev_data_read is None:
                    _LOGGER.debug('Data [%s] could not be read.',
                                  inverter.dev_name)
                    continue

                modbus_data.dev_names.append(inverter.dev_name)
                modbus_data.dev_data_readouts.append(inverter.read_data_json())
                _LOGGER.debug(inverter)

            if len(modbus_data.dev_data_readouts) > 0:
                DataManager.save_data(modbus_data)

            sleep(self.MEASURE_EVERY_SEC)