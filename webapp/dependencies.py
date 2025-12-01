"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import functools
from typing import TYPE_CHECKING, Callable, Type, TypeVar

from sqlalchemy.orm import scoped_session

from webapp.common.celery import CeleryHelper
from webapp.common.config import ConfigHelper
from webapp.common.contexts import ContextHelper
from webapp.common.remote_helper import RemoteHelper
from webapp.common.rest import RequestHelper
from webapp.common.server_auth import ServerAuthHelper
from webapp.repositories import (
    BaseRepository,
    ParkingSiteGroupRepository,
    ParkingSiteHistoryRepository,
    ParkingSiteRepository,
    ParkingSpotRepository,
    SourceRepository,
)
from webapp.services.import_service import GenericImportService
from webapp.services.import_service.generic import GenericParkingSiteImportService, GenericParkingSpotImportService
from webapp.services.matching_service import MatchingService
from webapp.services.sqlalchemy_service import SqlalchemyService

if TYPE_CHECKING:
    from webapp.common.events import EventHelper
    from webapp.services.import_service.generic.generic_import_runner import GenericImportRunner


T = TypeVar('T')
T_Repository = TypeVar('T_Repository', bound=BaseRepository)


def cache_dependency(fn: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator for methods of the Dependencies class that caches their return value inside the _cached_dependencies dict.
    """
    # Get name of wrapped function minus the "get_" prefix
    name = fn.__name__
    name = name[4:] if name.startswith('get_') else name

    @functools.wraps(fn)
    def wrapper(*args) -> T:
        self = args[0]
        # Check if dependency is cached
        if name not in self._cached_dependencies:
            # Create dependency by calling the wrapped function and cache it
            self._cached_dependencies[name] = fn(self)

        # Return the dependency from cache
        return self._cached_dependencies[name]

    return wrapper


class Dependencies:
    """
    Container class for dependency injection.

    Dependencies will be created as needed and cached in a dictionary by the "get_" methods.
    """

    # Dictionary for caching the dependencies
    _cached_dependencies: dict

    def __init__(self):
        self._cached_dependencies = {}

    @cache_dependency
    def get_celery_helper(self) -> CeleryHelper:
        return CeleryHelper()

    @cache_dependency
    def get_config_helper(self) -> ConfigHelper:
        return ConfigHelper()

    @cache_dependency
    def get_remote_helper(self) -> RemoteHelper:
        return RemoteHelper(
            config_helper=self.get_config_helper(),
        )

    @cache_dependency
    def get_context_helper(self) -> ContextHelper:
        return ContextHelper()

    @cache_dependency
    def get_request_helper(self) -> RequestHelper:
        return RequestHelper()

    @cache_dependency
    def get_server_auth_helper(self) -> ServerAuthHelper:
        return ServerAuthHelper(
            config_helper=self.get_config_helper(),
            context_helper=self.get_context_helper(),
        )

    @cache_dependency
    def get_event_helper(self) -> 'EventHelper':
        from webapp.common.events import EventHelper

        return EventHelper(
            celery_helper=self.get_celery_helper(),
            context_helper=self.get_context_helper(),
        )

    # Database
    @cache_dependency
    def get_db_session(self) -> scoped_session:
        # Late import (don't initialize all the extensions unless needed)
        from webapp.extensions import db

        return db.session

    # Repositories
    def _create_repository(self, repository_cls: Type[T_Repository], **kwargs) -> T_Repository:
        return repository_cls(
            session=self.get_db_session(),
            **kwargs,
        )

    @cache_dependency
    def get_parking_spot_repository(self) -> ParkingSpotRepository:
        return self._create_repository(ParkingSpotRepository)

    @cache_dependency
    def get_parking_site_repository(self) -> ParkingSiteRepository:
        return self._create_repository(ParkingSiteRepository)

    @cache_dependency
    def get_parking_site_history_repository(self) -> ParkingSiteHistoryRepository:
        return self._create_repository(ParkingSiteHistoryRepository)

    @cache_dependency
    def get_parking_site_group_repository(self) -> ParkingSiteGroupRepository:
        return self._create_repository(ParkingSiteGroupRepository)

    @cache_dependency
    def get_source_repository(self) -> SourceRepository:
        return self._create_repository(SourceRepository)

    def get_base_service_dependencies(self) -> dict:
        return {
            'context_helper': self.get_context_helper(),
            'config_helper': self.get_config_helper(),
            'event_helper': self.get_event_helper(),
        }

    @cache_dependency
    def get_sqlalchemy_service(self) -> SqlalchemyService:
        return SqlalchemyService(
            **self.get_base_service_dependencies(),
        )

    @cache_dependency
    def get_generic_parking_site_import_service(self) -> GenericParkingSiteImportService:
        return GenericParkingSiteImportService(
            source_repository=self.get_source_repository(),
            parking_site_repository=self.get_parking_site_repository(),
            parking_site_history_repository=self.get_parking_site_history_repository(),
            parking_site_group_repository=self.get_parking_site_group_repository(),
            **self.get_base_service_dependencies(),
        )

    @cache_dependency
    def get_generic_parking_spot_import_service(self) -> GenericParkingSpotImportService:
        return GenericParkingSpotImportService(
            source_repository=self.get_source_repository(),
            parking_site_repository=self.get_parking_site_repository(),
            parking_spot_repository=self.get_parking_spot_repository(),
            **self.get_base_service_dependencies(),
        )

    @cache_dependency
    def get_generic_import_service(self) -> GenericImportService:
        return GenericImportService(
            source_repository=self.get_source_repository(),
            generic_parking_site_import_service=self.get_generic_parking_site_import_service(),
            generic_parking_spot_import_service=self.get_generic_parking_spot_import_service(),
            **self.get_base_service_dependencies(),
        )

    @cache_dependency
    def get_matching_service(self) -> MatchingService:
        return MatchingService(
            parking_site_repository=self.get_parking_site_repository(),
            **self.get_base_service_dependencies(),
        )

    @cache_dependency
    def get_generic_import_runner(self) -> 'GenericImportRunner':
        from webapp.services.import_service.generic.generic_import_runner import GenericImportRunner

        return GenericImportRunner(
            celery_helper=self.get_celery_helper(),
            config_helper=self.get_config_helper(),
            generic_import_service=self.get_generic_import_service(),
        )


# Instantiate one global dependencies object so we don't need to clutter the environment with lots of globals
dependencies: Dependencies = Dependencies()
