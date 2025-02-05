"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from copy import deepcopy

from webapp.models import Source


def get_source(counter: int, **kwargs) -> Source:
    base_data = {'uid': f'source-{counter}'}

    data = deepcopy(base_data)
    data.update(kwargs)

    parking_site = Source(**data)

    return parking_site
