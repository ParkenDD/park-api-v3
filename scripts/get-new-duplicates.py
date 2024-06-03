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
from _helper import load_duplicates, save_duplicates


def main():
    parser = argparse.ArgumentParser(
        prog='ParkAPI: get new duplicates',
        description='This client helps get new duplicates.',
    )
    parser.add_argument('username')
    parser.add_argument(
        '-o',
        '--old-duplicates-file',
        dest='old_duplicates_file',
        help='Old duplicate file. If not provided, all duplicates will be replied.',
    )
    parser.add_argument('-u', '--url', default=DEFAULT_BASE_URL, help='Base URL')
    parser.add_argument('-r', '--radius', type=int, help='Set radius [m]')
    parser.add_argument('-s', '--silence', action='store_true', default=False, help='Silences the non-structured result message.')
    parser.add_argument(
        '-n',
        '--new-duplicates-file',
        dest='new_duplicates_file',
        help="New duplicates file. If not provides, duplicates will be printed to stdout. If it's the same as the old duplicates file, "
        'the old duplicates file will be updated.',
    )
    args = parser.parse_args()

    username: str = args.username
    base_url: str = args.url
    silence: bool = args.silence

    password = getpass(f'Password for {username}: ')

    old_duplicates_file_path: Optional[Path] = None if args.old_duplicates_file is None else Path(args.old_duplicates_file)
    new_duplicates_file_path: Optional[Path] = None if args.new_duplicates_file is None else Path(args.new_duplicates_file)
    radius: Optional[int] = args.radius

    # Check if data can be saved
    if new_duplicates_file_path is not None and new_duplicates_file_path != old_duplicates_file_path:
        if not new_duplicates_file_path.parent.is_dir():
            sys.exit('Error: The new duplicate file needs to have an existing parent directory.')
        if new_duplicates_file_path.is_file():
            sys.exit('Error: the new duplicate file should not exist so far.')

    # Load old duplicates if set
    if args.old_duplicates_file is None:
        old_duplicates: list[tuple[int, int]] = []
    else:
        if not old_duplicates_file_path.is_file():
            sys.exit('Error: please provide a valid duplicate file path.')
        old_duplicates = load_duplicates(old_duplicates_file_path)

    endpoint = f'{base_url}{DUPLICATES_BASE_PATH}/generate'
    requests_response = requests.post(
        url=endpoint,
        json={'old_duplicates': old_duplicates, 'radius': radius},
        auth=(username, password),
        headers={
            'Content-Type': 'application/json',
            'User-Agent': USER_AGENT,
        },
        timeout=300,
    )
    if requests_response.status_code != 200:
        sys.exit(f'Invalid http response code: {requests_response.status_code}: {requests_response.text}')

    response_items: list[dict] = requests_response.json()

    if args.new_duplicates_file is None:
        print(requests_response.text)  # noqa: T201
    else:
        new_duplicates_file_path: Path = Path(args.new_duplicates_file)
        save_duplicates(new_duplicates_file_path, requests_response.json(), append=old_duplicates_file_path == new_duplicates_file_path)

    if silence is False:
        print(f'Got {len(response_items)} new duplicates.')  # noqa: T201


if __name__ == '__main__':
    main()
