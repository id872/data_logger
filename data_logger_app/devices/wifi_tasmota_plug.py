# -*- coding: utf-8 -*-
""" This module supports Lanberg/Blitzwolf/Gosund Wifi plug
"""
from collections import OrderedDict
from json import loads
from urllib.parse import urljoin, quote
from urllib.request import Request, urlopen

from app_logger import app_logging
from devices.device import BaseDevice, dev_read_time_decorator


class WifiTasmotaPlug(BaseDevice):
    REQ_TIMEOUT_SEC = 2
    STATUS_SNS_CMD = 'Status 8'

    def __init__(self, dev_name, dev_ip):
        super().__init__(dev_name=dev_name, dev_id=dev_ip)
        self.dev_url = None
        self.initialize()

    def initialize(self):
        self.dev_url = urljoin('http://{}'.format(self.dev_id),
                               'cm?cmnd={}'.format(quote(self.STATUS_SNS_CMD)))

    def __get_dev_resp(self):
        if not self.dev_url:
            app_logging.error('Tasmota device is not initialized')
            return None
        try:
            request = Request(self.dev_url)
            return loads(urlopen(request, timeout=self.REQ_TIMEOUT_SEC).read().decode())
        # catching expected & unexpected exceptions from urllib library
        # pylint: disable=W0703
        except Exception as ex:
            self.read_error_count += 1
            app_logging.error(ex)
        return None

    @dev_read_time_decorator
    def read_data_json(self) -> dict or None:
        def get_energy_value(key):
            if dev_resp and dev_resp.get('StatusSNS') and dev_resp['StatusSNS'].get('ENERGY'):
                return dev_resp['StatusSNS']['ENERGY'].get(key)
            return None

        dev_resp = self.__get_dev_resp()
        return OrderedDict({
            'ac_power': get_energy_value('Power'),
            'ac_voltage': get_energy_value('Voltage'),
            'ac_current': get_energy_value('Current')
        })
