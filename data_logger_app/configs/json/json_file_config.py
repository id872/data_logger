from json import load
from os import path


class JsonFileConfig:
    JSON_CONFIG_FILE = path.join(path.dirname(path.abspath(__file__)), "auth_conf.json")

    def __init__(self):
        self.json_config = {}
        self.read_json_config_file()

    def read_json_config_file(self):
        if not path.exists(self.JSON_CONFIG_FILE):
            print("There is no {} file".format(self.JSON_CONFIG_FILE))
        else:
            with open(self.JSON_CONFIG_FILE) as file:
                json_file = load(file)

                try:
                    self.json_config["api_hash"] = json_file["api_hash"]
                    self.json_config["api_key"] = json_file["api_key"]
                    self.json_config["username"] = json_file["username"]
                    self.json_config["user_password"] = json_file["user_password"]
                except KeyError:
                    print("Invalid keys in the {} file".format(self.JSON_CONFIG_FILE))
