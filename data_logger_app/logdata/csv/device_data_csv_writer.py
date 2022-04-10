# -*- coding: utf-8 -*-
from csv import DictWriter
from os import path

from app_logger import app_logging
from execution_error import ExecutionError


class DeviceDataCsvWriter:
    def __init__(self):
        self.csv_writer = None

    @staticmethod
    def __get_merged_dict(log_date_time, dev_data, dev_names):
        if len(dev_names) != len(dev_data):
            raise ExecutionError('Device data and device names length mismatch')

        header_to_zip = [f'{n}_{key}' for n, d in zip(dev_names, dev_data) for key in d.keys()]
        data_to_zip = [f'{v:.2f}' for d in dev_data for v in d.values()]

        header_to_zip.insert(0, 'Date_Time')
        data_to_zip.insert(0, log_date_time)

        return dict(zip(header_to_zip, data_to_zip))

    def __write_data_to_file(self, file_path, dev_data, write_header=False):
        dev_names = dev_data.dev_names
        dev_data_readouts = dev_data.dev_data_readouts
        log_date_time = dev_data.log_date_time_csv

        try:
            with open(file_path, 'a') as csv_file:
                data_merged = self.__get_merged_dict(log_date_time, dev_data_readouts, dev_names)
                self.csv_writer = DictWriter(csv_file,
                                             fieldnames=data_merged.keys(),
                                             delimiter=',')
                if write_header:
                    self.csv_writer.writeheader()

                self.csv_writer.writerow(data_merged)
                app_logging.debug('Written device data:\n%s to:\n%s',
                                  data_merged, file_path)

        except (IOError, OSError, PermissionError):
            app_logging.error('Error while writing to: [%s]', file_path)

    def write_data(self, file_path, dev_data):
        self.__write_data_to_file(file_path,
                                  dev_data,
                                  write_header=not path.isfile(file_path))
