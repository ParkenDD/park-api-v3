# Changelog

## Version 0.3.0

Released 2024-05-07

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
