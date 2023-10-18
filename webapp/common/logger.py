"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import logging
import os
from logging.handlers import WatchedFileHandler
from typing import List

from webapp.common.config import ConfigHelper


class Logger:
    config_helper: ConfigHelper
    registered_logs: List[str] = []

    def __init__(self, config_helper: ConfigHelper):
        self.config_helper = config_helper

    def get_log(self, log_name: str):
        logger = logging.getLogger(f'{self.config_helper.get("LOGGING_PREFIX", "")}{log_name}')
        if log_name in self.registered_logs:
            return logger
        logger.setLevel(logging.INFO)

        # Init File Handler
        file_name = os.path.join(self.config_helper.get('LOG_DIR', ''), f'{log_name}.log')
        file_handler = WatchedFileHandler(file_name)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s '))
        logger.addHandler(file_handler)

        file_name = os.path.join(self.config_helper.get('LOG_DIR', ''), f'{log_name}.err')
        file_handler = WatchedFileHandler(file_name)
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s '))
        logger.addHandler(file_handler)

        if self.config_helper.get('DEBUG'):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_format = logging.Formatter('%(message)s')
            console_handler.setFormatter(console_format)
            logger.addHandler(console_handler)

        self.registered_logs.append(log_name)
        return logger

    def debug(self, log_name: str, message: str):
        self.get_log(log_name).debug(message)

    def info(self, log_name: str, message: str):
        self.get_log(log_name).info(message)

    def warn(self, log_name: str, message: str):
        self.get_log(log_name).warning(message)

    def error(self, log_name: str, message: str, details=None, extended_recipients=False):
        self.get_log(log_name).error(message if details is None else f'{message}\n{details}')

    def exception(self, log_name: str, message: str, details=None):
        self.get_log(log_name).exception(message if details is None else f'{message}\n{details}')

    def critical(self, log_name: str, message: str, details=None):
        self.get_log(log_name).critical(message if details is None else f'{message}\n{details}')
