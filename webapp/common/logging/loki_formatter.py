"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import logging

from .base_attribute_formatter import BaseAttributeFormatter


class LokiFormatter(BaseAttributeFormatter):
    def build_payload(self, record: logging.LogRecord) -> dict:
        attributes = self.build_attributes(record)

        stream = {
            'stream': attributes,
            'values': [[int(record.created * 1e9), record.msg]],
        }
        return {'streams': [stream]}
