"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import Request

from webapp.common.contexts import ContextHelper

from .exceptions import ServerApiMissingRoleException, ServerApiUnauthorizedException
from .server_auth_users import ServerAuthDatabase, ServerAuthRole, ServerAuthUser


class ServerAuthHelper:
    """
    Helper class for server API authentication via Basic Auth.
    """

    server_auth_users: ServerAuthDatabase
    context_helper: ContextHelper

    def __init__(self, *, server_auth_users: ServerAuthDatabase, context_helper: ContextHelper):
        self.server_auth_users = server_auth_users
        self.context_helper = context_helper

    def authenticate_request(self, request: Request) -> None:
        """
        Authenticates a request via Basic Auth. Raises ServerApiUnauthorizedException if authentication fails.
        """
        # First check if the Authorization header was set
        if not request.authorization or not request.authorization.username or not request.authorization.password:
            raise ServerApiUnauthorizedException(message='Missing basic auth credentials')

        # Authenticate user with server auth database
        user = self.server_auth_users.authenticate_user(
            request.authorization.username,
            request.authorization.password,
        )

        # Set user in request context
        request_ctx = self.context_helper.get_request_context()
        request_ctx.server_auth_user = user

    def is_authenticated(self) -> bool:
        """
        Returns True if the current request is authenticated by a server API user.
        """
        # Check user in request context
        request_ctx = self.context_helper.get_request_context()
        return request_ctx is not None and getattr(request_ctx, 'server_auth_user', None) is not None

    def get_current_user(self) -> ServerAuthUser:
        """
        If the current request is authenticated, return the corresponding ServerAuthUser.
        Raises ServerApiUnauthorizedException otherwise.
        """
        # Check request context
        request_ctx = self.context_helper.get_request_context()
        if request_ctx is None:
            raise ServerApiUnauthorizedException('No request context')

        # Get user from request context
        user = getattr(request_ctx, 'server_auth_user', None)
        if user is None:
            raise ServerApiUnauthorizedException('Unauthenticated request')
        return user

    def require_roles(self, *roles: ServerAuthRole, require_all: bool = False) -> None:
        """
        Verifies that the current request is authenticated and that the current user has the required roles.
        If require_all is True, the user must have ALL of the specified roles, otherwise (default) the user must have
        AT LEAST ONE of the specified roles.

        Raises ServerApiMissingRoleException if the role requirements are not met (or ServerApiUnauthorizedException
        if the request is not authenticated at all).
        """
        # Get current user's roles
        user_roles = self.get_current_user().roles

        if require_all:
            # User must have all of the specified roles
            result = all(role in user_roles for role in roles)
        else:
            # User must have at least one of the specified roles
            result = any(role in user_roles for role in roles)

        if not result:
            raise ServerApiMissingRoleException('Insufficient user roles')
