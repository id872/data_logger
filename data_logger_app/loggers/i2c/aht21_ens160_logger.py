"""Module for logging Air Quality data from I2C device"""

from time import sleep

from configs.data_config import CsvConfig, JsonRequestType
from configs.i2c_config import I2cConfig
from devices.aht21_ens160 import Aht21Ens160
from logdata.data_manager import DataManager
from logdata.json.dev_data import DevData
from loggers.app_logger import app_logging
from loggers.utils.thread_maker import make_thread


class Aht21Ens160Logger:
    """Logging purifier data to csv class"""

    WRITE_DATA_EVERY_SEC = 60 * 5  # seconds

    def __init__(self):
        self.devices = []
        self.__initialize_device()
        make_thread(self.__write_data)
        app_logging.info("I2C Aht21/Ens160 data logging...")

    def __initialize_device(self):
        app_logging.debug("Initializing AirPurifier device")
        self.devices = []

        for i2c_address, dev_name in I2cConfig.DEV_ID_NAME.items():
            self.devices.append(Aht21Ens160(dev_name, i2c_address))

    def __write_data(self):
        while True:
            i2c_data = DevData(CsvConfig.AHT_ENS_LOG_DIR_AND_FILE_PREFIX, JsonRequestType.I2C_AHT_ENS)

            for device in self.devices:
                i2c_data.dev_names.append(device.dev_name)
                i2c_data.dev_data_readouts.append(device.read_data_json())
                app_logging.debug(device)

            if len(i2c_data.dev_data_readouts) > 0:
                DataManager.save_data(i2c_data)

            sleep(self.WRITE_DATA_EVERY_SEC)
