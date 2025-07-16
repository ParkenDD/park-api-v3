"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from dataclasses import dataclass, field

from parkapi_sources.exceptions import ImportParkingSiteException


@dataclass
class ParkingSiteResponse:
    items: list[dict] = field(default_factory=list)
    errors: list[ImportParkingSiteException] = field(default_factory=list)

    def to_dict(self):
        return {
            'items': self.items,
            'errors': self.errors,
        }
