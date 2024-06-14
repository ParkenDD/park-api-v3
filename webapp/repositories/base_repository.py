"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, Type, TypeVar

from sqlalchemy.orm import scoped_session
from validataclass_search_queries.repositories import SearchQueryRepositoryMixin

from webapp.models import BaseModel
from webapp.repositories.exceptions import ObjectNotFoundException

T_Model = TypeVar('T_Model', bound=BaseModel)


class BaseRepository(SearchQueryRepositoryMixin[T_Model], Generic[T_Model], ABC):
    """
    Base class for data repository classes.

    These classes are used to abstract database access for specific types of data objects (e.g. a UserRepository
    provides methods to retrieve or modify user data in specific ways without caring for the underlying database
    structure, e.g. `fetch_user_by_email()` retrieves a User object for a given email, without meddling with database
    queries (even if those are already abstracted by an ORM).
    """

    # Database session and helpers
    session: scoped_session

    # This abstract property must be set to the model class the repository uses (e.g. `model_cls = User` for the
    # UserRepository)
    @property
    @abstractmethod
    def model_cls(self) -> Type[T_Model]:
        raise NotImplementedError

    def __init__(self, *, session: scoped_session):
        self.session = session

    def commit_transaction(self) -> None:
        """
        Commit the current database transaction by calling `session.commit()`.
        """
        self.session.commit()

    def rollback_transaction(self) -> None:
        """
        Rollback the current database transaction by calling `session.rollback()`.
        """
        self.session.rollback()

    def fetch_resource_by_id(
        self,
        resource_id: int,
        *,
        load_options: Optional[list] = None,
        resource_name: Optional[str] = None,
    ) -> T_Model:
        """
        Fetch a resource by its ID.
        Raises ObjectNotFoundException if the resource does not exist or is out of scope.
        """
        load_options = load_options or []

        resource = self.session.query(self.model_cls).options(*load_options).filter(self.model_cls.id == resource_id).one_or_none()

        return self._or_raise(
            resource,
            f'{resource_name or self.model_cls.__name__} with ID {resource_id} was not found.',
        )

    @staticmethod
    def _or_raise(
        resource: Optional[Any],
        exception_msg: str,
        exception_cls: Type[Exception] = ObjectNotFoundException,
    ) -> Any:
        """
        Returns the resource unless it is None.
        If None, raises an exception with the given message and type (default: `ObjectNotFoundException`).
        """
        if resource is None:
            raise exception_cls(exception_msg)
        return resource

    def _save_resources(self, *resources, commit: bool = True) -> None:
        """
        Saves one or more resources to the database. This means adding the objects to the session, flushing the session
        and (unless `commit=False`) committing the transaction.
        """
        for resource in resources:
            self.session.add(resource)
        self.session.flush()

        if commit:
            self.session.commit()

    def _delete_resources(self, *resources, commit: bool = True) -> None:
        """
        Deletes one or more resources from the database. This means deleting the objects from the session, flushing the
        session and (unless `commit=False`) committing the transaction.
        """
        for resource in resources:
            self.session.delete(resource)
        self.session.flush()

        if commit:
            self.session.commit()
