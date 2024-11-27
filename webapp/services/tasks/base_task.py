"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import abc
from abc import ABC

from celery.schedules import crontab


class BaseTask(ABC):
    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    @abc.abstractmethod
    def run_interval(self) -> int | crontab:
        raise RuntimeError('Not Implemented')

    @staticmethod
    @abc.abstractmethod
    def task(self):
        raise RuntimeError('Not Implemented')
