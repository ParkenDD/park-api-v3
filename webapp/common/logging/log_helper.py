"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import logging

from .models import LogMessageType


def log(
    logger: logging.Logger,
    level: int,
    message_type: LogMessageType,
    msg: str,
    attributes: dict | None = None,
) -> None:
    attributes = attributes or {}
    attributes['type'] = message_type

    logger.log(
        level,
        msg,
        extra={'attributes': attributes},
    )
