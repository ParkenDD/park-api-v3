"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from pathlib import Path


def load_admin_client_request_input(file: str) -> dict | list:
    json_path = Path(Path(__file__).parent.parent.parent, 'request_input', 'admin_rest_api', f'{file}.json')
    with json_path.open('r') as json_file:
        return json.loads(json_file.read())
