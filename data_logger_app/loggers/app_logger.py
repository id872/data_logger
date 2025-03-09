import logging
from datetime import datetime
from pathlib import Path
from sys import stdout

APP_LOGGER_NAME = "DevDataLogger"


def log_init():
    app_log_dir = Path(__file__).parent.parent / ".logs"
    if not app_log_dir.is_dir():
        app_log_dir.mkdir()

    log_file_path = app_log_dir / datetime.now().strftime("app_script__%Y_%m_%d__%H:%M:%S.log")
    logging.basicConfig(
        level=logging.INFO,
        filename=log_file_path,
        filemode="a",
        format="%(asctime)s.%(msecs)03d, [%(filename)s/%(funcName)s] -- %(levelname)s --> %(message)s",
        datefmt="%y-%m-%d_%H:%M:%S",
    )

    stdout_log_handler = logging.StreamHandler(stdout)
    stdout_log_handler.setLevel(logging.INFO)
    stdout_log_handler.setFormatter(
        logging.Formatter("%(asctime)s -- %(filename)s/%(funcName)s -- %(levelname)s --> %(message)s")
    )
    logging.getLogger(APP_LOGGER_NAME).addHandler(stdout_log_handler)


LOG_INFO = logging.INFO
LOG_DEBUG = logging.DEBUG

root_logging = logging.getLogger()
app_logging = logging.getLogger(APP_LOGGER_NAME)
