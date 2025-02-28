"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from logging.handlers import QueueListener


class AutostartQueueListener(QueueListener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start()
