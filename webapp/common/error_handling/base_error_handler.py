"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import logging
import traceback
from typing import Callable, Optional, Type

from sqlalchemy.orm import scoped_session

from webapp.common.logging import log
from webapp.common.logging.models import LogMessageType

logger = logging.getLogger(__name__)


class BaseErrorHandler:
    """
    Base class for error handlers.
    """

    # Mapping Exception->Callable
    _handlers: dict

    # Dependencies
    db_session: scoped_session

    # Whether the application is running in debug mode. Error handlers may decide to log more detailed errors when in debug mode.
    debug: bool

    def __init__(self, *, db_session: scoped_session, debug: bool = False):
        self._handlers = {}
        self.db_session = db_session
        self.debug = debug

    def register(self, error_class: Type[Exception], func: Callable):
        """
        Registers a handler for a specific type of Exception.
        """
        self._handlers[error_class] = func

    def handle_error(self, error: Exception):
        """
        Looks up the handler for an exception and calls it. Returns the result of the handler, which should be a tuple of an
        HTTP response and a response code. If no handler is registered for the exception, None is returned.
        """
        # Rollback any database transaction that we might be in
        self._rollback_db_transaction()

        # Look up error handler and call it
        handler = self._find_handler(type(error))
        if handler:
            return handler(error)
        return None

    def _find_handler(self, error_class: Type[Exception]) -> Optional[Callable]:
        """
        Finds the most specific handler for this exception by traversing the inheritance hierarchy.
        E.g. for a NotFound exception: First lookup NotFound, then HTTPException, then Exception, then BaseException, then object.
        """
        for cls in error_class.__mro__:
            handler = self._handlers.get(cls)
            if handler is not None:
                return handler

        # No handler found
        return None

    def _rollback_db_transaction(self) -> None:
        """
        Rolls back the current database transaction if there is one.
        """
        self.db_session.rollback()

    def _log_critical(self, error: Exception):
        """
        Helper function to write critical errors to the log.
        """
        log(logger, logging.ERROR, LogMessageType.EXCEPTION, f'{error}: {traceback.format_exc()}')
