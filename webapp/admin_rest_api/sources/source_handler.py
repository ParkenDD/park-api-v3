"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.admin_rest_api import AdminApiBaseHandler
from webapp.admin_rest_api.sources.source_validators import SourceInput
from webapp.models import Source
from webapp.repositories import SourceRepository
from webapp.repositories.exceptions import ObjectNotFoundException


class SourceHandler(AdminApiBaseHandler):
    source_repository: SourceRepository

    def __init__(self, *args, source_repository: SourceRepository, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_repository = source_repository

    def upsert_source(self, source_input: SourceInput) -> tuple[Source, bool]:
        try:
            source = self.source_repository.fetch_source_by_uid(source_input.uid)
            created = False
        except ObjectNotFoundException:
            source = Source(uid=source_input.uid)
            created = True

        for key, value in source_input.to_dict().items():
            if key == 'uid':
                continue
            setattr(source, key, value)

        self.source_repository.save_source(source)

        return source, created
