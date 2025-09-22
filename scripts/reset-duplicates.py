"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import argparse
import re
import string
import sys
from getpass import getpass
from http import HTTPStatus

import requests
from _constants import DEFAULT_BASE_URL, DUPLICATES_BASE_PATH, USER_AGENT


def main():
    parser = argparse.ArgumentParser(
        prog='ParkAPI: reset duplicates',
        description='This client helps to reset duplicates.',
    )
    parser.add_argument('username')
    parser.add_argument('-u', '--url', default=DEFAULT_BASE_URL, help='Base URL')
    parser.add_argument('-p', '--purpose', help='Filter for purpose')
    args = parser.parse_args()

    username: str = args.username
    base_url: str = args.url
    purpose: bool = args.purpose

    password = getpass(f'Password for {username}: ')

    # Remove weird copy-paste fragments
    password = ''.join([c for c in password if c in string.printable])
    password = re.sub(r'^\x5b.{1,3}\x7e', '', password)
    password = re.sub(r'\x5b.{1,3}\x7e$', '', password)

    request_data = {}
    if purpose:
        request_data['purpose'] = purpose

    endpoint = f'{base_url}{DUPLICATES_BASE_PATH}/reset'

    requests_response = requests.post(
        url=endpoint,
        json=request_data,
        auth=(username, password),
        headers={
            'Content-Type': 'application/json',
            'User-Agent': USER_AGENT,
        },
        timeout=300,
    )

    if requests_response.status_code != HTTPStatus.NO_CONTENT:
        sys.exit(f'Invalid http response code: {requests_response.status_code}: {requests_response.text}')


if __name__ == '__main__':
    main()
