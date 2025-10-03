from config import ManageConfig
import os
import sys
import logging
import requests

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

from space_net_lib.logger.logger import DefaultLogger
from space_net_lib.definition.path import manage_data_path

class SpaceNETManage:
    def __init__(self):
        self.log_config_path = os.path.join(manage_data_path, "logs", "current.logs")
        self.logger = DefaultLogger("ManageLogger",
                                    self.log_config_path,
                                    stdout_output_format="%(log_color)s%(levelname)s%(reset)s > %(message)s",
                                    log_file_format="%(asctime)s:%(levelname)s:%(message)s",)
        self.config = ManageConfig(self.logger)