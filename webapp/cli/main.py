"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import Flask

from webapp.cli.parking_site import parking_site_cli


def register_cli_to_app(app: Flask):
    app.cli.add_command(parking_site_cli)
