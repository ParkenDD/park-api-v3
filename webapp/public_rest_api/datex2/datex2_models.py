"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from validataclass.dataclasses import Default
from validataclass.helpers import OptionalUnset, UnsetValue

from webapp.common.dataclass import DataclassMixin


class Datex2FuelType(Enum):
    all = 'all'
    battery = 'battery'
    biodiesel = 'biodiesel'
    diesel = 'diesel'
    dieselBatteryHybrid = 'dieselBatteryHybrid'
    ethanol = 'ethanol'
    hydrogen = 'hydrogen'
    liquidGas = 'liquidGas'
    lpg = 'lpg'
    methane = 'methane'
    other = 'other'
    petrol = 'petrol'
    petrol95Octane = 'petrol95Octane'
    petrol98Octane = 'petrol98Octane'
    petrolBatteryHybrid = 'petrolBatteryHybrid'
    petrolLeaded = 'petrolLeaded'
    petrolUnleaded = ' petrolUnleaded'
    unknown = 'unknown'


class Datex2AssignmentType(Enum):
    allowedFor = 'allowedFor'
    onlyFor = 'onlyFor'
    optimisedFor = 'optimisedFor'
    prohibitedFor = 'prohibitedFor'


class Datex2UserType(Enum):
    allUsers = 'allUsers'
    commuters = 'commuters'
    customers = 'customers'
    disabled = 'disabled'
    elderlyUsers = 'elderlyUsers'
    employees = 'employees'
    families = 'families'
    handicapped = 'handicapped'
    hearingImpaired = 'hearingImpaired'
    hotelGuests = 'hotelGuests'
    longTermParker = 'longTermParker'
    members = 'members'
    men = 'men'
    other = 'other'
    overnightParker = 'overnightParker'
    parkAndCycleUser = 'parkAndCycleUser'
    parkAndRideUsers = 'parkAndRideUsers'
    parkAndWalkUser = 'parkAndWalkUser'
    pensioners = 'pensioners'
    pregnantWomen = 'pregnantWomen'
    registeredDisabledUsers = 'registeredDisabledUsers'
    reservationHolders = 'reservationHolders'
    residents = 'residents'
    seasonTicketHolders = 'seasonTicketHolders'
    shoppers = 'shoppers'
    shortTermParker = 'shortTermParker'
    sportEventAwaySupporters = 'sportEventAwaySupporters'
    sportEventHomeSupporters = 'sportEventHomeSupporters'
    staff = 'staff'
    students = 'students'
    subscribers = 'subscribers'
    unknown = 'unknown'
    visitors = 'visitors'
    visuallyImpaired = 'visuallyImpaired'
    wheelchairUsers = 'wheelchairUsers'
    women = 'women'


class Datex2VehicleType(Enum):
    agriculturalVehicle = 'agriculturalVehicle'
    anyVehicle = 'anyVehicle'
    articulatedBus = 'articulatedBus'
    articulatedTrolleyBus = 'articulatedTrolleyBus'
    articulatedVehicle = 'articulatedVehicle'
    bicycle = 'bicycle'
    bus = 'bus'
    car = 'car'
    caravan = 'caravan'
    carOrLightVehicle = 'carOrLightVehicle'
    carWithCaravan = 'carWithCaravan'
    carWithTrailer = 'carWithTrailer'
    constructionOrMaintenanceVehicle = 'constructionOrMaintenanceVehicle'
    fourWheelDrive = 'fourWheelDrive'
    heavyDutyTransporter = 'heavyDutyTransporter'
    heavyGoodsVehicle = 'heavyGoodsVehicle'
    heavyGoodsVehicleWithTrailer = 'heavyGoodsVehicleWithTrailer'
    heavyVehicle = 'heavyVehicle'
    highSidedVehicle = 'highSidedVehicle'
    largeCar = 'largeCar'
    largeGoodsVehicle = 'largeGoodsVehicle'
    lightCommercialVehicle = 'lightCommercialVehicle'
    lightCommercialVehicleWithTrailer = 'lightCommercialVehicleWithTrailer'
    lorry = 'lorry'
    metro = 'metro'
    minibus = 'minibus'
    moped = 'moped'
    motorcycle = 'motorcycle'
    motorcycleWithSideCar = 'motorcycleWithSideCar'
    motorhome = 'motorhome'
    motorscooter = 'motorscooter'
    other = 'other'
    passengerCar = 'passengerCar'
    smallCar = 'smallCar'
    tanker = 'tanker'
    threeWheeledVehicle = 'threeWheeledVehicle'
    trailer = 'trailer'
    tram = 'tram'
    trolleyBus = 'trolleyBus'
    twoWheeledVehicle = 'twoWheeledVehicle'
    unknown = 'unknown'
    van = 'van'
    vehicleWithCaravan = 'vehicleWithCaravan'
    vehicleWithCatalyticConverter = 'vehicleWithCatalyticConverter'
    vehicleWithoutCatalyticConverter = 'vehicleWithoutCatalyticConverter'
    vehicleWithTrailer = 'vehicleWithTrailer'
    withEvenNumberedRegistrationPlates = 'withEvenNumberedRegistrationPlates'
    withOddNumberedRegistrationPlates = 'withOddNumberedRegistrationPlates'


