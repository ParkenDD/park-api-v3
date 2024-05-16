"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from webapp.public_rest_api.datex2.datex2_mapper import Datex2Mapper
from webapp.public_rest_api.datex2.datex2_models import Datex2Publication
from webapp.repositories import SourceRepository
from webapp.shared.parking_site.generic_parking_site_handler import GenericParkingSiteHandler
from webapp.shared.parking_site.parking_site_search_query import ParkingSiteBaseSearchInput


class Datex2Handler(GenericParkingSiteHandler):
    source_repository: SourceRepository
    datex2_mapper: Datex2Mapper = Datex2Mapper()

    def __init__(self, *args, source_repository: SourceRepository, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_repository = source_repository

    def get_parking_sites(self, search_query: ParkingSiteBaseSearchInput) -> Datex2Publication:
        parking_sites = self.get_parking_site_list(search_query)

        if search_query.source_uid is None:
            name = 'Aggregated parking sites'
        else:
            source = self.source_repository.fetch_source_by_uid(search_query.source_uid)
            name = source.name

        return self.datex2_mapper.map_parking_sites(
            parking_sites=parking_sites,
            name=name,
        )
