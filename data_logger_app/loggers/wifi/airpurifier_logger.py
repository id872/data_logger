"""Module for logging air purity, temperature, humidity, fan RPM from AirPurifier device"""

from time import sleep

from configs.data_config import CsvConfig, JsonRequestType
from configs.wifi_airpurifier_config import WifiAirPurifierConfig
from devices.wifi_airpurifier import WifiAirPurifier
from logdata.data_manager import DataManager
from logdata.json.dev_data import DevData
from loggers.app_logger import app_logging
from loggers.utils.thread_maker import make_thread


class AirPurifierLogger:
    """Logging purifier data to csv class"""

    WRITE_DATA_EVERY_SEC = 60 * 5  # seconds

    def __init__(self):
        self.devices = []
        self.__initialize_device()
        make_thread(self.__write_data)
        app_logging.info("Airpurifier data logging...")

    def __initialize_device(self):
        app_logging.debug("Initializing AirPurifier device")
        self.devices = []

        for ip_address, dev_name in WifiAirPurifierConfig.DEV_ID_NAME.items():
            self.devices.append(
                WifiAirPurifier(
                    dev_name,
                    ip_address,
                    WifiAirPurifierConfig.DEV_ID_TOKEN.get(ip_address),
                )
            )

    def __write_data(self):
        while True:
            air_purifier_data = DevData(CsvConfig.PURIFIER_LOG_DIR_AND_FILE_PREFIX, JsonRequestType.PURIFIER)

            for device in self.devices:
                air_purifier_data.dev_names.append(device.dev_name)
                air_purifier_data.dev_data_readouts.append(device.read_data_json())
                app_logging.debug(device)

            if len(air_purifier_data.dev_data_readouts) > 0:
                DataManager.save_data(air_purifier_data)

            sleep(self.WRITE_DATA_EVERY_SEC)
