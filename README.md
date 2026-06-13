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

Per default, static data will be fetched every night at 1 am, and realtime data will be fetched every 5 minutes. You
can change the static moment using the config vars `STATIC_IMPORT_PULL_HOUR` and `STATIC_IMPORT_PULL_MINUTE`, and
the realtime frequency using `REALTIME_IMPORT_PULL_FREQUENCY`, which should be in seconds. Additionally, you can set
`REALTIME_OUTDATED_AFTER_MINUTES`, which will flag sources at outdated in our Prometheus endpoint after the defined
amount of time. It defaults to 30 minutes.

### Source status: static and realtime

Every source tracks two independent import states, `static_status` and `realtime_status`. Both are exposed in the
public source data and used by the Prometheus endpoint for monitoring. Each can take one of the following values:

- `PROVISIONED`: the source has been created (e.g. by `flask source init-converters`) but has not yet had a successful
  import. This is the initial state.
- `ACTIVE`: the last import succeeded.
- `FAILED`: the last import failed (for example because the upstream server was unreachable or returned invalid data).
- `DISABLED`: this kind of import does not apply to the source. In practice this is used for `realtime_status` of
  sources which only provide static data.

Static and realtime imports run on different schedules: static data is pulled nightly, realtime data every few minutes
(see above).

#### Realtime updates are blocked while static data is not active

Realtime data only makes sense on top of an up-to-date set of parking sites/spots. For that reason, **a realtime import
is skipped as long as the source's `static_status` is not `ACTIVE`**. Concretely, if a static import fails, the
`static_status` is set to `FAILED`, and every following realtime import for that source returns early without doing
anything — the `realtime_status` is left untouched, so it keeps its previous value.

Because static data is only pulled once per night by default, a failed static import means realtime updates stay blocked
until the next successful static pull. The realtime data will silently go stale (and eventually be flagged as outdated
via `REALTIME_OUTDATED_AFTER_MINUTES` in the Prometheus endpoint) even though the realtime source itself might be fine.

#### Recovering with `flask source pull`

To recover a source without waiting for the next nightly run, trigger an immediate pull for the affected source. The
`flask source pull` command first runs the static import and then, on success, the realtime import in one go:

```bash
make docker-run CMD="flask source pull my_source_uid"
```

