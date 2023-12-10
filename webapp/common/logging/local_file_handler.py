"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import logging
from logging.handlers import WatchedFileHandler
from pathlib import Path

from webapp.common.config import ConfigHelper


class LocalFileHandler(WatchedFileHandler):
    config_helper: ConfigHelper

    def __init__(self, *args, config_helper: ConfigHelper, **kwargs):
        super().__init__(Path(config_helper.get('LOG_DIR'), 'main.log'), *args, **kwargs)
        self.setLevel(logging.INFO)
        self.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(tags)s: %(message)s '))
