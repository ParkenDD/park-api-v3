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
repository. It's located at `/scripts/push-client.py`. You need python requests for this, please have a look at
"Prepare scripts environment" for preparations. You can use the script using:

```bash
python push-client.py source_uid some/file.csv
```

If you have requests, you can run the script with two arguments:
- the source uid which should be registered as user at `config.yaml` and should have a representation at ParkAPI-sources
- the path to the file to push

It also accepts the parameter -u for overwriting the URL the data should be pushed to. If you want to do a local test,
`-u http://localhost:5000` would be the way to go.

Afterward, the password will be asked in a secure way, then the upload progress begins.


## Flag duplicates via command line interface

*Warning: experimental feature. Interface might change.*

ParkAPI provides a mechanism to flag dataset as duplicates. There are two endpoints to do this, which are used by two
helper scripts. For both scripts you need python requests, please have a look at "Prepare scripts environment" for
preparations. Additionally, you will have to set up an admin user and password using at config using the config
key `SERVER_AUTH_USERS`. Please have a look at `config_dist_dev.yaml` for an example.


### Get possible duplicates

In order to get possible duplicates, you have to use the endpoint `/api/admin/v1/parking-sites/duplicates`. To use this
endpoint, there is a helper script in `scripts`. You can use it by:

```
python get-new-duplicates.py username
```

Per default, the scripts outputs the possible duplicates on stdout. You can modify this behaviour and other settings
using following optional options:
- `-o` for an old duplicate file path. These duplicates are sent to the server, and the result will not contain the old
  duplicates. This helps to just append new duplicates.
- `-n` for a new duplicate file path. The script saves an CSV to this file path instead of using stdout for results.
  If it's the same file path as the old duplicate file, the script will append the new duplicates to the old file.
- `-u` for a custom URL. If you cant to use this script for another environment, you will have to set the url. For
  example, if you cant to do a local test, you have to set it to `-u http://localhost:5000`.
- `-s` to silence the status output. Using this, you can pipe the JSON output to other applications like `json_pp`.
- `-si` to limit sources to a list of source ids. Has to be used like `-si 1 2 3`
- `-su` to limit sources to a list of source uids. Has to be used like `-su source1 source2 source3`

The source filter parameters `-si` and `-su` trigger a filter in which one of the parking sites has to be in this
source list. For example, with `-si 1` you will get any duplicate between source 1 and some other source without a
filter.

`-si` and `-su` are mutually exclusive and need to be set as the last parameter.
`get-new-duplicates.py username -su source1 source2` works, `get-new-duplicates.py -su source1 source2 username` does
not.


### Apply duplicates

The CSV file from the step before will have the following format:

```csv
parking_site_id;duplicate_parking_site_id;status;more columns for better decision making
```

`status` can be `KEEP` or `IGNORE`. Per default, it will be set to `KEEP` to keep all datasets active. If you want to
flag a `ParkingSite` as duplicate, please set the status to `IGNORE`. Example, if you want to flag the `ParkingSite`
with ID `10` as duplicates and keep the `ParkingSite` ID 11 active, it will look like this:

```csv
10;11;IGNORE;...
11;10;KEEP;...
```

Please keep in mind that Excel will most likely break your CSV files. Please use a proper CSV editing tool like
[LibreOffice Calc](https://www.libreoffice.org/discover/calc/).

If you finished your file, you can apply this file using

```
python apply-duplicates.py username your/duplicate-file.csv
```

Please keep in mind that you will have to apply all duplicates at this command, because the server cannot un-flag
duplicates without a full list of duplicates.

There is again `-u` as option for a custom URL. If you cant to use this script for another environment, you will have
to set the url. For example, if you cant to do a local test, you have to set it to `-u http://localhost:5000`.


## Configuration

Besides `PARK_API_CONVERTER`, there are a few other configuration options to set, you will find valid config keys in
`config_dist_dev.yaml`. You can set config values by two different approaches (or even mix them):

1) You can create a config file called `config.yaml` in your root folder.
2) You can set any config value by env var, but you have to prefix the config name with `PARKAPI_` then. For example,
   you can configure `SECRET_KEY` using the env var `$PARKAPI_SECRET_KEY`. ENV vars overwrite


## Prepare scripts environment

In order to use the scripts located in `scripts`, you will need [python requests](https://pypi.org/project/requests/).
You can use a system-installed version of requests, or you can create a virtual environment for this:

```bash
cd scripts
virtalenv venv
pip install "requests~=2.32.3"
source venv/bin/activate
```


## Debugging data sources

It might happen that data sources show unexpected behaviour in deployed systems, and sometimes it's difficult to
reproduce issues in dev environments. To help debugging, ParkAPI supports a request dump mechanism, which will work for
pull- as well as for push-converters.

The debug-mechanisms needs to config variables:

- `DEBUG_DUMP_DIR` as the directory where dumps are saved to, defaults to `./data/debug-dump/`
- `DEBUG_SOURCES` as a list of source UIDs which should be debugged, defaults to `[]`

If you set a source at `DEBUG_SOURCES`, ParkAPI will create a subdirectory `./data/debug-dump/{source_uid}`, and will
dump all communication from this converter in this folder. Per request, there will be two files:

- `{datetime}-metadata` for the request metadata, like path, HTTP status and HTTP headers
- `{datetime}-response-body` for pull converters / `{datetime}request-body` for push converters for the actual data dump

The `response-body` / `request-body` can be used as test data at ParkAPI sources to find specific issues at the data.
Or, the headers might give a good idea what actually happened when something failed.

Please keep in mind that dumping will need quite some storage, as every request with the fill request and response
body is dumped.

Please also keep in mind that especially the HTTP headers might include sensitive data like credentials, so please
handle them the same way you would handle a password. These files should never be part of a Github ticket, for example.


## Monitoring: Loki and Prometheus

ParkAPI v3 provides a Prometheus endpoint at `/metrics` which helps to monitor the status of all data sources. It also
provides a Loki integration to send properly tagged log messages to a Loki instance. This is enabled by the
configuration value `LOKI_ENABLED` to true. The url is set by `LOKI_URL`, additionall tags are injected by `LOKI_TAGS`,
and BasicAuth is set by `LOKI_USER` and `LOKI_PASSWORD` (if required).

## Extending and fixing ParkAPI

Merge requests are very welcome. Please keep in mind that ParkAPI v3 is an open source project under MIT licence, so any
code you add should be compatible with this licence. Bug reports are welcome, too, of course.
