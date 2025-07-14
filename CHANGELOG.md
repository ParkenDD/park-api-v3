# Changelog

## 0.26.0

Released 2025-07-14

### Features

* [ParkAPI Sources: Integrate B+B Parkhaus Push Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/237)


### Fixes

* [ParkAPI Sources: Freiburg: fixed closed status](https://github.com/ParkenDD/parkapi-sources-v3/pull/242)
* [ParkAPI Sources: recreate Makefile](https://github.com/ParkenDD/parkapi-sources-v3/pull/241)



## 0.25.1

### Fixes

* [ParkAPI Sources: Freiburg P+R Attribute](https://github.com/ParkenDD/parkapi-sources-v3/pull/235)
* [ParkAPI Sources: Freiburg OpeningTime logic](https://github.com/ParkenDD/parkapi-sources-v3/pull/234)


## 0.25.0

Released 2025-06-23

### Features

* [ParkAPI Sources: Freiburg P+R Converters](https://github.com/ParkenDD/parkapi-sources-v3/pull/230)


## 0.24.0

Released 2025-06-02

### Features

* [Sources + ParkingSpot Admin REST API](https://github.com/ParkenDD/park-api-v3/pull/293)


## 0.23.1

Released 2025-06-02

### Fixes

* [ParkAPI Sources: Extend static data to Freiburg](https://github.com/ParkenDD/parkapi-sources-v3/pull/226)


## 0.23.0

Released 2025-05-18

### Features

* [ParkAPI Sources: ParkingSite patch system](https://github.com/ParkenDD/parkapi-sources-v3/pull/208)
* [ParkAPI Sources: Freiburg ParkingSpots](https://github.com/ParkenDD/parkapi-sources-v3/pull/214)
* [ParkAPI Sources: Ulm Sensors ParkingSites and ParkingSpots](https://github.com/ParkenDD/parkapi-sources-v3/pull/203)
* [ParkAPI Sources: ParkingSpot type support for Friedrichshafen Sensors](https://github.com/ParkenDD/parkapi-sources-v3/pull/213)


### Maintenance

* Dependency updates


## 0.22.1

Released 2025-05-10

### Features

* [ensure valid metrics](https://github.com/ParkenDD/park-api-v3/pull/284)


## 0.22.0

Released 2025-05-10

### Features

* [better realtime monitoring](https://github.com/ParkenDD/park-api-v3/pull/283)


## 0.21.3

Released 2025-05-08

### Fixes

* Fixes migration in 0.21.2


## 0.21.2

Released 2025-05-08

### Fixes

* [Fixes realtime updates at heartbeat mechanism](https://github.com/ParkenDD/park-api-v3/pull/282)


## 0.21.1

Released 2025-04-12

This release introduces automated OpenAPI docs testing in integration tests.

### Fixes

* [Better OpenAPI documentation with automated OpenAPI testing with documentation fixes](https://github.com/ParkenDD/park-api-v3/pull/271)


## 0.21.0

Released 2025-04-09

This release is a major change, as it introduces parking spots. The new parking spot endpoint can be accessed via
`/api/public/v3/parking-spots`, you will find the documentation at
`/documentation/public.html#/paths/v3-parking-spots/get`.

Additionally, the project introduces integration tests via CI and multiple automated endpoint tests.

### Features

* [Parking spots and integration tests](https://github.com/ParkenDD/park-api-v3/pull/268)
* [ParkAPI Sources: Friedrichshafen Sensors](https://github.com/ParkenDD/parkapi-sources-v3/pull/198)


## 0.20.4

Released 2025-04-02

### Fixes

* [ParkAPI Sources: Update pum_bw mapping and data](https://github.com/ParkenDD/parkapi-sources-v3/pull/197)
* [ParkAPI Sources: Changed source_url for herrenberg_bike](https://github.com/ParkenDD/parkapi-sources-v3/pull/194)
* [Fixed bug in setting realtime_free_capacity greater than capacity](https://github.com/ParkenDD/park-api-v3/pull/263)
* [support unsetting duplicates](https://github.com/ParkenDD/park-api-v3/pull/267)


## 0.20.3

Release 2025-03-07

### Fixes

* [ParkAPI Sources: Fix and reduce validation errors in converters](https://github.com/ParkenDD/parkapi-sources-v3/pull/191)


## 0.20.2

Release 2025-02-22

### Fixes

* [ParkAPI Sources: introduce request helper](https://github.com/ParkenDD/parkapi-sources-v3/pull/190)


## 0.20.1

Released 2025-02-19

## Fixes

* [ParkAPI Sources: Fix bahn converter by creating session for client cert requests](https://github.com/ParkenDD/parkapi-sources-v3/pull/189)


## 0.20.0

Released 2025-02-19

## Features

* [Debug Mechanism](https://github.com/ParkenDD/park-api-v3/pull/250)
* [ParkAPI Sources: Debug Mode for dumping full communication per source](https://github.com/ParkenDD/parkapi-sources-v3/pull/187)
* [ParkAPI Sources: Add Aachen](https://github.com/ParkenDD/parkapi-sources-v3/pull/186)


## Maintenance

* [ParkAPI Sources: Datex2 Refactoring for good parent classes for any Datex2 source](https://github.com/ParkenDD/parkapi-sources-v3/pull/186)



## 0.19.0

### Features

* [Duplicate query: Add source_id and source_uid ](https://github.com/ParkenDD/park-api-v3/pull/242)


## 0.18.1

### Fixes

* [Hotfix ParkAPI OpeningTime output for ParkAPI v1](https://github.com/ParkenDD/park-api-v3/pull/241)


## 0.18.0

### Features

* [Switch to Alpine base image and Python 3.12](https://github.com/ParkenDD/park-api-v3/pull/237)


### Fixes

* [ParkAPI Sources: Add required attributes at several converters](https://github.com/ParkenDD/parkapi-sources-v3/pull/183)


### Maintenance

* [Several dependency updates](https://github.com/ParkenDD/park-api-v3/pull/237)


## 0.17.3

Released 2025-01-24

### Fixes

* [Better sources output and documentation](https://github.com/ParkenDD/park-api-v3/pull/231)


## 0.17.2

Released 2025-01-21

### Fixes

* Catch even more exceptions at plausibility check


## 0.17.1

Released 2025-01-21

### Fixes

* Fix issue with database fields which can be None


## 0.17.0

Released 2025-01-21

### Features

* [Add plausibility check for realtime_free_capacity values](https://github.com/ParkenDD/park-api-v3/pull/222)
* [ParkAPI Sources: Add VRN Park and Ride Realtime Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/180)
* [ParkAPI Sources: Add bahnv2 bike parking locked and open](https://github.com/ParkenDD/parkapi-sources-v3/pull/172)

### Fixes

* [ParkAPI Sources: opendata_swiss: change to new source_url](https://github.com/ParkenDD/parkapi-sources-v3/pull/179)


## 0.16.5

Released 2025-01-07

### Fixes

* [Fixes a config format issue](https://github.com/ParkenDD/park-api-v3/pull/230)


## 0.16.4

Released 2024-12-31

### Fixes

* [Fixes an issue with default minute value at crontab](https://github.com/ParkenDD/park-api-v3/pull/227)


## 0.16.3

Released 2024-12-26

### Fixes

* [Fixes an issue with logs not sent to Loki in Celery](https://github.com/ParkenDD/park-api-v3/pull/226)


## 0.16.2

Released 2024-11-28

### Fixes

* [Fixes an issue with Celery Tasks sometimes preventing static data imports](https://github.com/ParkenDD/park-api-v3/pull/224)


## 0.16.1

Released 2024-11-27

### Fixes

* [Improved cron and logging](https://github.com/ParkenDD/park-api-v3/pull/223)
* [ParkAPI Sources: GeoJSON Approach cleanup](https://github.com/ParkenDD/parkapi-sources-v3/pull/173)
* [ParkAPI Sources: Fix DateTime Format at Karlsruhe](https://github.com/ParkenDD/parkapi-sources-v3/pull/173)
* [ParkAPI Sources: Fix optional attributes at Kienzler](https://github.com/ParkenDD/parkapi-sources-v3/pull/173)


## 0.16.0

Released 2024-11-25

## Features

* [ParkAPI Sources: New Source: Velobrix](https://github.com/ParkenDD/parkapi-sources-v3/pull/165)
* [ParkAPI Sources: Kienzler: use static data as additional data input](https://github.com/ParkenDD/parkapi-sources-v3/pull/168)


## 0.15.3

Released 2024-11-20

### Fixes

* [Allow Realtime Opening Status Null](https://github.com/ParkenDD/park-api-v3/pull/221)


## 0.15.2

Released 2024-11-12

### Fixes

* [ParkAPI Sources: APCOA: Remove park control objects and added production endpoint](https://github.com/ParkenDD/parkapi-sources-v3/pull/162)
* [ParkAPI Sources: radvis_bw: filter unprintable characters](https://github.com/ParkenDD/parkapi-sources-v3/pull/167)
* [ParkAPI Sources: multiple converters: set opening status to none if unset](https://github.com/ParkenDD/parkapi-sources-v3/pull/160)


## 0.15.1

Released 2024-10-29

## Fixes

* [documentation fixes](https://github.com/ParkenDD/park-api-v3/pull/218)
* [ruff modernization](https://github.com/ParkenDD/park-api-v3/pull/218)
* [ParkAPI Sources: Fixed Karlsruhe format for stand_stammdaten ](https://github.com/ParkenDD/parkapi-sources-v3/pull/152)
* [ParkAPI Sources: ruff modernization](https://github.com/ParkenDD/parkapi-sources-v3/pull/155)


## 0.15.0

Released 2024-10-17

### Features

* [ParkAPI Sources: Add Kienzler VVS Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/147)


### Fixes

* [ParkAPI Sources: Update pbw data for static parking sites](https://github.com/ParkenDD/parkapi-sources-v3/pull/144)
* [ParkAPI Sources: Update kienzler data for static parking sites](https://github.com/ParkenDD/parkapi-sources-v3/pull/145)
* [ParkAPI Sources: Fix bfrk_bw_car attribute after source change](https://github.com/ParkenDD/parkapi-sources-v3/pull/149)


## 0.14.3

Released 2024-09-24

### Fixes

* [ParkAPI Sources: Fix BFRK infraid](https://github.com/ParkenDD/parkapi-sources-v3/pull/140)


## 0.14.2

Released 2024-09-24

### Fixes

* [ParkAPI Sources: enforce capacity](https://github.com/ParkenDD/parkapi-sources-v3/pull/133)
* [ParkAPI Sources: remove confusing herrenberg field](https://github.com/ParkenDD/parkapi-sources-v3/pull/134)
* [ParkAPI Sources: set kienzler public url](https://github.com/ParkenDD/parkapi-sources-v3/pull/135)
* [ParkAPI Sources: fix Herrenberg parking type mapping](https://github.com/ParkenDD/parkapi-sources-v3/pull/136)


## 0.14.1

Released 2024-09-22

### Fixes

* [Remove generic bike](https://github.com/ParkenDD/park-api-v3/pull/205)
* [ParkAPI Sources: Add VRS data](https://github.com/ParkenDD/parkapi-sources-v3/pull/123)
* [ParkAPI Sources: Fix bahn mapping](https://github.com/ParkenDD/parkapi-sources-v3/pull/124)
* [ParkAPI Sources: Fix PBW Mapping](https://github.com/ParkenDD/parkapi-sources-v3/pull/125)
* [ParkAPI Sources: Fix Heidelberg fee](https://github.com/ParkenDD/parkapi-sources-v3/pull/126)
* [ParkAPI Sources: Split up kienzler requests](https://github.com/ParkenDD/parkapi-sources-v3/pull/128)
* [ParkAPI Sources: Fix bfrk mapping](https://github.com/ParkenDD/parkapi-sources-v3/pull/129)


## 0.14.0

Released 2024-09-16

### Features

* [ParkAPI Sources: Herrenberg static bike pull converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/110)


### Fixes

* [ParkAPI Sources: Park and Ride at BFRK](https://github.com/ParkenDD/parkapi-sources-v3/pull/121)
* [small fixes in openapi docs](https://github.com/ParkenDD/park-api-v3/pull/200)


## 0.13.1

Released 2024-09-09

### Fixes

* [ParkAPI Sources: has_fee True at all Heidelberg parking sites](https://github.com/ParkenDD/parkapi-sources-v3/pull/117)


## 0.13.0

Released 2024-09-03

### Features

* [ParkAPI Sources: Hüfner Push Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/106)


### Fixes

* [ParkAPI Sources: BFRK: Make URL configurable](https://github.com/ParkenDD/parkapi-sources-v3/pull/114)
* [ParkAPI Sources: Karlsruhe Bike: Ignore missing capacities](https://github.com/ParkenDD/parkapi-sources-v3/pull/113)
* [ParkAPI Sources: APCOA: Ignore missing coordinates](https://github.com/ParkenDD/parkapi-sources-v3/pull/112)
* [ParkAPI Sources: APCOA: Fox OSM Opening Times](https://github.com/ParkenDD/parkapi-sources-v3/pull/107)


## 0.12.0

Released 2024-08-24

### Features

* [ParkAPI Sources: BFRK: Use API](https://github.com/ParkenDD/parkapi-sources-v3/pull/109)
* [Add max_width Support](https://github.com/ParkenDD/park-api-v3/pull/194)


### Fixes

* [ParkAPI Sources: Dynamic Realtime Setting at Karlsruhe](https://github.com/ParkenDD/parkapi-sources-v3/pull/105)
* [ParkAPI Sources: Fixes VRS UID mapping](https://github.com/ParkenDD/parkapi-sources-v3/pull/108)


## 0.11.0

Released 2024-08-20

### Features

* [ParkAPI Sources: Converters for Bondorf, Kirchheim, Neustadt and Vaihingen](https://github.com/ParkenDD/parkapi-sources-v3/pull/98)
* [ParkAPI Sources: Converter for Konstanz](https://github.com/ParkenDD/parkapi-sources-v3/pull/102)


### Fixes

* [ParlAPI Sources: Fixes env vars at Kienzler split-up](https://github.com/ParkenDD/parkapi-sources-v3/pull/101)


## 0.10.0

Released 2024-08-15

### Features

* [Introduce parking site groups](https://github.com/ParkenDD/park-api-v3/pull/192)
* [ParkAPI Sources: parking site groups](https://github.com/ParkenDD/parkapi-sources-v3/pull/95)
* [ParkAPI Sources: split up kienzler](https://github.com/ParkenDD/parkapi-sources-v3/pull/96)


### Fixes

* [Query optimization for much faster response times with large dataabses](https://github.com/ParkenDD/park-api-v3/pull/192)
* [ParkAPI Sources: Karlsruhe converter: Updated parking place name and opening_status attributes](https://github.com/ParkenDD/parkapi-sources-v3/pull/94)


## 0.9.0

Released 2024-08-08

### Features

* [ParkAPI Sources: Opendata Swiss pull converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/70)

### Fixes

* [ParkAPI Sources: Ellwangen converter: Added OSM opening_hours](https://github.com/ParkenDD/parkapi-sources-v3/pull/90)
* [ParkAPI Sources: Updated the source_url Karlsruhe converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/88)
* [ParkAPI Sources: Goldbeck converter: Added OSM opening_hours](https://github.com/ParkenDD/parkapi-sources-v3/pull/89)
* [ParkAPI Sources: Fix Ulm scraper](https://github.com/ParkenDD/parkapi-sources-v3/pull/82)
* [ParkAPI Sources: Fix Herrenberg address](https://github.com/ParkenDD/parkapi-sources-v3/pull/83)
* [ParkAPI Sources: Fix Herrenberg state mapping](https://github.com/ParkenDD/parkapi-sources-v3/pull/84)
* [ParkAPI Sources: Fix BFRK is_covered naming](https://github.com/ParkenDD/parkapi-sources-v3/pull/85)



## 0.8.0

Released 2024-07-23

### Features

* [Goldbeck support](https://github.com/ParkenDD/parkapi-sources-v3/pull/68)


## 0.7.6

Released 2024-07-23

### Features

* [Add pull errors to log](https://github.com/ParkenDD/park-api-v3/pull/178)

### Maintenance

* Dependency updates


## 0.7.5

Released 2024-07-18

### Fixes

* Fix more metrics logic


## 0.7.4

Released 2024-07-18

### Fixes

* Fix metrics logic


## 0.7.3

Released 2024-07-18

### Fixes

* [Add free capacity to Parking Site metrics, better labels](https://github.com/ParkenDD/park-api-v3/pull/177)


## 0.7.2

Released 2024-07-18

### Fixes

* [Add names to Parking Site metrics](https://github.com/ParkenDD/park-api-v3/pull/176)


## 0.7.1

Released 2024-07-13

### Fixes

* [ParkAPI Sources: Fix Herrenberg base class to fix realtime updates](https://github.com/ParkenDD/parkapi-sources-v3/pull/73)


## Version 0.7.0

Released 2024-07-13

### Features

* [ParkAPI Sources: Add Herrenberg converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/71)
* [ParkAPI Sources: Add APCOA converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/72)


## Version 0.6.3

Released 2024-06-19

### Fixes

* [set karlsruhe to realtime](https://github.com/ParkenDD/parkapi-sources-v3/pull/65)


## Version 0.6.2

Released 2024-06-18

### Fixes

* [Add ACTIVE status to P+M BW Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/64)


## Version 0.6.1

Released 2024-06-18

### Fixes

* [ParkAPI Sources: Renames and extends P+M BW Converter with static data](https://github.com/ParkenDD/parkapi-sources-v3/pull/63)


## Version 0.6.0

Released 2024-06-14

### Features

* [Multiple new converters at ParkAPI Sources 0.5.0](https://github.com/ParkenDD/parkapi-sources-v3/blob/main/CHANGELOG.md#050)

### Fixes

* [Fixes calculating geo-distance at matching service](https://github.com/ParkenDD/park-api-v3/pull/162)
* [Multiple fixes at ParkAPI Sources 0.5.0](https://github.com/ParkenDD/parkapi-sources-v3/blob/main/CHANGELOG.md#050)

### Maintenance

* Replace black by ruff formatter
* Dependency updates


## Version 0.5.1

Released 2024-06-04

### Fixes

* [Fixes an issue with wrong koordinates at Karlsruhe](https://github.com/ParkenDD/parkapi-sources-v3/pull/48)
* [Fixes an issue with Bahn data without capacity](https://github.com/ParkenDD/parkapi-sources-v3/pull/49)
* [Better usability of the get-new-duplicates script](https://github.com/ParkenDD/park-api-v3/pull/155)


## Version 0.5.0

Released 2024-05-30

### Features

* Deletes ParkingSites if they don't exist in the latest pull / push
* Several Improvements for Duplicate Matching Service:
  * Don't offer ParkingSites with different purposes as duplicates
  * Don't offer ParkingSites from the same source as duplicates as this is an data source issue
  * Add several fields at the duplicate JSON / CSV output
  * Add header line to duplicate CSVs
  * Give the ability to set the radius from client side


### Fixes

* Add missing fields to OpenAPI documentation


## Version 0.4.3

Released 2024-05-29

### Fixes

* Version updates in dependencies, especially a lat-lon bugfix in parkapi-sources


## Version 0.4.2

Released 2024-05-28

### Fixes

* Fixes issue in database migration downgrade leading to database not matching the model
* Catches and logs an issue with invalid data at duplicate distance calculation


## Version 0.4.1

Released 2024-05-16

### Fixes

* Issue in database migration leading to database not matching the model


## Version 0.4.0

Released 2024-05-16

### Features

* [New ParkAPI sources](https://github.com/ParkenDD/parkapi-sources-v3/blob/main/CHANGELOG.md#040)
* [New experimental ParkAPI source RadVIS](https://github.com/ParkenDD/parkapi-sources-v3/blob/main/CHANGELOG.md#040)
* [Experimental duplicate matching](https://github.com/ParkenDD/park-api-v3/pull/144),
  additional information [at README](https://github.com/ParkenDD/park-api-v3?tab=readme-ov-file#flag-duplicates-via-command-line-interface)
* Data model extension at `ParkingSite.type` (new enum values), `ParkingSite.tags` (generic tag system) and `ParkingSite.photo_url` (photos)

### Fixes

* [Some converter fixes from ParkAPI sources project](https://github.com/ParkenDD/parkapi-sources-v3/blob/main/CHANGELOG.md#040)


### Fixes and Maintenance

* Dependency updates


## Version 0.3.0

Released 2024-05-08

### Features

* Parking-Site endpoints now support optional cursor-pagination


## Version 0.2.0

Released 2024-05-03

### Features

* [New ParkAPI sources](https://github.com/ParkenDD/parkapi-sources-v3/blob/main/CHANGELOG.md#030)
* [Normalizes radius search](https://github.com/ParkenDD/park-api-v3/pull/133)

### Fixes and Maintenance

* [Fixes OpenAPI response schema at generic parking site endpoints](https://github.com/ParkenDD/park-api-v3/pull/135)
* Dependency updates


## Version 0.1.1

Released 2024-04-21

### Fixes

* Update dependencies, include fixing CVE-2024-1135 at gunicorn
* Fix issue with heartbeat and new python module approach


## Version 0.1.0

Released 2024-04-21

First release with SemVer versioning. Included refactored ParkAPI Sources, now
[based on Python module instead of Git Submodules](https://pypi.org/project/parkapi-sources/), and bike parking
support. Includes a data model change, therefore a database migration is required.
