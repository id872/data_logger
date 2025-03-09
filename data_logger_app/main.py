"""Main module for logging sensor/device data"""

from logdata.data_manager import get_json_post_payload_data, reload_json_config
from loggers.app_logger import LOG_DEBUG, LOG_INFO, app_logging, log_init, root_logging

# from loggers.modbus.santerno_logger import SanternoLogger
from loggers.w1.ds18b20_logger import Ds18b20Logger

# from loggers.wifi.airpurifier_logger import AirPurifierLogger
from loggers.wifi.tasmota_plug_logger import TasmotaPlugLogger


def get_option():
    try:
        return int(input("{}\n".format(get_option.MSG)))
    except (ValueError, SyntaxError):
        print("Not a number. Try again.")
        return None


get_option.MSG = " ".join(
    [
        "1 -> Print this message.",
        "2 -> Set INFO level logging to file.",
        "3 -> Set DEBUG level logging to file.",
        "4 -> PV_Active?",
        "5 -> W1 sensor temperatures.",
        "6 -> Show JSON post payload.",
        "7 -> Reload JSON config.",
        "8 -> Quit.",
    ]
)


def main():
    log_init()
    # pv_logger = SanternoLogger()
    therm_logger = Ds18b20Logger()
    # air_purifier_logger = AirPurifierLogger()
    tasmota_plug_logger = TasmotaPlugLogger()

    while True:
        option = get_option()

        if option is None or option == 1:
            continue
        if option == 2:
            root_logging.handlers[0].setLevel(LOG_INFO)
            app_logging.info("File logger was set to INFO")
        elif option == 3:
            root_logging.handlers[0].setLevel(LOG_DEBUG)
            app_logging.info("File logger was set to DEBUG")
        elif option == 4:
            if "pv_logger" not in locals():
                continue
            # app_logging.info(pv_logger.measure_active)
        elif option == 5:
            if "therm_logger" not in locals():
                continue
            for sensor in therm_logger.sensors:
                app_logging.info("%s -> %s", sensor.dev_name, sensor.temperatures)
        elif option == 6:
            app_logging.info(get_json_post_payload_data())
        elif option == 7:
            reload_json_config()
        elif option == 8:
            exit(1)


if __name__ == "__main__":
    main()
