"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Optional

from validataclass_search_queries.pagination import PaginatedResult
from validataclass_search_queries.search_queries import BaseSearchQuery

from webapp.models import Source
from webapp.repositories import BaseRepository
from webapp.repositories.exceptions import ObjectNotFoundException


class SourceRepository(BaseRepository):
    model_cls = Source

    def fetch_sources(self, *, search_query: Optional[BaseSearchQuery] = None) -> PaginatedResult[Source]:
        query = self.session.query(Source)

        return self._search_and_paginate(query, search_query)

    def fetch_source_by_uid(self, uid: str) -> Source:
        source: Source = self.session.query(Source).filter(Source.uid == uid).first()

        if not source:
            raise ObjectNotFoundException(message=f'Source with uid {uid} not found')

        return source

    def save_source(self, source: Source, *, commit: bool = True):
        return self._save_resources(source, commit=commit)
