"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from .flask_attributes_mixin import FlaskAttributesMixin
from .loki_formatter import LokiFormatter


class FlaskLokiFormatter(FlaskAttributesMixin, LokiFormatter): ...
