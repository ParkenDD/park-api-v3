"""
Copyright 2023 binary butterfly GmbH, Robpol86
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.

This helper class is inspired by Robpol86's Flask-Celery-Helper: https://github.com/Robpol86/Flask-Celery-Helper .
"""

import json
from abc import ABC
from typing import Callable

from celery import Celery, Task, _state
from flask import Flask
from kombu.serialization import register

from webapp.common.json import DefaultJSONEncoder
from webapp.common.logging.models import LogMessageType, LogTag


class CeleryState:
    """Remembers the configuration for the (celery, app) tuple. Modeled from SQLAlchemy."""

    celery: Celery
    app: Flask

    def __init__(self, celery: Celery, app: Flask):
        self.celery = celery
        self.app = app


class LogErrorsCelery(Celery):
    """Celery extension for Flask applications.

    Involves a hack to allow views and tests importing the celery instance from extensions.py to access the regular
    Celery instance methods. This is done by subclassing celery.Celery and overwriting celery._state._register_app()
    with a lambda/function that does nothing at all.

    That way, on the first super() in this class' __init__(), all of the required instance objects are initialized, but
    the Celery application is not registered. This class will be initialized in extensions.py but at that moment the
    Flask application is not yet available.

    Then, once the Flask application is available, this class' init_app() method will be called, with the Flask
    application as an argument. init_app() will again call celery.Celery.__init__() but this time with the
    celery._state._register_app() restored to its original functionality. in init_app() the actual Celery application is
    initialized like normal.
    """

    original_register_app: Callable

    def __init__(self):
        """If app argument provided then initialize celery using application config values.

        If no app argument provided you should do initialization later with init_app method.

        Keyword arguments:
        app -- Flask application instance.
        """
        self.original_register_app = _state._register_app  # Backup Celery app registration function.
        _state._register_app = lambda _: None  # Upon Celery app registration attempt, do nothing.
        super().__init__()

    def init_app(self, app: Flask):
        # register custom encoder, so Enumerations do not make json.dump exceptions
        # In some tutorials they recommend registering an own ContentType when setting encoders because if you set
        # content_type = application/json you will overwrite the old encoder. But if we just want another encoder, this is exactly what we
        # want. We tested this, but if something breaks some time later this might be a place to start.
        register(
            'extended_json',
            lambda obj: json.dumps(obj, cls=DefaultJSONEncoder),
            lambda obj: json.loads(obj),
            content_type='application/json',
            content_encoding='utf-8',
        )

        _state._register_app = self.original_register_app  # Restore Celery app registration function.

        # register as extension (TODO: determine if we need this any more)
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        if 'celery' in app.extensions:
            raise ValueError('Already registered extension CELERY.')
        app.extensions['celery'] = CeleryState(self, app)

        self.conf.update({
            'accept_content': ['extended_json'],
            'task_serializer': 'extended_json',
            'result_serializer': 'extended_json',
        })

        super().__init__(
            app.import_name,
            broker=app.config['CELERY_BROKER_URL'],
            broker_connection_retry_on_startup=True,
        )

        class ContextTask(Task, ABC):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    from webapp.dependencies import dependencies

                    dependencies.get_logger().set_tag(LogTag.INITIATOR, 'celery')
                    return self.run(*args, **kwargs)

            def on_failure(self, exc, _task_id, _args, _kwargs, exc_info):
                with app.app_context():
                    # late import to avoid import loops
                    from webapp.dependencies import dependencies

                    dependencies.get_logger().critical(
                        LogMessageType.EXCEPTION,
                        f'{str(exc).strip()}: {str(exc_info).strip()}',
                    )

        ContextTask.abstract = True
        self.Task = ContextTask
