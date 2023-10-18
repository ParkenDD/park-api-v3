"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


class DefaultJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for this app.
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, Enum):
            return obj.value

        # Serialize data models using to_dict
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()

        return obj.__dict__
