# ParkAPI v3

ParkAPI v3 is a web service which collects and provides access to parking data for cars and bikes. It uses
[ParkAPI-sources v3](https://github.com/ParkenDD/parkapi-sources-v3) as a 
[Python module](https://pypi.org/project/parkapi-sources/).

## Data model

The data model is rather simple (for now): we have data sources and parking sites in an 1:n relation.

The data model is documented using an OpenAPI documentation:
 - [public endpoints](https://api.mobidata-bw.de/park-api/documentation/public.html) for public data access
 - [admin endpoints](https://api.mobidata-bw.de/park-api/documentation/admin.html) for pushing or managing data

### Source

The source object represents a specific data source. Every data source has a unique identifier called `source.uid`. 
The `uid` is the central identifier which defines the data handling and, at push endpoints, even the user for basic 
authorization.

Additionally, every source has a human-readable name and a public URL where the user gets more information.

There are a few other fields at source, mostly related to import status including error counters and licence
information. For a complete overview, please have a look at the
[OpenAPI documentation](https://api.mobidata-bw.de/park-api/documentation/public.html#/paths/v3-parking-sites/get).

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
[OpenAPI documentation](https://api.mobidata-bw.de/park-api/documentation/public.html#/paths/v3-parking-sites/get).

This data model has its limits for on-street parking, where there is no user-visible area which creates the
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
need to correspond to an implementation in ParkAPI-sources which actually does the data pulling. ParkAPI-sources 
supports JSON data handling as well as HTML scraping, so almost every data format can be converted.

Data pulling is done every five minutes. It uses
[Celery's beat system](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html) which creates tasks per source
regularly, the Celery workers actually do the work then. If you decide to run a subset of ParkAPIv3s services or
build your own infrastructure (e.g. run ParkAPIv3 per systemd services), please keep in mind that both, heartbeat and
worker, are required to run.

If you want to create new data sources, please have a look at
[ParkAPI-sources' README.md](https://github.com/ParkenDD/parkapi-sources-v3?tab=readme-ov-file#write-a-new-converter).

## Push services

Push services are ParkAPIv3 endpoints which other clients send data to. This is the recommended way of
publishing realtime data, because if the client knows best when it gets an update, and therefore you will experience the
best realtime experience using push services. Push-services can also be used for pushing data which comes by other
data transport channels, e.g. per mail client.

Each source uid used for pushing requires an entry in config value `PARK_API_CONVERTER`, mapping the uid to the basic 
auth credentials that clients must provide to push to this source. have basic auth credentials. Other auth methods are
not supported so far. The `hash` is a `sha256` hash. You can create such a hash by

```python
from hashlib import sha256
sha256(b'your-very-long-random-generated-password').hexdigest()
```

You can create sha256 hashes by other tools, too, but keep in mind not to hash newlines at the end of the string (this
happens at bash quite easy).

Additionally, there should be a suitable ParkAPI v3 converter at ParkAPI-sources to convert pushed data in ParkAPI v3's 
internal format. It has to have the same source UID as the one configured in the `PARK_API_CONVERTER` config.

Push services have four different entrypoints for common data formats: XML, JSON, CSV and XLSX which are all different 
endpoints. The endpoints do some basic file loading and then hand it over to ParkAPI-sources.

If you want to create new data sources, please have a look at
[ParkAPI-sources' README.md](https://github.com/ParkenDD/parkapi-sources-v3?tab=readme-ov-file#write-a-new-converter.

### Using the push command line interface

In order to test push tasks or to upload files you got per e-mail, there is an upload script included in this
repository. It's located at `/push-client/push-client.py`. It requires python requests, so either, you have that
installed at your system, or you create a virtual environment for that:

```bash
cd push-client
virtalenv venv
pip install "requests~=2.31.0"
source venv/bin/activate
python push-client.py
```

If you have requests, you can run the script with two arguments:
- the source uid which should be registered as user at `config.yaml` and should have a representation at ParkAPI-sources
- the path to the file to push

It also accepts the parameter -u for overwriting the URL the data should be pushed to. If you want to do a local test,
`-u http://localhost:5000` would be the way to go.

Afterward, the password will be asked in a secure way, then the upload progress begins.

## Configuration

Besides `PARK_API_CONVERTER`, there are a few other configuration options to set, you will find valid config keys in 
`config_dist_dev.yaml`. You can set config values by two different approaches (or even mix them):

1) You can create a config file called `config.yaml` in your root folder.
2) You can set any config value by env var, but you have to prefix the config name with `PARKAPI_` then. For example, 
   you can configure `SECRET_KEY` using the env var `$PARKAPI_SECRET_KEY`. ENV vars overwrite 


## Monitoring: Loki and Prometheus

ParkAPI v3 provides a Prometheus endpoint at `/metrics` which helps to monitor the status of all data sources. It also
provides a Loki integration to send properly tagged log messages to a Loki instance. This is enabled by the
configuration value `LOKI_ENABLED` to true. The url is set by `LOKI_URL`, additionall tags are injected by `LOKI_TAGS`,
and BasicAuth is set by `LOKI_USER` and `LOKI_PASSWORD` (if required).

## Extending and fixing ParkAPI

Merge requests are very welcome. Please keep in mind that ParkAPI v3 is an open source project under MIT licence, so any
code you add should be compatible with this licence. Bug reports are welcome, too, of course.
