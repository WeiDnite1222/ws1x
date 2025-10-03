r"""
 ____ ____   ___
|  _ \___ \ / _ \
| | | |__) | | | |
| |_| / __/| |_| |
|____/_____|\___/
Usage/Read/Write/Update configuration easily as drinking H2O(Water).
"""
import os
import threading
import time
from typing import Dict, Any, List
from space_net_lib.config.rw_yaml import yaml_parser_with_except, yaml_writer_with_except
from space_net_lib.config.rw_json import json_parser_with_except, json_writer_with_except
from space_net_lib.definition.path import convert_path_keyword_to_read_value
import logging
import traceback

D2OParser = {
    "yaml": yaml_parser_with_except,
    "json": json_parser_with_except,
}

D2OWriter = {
    "yaml": yaml_writer_with_except,
    "json": json_writer_with_except,
}


class DataStoreObject:
    """
    Read yaml/json file and store values as variables(dict).

    Intro: Automatically read values from yaml/json file when it created.
    If the target configuration path does not exist or fails on parsing, the preset data is used.
    Update existing configuration when the default setting is updated.
    """
    def __init__(self, name: str, logger, live_path=None) -> None:
        self.name: str = name
        self.logger: logging.Logger = logger
        self.cfg_mappings: Dict[str, Dict[str, Any]] = {}

    def load_data(self) -> None:
        if not hasattr(self, "cfg_mappings"):
            self.logger.warning("Configuration mappings for d2o name {}'s is missing. Use default data instead.".format(self.name))
            return

        for config_name, cfg_structure in self.cfg_mappings.items():
            # The config(string) must be the variable default_setting's name.

            if cfg_structure is None:
                self.logger.warning("Config name {}'s structure is broken. Ignoring...".format(config_name))
                continue

            saved_location = cfg_structure.get("savedLocation", None)
            default_setting = cfg_structure.get("defaultSetting", None)
            cfg_type = cfg_structure.get("cfgType", None)
            cfg_settings = cfg_structure.get("cfgSettings", {})

            if not hasattr(self, config_name):
                self.logger.warning("Mapping default setting for config name {} does not exist. Ignoring...".format(config_name))
                continue

            if saved_location is None:
                self.logger.warning("Key name savedLocation for config {} is invalid. The default data is used.\n".format(config_name))
                continue
            else:
                saved_location = convert_path_keyword_to_read_value(saved_location)

            if not os.path.exists(saved_location):
                self.logger.info("Config path {} does not exist. Creating...".format(saved_location))
                func = D2OWriter.get(cfg_type, None)

                if func is None:
                    self.logger.warning("Unknow type of config {}. Perhaps you set the key cfgType?\n".format(cfg_type))
                    continue

                result = func(saved_location, default_setting)

                if result is not None:
                    self.logger.error("An error occurred while creating the config file name {}. ERROR > {}".format(config_name , result))
                    continue

                # ignore parser because the new config data is the same as the default setting.
                continue

            if cfg_type is None:
                self.logger.warning("Mapping default setting for config name {} is invalid. The default data is used.".format(config_name))
                continue

            if cfg_settings is None:
                self.logger.warning("The cfgSettings for config {} is invalid. You can ignore this message if you don't need it."
                      .format(config_name))

            func = D2OParser.get(cfg_type, None)

            if func is None:
                self.logger.warning("Unsupported/Unknown type of config {}. Perhaps you set the key cfgType?\n".format(cfg_type))
                continue

            new_setting, error = func(saved_location)

            if error is not None:
                self.logger.error("An error occurred while parsing the config file > {}".format(error))
                continue

            set_none_if_value_same = cfg_settings.get("set_value_to_none_if_exist_same_as_default",
                                                                          None)
            replace_keyword_in_config = cfg_settings.get("replace_keyword_in_config", False)
            disable_update = cfg_settings.get("disable_update", False)

            try:
                merged_data, update_flag = self.merge_dictionary(default_setting, new_setting,
                                                    set_none_if_value_same=set_none_if_value_same)
            except Exception as error:
                self.logger.error("An unexpected error occurred while merging the config file name {} ERROR: {}".format(config_name, error))
                traceback.print_exc()
                continue

            if update_flag and not disable_update:
                self.logger.info("Found new key in default settings for config name {}. Updating...".format(config_name))
                func = D2OWriter.get(cfg_type, None)
                result = func(saved_location, merged_data)

                if result is not None:
                    pself.logger.error("An error occurred while updating the config file > {}".format(result))

            if replace_keyword_in_config:
                merged_data = self.replace_keyword_in_config(merged_data)

            setattr(self, config_name, merged_data)


    def merge_dictionary(self, default_dict, new_dict, set_none_if_value_same=False,
                         preserve_extra_keys=True) -> (Dict[str, Any], bool):
        update_flag = False
        merged_dict = {}

        for key, value in default_dict.items():
            if key in new_dict:
                exist_value = new_dict[key]

                if isinstance(value, dict) and isinstance(exist_value, dict):
                    sub_merged, sub_updated = self.merge_dictionary(
                        value, exist_value,
                        set_none_if_value_same=set_none_if_value_same,
                        preserve_extra_keys=preserve_extra_keys,
                    )
                    merged_dict[key] = sub_merged
                    update_flag = update_flag or sub_updated
                else:
                    if set_none_if_value_same and exist_value == value:
                        merged_dict[key] = None
                    else:
                        merged_dict[key] = exist_value
            else:
                merged_dict[key] = value
                update_flag = True

        if preserve_extra_keys:
            for k, ev in new_dict.items():
                if k not in default_dict:
                    merged_dict[k] = ev

        return merged_dict, update_flag

    def get_all_keys(self, dictionary) -> List[str or Any]:
        keys = []
        for key, value in dictionary.items():
            keys.append({key: value})
            if isinstance(value, dict):
                keys.extend(self.get_all_keys(value))
        return keys

    def replace_keyword_in_config(self, dictionary) -> Dict[str, Any]:
        for key, value in dictionary.items():
            if isinstance(value, dict):
                dictionary[key] = self.replace_keyword_in_config(value)
            elif isinstance(value, str):
                dictionary[key] = convert_path_keyword_to_read_value(value)
            else:
                dictionary[key] = value

        return dictionary

    def get_full_config_path(self):
        paths_list = []
        for config_name, cfg_structure in self.cfg_mappings.items():
            # The config(string) must be the variable default_setting's name.

            if cfg_structure is None:
                self.logger.warning("Config name {}'s structure is broken. Ignoring...".format(config_name))
                continue

            saved_location = cfg_structure.get("savedLocation", None)

            if saved_location is None:
                saved_location = "<UNKNOWN>"

            paths_list.append({"name": config_name, "path": saved_location})

        return paths_list