class Datex2ParkingOccupancyTrend(Enum):
    decreasing = 'decreasing'
    decreasingQuickly = 'decreasingQuickly'
    decreasingSlowly = 'decreasingSlowly'
    increasing = 'increasing'
    increasingQuickly = 'increasingQuickly'
    increasingSlowly = 'increasingSlowly'
    other = 'other'
    stable = 'stable'
    unknown = 'unknown'


class Datex2ParkingSiteType(Enum):
    carPark = 'carPark'
    motorwayParking = 'motorwayParking'
    offStreetParkingGround = 'offStreetParkingGround'
    onStreet = 'onStreet'
    other = 'other'
    restArea = 'restArea'
    specialLocationParking = 'specialLocationParking'
    temporaryParking = 'temporaryParking'


class Datex2Accessibility(Enum):
    barrierFreeAccessible = 'barrierFreeAccessible'
    handicappedAccessible = 'handicappedAccessible'
    handicappedEasements = 'handicappedEasements'
    handicappedMarked = 'handicappedMarked'
    none = 'none'
    orientationSystemForBlindPeople = 'orientationSystemForBlindPeople'
    other = 'other'
    unknown = 'unknown'
    wheelChairAccessible = 'wheelChairAccessible'


class Datex2Availability(Enum):
    available = 'available'
    closed = 'closed'
    occupied = 'occupied'
    unknown = 'unknown'


@dataclass(kw_only=True)
class Datex2Assignment(DataclassMixin):
    additionalAssignment: OptionalUnset[str] = UnsetValue
    availableSpaces: OptionalUnset[int] = UnsetValue  # should be >= 0
    fuelType: OptionalUnset[Datex2FuelType] = UnsetValue
    typeOfAssignment: Datex2AssignmentType
    user: OptionalUnset[Datex2UserType] = UnsetValue
    vehicleType: OptionalUnset[Datex2VehicleType] = UnsetValue


@dataclass(kw_only=True)
class Datex2GmlLinearRing(DataclassMixin):  # TODO: undefined
    pass


@dataclass(kw_only=True)
class Datex2Coordinate(DataclassMixin):
    latitude: float  # should use ETRS89 coordinate system
    longitude: float  # should use ETRS89 coordinate system


@dataclass(kw_only=True)
class Datex2Dimension(DataclassMixin):
    height: OptionalUnset[float] = UnsetValue  # unit: meter
    length: OptionalUnset[float] = UnsetValue  # unit: meter
    orientationOfLengthAxis: OptionalUnset[float] = UnsetValue  # unit: degree
    usableArea: OptionalUnset[float] = UnsetValue  # unit: m^2
    width: OptionalUnset[float] = UnsetValue  # unit: meter


@dataclass(kw_only=True)
class Datex2LocationAndDimension(DataclassMixin):
    coordinatesForDisplay: Datex2Coordinate
    gmlLinearRing: OptionalUnset[Datex2GmlLinearRing] = UnsetValue
    dimension: OptionalUnset[Datex2Dimension] = UnsetValue
    level: OptionalUnset[int] = UnsetValue  # 0 = grund level
    locationDescriptor: OptionalUnset[str] = UnsetValue
    roadName: OptionalUnset[str] = UnsetValue
    roadNumber: OptionalUnset[str] = UnsetValue
    specificAccessInformation: OptionalUnset[list[str]] = UnsetValue