A successful static import sets `static_status` back to `ACTIVE`, which immediately unblocks realtime updates, and the
realtime import that follows in the same command brings the realtime data up to date again. If the static import keeps
failing, the underlying source problem has to be fixed first — see [Debugging data sources](#debugging-data-sources)
for how to inspect the actual upstream requests and responses. See
[Flask command line interface](#flask-command-line-interface) for more details on the `flask source` commands.

#### `has_realtime_data` and outdated realtime data in the public API

Every `ParkingSite` and `ParkingSpot` carries a `has_realtime_data` flag and, when it is `true`, a set of `realtime_*`
fields (e.g. `realtime_capacity`, `realtime_free_capacity`, `realtime_status`, `realtime_data_updated_at`).

When serving public `ParkingSite` and `ParkingSpot` data, ParkAPI does not trust stale realtime data: if a dataset's
`realtime_data_updated_at` is older than `UNSET_REALTIME_AFTER_MINUTES` (default 30 minutes, configurable), it is
treated as if it had no realtime data at all. In that case `has_realtime_data` is returned as `false` and all
`realtime_*` fields are dropped from the output. Datasets without realtime support (`has_realtime_data` already `false`)
never expose `realtime_*` fields.

This calculation can be turned off per request with the `calculate_has_realtime_data` query parameter, which is
available on all four public list and item endpoints (`/v3/parking-sites`, `/v3/parking-sites/<id>`,
`/v3/parking-spots` and `/v3/parking-spots/<id>`):

- `calculate_has_realtime_data=true` (default): the behaviour described above is applied.
- `calculate_has_realtime_data=false`: the outdating calculation is skipped and the raw, stored `has_realtime_data`
  value (and its `realtime_*` fields) is returned unchanged.

Note that this outdating logic is independent of the Prometheus `REALTIME_OUTDATED_AFTER_MINUTES` setting, which only
affects monitoring metrics and not the public API output.


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


## Official region code

Every `ParkingSite` and `ParkingSpot` carries an optional `official_region_code` field. For Germany this holds the
official *Regionalschlüssel* / *Gemeindeschlüssel*, the administrative key which identifies the municipality a parking
site or spot is located in. The code is not provided by the data sources but derived automatically from the object's
coordinates during import, the same way the OCPDB does it for its `Location` model.

### How it is assigned

Whenever a parking site or spot is imported (both via pull and push), ParkAPI tries to assign an
`official_region_code`. A code is only assigned if:

- the object does not already have a code set,
- it has valid `lat`/`lon` coordinates, and
- a region code database is available for the country (currently only Germany / `DEU` is supported).

The actual lookup is a PostGIS spatial query: the coordinates are matched against the municipality polygons via
`ST_Contains`. If no polygon contains the coordinates, the code is left empty and a warning is logged. If the
coordinates fall outside of the imported data (e.g. a parking site outside of Germany), no code is assigned.

Because the lookup relies on PostGIS spatial functions, the feature is **only available on PostgreSQL/PostGIS**, not on
MySQL/MariaDB. The presence of the region code database is detected at runtime, so ParkAPI keeps working (just without
region codes) until the database has been imported.

### Importing the region code database

The region codes live in a separate `regionalschluessel` table which is **not** managed by the ORM or by migrations.
It is imported from the official German administrative boundaries geopackage (VG25) via `ogr2ogr`. The import logic is
in `scripts/import-regionalschluessel.sh`, which downloads the geopackage (if not already present) and loads the
`v_vg25_gem` layer into the `regionalschluessel` table, reprojecting it to EPSG:4326. A marker file
(`/data/.vg25-imported`) prevents re-importing on subsequent runs.

In the docker dev environment this runs automatically via the `regionalschluessel-importer` container (see
`docker-compose.yml`), which uses a GDAL image and waits for PostgreSQL to be healthy before importing. You can also
trigger the import manually with `make import-regionalschluessel`. It can be configured with the following environment
variables:

- `VG25_GEOPACKAGE_URL`: download URL of the VG25 geopackage. Defaults to the MobiData BW mirror.
- `VG25_GEOPACKAGE_WGET_USER_AGENT`: user agent used for the download.

Once the table is imported, region codes are assigned automatically on the next import of a source. To backfill codes
for already-imported data, trigger a fresh import (e.g. via `flask source pull`).


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


### Reset duplicates

In order to reset all duplicates, you can use the endpoint `/api/admin/v1/parking-sites/duplicates/reset`.

There is a helper script for this, too:

```
python reset-duplicates.py username
```

It accepts following parameters:
- `-u` for a custom URL. If you cant to use this script for another environment, you will have to set the url. For
  example, if you cant to do a local test, you have to set it to `-u http://localhost:5000`.
- `-p` for a purpose to filter for.


## Flask command line interface

Besides the standalone helper scripts in `scripts/` (see above), ParkAPI ships a set of CLI commands which run
inside the application context. They are implemented as [Flask CLI](https://flask.palletsprojects.com/en/stable/cli/)
commands and registered in `webapp/cli/`. As they need a working application context (database, config, RabbitMQ), they
are usually run inside the `flask` docker container.

The application entrypoint is configured via `FLASK_APP="webapp:launch()"` (see `.flaskenv`), so you can invoke any
command with `flask <command>`. Inside the docker dev environment, the most convenient way is the `docker-run` makefile
target, which runs an arbitrary command in the `flask` container:

```bash
make docker-run CMD="flask <command>"
```

Alternatively, open a shell in the container with `make docker-shell` and run `flask <command>` directly.

### Source commands

The `source` command group bundles all data-source related commands. Run `flask source --help` for an overview.

- `flask source init-converters`: creates or updates all sources configured in `PARK_API_CONVERTER` in the database
  (both static and realtime metadata). This is the same command the `flask-init-converters` init container runs on
  startup, so a fresh dev environment already has its sources set up.

  ```bash
  make docker-run CMD="flask source init-converters"
  ```

- `flask source pull SOURCE`: triggers an immediate pull import (static and realtime) for a single generic/pull source,
  identified by its `source_uid`. Useful for testing a converter without waiting for the scheduled Celery task.

  ```bash
  make docker-run CMD="flask source pull my_source_uid"
  ```

- `flask source xlsx-import SOURCE IMPORT_FILE_PATH`: imports parking sites for a source from a local XLSX file. The
  file path is resolved inside the container, so make sure the file is available there (e.g. via the mounted project
  directory).

  ```bash
  make docker-run CMD="flask source xlsx-import my_source_uid data/my-file.xlsx"
  ```

- `flask source delete SOURCE_UID`: deletes a source and **all** of its parking sites. This is irreversible, so use it
  with care.

  ```bash
  make docker-run CMD="flask source delete my_source_uid"
  ```

### Built-in Flask commands

A few commands come from Flask and its extensions and are wrapped by makefile targets for convenience:

- `flask db upgrade` / `flask db downgrade` / `flask db migrate -m "..."`: database migrations provided by
  [Flask-Migrate](https://flask-migrate.readthedocs.io/). Use `make apply-migrations`, `make downgrade-migrations` and
  `make generate-migration MSG="..."` respectively.
- `flask shell`: an interactive Python shell with the application context loaded. Use `make flask-shell`.


## Application entrypoints

The actual long-running processes are started via dedicated entrypoint scripts in the project root. In the docker dev
environment they are wired up as container commands in `docker-compose.yml`, so you normally do not run them by hand:

- `run_flask_dev.py`: starts the Flask development server (the `flask` container, reachable at
  `http://localhost:5000`).
- `run_celery_dev.py`: starts a Celery worker which processes background tasks like data pulls (the `worker`
  container).
- `run_celery_heartbeat_dev.py`: starts the Celery beat scheduler which regularly enqueues the periodic import tasks
  (the `worker-heartbeat` container). Both worker and heartbeat are required for pull imports to run.

For production deployments, the application is served as a WSGI app via `webapp:launch()` and the Celery worker/beat
are started with the regular Celery CLI against `webapp.entry_point_celery:celery`.


## Configuration

Besides `PARK_API_CONVERTER`, there are a few other configuration options to set, you will find valid config keys in
`config_dist_dev.yaml`. You can set config values by two different approaches (or even mix them):

1) You can create a config file called `config.yaml` in your root folder.
2) You can set any config value by env var, but you have to prefix the config name with `PARKAPI_` then. For example,
   you can configure `SECRET_KEY` using the env var `PARKAPI_SECRET_KEY`. ENV vars overwrite values given via config
   file.

### Source configuration

The config key `PARK_API_CONVERTER`, a list of dicts, provides the source config.

```yaml
PARK_API_CONVERTER:
  - uid: pull_converter
  - uid: push_converter
    hash: 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
  - uid: generic_converter
    hash: 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
    generic_source: true
  - uid: env_var_converter
    env:
      PARK_API_DEMO_ENV_VAR: demo_env_value
      PARK_API_OTHER_DEMO_ENV_VAR: other_demo_env_value
```

* `pull_converter` is an example for a simple pull converter. If the pull converter works without credentials,
  one does not need any additional parameters. The converter `uid` has to be available
  [at ParkAPI Sources](https://github.com/ParkenDD/parkapi-sources-v3).
* `push_converter` is an example for a simple push converter. This enables a BasicAuth user. You will need a `hash`,
  which is a SHA256-hash of the BasicAuth password. The `uid` will be used as BasicAuth username. The converter `uid`
  has to be available [at ParkAPI Sources](https://github.com/ParkenDD/parkapi-sources-v3).
* `generic_converter` is an example for a generic converter using the REST API endpoints, not needing
  a converter provided by ParkAPI Sources. Credentials work pretty much the same as described in
  `push_converter`.
* `env_var_converter` is an example for a converter needing additional information to work, usually credentials. You
  can look up these env vars at the specific ParkAPI sources converter.

Additionally, you can add source UIDs to `DEBUG_SOURCES`. This enables a debug mode, where all requests are dumped to
a path which is defined at `DEBUG_DUMP_DIR`, defaulting to `data/debug-dump`. Especially at realtime sources, this
might end up into a lot of data dumped to your disk, so use this mechanism with caution (or plenty of storage space).

### Import and realtime parameters

The following config keys control when data is pulled and how long realtime data is considered valid. All of them have
sensible defaults (shown below), so you only need to set them if you want to deviate from the default behaviour.

| Config key                       | Default | Description                                                                                                                                                                                                                                                                            |
|----------------------------------|---------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `STATIC_IMPORT_PULL_HOUR`        | `1`     | Hour of the day (0–23, server time) at which the nightly static data pull for all pull sources is scheduled.                                                                                                                                                                           |
| `STATIC_IMPORT_PULL_MINUTE`      | `0`     | Minute of the hour (0–59) at which the static data pull runs, combined with `STATIC_IMPORT_PULL_HOUR`.                                                                                                                                                                                 |
| `REALTIME_IMPORT_PULL_FREQUENCY` | `300`   | Interval in seconds between realtime data pulls for realtime pull sources. The default of `300` pulls every 5 minutes.                                                                                                                                                                 |
| `REALTIME_OUTDATED_AFTER_MINUTES`| `30`    | Age in minutes after which a parking site's / spot's realtime data is counted as outdated in the Prometheus metrics (`/metrics`). This only affects monitoring; it does not change the served API data.                                                                                |
| `UNSET_REALTIME_AFTER_MINUTES`   | `15`    | Age in minutes after which realtime data is hidden in the public API. When a parking site's `realtime_data_updated_at` is older than this, `has_realtime_data` is set to `False` and all `realtime_*` fields are dropped from the response, so clients never receive stale realtime data. |

Note that `STATIC_IMPORT_PULL_*` and `REALTIME_IMPORT_PULL_FREQUENCY` only affect **pull** sources; **push** sources
deliver data on their own schedule. `UNSET_REALTIME_AFTER_MINUTES` applies to all sources, regardless of pull or push.


## Development setup

ParkAPI provides some help to get a development environment. As you will need a PostgreSQL database for a working setup,
the development setup is built on docker and docker compose. Additionally, there are some makefile targets for common
tasks.

The development setup is tested with common linux distributions with an installed `docker` and `docker compose`. MacOS
will work, too, Windows not so much.

The ParkAPI dev environment starts the following containers:

- `flask`: the main application, reachable at `http://localhost:5000`
- `worker`: the background worker, eg for pulling data sources
- `worker-heartbeat`: a celery heartbeat, responsible for regular creating tasks for the worker
- `flask-init-converters`: an init container which will create / update configured datasources in our database
- `postgresql`: the database, reachable at `localhost:5432` (eg for looking into data using an SQL client)
- `rabbitmq`: the queue connecting `flask`, `worker-heartbeat` and `worker`
- `mocked-loki`: a small flask service for mocking loki, outputting every data pushed to stdout

The following makefile targets help with regular tasks. All of them are just shortcuts to commands you can run
manually, too. For further details, please have a look at the `Makefile`.

- `make first-start`: shortcut to create a working dev environment. Pulls and builds images, copies and migrates the database
- `make docker-up` or just `make`: starts all containers in foreground, which is helpful to get all logs
- `make docker-up-detached`: starts all containers in background
- `make docker-down`: stops all containers
- `make docker-purge`: purges all containers including volumes, good for a fresh start
- `make docker-rebuild`: rebuilds local python image
- `make docker-logs`: outputs container logs, supports `SERVICE` for limit to a specific service, eg `make docker-logs SERVICE=flask`
- `make docker-shell`: get a shell inside the `flask` docker container, helpful for debugging in container / flask scope
- `make apply-migrations`: applies database migrations to the database
- `make downgrade-migrations`: downgrades the database by one migration
- `make generate-migration MSG="my new migration"`: creates a new database migration
- `make import-regionalschluessel`: imports the region code database (VG25) into the `regionalschluessel` table
- `make test-unit`: runs all unit tests
- `make test-integration`: runs all integration tests
- `make lint-fix`: runs the formatter / linter and tries to fix issues
- `make lint-check`: runs the formatter / linter and checks for issues

Additionally, there is a pre-commit-hook, which also helps with linting. For more information and tutorials, please
have a look at the [pre-commit-hook website](https://pre-commit.com). If you have a working pre-commit setup, you can
install the pre-commit-hook with `pre-commit install`.


## Testing

ParkAPI provides unit- and integration-tests. Unit tests run without any external dependencies, integration tests
require at least a working Flask context, but most times external services like `postgresql` and / or `rabbitmq`. You
can run the tests with the makefile targets above.

ParkAPI testing is based on [pytest](https://docs.pytest.org/en/stable/). There are some fixtures which will help to
write tests, especially a flask test client which will reset the database for any new test run. Please have a look at
the `conftest.py` files for more details.


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
provides a Loki and an OpenTelemetry integration to send properly tagged log messages to a Loki or other log collection
instance. This is using the push handlers plus the formatters
`webapp.common.logging.loki_formatter.LokiFormatter` or
`webapp.common.logging.open_telemetry_formatter.OpenTelemetryFormatter`. See `config_dist_dev.yaml` for details.

## Extending and fixing ParkAPI

Merge requests are very welcome. Please keep in mind that ParkAPI v3 is an open source project under MIT licence, so any
code you add should be compatible with this licence. Bug reports are welcome, too, of course.
