"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import Flask

from webapp.common.json import JSONProvider


class App(Flask):
    """
    Flask application for ParkAPI.
    """

    json_provider_class = JSONProvider
