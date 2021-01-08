# -*- coding: utf-8 -*-
""" Module for communication with Santerno Inverters
"""
from collections import OrderedDict
from importlib import reload
from time import sleep

import minimalmodbus

from app_logger import app_logging
from configs.modbus_config import SanternoConfig
from devices.device import BaseDevice, dev_read_time_decorator


def modbus_wait_for_not_busy(func_decorated):
    def func_wrapper(self, *args, **kwargs):
        while self.is_busy():
            sleep(SanternoConfig.RS_485_MODBUS_TIMEOUT)
            continue
        return func_decorated(self, *args, **kwargs)

    return func_wrapper


class ModbusSanterno(BaseDevice):
    REGISTER_CURRENT_POWER = 1658
    REGISTER_FIELD_VOLTAGE = 1650
    REGISTER_FIELD_CURRENT = 1652
    REGISTER_PRODUCED_POWER = 1661
    REGISTER_CPU_TEMP = 1707
    REGISTER_RADIATOR_TEMP = 1709

    MAX_ATTEMPTS_FOR_VALUE = 6
    RETRY_TIME = SanternoConfig.RS_485_MODBUS_TIMEOUT + 0.01
    H_THRESHOLD_WATT = 3600

    MEASURING_ACTIVE_THRESHOLD_WATT = 10

    __modbus_is_busy = False

    def __init__(self, inverter_name, slave_address, tty_port):
        super().__init__(dev_name=inverter_name, dev_id=slave_address)
        self.tty_port = tty_port
        self.inverter_instrument = None
        self.__try_initialize()

    @classmethod
    def is_busy(cls):
        return cls.__modbus_is_busy

    @staticmethod
    def reload_minimalmodbus():
        app_logging.debug('minimalmodbus reloading...')
        reload(minimalmodbus)

    def __try_initialize(self):
        if self.inverter_instrument is not None:
            return True
        try:
            self.inverter_instrument = minimalmodbus.Instrument(
                self.tty_port,
                self.dev_id)
        # catching expected & unexpected exceptions from third-party library
        # pylint: disable=W0703
        except Exception as error:
            app_logging.error(error)

        if self.inverter_instrument:
            self.inverter_instrument.serial.baudrate = SanternoConfig.RS_485_BAUDRATE
            self.inverter_instrument.serial.stopbits = SanternoConfig.RS_485_STOP_BITS
            self.inverter_instrument.mode = SanternoConfig.RS_485_MODBUS_MODE
            self.inverter_instrument.serial.timeout = SanternoConfig.RS_485_MODBUS_TIMEOUT
            self.inverter_instrument.close_port_after_each_call = \
                SanternoConfig.RS_485_CLOSE_PORT_AFTER_CALL
            app_logging.debug('Inverter %s on %s is ready', self.dev_name, self.tty_port)
            return True
        app_logging.debug('Inverter [%s] is not initialized', self.dev_name)
        return False

    @modbus_wait_for_not_busy
    def __read_register(self, adr_reg, no_reg=1):
        if not self.inverter_instrument:
            app_logging.error('Santerno device is not initialized')
            return None

        attempts = 0
        errors = set()

        ModbusSanterno.__modbus_is_busy = True
        while attempts < self.MAX_ATTEMPTS_FOR_VALUE:
            try:
                val = self.inverter_instrument.read_registers(adr_reg, no_reg)
                ModbusSanterno.__modbus_is_busy = False
                return val
            # catching expected & unexpected exceptions from third-party library
            # pylint: disable=W0703
            except Exception as ex:
                self.read_error_count += 1
                errors.add(str(ex))

            attempts += 1
            sleep(self.RETRY_TIME)

        ModbusSanterno.__modbus_is_busy = False
        app_logging.debug("[%s] Value could not be read. Attempts [%d] Modbus address [%s]\n%s",
                          self.dev_name,
                          attempts,
                          adr_reg,
                          '\n'.join(errors))

        return None

    def _read_current_power(self):
        """ Reads the inverter current power generated (AC) """

        curr_pwr = self.__read_register(self.REGISTER_CURRENT_POWER)

        if curr_pwr is not None and \
                curr_pwr[0] < self.H_THRESHOLD_WATT:
            return curr_pwr[0]
        return None

    def _read_produced_power(self):
        """ Reads the inverter total power produced (kWh) """

        pwr = self.__read_register(self.REGISTER_PRODUCED_POWER, 2)

        if pwr is not None and len(pwr) == 2:
            return ((pwr[1] << 16) | pwr[0]) / 100.0
        return None

    def _read_cpu_temperature(self):
        """ Reads the inverter CPU temperature """

        cpu_temp = self.__read_register(self.REGISTER_CPU_TEMP)

        if cpu_temp is not None:
            return cpu_temp[0] / 100.0

        return None

    def _read_radiator_temperature(self):
        """ Reads the inverter radiator temperature """

        radiator_temp = self.__read_register(self.REGISTER_RADIATOR_TEMP)

        if radiator_temp is not None:
            return radiator_temp[0] / 100.0

        return None

    def _read_field_voltage(self):
        """ Reads the inverter DC Voltage """

        voltage = self.__read_register(self.REGISTER_FIELD_VOLTAGE)

        if voltage is not None:
            return voltage[0] / 10.0

        return None

    def _read_field_current(self):
        """ Reads the inverter DC Current """

        current = self.__read_register(self.REGISTER_FIELD_CURRENT)

        if current is not None:
            return current[0] / 100.0

        return None

    def is_up(self):
        """ Checks if inverter produces power """

        power_val = self._read_current_power()
        return power_val is not None and power_val > self.MEASURING_ACTIVE_THRESHOLD_WATT

    @dev_read_time_decorator
    def read_data_json(self) -> dict or None:
        return OrderedDict({
            'ac_power': self._read_current_power(),
            'dc_voltage': self._read_field_voltage(),
            'dc_current': self._read_field_current(),
            'cpu_temperature': self._read_cpu_temperature(),
            'radiator_temperature': self._read_radiator_temperature(),
            'power_produced': self._read_produced_power()
        })
