import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

from space_net_lib.datastructure.d2object import d2o
from space_net_lib.datastructure.d2object.d2o import D2OUpdater

D2OUpdater = D2OUpdater

class APIConfig(d2o.DataStoreObject):
    def __init__(self, logger):
        d2o.DataStoreObject.__init__(self, "APIConfig", logger)

        self.api_main = {
            "server-name": "An API Server",
            "server-docs-link": "your-api-docs-link",
        }

        self.api_access = {
            "max_api_access_rate_desc": "Rate limits for API access per 10 minutes. Default is 420",
            "max_api_access_rate": 420
        }

        self.api_database = {
            "database-name": "your-database-name-here",
            "database-url": "your-database-url-here",
            "username": "your-username-here",
            "password": "your-password-here",
        }

        self.api_yazule = {
            "cf_turnstile_secret_token": "your-turnstile-secret-token-here",
        }

        self.api_communicate_support = {
            "__comment__": "This config is for other SpaceNET application can access api without"
                           "rate limits or use private method.",
            "communicate_token": "set-password-here",
            "dynamic_pages_secret_password": "set-password-here"
        }

        self.cfg_mappings = {
            "api_main": {
                "defaultSetting": self.api_main,
                "savedLocation": "${SPACENET_API_CONFIG_PATH}/config/main.yaml",
                "cfgType": "yaml",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": False,
                }
            },
            "api_access": {
                "defaultSetting": self.api_access,
                "savedLocation": "${SPACENET_API_CONFIG_PATH}/config/access.yaml",
                "cfgType": "yaml",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": True,
                }
            },
            "api_database": {
                "defaultSetting": self.api_database,
                "savedLocation": "${SPACENET_API_CONFIG_PATH}/config/database.yaml",
                "cfgType": "yaml",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": True,
                }
            },
            "api_yazule": {
                "defaultSetting": self.api_yazule,
                "savedLocation": "${SPACENET_API_CONFIG_PATH}/config/yazule.yaml",
                "cfgType": "yaml",
                "sfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": True,
                }
            },
            "api_communicate_support": {
                "defaultSetting": self.api_communicate_support,
                "savedLocation": "${SPACENET_API_CONFIG_PATH}/config/communicate.yaml",
                "cfgType": "yaml",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": True,
                }
            }
        }

        self.load_data()
