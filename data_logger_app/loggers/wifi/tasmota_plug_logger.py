# -*- coding: utf-8 -*-
"""Module for logging AC power from Tasmota device
"""
from time import sleep

from app_logger import app_logging
from configs.data_config import CsvConfig, JsonRequestType
from configs.wifi_tasmota_plug_config import WifiTasmotaPlugConfig
from devices.wifi_tasmota_plug import WifiTasmotaPlug
from logdata.data_manager import DataManager
from logdata.json.dev_data import DevData
from loggers.utils.thread_maker import make_thread


class TasmotaPlugLogger:
    """ Logging purifier data to csv class """
    WRITE_DATA_EVERY_SEC = 60 * 4  # seconds

    def __init__(self):
        self.devices = []
        self.__initialize_device()
        make_thread(self.__write_data)
        app_logging.info('Tasmota data logging...')

    def __initialize_device(self):
        app_logging.debug('Initializing AirPurifier device')
        self.devices = []

        for ip_address, dev_name in WifiTasmotaPlugConfig.DEV_ID_NAME.items():
            self.devices.append(WifiTasmotaPlug(
                dev_name,
                ip_address))

    def __write_data(self):
        while True:
            tasmota_data = DevData(CsvConfig.TASMOTA_PLUG_LOG_DIR_AND_FILE_PREFIX,
                                   JsonRequestType.TASMOTA_PLUG)

            for device in self.devices:
                tasmota_data.dev_names.append(device.dev_name)
                tasmota_data.dev_data_readouts.append(device.read_data_json())
                app_logging.debug(device)

            if len(tasmota_data.dev_data_readouts) > 0:
                DataManager.save_data(tasmota_data)

            sleep(self.WRITE_DATA_EVERY_SEC)
