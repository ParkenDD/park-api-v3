"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from opening_hours import OpeningHours

from webapp.models.parking_site import ParkingSiteType
from webapp.repositories import SourceRepository
from webapp.shared.parking_site import GenericParkingSiteHandler
from webapp.shared.parking_site.parking_site_search_query import ParkingSiteSearchInput


class ParkApiV1Handler(GenericParkingSiteHandler):
    source_repository: SourceRepository

    key_mapping: dict[str, str] = {
        'name': 'name',
        'id': 'original_uid',
        'capacity': 'total',
        'public_url': 'url',
        'opening_hours': 'opening_hours',
        'address': 'address',
    }
    type_mapping: [ParkingSiteType, str] = {
        ParkingSiteType.ON_STREET: 'street',
        ParkingSiteType.OFF_STREET_PARKING_GROUND: 'lot',
        ParkingSiteType.UNDERGROUND: 'underground',
        ParkingSiteType.CAR_PARK: 'garage',
    }

    def __init__(self, *args, source_repository: SourceRepository, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_repository = source_repository

    def get_sources_as_dict(self) -> dict:
        sources = self.source_repository.fetch_sources()

        result = {
            'api_version': '1.0',
            'server_version': '3.0.0',
            'reference': 'https://github.com/binary-butterfly/park-api',
            'cities': {},
        }

        for source in sources:
            result['cities'][source.name if source.name else source.uid] = source.uid

        return result

    def get_parking_site_list_as_dict(self, search_query: ParkingSiteSearchInput) -> dict:
        source = self.source_repository.fetch_source_by_uid(search_query.source_uid)

        parking_sites = self.get_parking_site_list(search_query=search_query)
        lots = []
        for parking_site in parking_sites:
            lot = {
                'coords': {
                    'lat': float(parking_site.lat),
                    'lon': float(parking_site.lon),
                },
                'lot_type': self.type_mapping.get(parking_site.type, 'unknown'),
            }
            for key in self.key_mapping:
                if getattr(parking_site, key) is None or getattr(parking_site, key) == '':
                    continue
                lot[key] = getattr(parking_site, key)

            if parking_site.has_realtime_data and parking_site.realtime_free_capacity is not None:
                lot['free'] = parking_site.realtime_free_capacity
            if parking_site.has_realtime_data and parking_site.realtime_opening_status is not None:
                lot['state'] = parking_site.realtime_opening_status.name.lower()
            elif parking_site.opening_hours:
                oh = OpeningHours(parking_site.opening_hours)
                lot['state'] = oh.state()
            else:
                lot['state'] = 'unknown'

            lots.append(lot)

        response = {
            'lots': lots,
            'last_updated': source.combined_updated_at,
            'last_downloaded': source.combined_updated_at,
        }
        response['last_updated'] = source.combined_updated_at
        response['last_downloaded'] = source.combined_updated_at
        if source.public_url:
            response['data_source'] = source.public_url

        return response