class D2OUpdater(threading.Thread):
    def __init__(self, d2o_list: List[DataStoreObject], refresh_time=10, daemon=True):
        threading.Thread.__init__(self, daemon=daemon)

        self.d2o_list = d2o_list
        self.refresh_time = refresh_time

    def run(self):
        while True:
            time.sleep(self.refresh_time)

            for d2o in self.d2o_list:
                d2o.load_data()

class ExampleConfig(DataStoreObject):
    def __init__(self, name, logger):
        DataStoreObject.__init__(self, name, logger)

        self.my_favorite_thing = {
            "1": "dragonite",
            "2": "dragonite",
            "3": "dragonite",
        }

        self.coding_these_thing_let_me_feel_tired = {
            "messageA": "I can exactly say that my server code looks like shredded paper."
                        "That's the reason why I started this project..."
        }

        self.cfg_mappings = {
            "my_favorite_thing": {
                "defaultSetting": self.my_favorite_thing,
                "savedLocation": "./favorite.yaml",
                "cfgType": "yaml",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": True,
                }
            },
            "coding_these_thing_let_me_feel_tired": {
                "defaultSetting": self.coding_these_thing_let_me_feel_tired,
                "savedLocation": "./coding_these_thing_let_me_feel_tired.yaml",
                "cfgType": "yaml",
                "cfgSettings": {
                    "set_value_to_none_if_exist_same_as_default": True,
                }
            }
        }

        self.load_data()