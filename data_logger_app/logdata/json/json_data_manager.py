# -*- coding: utf-8 -*-
from time import sleep

from app_logger import app_logging
from configs.data_config import JsonRequestType, PostRequestConfig
from logdata.json.json_helper import JsonRequestHelper
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
    def __init__(self):
        self.__busy = False
        self.__json = JsonRequestHelper()

    def is_busy(self):
        return self.__busy

    def get_post_payload(self):
        return self.__json.post_payload

    def reload_json_config(self):
        self.__json.reload_json_config()

    def __check_server_response_and_clear_data(self, resp):
        _ = [self.__json.clear_data(jrt) for jrt in JsonRequestType if jrt.value in resp]

        for jrt in JsonRequestType:
            req_data = self.__json.post_payload_data.get(jrt.value)
            if req_data and len(req_data) > 0:
                app_logging.debug('Invalid response [%s] on [%s] request.',
                                  resp, jrt.value)

    def __send_json_data(self):
        self.__busy = True
        self.__check_server_response_and_clear_data(
            PostRequest(self.get_post_payload()).encrypt_and_send(self.__json.api_key))
        self.__busy = False

    @wait_for_not_busy
    def process_data(self, dev_data):
        if not PostRequestConfig.LOGGING_ENABLED:
            return

        self.__json.add_dev_readout(dev_data)
        make_thread(self.__send_json_data, is_daemon=False)
