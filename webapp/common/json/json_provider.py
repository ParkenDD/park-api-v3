"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from typing import Any

from flask.json.provider import DefaultJSONProvider

from .default_json_encoder import DefaultJSONEncoder


class JSONProvider(DefaultJSONProvider):
    """
    Custom JSON provider for this app.
    """

    def dumps(self, object_: Any, **kwargs: Any) -> str:
        return json.dumps(object_, cls=DefaultJSONEncoder)
