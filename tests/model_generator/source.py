"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from copy import deepcopy

from webapp.models import Source
from webapp.models.source import SourceStatus


def get_source(**kwargs) -> Source:
    base_data = {
        'uid': 'source',
        'static_status': SourceStatus.ACTIVE,
    }

    data = deepcopy(base_data)
    data.update(kwargs)

    return Source(**data)


def get_source_by_counter(counter: int, **kwargs) -> Source:
    return Source(uid=f'source-{counter}', **kwargs)
