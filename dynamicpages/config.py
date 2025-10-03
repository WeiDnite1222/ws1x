import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

from space_net_lib.datastructure.d2object import d2o
from space_net_lib.datastructure.d2object.d2o import D2OUpdater

D2OUpdater = D2OUpdater

class DPConfig(d2o.DataStoreObject):
    def __init__(self, logger):
        d2o.DataStoreObject.__init__(self, "DynamicPagesConfig", logger)

        self.dynamic_main = {
            "server-name": "A DynamicPages Server (Powered by FastAPI and PagesUtil)",
            "webRootDir": "${SPACENET_DP_DATA_PATH}",
            "__COMMENT__": "if you want to specify the web root directory. Just replace \"${DYNAMIC_WEB_ROOT_DIR}\" "
                           "to another directory.",
        }

        self.sites_config = {
            "index.html" : {
                "__EXAMPLE__": "...",
                "updateMethodList": [
                    {
                        "sleepTime": 360,
                        "mapFuncNameInPagesUtil": "test",
                    }
                ]
            }
        }

        self.dynamic_insert_config = {
        }

        self.communicate_support = {
            "__comment__": "This config is for other SpaceNET application can access api without"
                           "rate limits or use private method.",
            "communicate_token": "set-password-here",
            "dynamic_pages_secret_password": "set-password-here",
        }

        self.dynamic_pages_daemon = {
            "enableFailAttempt": True,
            "processAttempt": 5,
            "insertLastUpdateTime": False,
            "skipUpdateIfAnyProcessFailed": False,
            "useOldCacheWhenStart": True,
            "useCacheWhenProcessFailed": False,
        }

        self.dp_cloudflare = {
            "turnstile-secret-token": "turnstile-secret-token-here",
        }

        self.error_pages = {
            "__comment__": "Change HTTP error code value to your custom page filepath."
                           "(If the DynamicPages can't find the file it will use normal text"
                           "with error code as the error page)",
            "302": None,
            "400": None,
            "401": None,
            "403": None,
            "404": None,
            "405": None,
            "406": None,
            "407": None,
            "408": None,
            "422": None,
            "500": None,
            "502": None,
        }

        self.cache_settings = {
            "savePageCache": True,
            "sleepTime": 50,
        }

        self.cfg_mappings = {
            "dynamic_main": {
                "defaultSetting": self.dynamic_main,
                "savedLocation": "${SPACENET_DP_CONFIG_PATH}/config/main.yaml",
                "cfgType": "yaml",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": False,
                    "replace_keyword_in_config": True
                }
            },
            "sites_config": {
                "defaultSetting": self.sites_config,
                "savedLocation": "${SPACENET_DP_CONFIG_PATH}/config/sites.json",
                "cfgType": "json",
                "cfgSettings": {
                    "disable_update": True,
                    "set_value_to_none_if_exist_same_as_default": False,
                    "replace_keyword_in_config": False,
                }
            },
            "communicate_support": {
                "defaultSetting": self.communicate_support,
                "savedLocation": "${SPACENET_DP_CONFIG_PATH}/config/communicate.yaml",
                "cfgType": "yaml",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": False,
                    "replace_keyword_in_config": False,
                }
            },
            "dynamic_pages_daemon": {
                "defaultSetting": self.dynamic_pages_daemon,
                "savedLocation": "${SPACENET_DP_CONFIG_PATH}/config/daemon.yaml",
                "cfgType": "yaml",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": False,
                    "replace_keyword_in_config": False,
                }
            },
            "error_pages": {
                "defaultSetting": self.error_pages,
                "savedLocation": "${SPACENET_DP_CONFIG_PATH}/config/error_pages.yaml",
                "cfgType": "yaml",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": False,
                    "replace_keyword_in_config": False,
                }
            },
            "dynamic_insert_config": {
                "defaultSetting": self.dynamic_insert_config,
                "savedLocation": "${SPACENET_DP_CONFIG_PATH}/config/dynamic_insert.json",
                "cfgType": "json",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": False,
                    "replace_keyword_in_config": False,
                }
            },
            "cache_settings": {
                "defaultSetting": self.cache_settings,
                "savedLocation": "${SPACENET_DP_CONFIG_PATH}/config/cache.yaml",
                "cfgType": "yaml",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": False,
                    "replace_keyword_in_config": False,
                }
            },
            "dp_cloudflare": {
                "defaultSetting": self.dp_cloudflare,
                "savedLocation": "${SPACENET_DP_CONFIG_PATH}/config/cloudflare.yaml",
                "cfgType": "yaml",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": False,
                    "replace_keyword_in_config": False,
                }
            }
        }

        self.load_data()


class DPSConfig(d2o.DataStoreObject):
    def __init__(self, logger):
        d2o.DataStoreObject.__init__(self, "DynamicPagesServiceConfig", logger)

        self.service_daemon_main = {
            "__commit__1": "enableMaintenanceModeA -> Return 553 to any IP",
            "enableMaintenanceModeA": False,
            "__commit__2": "enableMaintenanceModeB -> Return 553 if IP is not in allowList",
            "enableMaintenanceModeB": False,
            "blockAllRequests": False,
            "enableHTTPStatusMode": False,
            "responseCustomHTTPStatusCode": 404,
            'disableCDNCache': False,
            "allowIPList": []
        }

        self.cfg_mappings = {
            "service_daemon_main": {
                "defaultSetting": self.service_daemon_main,
                "savedLocation": "${SPACENET_DP_CONFIG_PATH}/config/service_control.yaml",
                "cfgType": "yaml",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": False,
                    "replace_keyword_in_config": False,
                }
            }
        }

        self.load_data()
