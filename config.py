import os
import json


class Config:
    def __init__(self, config_filename):
        if "HEROKU" in os.environ.keys():
            self.token = os.environ['token']
            self.appid = os.environ['appid']
            self.login = os.environ['login']
            self.password = os.environ['password']
            self.db_name = os.environ['db_name']
            self.host = os.environ['host']
        else:
            with open(config_filename) as config_file:
                config = json.load(config_file)
            self.token = config['token']
            self.appid = config['appid']
            self.login = config['login']
            self.password = config['password']
            self.db_name = config['db_name']
            self.host = config['host']
