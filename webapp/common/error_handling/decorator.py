"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import traceback
from functools import wraps

from webapp.dependencies import dependencies


def catch_exception(func):
    @wraps(func)
    def with_catch_exception(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            dependencies.get_logger().error('cli', '%s' % e, traceback.format_exc())

    return with_catch_exception
