# -*- coding: utf-8 -*-
from base64 import b64encode

from configs.json.json_file_config import JsonFileConfig
from execution_error import ExecutionError


class JsonRequestHelper:
    def __init__(self):
        json_config_data = JsonFileConfig().json_config

        self.post_payload = {
            'data': {
                'username': json_config_data['username'],
                'user_password': json_config_data['user_password']
            },
            'hash': b64encode(json_config_data['api_hash'].encode()).decode()
        }
        self.post_payload_data = self.post_payload['data']

        self.api_key = json_config_data['api_key']

    def add_dev_readout(self, dev_data):
        self.post_payload_data.setdefault(dev_data.json_request_type.value, []).append({
            "readout_time": dev_data.log_date_time_sql,
            "data": []})

        if len(dev_data.dev_names) != len(dev_data.dev_data_readouts):
            raise ExecutionError('Device names and device data length mismatch')

        for dev_name, readout_data in zip(dev_data.dev_names, dev_data.dev_data_readouts):
            readout_data['dev_name'] = dev_name
            self.post_payload_data.setdefault(dev_data.json_request_type.value, []).append(
                readout_data)

    def clear_data(self, json_req_type):
        self.post_payload_data[json_req_type.value] = []

    def reload_json_config(self):
        json_config_data = JsonFileConfig().json_config
        self.post_payload['hash'] = b64encode(json_config_data['api_hash'].encode()).decode()
        self.post_payload_data['username'] = json_config_data['username']
        self.post_payload_data['user_password'] = json_config_data['user_password']
        self.api_key = json_config_data['api_key']
