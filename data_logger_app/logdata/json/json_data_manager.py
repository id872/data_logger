from time import sleep

from configs.data_config import JsonRequestType, PostRequestConfig
from connection_check import is_network_connected
from logdata.json.json_helper import JsonRequestHelper
from loggers.app_logger import app_logging
from loggers.utils.thread_maker import make_thread
from request.post_request import PostRequest


def wait_for_not_busy(func_decorated):
    def func_wrapper(self, *args, **kwargs):
        while self.is_busy():
            sleep(0.1)
            continue
        return func_decorated(self, *args, **kwargs)

    return func_wrapper


class JsonDataManager:
    _POP_AFTER_RESP_FAILS = 3
    _ERR_RESP_PATTERN = "{}_data_error"
    _OK_RESP_PATTERN = "{}_inserted_ok"

    def __init__(self):
        self.__busy = False
        self.__json = JsonRequestHelper()
        self._resp_fail_counters = {}

    def is_busy(self):
        return self.__busy

    def get_post_payload(self):
        return self.__json.post_payload

    def reload_json_config(self):
        self.__json.reload_json_config()

    def __check_server_response_and_clear_data(self, resp: str):
        _ = [self.__json.clear_data(jrt) for jrt in JsonRequestType if self._OK_RESP_PATTERN.format(jrt) in resp]

        for jrt in JsonRequestType:
            self._resp_fail_counters.setdefault(jrt, 0)

            req_data = self.__json.post_payload_data.get(jrt)
            if req_data and len(req_data) > 0:
                app_logging.error("Invalid response [%s] on [%s] request.", resp, jrt)
                if (resp == "" and is_network_connected()) or self._ERR_RESP_PATTERN.format(jrt) in resp:
                    self._resp_fail_counters[jrt] += 1
            else:
                self._resp_fail_counters[jrt] = 0

            if req_data and len(req_data) > 1 and self._resp_fail_counters[jrt] >= self._POP_AFTER_RESP_FAILS:
                readout = self.__json.post_payload_data.get(jrt).pop(0)
                app_logging.error("POP readout type: %s \n data: %s", jrt, readout)

    def __send_json_data(self):
        self.__busy = True
        self.__check_server_response_and_clear_data(
            PostRequest(self.get_post_payload()).encrypt_and_send(self.__json.api_key)
        )
        self.__busy = False

    @wait_for_not_busy
    def process_data(self, dev_data):
        if not PostRequestConfig.LOGGING_ENABLED:
            return

        self.__json.add_dev_readout(dev_data)
        make_thread(self.__send_json_data, is_daemon=False)
