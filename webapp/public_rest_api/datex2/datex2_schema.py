"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask_openapi.schema import (
    ArrayField,
    BooleanField,
    DateTimeField,
    EnumField,
    IntegerField,
    JsonSchema,
    NumericField,
    ObjectField,
    StringField,
    UriField,
)

from webapp.public_rest_api.datex2.datex2_models import (
    Datex2Accessibility,
    Datex2AssignmentType,
    Datex2Availability,
    Datex2FuelType,
    Datex2ParkingOccupancyTrend,
    Datex2ParkingSiteType,
    Datex2UserType,
    Datex2VehicleType,
)

datex2_coordinate_schema = ObjectField(
    description='A pair of planar coordinates defining the geodetic position of a single point using the European Terrestrial Reference '
    'System 1989 (ETRS89).',
    properties={
        'latitude': NumericField(
            description='Latitude in decimal degrees using the European Terrestrial Reference System 1989 (ETRS89).',
        ),
        'longitude': NumericField(
            description='Longitude in decimal degrees using the European Terrestrial Reference System 1989 (ETRS89).',
        ),
    },
)

datex2_gml_linear_ring = ObjectField(
    properties={},  # TODO: undefined
    required=False,
)

datex2_dimension = ObjectField(
    description='A component that provides dimension information. The product of width and height must not be necessarily be the square '
    'footage (e.g. in multi-storey buildings or when some zones are not part of the square footage).',
    properties={
        'height': NumericField(required=False, description='Height in meters.'),
        'length': NumericField(required=False, description='Length in meters.'),
        'orientationOfLengthAxis': NumericField(
            required=False,
            description='The orientation of the length axis in degree. In the case of a parking space, this corresponds to the direction,'
            ' in which a vehicle is parked.',
        ),
        'usableArea': NumericField(
            required=False,
            description='The area measured in square metres, that is available for some specific purpose.',
        ),
        'width': NumericField(required=False, description='Width in meters.'),
    },
    required=False,
)

datex2_assignment_schema = ObjectField(
    description='An assignment for a parking site or a parking space. Might be including or excluding, depending on typeOfAssignment.',
    properties={
        'additionalAssignment': StringField(
            required=False, description='An additional assignment in natural language.'
        ),
        'availableSpaces': IntegerField(
            minimum=0,
            required=False,
            description='The total number of currently vacant parking spaces within this site for the given assignment. (e.g. for lorries).'
            ' Use only with type of assignment = "optimised" or "allowed". Do not use when describing a single parking space.',
        ),
        'fuelType': EnumField(
            enum=Datex2FuelType, required=False, description='The type of fuel this assignment refers to.'
        ),
        'typeOfAssignment': EnumField(
            enum=Datex2AssignmentType,
            description='Defines, if this assignment is of including or excluding nature.',
        ),
        'user': EnumField(enum=Datex2UserType, required=False, description='A user this assignment refers to.'),
        'vehicleType': EnumField(
            enum=Datex2VehicleType, required=False, description='The vehicle type this assignment refers to.'
        ),
    },
)

datex2_location_and_dimension_schema = ObjectField(
    description='Location',
    properties={
        'coordinatesForDisplay': datex2_coordinate_schema,
        'gmlLinearRing': datex2_gml_linear_ring,
        'dimension': datex2_dimension,
        'level': IntegerField(
            required=False,
            description='The level of the parking space (0 = ground etc.), or the first level of the entire parking site (for example, if '
            'a parking site is located on the roof of a building).',
        ),
        'locationDescriptor': StringField(
            required=False, description='Supplementary human-readable description of the location'
        ),
        'roadName': StringField(required=False, description='Information on a road'),
        'roadNumber': StringField(required=False, description='The road number designated by the road authority'),
        'specificAccessInformation': ArrayField(
            items=StringField(),
            required=False,
            description='Information on one specific access (entrance or exit) in human readable text, for example the corresponding road '
            'where it is located.',
        ),
    },
)

