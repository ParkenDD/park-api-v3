"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import logging
from logging import StreamHandler

from .otel_formatter import OtelFormatter


class StdoutHandler(StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLevel(logging.DEBUG)
        self.setFormatter(OtelFormatter())
