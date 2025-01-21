"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import argparse
import sys
from getpass import getpass
from pathlib import Path
from typing import Optional

import requests
from _constants import DEFAULT_BASE_URL, DUPLICATES_BASE_PATH, USER_AGENT
from _helper import load_duplicates


def main():
    parser = argparse.ArgumentParser(
        prog='ParkAPI: apply duplicates',
        description='This client helps apply duplicates.',
    )
    parser.add_argument('username')
    parser.add_argument(
        'duplicates_file',
        help='Duplicate file.',
    )
    parser.add_argument('-u', '--url', default=DEFAULT_BASE_URL, help='Base URL')
    args = parser.parse_args()

    username: str = args.username
    base_url: str = args.url

    password = getpass(f'Password for {username}: ')

    duplicates_file_path: Optional[Path] = None if args.duplicates_file is None else Path(args.duplicates_file)

    # Check if duplicate file exists
    if not duplicates_file_path.is_file():
        sys.exit('Error: please provide a valid duplicate file path.')
    duplicates = load_duplicates(duplicates_file_path, ignore=True)

    endpoint = f'{base_url}{DUPLICATES_BASE_PATH}/apply'
    requests_response = requests.post(
        url=endpoint,
        json=duplicates,
        auth=(username, password),
        headers={
            'Content-Type': 'application/json',
            'User-Agent': USER_AGENT,
        },
        timeout=300,
    )
    if requests_response.status_code != 204:
        sys.exit(f'Invalid http response code: {requests_response.status_code}: {requests_response.text}')


if __name__ == '__main__':
    main()
