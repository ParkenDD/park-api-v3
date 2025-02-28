"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

from flask import has_app_context
from flask.globals import app_ctx


class FlaskAttributesMixin:
    @staticmethod
    def add_additional_attributes(record_attributes: dict[str, Any]) -> None:
        if has_app_context() and hasattr(app_ctx, 'butterfly_butterfly_telemetry_context'):
            record_attributes.update(getattr(app_ctx, 'butterfly_butterfly_telemetry_context'))
