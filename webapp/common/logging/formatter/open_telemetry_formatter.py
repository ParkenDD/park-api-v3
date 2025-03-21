"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import logging
import secrets

from .base_attribute_formatter import BaseAttributeFormatter


class OpenTelemetryFormatter(BaseAttributeFormatter):
    log_level_mapping: dict[int, int] = {
        logging.DEBUG: 5,
        logging.INFO: 10,
        logging.WARNING: 15,
        logging.ERROR: 20,
        logging.CRITICAL: 25,
    }

    def build_payload(self, record: logging.LogRecord) -> dict:
        trace_id = getattr(record, 'trace_id', secrets.token_hex(16))
        span_id = getattr(record, 'span_id', secrets.token_hex(8))

        return {
            'Timestamp': int(record.created * 1e9),
            'Attributes': {
                **self.build_attributes(record),
                'logger.file_name': record.filename,
                'logger.module_path': record.name,
                'logger.module': record.module,
            },
            'Resource': {
                'service.name': self.service_name,
                'service.pid': record.process,
            },
            'TraceId': trace_id,
            'SpanId': span_id,
            'SeverityText': 'WARN' if record.levelno == logging.WARNING else record.levelname,
            'SeverityNumber': self.log_level_mapping[record.levelno],
            'Body': record.msg,
        }
