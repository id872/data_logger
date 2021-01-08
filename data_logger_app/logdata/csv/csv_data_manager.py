# -*- coding: utf-8 -*-
from os import listdir, makedirs, path
from time import strftime

from app_logger import app_logging
from configs.data_config import CsvConfig
from execution_error import ExecutionError
from logdata.csv.device_data_csv_writer import DeviceDataCsvWriter


class CsvDataManager:
    def __init__(self):
        self.device_data_csv_writer = DeviceDataCsvWriter()

    @staticmethod
    def __create_log_dir(directory_for_file):
        try:
            makedirs(directory_for_file)
            app_logging.debug('Log directory: %s created', directory_for_file)
        except (IOError, OSError, PermissionError) as error:
            raise ExecutionError(f'Log dir: {directory_for_file} cannot be created') from error

    def __write_file(self, file_path, dev_data):
        self.device_data_csv_writer.write_data(file_path, dev_data)

    def __try_get_existing_file_path(self, log_dir_file_prefix):
        def get_file_path():
            for file_name in f_names:
                if curr_date_f_name in file_name:
                    return path.join(dst_log_dir, file_name)
            app_logging.debug('New file need to be created...')
            return path.join(dst_log_dir, strftime(f'{curr_date_f_name}_%H:%M:%S.csv'))

        dst_log_dir = path.join(CsvConfig.LOG_ROOT_DIR, log_dir_file_prefix)
        if not path.isdir(dst_log_dir):
            self.__create_log_dir(dst_log_dir)

        f_names = [f for f in listdir(dst_log_dir) if path.isfile(path.join(dst_log_dir, f))]

        curr_date_f_name = strftime(f'{log_dir_file_prefix}_%Y-%m-%d')
        return get_file_path()

    def process_data(self, dev_data):
        if not CsvConfig.LOGGING_ENABLED:
            return

        file_path = self.__try_get_existing_file_path(dev_data.log_dir_file_prefix)
        self.__write_file(file_path, dev_data)
