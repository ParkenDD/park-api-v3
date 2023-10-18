"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""


class CeleryHelper:
    """
    Helper class for wrapping calls to celery tasks.

    The purpose of this class is to make code that calls/starts celery tasks better unit-testable by wrapping the celery calls.
    For example, `celery_helper.delay(some_task, args...)` would effectively call `some_task.delay(args)`. When writing unit tests,
    you can simply mock the CeleryHelper and just check whether the `delay()` method was called with the correct task.
    """

    # Note: No type hint for the task parameter because PyCharm does not recognize functions with the @celery.task decorator as Tasks...
    @staticmethod
    def delay(task, *args, **kwargs):
        """
        Queues a celery task. Effectively just calls `task.delay(*args, **kwargs)`.
        """
        return task.delay(*args, **kwargs)

    @staticmethod
    def apply_async(task, *args, **kwargs):
        """
        Queues a celery task. Effectively just calls `task.apply_async(*args, **kwargs)`.
        """
        return task.apply_async(*args, **kwargs)

    @staticmethod
    def with_delay(task, delay_seconds: int, *args, **kwargs):
        """
        Queues a celery task with a specified delay.
        """
        return task.apply_async(args=args, kwargs=kwargs, countdown=delay_seconds)
