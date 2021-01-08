import logging
from datetime import datetime
from os import path, makedirs
from sys import stdout

APP_LOGS_DIR = path.join(path.dirname(path.abspath(__file__)), '.logs')
APP_LOGGER_NAME = 'DevDataLogger'


def log_init():
    if not path.isdir(APP_LOGS_DIR):
        makedirs(APP_LOGS_DIR)

    log_file_path = path.join(APP_LOGS_DIR,
                              datetime.now().strftime("app_script__%d_%m_%Y__%H:%M:%S.log"))
    logging.basicConfig(level=logging.DEBUG,
                        filename=log_file_path,
                        filemode='a',
                        format='%(asctime)s.%(msecs)03d, [%(filename)s/%(funcName)s] -- '
                               '%(levelname)s --> %(message)s',
                        datefmt='%d-%m-%y_%H:%M:%S')

    stdout_log_handler = logging.StreamHandler(stdout)
    stdout_log_handler.setLevel(logging.INFO)
    stdout_log_handler.setFormatter(
        logging.Formatter('%(asctime)s -- %(filename)s/%(funcName)s -- '
                          '%(levelname)s --> %(message)s'))
    logging.getLogger(APP_LOGGER_NAME).addHandler(stdout_log_handler)


LOG_INFO = logging.INFO
LOG_DEBUG = logging.DEBUG

root_logging = logging.getLogger()
app_logging = logging.getLogger(APP_LOGGER_NAME)
