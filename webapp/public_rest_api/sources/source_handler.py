"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass_search_queries.pagination import PaginatedResult

from webapp.models import Source
from webapp.public_rest_api.base_handler import PublicApiBaseHandler
from webapp.public_rest_api.sources.source_validators import SourceSearchQueryInput
from webapp.repositories import SourceRepository


class SourceHandler(PublicApiBaseHandler):
    source_repository: SourceRepository

    def __init__(self, *args, source_repository: SourceRepository, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_repository = source_repository

    def get_source_list(self, search_query: SourceSearchQueryInput) -> PaginatedResult[Source]:
        return self.source_repository.fetch_sources(search_query=search_query)

    def get_source_item(self, source_id: int) -> Source:
        return self.source_repository.fetch_resource_by_id(source_id)
