import os
import sys
import yaml

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

from space_net_lib.datastructure.d2object import d2o

class ManageConfig(d2o.DataStoreObject):
    def __init__(self, logger):
        d2o.DataStoreObject.__init__(self, "ManageConfig", logger)

        self.global_config = {
            "language": "en_US",
            "username": "User",
            "__DESCRIPTION__": "Change the key name\"language\" to your first language (if available). "
                               "Also you can put your name in the \"username\" key. "
                               "It will be displayed at the top left of the window.",
        }

        self.server_data = {
            "Example Server": {
                "__EXAMPLE__": "This key is for application to identify the example data. "
                               "If you copied this example (like using it to create new item) and forgot to remove this key, "
                               "the application will ignore this item until you delete it.",
                "name": "Example Server",
                "ipAddress": "localhost",
                "port": 12161,
                "description": "An Example Server",
                "__DESCRIPTION__": "This is an example server. Try adding more servers like this format."
                               "(You can delete this item after you read this message)",
            }
        }

        self.server_daemon = {
            "Cloudflare": {
                "currentRootDomain": None,
                "enableDomainDNSRecordUpdater": False,
                "dnsRecordList": []
            },
            "processAttempt": 5
        }

        self.secret = {
            "Cloudflare": {
                "cf-dns-record-secret-token": "YOUR-TOKEN-HERE",
            }
        }

        self.communicate_support = {
            "S-API-KEY": "PUT YOUR SpaceNET-API KEY HERE",
            "DP-Private-KEY": "PUT YOUR DynamicPages PRIVATE KEY HERE",
        }

        self.cfg_mappings = {
            "global_config": {
                "defaultSetting": self.global_config,
                "savedLocation": "${SPACENET_MANAGE_CONFIG_PATH}/config/global.yaml",
                "cfgType": "yaml",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": False,
                }
            },
            "server_data": {
                "defaultSetting": self.server_data,
                "savedLocation": "${SPACENET_MANAGE_CONFIG_PATH}/config/server.yaml",
                "cfgType": "yaml",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": False,
                }
            },
            "communicate_support": {
                "defaultSetting": self.communicate_support,
                "savedLocation": "${SPACENET_MANAGE_CONFIG_PATH}/config/communicate.yaml",
                "cfgType": "yaml",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": True,
                }
            },
            "server_daemon": {
                "defaultSetting": self.server_daemon,
                "savedLocation": "${SPACENET_MANAGE_CONFIG_PATH}/config/daemon.yaml",
                "cfgType": "yaml",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": False,
                }
            },
            "secret": {
                "defaultSetting": self.secret,
                "savedLocation": "${SPACENET_MANAGE_CONFIG_PATH}/config/secret.yaml",
                "cfgType": "yaml",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": False,
                }
            }
        }

        self.load_data()
