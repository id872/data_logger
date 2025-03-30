from enum import Enum


class JsonRequestType(str, Enum):
    SANTERNO = "santerno_readouts"
    DS18B20 = "ds18b20_readouts"
    PURIFIER = "purifier_readouts"
    TASMOTA_PLUG = "tasmota_readouts"
    I2C_AHT_ENS = "aht_ens_readouts"

    def __str__(self) -> str:
        return self.value


class CsvConfig:
    LOGGING_ENABLED = True
    LOG_ROOT_DIR = "/home/logs"

    SANTERNO_LOG_DIR_AND_FILE_PREFIX = "Power"
    DS18B20_LOG_DIR_AND_FILE_PREFIX = "Temperature"
    PURIFIER_LOG_DIR_AND_FILE_PREFIX = "Purifier"
    TASMOTA_PLUG_LOG_DIR_AND_FILE_PREFIX = "Tasmota"
    AHT_ENS_LOG_DIR_AND_FILE_PREFIX = "AhtEns"


class PostRequestConfig:
    LOGGING_ENABLED = True
    REQUEST_URL = "https://monit.pl.eu.org/add"
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0"
    REQUEST_TIMEOUT = 30
