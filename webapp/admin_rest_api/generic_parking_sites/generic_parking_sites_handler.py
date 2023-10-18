"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.admin_rest_api import AdminApiBaseHandler
from webapp.repositories import ParkingSiteRepository, SourceRepository


class GenericParkingSitesHandler(AdminApiBaseHandler):
    source_repository: SourceRepository
    parking_site_repository: ParkingSiteRepository

    def __init__(
        self,
        *args,
        source_repository: SourceRepository,
        parking_site_repository: ParkingSiteRepository,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.source_repository = source_repository
        self.parking_site_repository = parking_site_repository

    def handle_json_data(self, data: dict | list):
        pass

    def handle_csv_data(self, data: bytes):
        pass

    def handle_xlsx_data(self, data: bytes):
        pass