datex_2_parking_site_schema = ObjectField(
    description='A collection of parking spaces within a building, an open ground or some on street area. Usually seen as one entity and'
    ' manged as such.',
    properties={
        '_id': StringField(),
        'assignedFor': ArrayField(items=datex2_assignment_schema, required=False),
        'locationAndDimension': datex2_location_and_dimension_schema,
        'availableSpaces': IntegerField(
            minimum=0,
            required=False,
            description='The total number of currently vacant parking spaces available in the specified parking site.',
        ),
        'description': StringField(required=False, description='A description for this parking site.'),
        'equipmentAndServices': ArrayField(
            items=StringField(),
            required=False,
            description='Equipment and services available at this parking site, described in natural language.',
        ),
        'freeParking': BooleanField(required=False, description='If true, parking is free at this site.'),
        'isOpenNow': BooleanField(required=False, description='True, if the parking site is open right now.'),
        'lastUpdate': DateTimeField(required=False, description='Last update time of this parking site information.'),
        'maximumParkingDuration': IntegerField(
            minimum=0,
            required=False,
            description='The maximum parking duration in seconds for this parking site.',
        ),
        'name': StringField(required=False, description='Name for this parking site.'),
        'numberOfSpaces': IntegerField(
            minimum=0,
            required=False,
            description='The total number of parking spaces at this site, not including closed spaces (due to maintenance, for example).',
        ),
        'occupancyTrend': EnumField(
            enum=Datex2ParkingOccupancyTrend,
            required=False,
            description='The trend of the occupancy of the parking spaces in the specified parking site.',
        ),
        'openingTimesDescription': ArrayField(
            items=StringField(),
            required=False,
            description='Opening times of this parking site, described in natural language.',
        ),
        'operatorInformation': ArrayField(
            items=StringField(),
            required=False,
            description='Information about the operator of this parking site.',
        ),
        'security': ArrayField(
            items=StringField(),
            required=False,
            description='Security aspects at this parking site, described in natural language.',
        ),
        'tariffDescription': ArrayField(
            items=StringField(),
            required=False,
            description='Information about the parking-tariffs in natural language.',
        ),
        'temporaryClosed': BooleanField(
            required=False,
            description='True, if the parking site is closed ignoring its regular opening times, for example due to maintenance or '
            'constructions.',
        ),
        'type': EnumField(enum=Datex2ParkingSiteType, description='Type of this parking site.'),
        'urlLinkAddress': UriField(
            required=False,
            description='A Uniform Resource Locator (URL) address pointing to a resource available on the Internet from where further '
            'relevant information may be obtained.',
        ),
        'zoneDescription': ArrayField(
            items=StringField(),
            required=False,
            description='A description of some specific zone this parking site might belong to.',
        ),
    },
)

datex_2_parking_space_schema = ObjectField(
    description='A parking space, i.e. a single slot for one vehicle. Includes dynamic information if it is available or not.',
    properties={
        '_id': StringField(),
        'assignedFor': ArrayField(items=datex2_assignment_schema, required=False),
        'locationAndDimension': datex2_location_and_dimension_schema,
        'accessibility': EnumField(
            enum=Datex2Accessibility,
            required=False,
            description='Information on accessibility, easements and marking for handicapped people.',
        ),
        'availability': EnumField(
            enum=Datex2Availability, description='Information if this space is closed, available or occupied.'
        ),
        'externalIdentifier': StringField(
            required=False, description='An external identfier for this parking space, e.g. "R145"'
        ),
        'lastUpdate': DateTimeField(
            required=False, description='Point of time of the latest update of this information.'
        ),
        'maximumParkingDuration': IntegerField(
            required=False,
            description='The maximum parking duration in seconds for this parking space.',
        ),
        'nextAvailableTimeSlot': ArrayField(
            items=DateTimeField(),
            required=False,
            description='In case there is a reservation or time management: Point of time this space will be available for usage.',
        ),
    },
)

datex_2_parking_publication_light = ObjectField(
    description='A simplified publication to transfer parking information.',
    properties={
        'parkingSite': ArrayField(items=datex_2_parking_site_schema),
        'parkingSpace': ArrayField(items=datex_2_parking_space_schema),
        'description': StringField(required=False, description='A description for the parking light publication.'),
        'name': StringField(required=False, description='The name of the parking light publication.'),
        'lang': StringField(),
        'publicationTime': StringField(required=False),
    },
)

datex2_parking_sites_schema = JsonSchema(
    title='Datex2 PayloadPublication',
    properties={
        '_version': StringField(),
        '_modelBaseVersion': StringField(),
        '_extensionName': StringField(required=False),
        '_extensionVersion': StringField(required=False),
        '_profileName': StringField(),
        '_profileVersion': StringField(),
        'parkingPublicationLight': datex_2_parking_publication_light,
    },
)

datex2_parking_sites_example = {}
