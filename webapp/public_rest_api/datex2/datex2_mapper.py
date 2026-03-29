"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.helpers import UnsetValue

from webapp.models import ParkingSite
from webapp.models.parking_site import OpeningStatus, ParkingSiteType
from webapp.public_rest_api.datex2.datex2_models import (
    Datex2Assignment,
    Datex2AssignmentType,
    Datex2Coordinate,
    Datex2FuelType,
    Datex2LocationAndDimension,
    Datex2ParkingPublicationLight,
    Datex2ParkingSite,
    Datex2ParkingSiteType,
    Datex2Publication,
    Datex2UserType,
)


class Datex2Mapper:
    def map_parking_sites(self, name: str, parking_sites: list[ParkingSite]) -> Datex2Publication:
        return Datex2Publication(
            parkingPublicationLight=Datex2ParkingPublicationLight(
                name=name,
                parkingSite=[self.map_parking_site(parking_site) for parking_site in parking_sites],
            ),
        )

    def map_parking_site(self, parking_site: ParkingSite) -> Datex2ParkingSite:
        datex2_parking_site = Datex2ParkingSite(
            uid=str(parking_site.id),
            type=self.map_parking_site_type(parking_site.type),
            locationAndDimension=Datex2LocationAndDimension(
                coordinatesForDisplay=Datex2Coordinate(
                    latitude=float(parking_site.lat),
                    longitude=float(parking_site.lon),
                ),
            ),
        )

        if parking_site.realtime_free_capacity is not None:
            datex2_parking_site.availableSpaces = parking_site.realtime_free_capacity

        if parking_site.realtime_capacity is not None:
            datex2_parking_site.numberOfSpaces = parking_site.realtime_capacity
        else:
            datex2_parking_site.numberOfSpaces = parking_site.capacity

        # Add different assignments, starting with disabled
        if parking_site.realtime_free_capacity_disabled is not None:
            datex2_parking_site.assignedFor.append(
                Datex2Assignment(
                    availableSpaces=parking_site.realtime_free_capacity_disabled,
                    typeOfAssignment=Datex2AssignmentType.onlyFor,
                    user=Datex2UserType.wheelchairUsers,
                ),
            )

        # Assignment women
        if parking_site.realtime_free_capacity_woman is not None:
            datex2_parking_site.assignedFor.append(
                Datex2Assignment(
                    availableSpaces=parking_site.realtime_free_capacity_woman,
                    typeOfAssignment=Datex2AssignmentType.onlyFor,
                    user=Datex2UserType.women,
                ),
            )

        # Assignment family
        if parking_site.realtime_free_capacity_family is not None:
            datex2_parking_site.assignedFor.append(
                Datex2Assignment(
                    availableSpaces=parking_site.realtime_free_capacity_family,
                    typeOfAssignment=Datex2AssignmentType.onlyFor,
                    user=Datex2UserType.families,
                ),
            )

        # Assignment charging
        if parking_site.realtime_free_capacity_charging is not None:
            datex2_parking_site.assignedFor.append(
                Datex2Assignment(
                    availableSpaces=parking_site.realtime_free_capacity_charging,
                    typeOfAssignment=Datex2AssignmentType.onlyFor,
                    fuelType=Datex2FuelType.battery,
                ),
            )

        # TODO: carsharing seems to be impossible to map
        # TODO: it seems that there is no way to make assignments to numberOfSpaces, just to availableSpaces, which is not helpful for most
        #  data sources, as usually there is no realtime data at parking spots for groups, just static data.

        if len(datex2_parking_site.assignedFor) == 0:
            datex2_parking_site.assignedFor = UnsetValue

        if parking_site.realtime_opening_status == OpeningStatus.OPEN:
            datex2_parking_site.isOpenNow = True
        elif parking_site.realtime_opening_status == OpeningStatus.CLOSED:
            datex2_parking_site.isOpenNow = False

        field_mapping = {
            'description': 'description',
            'modified': 'lastUpdate',
            'max_stay': 'maximumParkingDuration',
            'name': 'name',
            'fee_description': 'tariffDescription',
            'public_url': 'urlLinkAddress',
        }

        for source, target in field_mapping.items():
            if getattr(parking_site, source, None) is None:
                continue
            setattr(datex2_parking_site, target, getattr(parking_site, source))

        return datex2_parking_site

    @staticmethod
    def map_parking_site_type(parking_site_type: ParkingSiteType) -> Datex2ParkingSiteType:
        return {
            ParkingSiteType.CAR_PARK: Datex2ParkingSiteType.carPark,
            ParkingSiteType.ON_STREET: Datex2ParkingSiteType.onStreet,
            ParkingSiteType.UNDERGROUND: Datex2ParkingSiteType.carPark,
            ParkingSiteType.OFF_STREET_PARKING_GROUND: Datex2ParkingSiteType.offStreetParkingGround,
        }.get(parking_site_type, Datex2ParkingSiteType.other)
