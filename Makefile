DOCKER_COMPOSE = docker compose -f docker-compose.yml -f docker-compose.override.yml
FLASK_RUN = $(DOCKER_COMPOSE) run --rm flask

DOCKER_REGISTRY = ghcr.io

# Separate environment for running integration tests
TESTING_COMPOSE_PROJECT_NAME = park-api_integrationtests
TESTING_DOCKER_COMPOSE = $(DOCKER_COMPOSE) -p $(TESTING_COMPOSE_PROJECT_NAME)

# Include local file with custom variables/rules (only if the file exists)
-include Makefile.env

# Default target when running `make`
.PHONY: all
all: docker-up


# Configuration
# -------------

.PHONY: config
config: .env config.yaml

# Create .env file to set the UID/GID for the docker containers to run as to the current user
.env:
	echo "DOCKER_LOCAL_USER=$(shell id -u):$(shell id -g)" >> .env

# Create config file from config_dist_dev.yaml if it does not exist yet
config.yaml:
	cp config_dist_dev.yaml config.yaml


# Container management
# --------------------

.PHONY: first-start
first-start: config docker-login docker-build apply-migrations
	$(DOCKER_COMPOSE) down
	@echo
	@echo 'Database is all set up! \o/'
	@echo 'You can now start the project with "make docker-up"'

# Login to Docker registry
.PHONY: docker-login
docker-login:
	docker login $(DOCKER_REGISTRY)

# Builds and starts all docker containers
.PHONY: docker-up
docker-up: config docker-build
	$(DOCKER_COMPOSE) up

# Start containers in background (or recreate containers while they are running attached to another terminal)
.PHONY: docker-up-detached
docker-up-detached: config docker-build
	$(DOCKER_COMPOSE) up --detach

.PHONY: docker-down
docker-down: .env
	$(DOCKER_COMPOSE) down --remove-orphans
	$(TESTING_DOCKER_COMPOSE) down --remove-orphans

.PHONY: docker-testing-down
docker-testing-down: .env
	$(TESTING_DOCKER_COMPOSE) down --remove-orphans --volumes

# Restart all containers (default) or only the containers specified by SERVICE (e.g. `make docker-restart SERVICE=flask`)
.PHONY: docker-restart
docker-restart: .env
	$(DOCKER_COMPOSE) restart $(SERVICE)

# Tear down all containers and delete all volumes
.PHONY: docker-purge
docker-purge: .env
	$(DOCKER_COMPOSE) down --remove-orphans --volumes
	$(TESTING_DOCKER_COMPOSE) down --remove-orphans --volumes

# Build the Docker image for the flask service
.PHONY: docker-build
docker-build: .env
	$(DOCKER_COMPOSE) build flask

# Force a rebuild of all images (including pulling the base images)
.PHONY: docker-rebuild
docker-rebuild: .env
	$(DOCKER_COMPOSE) build --no-cache --pull flask

# Pull all images except for locally built images
.PHONY: docker-pull
docker-pull: .env
	$(DOCKER_COMPOSE) pull --ignore-buildable

# Show application logs, optionally with `make docker-logs SERVICE=flask` only for specified containers
.PHONY: docker-logs
docker-logs: .env
	$(DOCKER_COMPOSE) logs -f $(SERVICE)

# Run arbitrary commands in the flask docker container
.PHONY: docker-run
docker-run: config
	@test -n "$(CMD)" || ( echo 'Usage: make docker-run CMD="insert command here"'; exit 1 )
	$(FLASK_RUN) $(CMD)

# Start a shell (bash) in the flask docker container
.PHONY: docker-shell
docker-shell: config
	$(FLASK_RUN) bash

# Start an interactive Python shell with Flask application context in a docker container
.PHONY: flask-shell
flask-shell: config
	$(FLASK_RUN) flask shell


# Database management
# -------------------

# Runs database migrations to upgrade the database to the current version (with "migrate" as an shorter alias)
.PHONY: apply-migrations migrate
migrate: apply-migrations
apply-migrations: config
	$(FLASK_RUN) flask db upgrade

# Runs database migrations to DOWNGRADE the database to the previous version
.PHONY: downgrade-migrations
downgrade-migrations: config
	$(FLASK_RUN) flask db downgrade

# Auto-generates a new database migration (requires a revision message as MSG)
.PHONY: generate-migration
generate-migration: config
	@test -n "$(MSG)" || ( echo 'Usage: make generate-migration MSG="Example revision message"'; exit 1 )
	$(FLASK_RUN) flask db migrate -m "$(MSG)"


# Cleanup
# -------

# Clean up "volatile" files (caches, test reports, venv, generated assets, ...)
.PHONY: clean
clean: docker-down
	rm -rf node_modules/ logs/ venv/ static/js/ static/webpack-assets.json reports/ .pytest_cache .coverage .npm

# Clean up whole environment (like "clean", but also removes config files and database files)
.PHONY: clean-all
clean-all: docker-purge clean
	rm config.yaml .env


# Test suites
# -----------

# Run unit tests only
.PHONY: test
test: test-unit

# Run all test suites (unit and integration tests)
.PHONY: test-all
test-all: test-unit test-integration

# Run unit tests only and generate coverage report in HTML format
.PHONY: test-unit
test-unit: config
	$(FLASK_RUN) python -m pytest tests/unit --cov=webapp --cov-report=html

# Run integration tests in a separate environment
.PHONY: test-integration
test-integration: config
	$(TESTING_DOCKER_COMPOSE) run --rm flask python -m pytest tests/integration
	$(TESTING_DOCKER_COMPOSE) down

# Open coverage report in browser (determined by BROWSER env variable, defaults to firefox)
.PHONY: open-coverage
open-coverage:
	@test -f ./reports/coverage_html/index.html || make test-unit
	$(or $(BROWSER),firefox) ./reports/coverage_html/index.html


.PHONY: lint-fix
lint-fix:
	$(FLASK_RUN) ruff --exclude webapp/converters --fix ./webapp
	$(FLASK_RUN) black --exclude webapp/converter ./webapp

.PHONY: lint-check
lint-check:
	$(FLASK_RUN) ruff --exclude webapp/converter ./webapp
	$(FLASK_RUN) black --exclude webapp/converter -S --check --diff webapp
