"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import argparse
import sys
from getpass import getpass
from pathlib import Path

import requests
from _constants import DATA_TYPES, DEFAULT_BASE_URL, PUSH_BASE_PATH, USER_AGENT


def main():
    parser = argparse.ArgumentParser(
        prog='ParkAPI Push Client',
        description='This client helps to push static ParkAPI data',
    )
    parser.add_argument('source_uid')
    parser.add_argument('file_path')
    parser.add_argument('-u', '--url', default=DEFAULT_BASE_URL, help='Base URL')
    args = parser.parse_args()
    source_uid: str = args.source_uid
    file_path: Path = Path(args.file_path)
    base_url: str = args.url

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

    endpoint = f'{base_url}{PUSH_BASE_PATH}/{file_ending}'
    requests_response = requests.post(
        url=endpoint,
        data=file_data,
        auth=(source_uid, password),
        headers={
            'Content-Type': DATA_TYPES[file_ending],
            'User-Agent': USER_AGENT,
        },
        timeout=300,
    )

    if requests_response.status_code == 200:
        print(f'Upload successful. Result: {requests_response.json()}')  # noqa: T201
        return

    if requests_response.status_code == 400:
        sys.exit(f'Invalid input data: {requests_response.json()}')

    if requests_response.status_code == 401:
        sys.exit('Access denied.')

    sys.exit(f'Unknown error with HTTP status code {requests_response.status_code}.')


if __name__ == '__main__':
    main()
