# Changelog

## Version 0.6.2

Released 2024-06-18

## Fixes

* [Add ACTIVE status to P+M BW Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/64)


## Version 0.6.1

Released 2024-06-18

## Fixes

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
