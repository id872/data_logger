# -*- coding: utf-8 -*-
import logging

from logdata.csv.csv_data_manager import CsvDataManager
from logdata.json.json_data_manager import JsonDataManager

_LOGGER = logging.getLogger('DevDataLogger')


def get_json_post_payload_data():
    return DataManager.json_post_payload().get('data')


def reload_json_config():
    DataManager.reload_json_config()


class DataManager:
    """ This is main class for logging data from devices """
    __manager_csv = CsvDataManager()
    __manager_json = JsonDataManager()

    def __init__(self):
        pass

    @classmethod
    def __feed_managers(cls, dev_data):
        cls.__manager_csv.process_data(dev_data)
        cls.__manager_json.process_data(dev_data)

    @classmethod
    def json_post_payload(cls):
        return cls.__manager_json.get_post_payload()

    @classmethod
    def reload_json_config(cls):
        cls.__manager_json.reload_json_config()

    @classmethod
    def save_data(cls, dev_data):
        """
        Device returns data in JSON format. It contains
        container_name key indicating from which device data came
        :param dev_data: dict
        :return: None
        """
        if None in dev_data.dev_data_readouts:
            _LOGGER.debug("No data: %s for %s",
                          dev_data, dev_data.log_dir_file_prefix)
            return

        cls.__feed_managers(dev_data)