@dataclass(kw_only=True)
class Datex2ParkingSite(DataclassMixin):
    uid: str
    assignedFor: OptionalUnset[list[Datex2Assignment]] = Default([])
    locationAndDimension: Datex2LocationAndDimension
    availableSpaces: OptionalUnset[int] = UnsetValue  # should be >= 0
    description: OptionalUnset[str] = UnsetValue
    equipmentAndServices: OptionalUnset[list[str]] = UnsetValue
    freeParking: OptionalUnset[bool] = UnsetValue
    isOpenNow: OptionalUnset[bool] = UnsetValue
    lastUpdate: OptionalUnset[datetime] = UnsetValue
    maximumParkingDuration: OptionalUnset[int] = UnsetValue  # unit: seconds
    name: OptionalUnset[str] = UnsetValue
    numberOfSpaces: OptionalUnset[int] = UnsetValue  # should be >= 0
    occupancyTrend: OptionalUnset[Datex2ParkingOccupancyTrend] = UnsetValue
    openingTimesDescription: OptionalUnset[list[str]] = UnsetValue
    operatorInformation: OptionalUnset[list[str]] = UnsetValue
    security: OptionalUnset[list[str]] = UnsetValue
    tariffDescription: OptionalUnset[list[str]] = UnsetValue
    temporaryClosed: OptionalUnset[bool] = UnsetValue
    type: Datex2ParkingSiteType
    urlLinkAddress: OptionalUnset[str] = UnsetValue  # format: url
    zoneDescription: OptionalUnset[list[str]] = UnsetValue

    def to_dict(self) -> dict:
        result = super().to_dict()
        result['_id'] = result['uid']
        del result['uid']
        return result


@dataclass(kw_only=True)
class Datex2ParkingSpace(DataclassMixin):
    uid: str
    assignedFor: list[Datex2Assignment] = field(default_factory=list)
    locationAndDimension: Datex2LocationAndDimension
    accessibility: OptionalUnset[Datex2Accessibility] = UnsetValue
    availability: Datex2Availability
    externalIdentifier: OptionalUnset[str] = UnsetValue
    lastUpdate: OptionalUnset[datetime] = UnsetValue
    maximumParkingDuration: OptionalUnset[int] = UnsetValue  # unit: seconds
    nextAvailableTimeSlot: OptionalUnset[list[datetime]] = UnsetValue
    # parkingSiteReference: OptionalUnset[Reference] = UnsetValue  # TODO: what is Reference?

    def to_dict(self) -> dict:
        result = super().to_dict()
        result['_id'] = result['uid']
        del result['uid']
        return result


@dataclass(kw_only=True)
class Datex2ParkingPublicationLight(DataclassMixin):
    parkingSite: list[Datex2ParkingSite] = field(default_factory=list)
    parkingSpace: list[Datex2ParkingSpace] = field(default_factory=list)
    description: OptionalUnset[str] = UnsetValue
    name: OptionalUnset[str] = UnsetValue
    lang: OptionalUnset[str] = UnsetValue  # TODO: unclear if required
    publicationTime: OptionalUnset[datetime] = UnsetValue  # TODO: unclear if required


@dataclass(kw_only=True)
class Datex2Publication(DataclassMixin):
    version: str = '3.4'
    modelBaseVersion: str = '3'
    extensionName: OptionalUnset[str] = UnsetValue  # TODO: unclear if required
    extensionVersion: OptionalUnset[str] = UnsetValue  # TODO: unclear if required
    profileName: OptionalUnset[str] = UnsetValue  # TODO: unclear if required
    profileVersion: OptionalUnset[str] = UnsetValue  # TODO: unclear if required
    parkingPublicationLight: Datex2ParkingPublicationLight

    def to_dict(self) -> dict:
        pre_result = super().to_dict()
        result = {'parkingPublicationLight': pre_result['parkingPublicationLight']}

        for key, value in pre_result.items():
            if key != 'parkingPublicationLight':
                result[f'_{key}'] = value

        return result
