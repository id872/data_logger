# -*- coding: utf-8 -*-
from enum import Enum


class JsonRequestType(Enum):
    SANTERNO = 'santerno_readouts'
    DS18B20 = 'ds18b20_readouts'
    PURIFIER = 'purifier_readouts'
    TASMOTA_PLUG = 'tasmota_readouts'


class CsvConfig:
    LOGGING_ENABLED = True
    LOG_ROOT_DIR = '/home/logs'

    SANTERNO_LOG_DIR_AND_FILE_PREFIX = 'Power'
    DS18B20_LOG_DIR_AND_FILE_PREFIX = 'Temperature'
    PURIFIER_LOG_DIR_AND_FILE_PREFIX = 'Purifier'
    TASMOTA_PLUG_LOG_DIR_AND_FILE_PREFIX = 'Tasmota'


class PostRequestConfig:
    LOGGING_ENABLED = True
    REQUEST_URL = 'https://yourserver.com/add'
    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0'
    REQUEST_TIMEOUT = 59
