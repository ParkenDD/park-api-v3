"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

from opening_hours import OpeningHours  # noqa

from webapp.models.parking_site import ParkingSiteType
from webapp.repositories import SourceRepository
from webapp.shared.parking_site.generic_parking_site_handler import GenericParkingSiteHandler
from webapp.shared.parking_site.parking_site_search_query import ParkingSiteSearchInput


class ParkApiV2Handler(GenericParkingSiteHandler):
    source_repository: SourceRepository
    key_mapping: dict[str, str] = {
        'created_at': 'date_created',
        'modified_at': 'date_updated',
        'original_uid': 'lot_id',
        'name': 'name',
        'address': 'address',
        'capacity': 'max_capacity',
        'public_url': 'public_url',
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

    def get_source_as_dict(self, source_uid: str) -> dict:
        source = self.source_repository.fetch_source_by_uid(source_uid)

        result = {
            'date_created': source.created_at,
            'date_updated': source.combined_updated_at,
            'pool_id': source.uid,
            'name': source.name or source.uid,
        }
        if source.public_url:
            result['public_url'] = source.public_url

        return result

    def get_parking_site_list_as_dict(self, search_query: ParkingSiteSearchInput) -> dict:
        parking_sites = self.get_parking_site_list(search_query)

        lots = []
        for parking_site in parking_sites:
            lot: dict[str, Any] = {
                'coordinates': [float(parking_site.lon), float(parking_site.lat)],
                'has_live_capacity': parking_site.has_realtime_data,
                'pool_id': parking_site.source.uid,
                'type': self.type_mapping.get(parking_site.type, 'unknown'),
            }
            for source_key, destination_key in self.key_mapping.items():
                if getattr(parking_site, source_key) is None or getattr(parking_site, source_key) == '':
                    continue
                lot[destination_key] = getattr(parking_site, source_key)

            if parking_site.opening_hours or (
                parking_site.has_realtime_data and parking_site.realtime_free_capacity is not None
            ):
                lot['latest_data'] = {'timestamp': parking_site.modified_at}

            if parking_site.opening_hours:
                oh = OpeningHours(parking_site.opening_hours)
                lot['latest_data']['status'] = str(oh.state())

            if parking_site.has_realtime_data and parking_site.realtime_free_capacity is not None:
                lot['latest_data']['lot_timestamp'] = (parking_site.realtime_data_updated_at,)
                if parking_site.realtime_capacity is None:
                    capacity = parking_site.capacity
                else:
                    capacity = parking_site.realtime_capacity

                if capacity:
                    lot['latest_data']['capacity'] = capacity
                    lot['latest_data']['num_free'] = parking_site.realtime_free_capacity
                    lot['latest_data']['num_occupied'] = capacity - parking_site.realtime_free_capacity
                    lot['latest_data']['percent_free'] = round(parking_site.realtime_free_capacity / capacity * 100, 2)

            lots.append(lot)

        return {
            'count': len(lots),
            'next': None,
            'previous': None,
            'results': lots,
        }
