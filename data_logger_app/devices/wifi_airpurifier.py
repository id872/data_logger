# -*- coding: utf-8 -*-
""" This module supports Xiaomi Air Purifier device
"""
import logging
from collections import OrderedDict

from miio.airpurifier import AirPurifier

from app_logger import app_logging
from devices.device import BaseDevice, dev_read_time_decorator

logging.getLogger('miio.miioprotocol').disabled = True
logging.getLogger('miio.protocol').disabled = True


class WifiAirPurifier(BaseDevice):
    def __init__(self, dev_name, dev_ip, dev_token):
        super().__init__(dev_name=dev_name, dev_id=dev_ip)
        self.device_token = dev_token
        self.wifi_device = None

    def try_initialize(self):
        if self.wifi_device is not None:
            return True
        try:
            self.wifi_device = AirPurifier(self.dev_id, self.device_token)
            app_logging.debug('AirPurifier device [%s] initialized', self.dev_id)
            return True
        # catching expected & unexpected exceptions from third-party library
        # pylint: disable=W0703
        except Exception as ex:
            app_logging.error('Initialization error. %s', ex)
        return False

    def __get_dev_resp(self):
        if not self.try_initialize():
            app_logging.error('AirPurifier device is not initialized')
            return None
        try:
            return self.wifi_device.status()
        # catching expected & unexpected exceptions from third-party library
        # pylint: disable=W0703
        except Exception as ex:
            self.read_error_count += 1
            app_logging.error(ex)
        return None

    @dev_read_time_decorator
    def read_data_json(self) -> dict or None:
        def try_get_attr(name):
            return getattr(dev_resp, name) if hasattr(dev_resp, name) else None

        dev_resp = self.__get_dev_resp()
        return OrderedDict({
            'aqi': try_get_attr('aqi'),
            'humidity': try_get_attr('humidity'),
            'temperature': try_get_attr('temperature'),
            'fan_rpm': try_get_attr('motor_speed')
        })
