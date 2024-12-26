"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import Flask, make_response, request


def empty_json_response():
    response = make_response('')
    response.mimetype = 'application/json'
    return response


app = Flask('mocked_loki')


@app.post('/loki/api/v1/push')
def loki_push_logs():
    print(f'<< {request.data}')
    return empty_json_response(), 204


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
