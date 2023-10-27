"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from webapp.models import ParkingSite
from webapp.models.parking_site import OpeningStatus, ParkingSiteType

from .parking_site_generic_import_validator import LotDataInput, LotInfoInput


class ParkingSiteGenericImportMapper:
    type_mapping: dict[str, ParkingSiteType] = {
        'bus': None,
        'garage': ParkingSiteType.CAR_PARK,
        'level': ParkingSiteType.OFF_STREET_PARKING_GROUND,
        'lot': ParkingSiteType.OFF_STREET_PARKING_GROUND,
        'street': ParkingSiteType.ON_STREET,
        'underground': ParkingSiteType.UNDERGROUND,
        'unknown': None,
    }
    opening_mapping: dict[str, OpeningStatus] = {
        'open': OpeningStatus.OPEN,
        'closed': OpeningStatus.CLOSED,
        'unknown': OpeningStatus.UNKNOWN,
        'nodata': OpeningStatus.UNKNOWN,
        'error': OpeningStatus.UNKNOWN,
    }

    def map_lot_info_to_parking_site(self, lot_info_input: LotInfoInput, parking_site: ParkingSite):
        for key in ['name', 'public_url', 'address', 'capacity']:
            setattr(parking_site, key, getattr(lot_info_input, key))

        parking_site.lat = lot_info_input.latitude
        parking_site.lon = lot_info_input.longitude
        parking_site.has_realtime_data = lot_info_input.has_live_capacity
        parking_site.type = self.type_mapping.get(lot_info_input.type)
        parking_site.static_data_updated_at = datetime.now(tz=timezone.utc)

    def map_lot_data_to_parking_site(self, lot_data_input: LotDataInput, parking_site: ParkingSite):
        if lot_data_input.num_free is not None:
            parking_site.realtime_free_capacity = lot_data_input.num_free
        elif lot_data_input.num_occupied is not None and lot_data_input.capacity is not None:
            parking_site.realtime_free_capacity = lot_data_input.capacity - lot_data_input.num_occupied
        else:
            parking_site.realtime_free_capacity = None
        parking_site.realtime_capacity = lot_data_input.capacity
        parking_site.realtime_opening_status = self.opening_mapping.get(lot_data_input.status, OpeningStatus.UNKNOWN)
