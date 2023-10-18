"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import functools

from webapp.dependencies import dependencies

from .server_auth_helper import ServerAuthHelper
from .server_auth_users import ServerAuthRole


def require_roles(*roles: ServerAuthRole, require_all: bool = False):
    """
    Decorator for server API view functions that ensures that the authenticated user has the required roles.
    If require_all is True, the user must have ALL of the specified roles, otherwise (default) the user must have
    AT LEAST ONE of the specified roles.

    Raises ServerApiMissingRoleException if the role requirements are not met (or ServerApiUnauthorizedException
    if the request is not authenticated at all).
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check that authenticated user has required roles
            server_auth_helper: ServerAuthHelper = dependencies.get_server_auth_helper()
            server_auth_helper.require_roles(*roles, require_all=require_all)

            # Call wrapped function
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Singular version of require_roles
def require_role(role: ServerAuthRole):
    """
    Decorator for server API view functions that ensures that the authenticated user has the required role.

    Raises ServerApiMissingRoleException if the role requirements are not met (or ServerApiUnauthorizedException
    if the request is not authenticated at all).
    """
    return require_roles(role)


def skip_basic_auth(fn):
    fn.skip_basic_auth = True
    return fn
