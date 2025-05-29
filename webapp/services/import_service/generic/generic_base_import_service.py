"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources import ParkAPISources

from webapp.repositories import SourceRepository
from webapp.services.base_service import BaseService


class GenericBaseImportService(BaseService):
    source_repository: SourceRepository
    park_api_sources: ParkAPISources

    def __init__(self, *args, source_repository: SourceRepository, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_repository = source_repository
