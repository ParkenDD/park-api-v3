# ParkAPI v3

ParkAPI v3 is a web service which collects and provides access to parking data. It uses
[ParkAPI-sources](https://github.com/ParkenDD/ParkAPI2-sources) as a
[Git Submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules) at `webapp/converter` to collect data in different data structures.

## Data model

The data model is rather simple (for now): we have data sources and parking sites in an 1:n relation.

The data model is documented using an OpenAPI documentation:
 - [public endpoints](https://dev-ipl.mobidata-bw.de/park-api/documentation/public.html) for public data access
 - [admin endpoints](https://dev-ipl.mobidata-bw.de/park-api/documentation/admin.html) for pushing or managing data

### Source

The source object represents a specific data source. Every data source has a unique identifier called `source.uid` in
the new data model and `PoolInfo.id` in legacy data sources. The `uid` is the central identifier which defines the
data handling and, at push endpoints, even the user for basic authorization.

Additionally, every source has a human-readable name and a public URL where the user gets more information.

There are a few other fields at source, mostly related to import status including error counters and licence
information. For a complete overview, please have a look at the
[OpenAPI documentation](webapp/models/source.py).

If, until now, you used the ParkAPI v1 model, you might recognize that there is a change of perspective: at v1, the
main object for collecting data was city, not source. This turned out not to be very realistic, because often there are
multiple operators per city. ParkAPI v2 changed this to a source-based approach, and added geo-based queries to
searches in order not to rely on a city as a query parameter.

### Parking Site

`ParkingSite` represents a location where multiple parking spaces are located as a defined area or building. Every
parking site has a data source where it comes from. It also has all the relevant data which describes the parking site:
a name, an address, a url and other meta information. Additionally, it has static and, if the data source provides it,
realtime data for capacities. It also has opening times in OSM format and also, if available, a realtime opening status.
For a complete overview, please have a look at the
[OpenAPI documentation](webapp/models/parking_site.py).

This data model has it's limits for on-street parking, where there is no user-visible area which creates the
borders of a specific parking site. Usually, there are definitions for areas like parts of streets, which also apply
on fees or rules for this area, so it's a good idea to stick to them instead of importing every single parking space as
a whole parking site.

There is a limit if it comes to attributes of parking spots: it's simple to define capacities for a single defined
attribute, like family parking or parking with a charge station. The difficulty begins if there are parking spaces with
multiple attributes at once, for example one parking spot which is for families and has a charge station at the same
time. A possible solution would be to extend the data model to a parking space perspective, where every single parking
space has a representation in the data model. Most data sources are not able to provide such in-detail information, so
in order to provide data in a more consistent way, we decided against this (in the first place).

## Input: push and pull

There are two ways to get data in the system: pulling data from other servers using ParkAPI-source directly, and pushing
data to endpoints of this service which is also handled by ParkAPI-sources. In both cases, ParkAPI v3 stores the data:
ParkAPI-sources "just" transforms the data to a unified model.

### Pull data

Source UIDs which should be pulled have to be in `PARK_API_CONVERTER` as described in `config_dist_dev.yaml`. The UIDs
need to correspond to an implementation in ParkAPI-sources which actually does the data pulling. ParkAPI-sources supports JSON data
handling as well as HTML scraping, so almost every data format can be converted. Pulling data is done by the old
ParkAPI v1 and v2 converters (so far).

Data pulling is done every five minutes. It uses
[Celery's beat system](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html) which creates tasks per source
regularly, the Celery workers actually do the work then. If you decide to run a subset of ParkAPIv2s services or
build your own infrastructure (eg run ParkAPIv3 per systemd services), please keep in mind that both, heartbeat and
worker, are required to run.

If you want to create new data sources, please have a look at
[ParkAPI-sources' README.md](https://github.com/ParkenDD/ParkAPI2-sources#polling--scraping-data-1).

## Push services

Push services are ParkAPIv3 endpoints which other clients send data to. This is the recommended way of
publishing realtime data, because if the client knows best when it gets an update, and therefore you will experience the
best realtime experience using push services. Push-services can also be used for pushing data which comes by other
data transport channels, eg per mail client.

Each source uid used for pushing requires an entry in config value `SERVER_AUTH_USERS`, mapping the uid to the basic auth credentials that clients must provide to push to this source.
have basic auth credentials. Other auth methods are not supported so far. The `hash` is a `sha256` hash. You can create
such a hash by

```python
from hashlib import sha256
sha256(b'your-very-long-random-generated-password').hexdigest()
```

You can create sha256 hashes by other tools, too, but keep in mind not to hash newlines at the end of the string (this
happens at bash quite easy).

Additionally, there should be a suitable ParkAPI v3 converter at ParkAPI-sources to convert pushed data in ParkAPI v3's 
internal format. It has to have the same source UID as the one configured in the `SERVER_AUTH_USERS` config.

Push services have four different entrypoints for common data formats: XML, JSON, CSV and XLSX. The endpoints do some
basic file loading and then hand it over to ParkAPI-sources.

If you want to create new data sources, please have a look at
[ParkAPI-sources' README.md](https://github.com/ParkenDD/ParkAPI2-sources#pushed-data-1).

### Using the push command line interface

In order to test push tasks or to upload files you got per e-mail, there is an upload script included in this
repository. It's located at `/push-client/push-client.py`. It requires python requests, so either, you have that
installed at your system, or you create a virtual environment for that:

```bash
cd push-client
virtalenv venv
source venv/bin/activate
python push-client.py
```

If you have requests, you can run the script with two arguments:
- the source uid which should be registered as user at `config.yaml` and should have a representation at ParkAPI-sources
- the path to the file to push

Afterward, the password will be asked in a secure way, then the upload progress begins.

## Configuration

Besides `PARK_API_CONVERTER` and `SERVER_AUTH_USERS`, there are a few other configuration options to set, you will find
example values in `config_dist_dev.yaml`. You can set any config value by env var too, but you have to prefix the config
name with `PARKAPI_` then. For example, you can configure `SECRET_KEY` using the env var `$PARKAPI_SECRET_KEY`.

## Monitoring: Loki and Prometheus

ParkAPI v3 provides a Prometheus endpoint at `/metrics` which helps to monitor the status of all data sources. It also
provides a Loki integration to send properly tagged log messages to a Loki instance. This is enabled by the
configuration value `LOKI_ENABLED` to true. The url is set by `LOKI_URL`, additionall tags are injected by `LOKI_TAGS`,
and BasicAuth is set by `LOKI_USER` and `LOKI_PASSWORD` (if required).

## Extending and fixing ParkAPI

Merge requests are very welcome. Please keep in mind that ParkAPI v3 is an open source project under MIT licence, so any
code you add should be compatible with this licence. Bug reports are welcome, too, of course.
