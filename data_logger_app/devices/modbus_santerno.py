# -*- coding: utf-8 -*-
""" This module supports communication with Santerno Inverters
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
    __REGISTER_CURRENT_POWER = 1658
    __REGISTER_FIELD_VOLTAGE = 1650
    __REGISTER_FIELD_CURRENT = 1652
    __REGISTER_PRODUCED_POWER = 1661
    __REGISTER_CPU_TEMP = 1707
    __REGISTER_RADIATOR_TEMP = 1709
    __REGISTER_GRID_VOLTAGE = 1654
    __REGISTER_GRID_FREQ = 1655
    __REGISTER_GRID_CURRENT = 1656

    __MAX_ATTEMPTS_FOR_VALUE = 6
    __RETRY_TIME = SanternoConfig.RS_485_MODBUS_TIMEOUT + 0.01
    __H_THRESHOLD_WATT = 3600
    __H_THRESHOLD_GRID_CURRENT = 30

    __MEASURING_ACTIVE_THRESHOLD_WATT = 10

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

    @staticmethod
    def __get_register_value(reg_data, factor):
        value = 0
        for x in [reg_val << (reg_idx * 16) for reg_idx, reg_val in enumerate(reg_data)]:
            value |= x

        return value * factor

    @modbus_wait_for_not_busy
    def __read_register(self, adr_reg, val_factor, no_reg=1):
        if not self.inverter_instrument:
            app_logging.error('Santerno device is not initialized')
            return None

        attempts = 0
        errors = set()

        ModbusSanterno.__modbus_is_busy = True
        while attempts < self.__MAX_ATTEMPTS_FOR_VALUE:
            try:
                reg_read_data = self.inverter_instrument.read_registers(adr_reg, no_reg)
                ModbusSanterno.__modbus_is_busy = False
                return self.__get_register_value(reg_read_data, val_factor) if reg_read_data else None
            # catching expected & unexpected exceptions from third-party library
            # pylint: disable=W0703
            except Exception as ex:
                self.read_error_count += 1
                errors.add(str(ex))

            attempts += 1
            sleep(self.__RETRY_TIME)

        ModbusSanterno.__modbus_is_busy = False
        app_logging.debug("[%s] Value could not be read. Attempts [%d] Modbus address [%s]\n%s",
                          self.dev_name,
                          attempts,
                          adr_reg,
                          '\n'.join(errors))

        return None

    def __read_current_power(self):
        """ Reads the inverter current power generated (AC) """

        curr_pwr = self.__read_register(self.__REGISTER_CURRENT_POWER, 1)

        if curr_pwr is not None and curr_pwr < self.__H_THRESHOLD_WATT:
            return curr_pwr
        return None

    def __read_produced_power(self):
        """ Reads the inverter total power produced (kWh) """

        return self.__read_register(self.__REGISTER_PRODUCED_POWER, 0.01, 2)

    def __read_cpu_temperature(self):
        """ Reads the inverter CPU temperature """

        return self.__read_register(self.__REGISTER_CPU_TEMP, 0.01)

    def __read_radiator_temperature(self):
        """ Reads the inverter radiator temperature """

        return self.__read_register(self.__REGISTER_RADIATOR_TEMP, 0.01)

    def __read_field_voltage(self):
        """ Reads the inverter DC Voltage """

        return self.__read_register(self.__REGISTER_FIELD_VOLTAGE, 0.1)

    def __read_field_current(self):
        """ Reads the inverter DC Current """

        return self.__read_register(self.__REGISTER_FIELD_CURRENT, 0.01)

    def __read_grid_voltage(self):
        """ Reads the grid AC Voltage """

        return self.__read_register(self.__REGISTER_GRID_VOLTAGE, 0.1)

    def __read_grid_freq(self):
        """ Reads the grid AC frequency """

        return self.__read_register(self.__REGISTER_GRID_FREQ, 0.01)

    def __read_grid_current(self):
        """ Reads the grid AC Current """

        grid_current = self.__read_register(self.__REGISTER_GRID_CURRENT, 0.01)

        if grid_current is not None and grid_current < self.__H_THRESHOLD_GRID_CURRENT:
            return grid_current

        return None

    def is_up(self):
        """ Checks if inverter produces power """

        power_val = self.__read_current_power()
        return power_val is not None and power_val > self.__MEASURING_ACTIVE_THRESHOLD_WATT

    @dev_read_time_decorator
    def read_data_json(self) -> dict or None:
        return OrderedDict({
            'ac_power': self.__read_current_power(),
            'dc_voltage': self.__read_field_voltage(),
            'dc_current': self.__read_field_current(),
            'cpu_temperature': self.__read_cpu_temperature(),
            'radiator_temperature': self.__read_radiator_temperature(),
            'power_produced': self.__read_produced_power(),
            'grid_voltage': self.__read_grid_voltage(),
            'grid_freq': self.__read_grid_freq(),
            'grid_current': self.__read_grid_current()
        })
