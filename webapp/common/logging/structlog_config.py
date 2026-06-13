"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

import structlog

# Keys structlog / the standard library expect as top-level keyword arguments to ``logging.log()``. Everything else a
# log call provides (e.g. ``type``) is collected into the ``attributes`` dict the formatters and handlers read.
_RESERVED_KEYS = ('event', 'exc_info', 'stack_info', 'stacklevel')


def pack_attributes(_logger: Any, _method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """
    Move all custom key-value pairs of a log call into a single ``attributes`` dict so that the standard library
    formatters (Loki, OpenTelemetry) and the SplitLogFileHandler keep receiving ``record.attributes``.
    """
    attributes = {key: event_dict.pop(key) for key in list(event_dict) if key not in _RESERVED_KEYS}
    if attributes:
        event_dict['attributes'] = attributes
    return event_dict


def configure_structlog() -> None:
    """
    Route structlog through the standard library logging, so the existing handlers and formatters stay in charge of
    emitting log records.
    """
    structlog.configure(
        processors=[
            pack_attributes,
            structlog.stdlib.render_to_log_kwargs,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
