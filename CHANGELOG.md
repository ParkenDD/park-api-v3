# Changelog

## Version 0.1.1

Released 2024-04-21

- Update dependencies, include fixing CVE-2024-1135 at gunicorn
- Fix issue with heartbeat and new python module approach

## Version 0.1.0

Released 2024-04-21

First release with SemVer versioning. Included refactored ParkAPI Sources, now 
[based on Python module instead of Git Submodules](https://pypi.org/project/parkapi-sources/), and bike parking 
support. Includes a data model change, therefore a database migration is required.
