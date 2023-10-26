"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask_failsafe import failsafe
from werkzeug._reloader import run_with_reloader


@failsafe
def run():
    from webapp.entry_point_celery import celery
    celery.start(argv=['--quiet', 'beat'])


if __name__ == '__main__':
    run_with_reloader(run)
