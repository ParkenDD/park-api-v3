"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import argparse
import sys
from getpass import getpass
from pathlib import Path

import requests

DATA_TYPES = {
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'csv': 'text/csv',
    'xml': 'application/xml',
    'json': 'application/json',
}

PUSH_BASE_URL = 'http://localhost:5000/api/admin/v1/generic-parking-sites'


def main():
    parser = argparse.ArgumentParser(
        prog='ParkAPI Push Client',
        description='This client helps to push static ParkAPI data',
    )
    parser.add_argument('source_uid')
    parser.add_argument('file_path')
    args = parser.parse_args()
    source_uid: str = args.source_uid
    file_path: Path = Path(args.file_path)

    if not file_path.is_file():
        sys.exit('Error: please add a file as second argument.')

    password = getpass(f'Password for source UID {source_uid}: ')

    file_ending = None
    for ending in DATA_TYPES:
        if file_path.name.endswith(f'.{ending}'):
            file_ending = ending

    if file_ending is None:
        sys.exit(f'Error: invalid ending. Allowed endings are: {", ".join(DATA_TYPES.keys())}')

    with file_path.open('rb') as file:
        file_data = file.read()

    endpoint = f'{PUSH_BASE_URL}/{file_ending}'
    requests_response = requests.post(
        url=endpoint,
        data=file_data,
        auth=(source_uid, password),
        headers={'Content-Type': DATA_TYPES[file_ending]},
    )

    if requests_response.status_code == 200:
        sys.exit(f'Upload successful. Result: {requests_response.json()}')

    if requests_response.status_code == 400:
        sys.exit(f'Invalid input data: {requests_response.json()}')

    if requests_response.status_code == 401:
        sys.exit('Access denied.')

    sys.exit(f'Unknown error with HTTP status code {requests_response.status_code}.')


if __name__ == "__main__":
    main()
